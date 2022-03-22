"""
Run a cpymad MAD-X simulation for the LHC optics (2018),
assign measured errors from a WISE realization and correct
the nonlinear errors in the IR.
At the end output for SixTrack input is written.

The ``main()`` function set's up the beams and is responsible to assign the
IRNL corrections to the right optics. These are the things that make this
study specific.

The class ``LHCBeam`` is setting up and running cpymad.
This class can be useful for a lot of different studies, by extending
it with extra functionality.
"""
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence, ClassVar, Dict, Union

import pandas as pd
import tfs
from cpymad.madx import Madx
from irnl_rdt_correction.irnl_rdt_correction import main as irnl_correct, write_tfs, write_command
from optics_functions.coupling import coupling_via_cmatrix, closest_tune_approach
from pandas import DataFrame
from tfs import TfsDataFrame

from cpymad_lhc.coupling_correction import correct_coupling
from cpymad_lhc.general import (get_tfs, switch_magentic_errors, match_tune, get_k_strings, amplitude_detuning_ptc,
                                sixtrack_output, get_lhc_sequence_filename_and_bv)
from cpymad_lhc.ir_orbit import orbit_setup, log_orbit
from cpymad_lhc.logging import cpymad_logging_setup, MADXOUT, MADXCMD

LOG = logging.getLogger(__name__)  # setup in main()
LOG_LEVEL = logging.DEBUG

PATHS = {
    # original afs paths ---
    # "db5": Path("/afs/cern.ch/eng/lhc/optics/V6.503"),
    # "optics2016": Path("/afs/cern.ch/eng/lhc/optics/runII/2016"),
    # "optics2018": Path("/afs/cern.ch/eng/lhc/optics/runII/2018"),
    # "external": Path("/afs/cern.ch/work/j/jdilly/public/macros"),
    # "wise": Path("/afs/cern.ch/work/j/jdilly/wise/WISE-2015-LHCsqueeze-0.4_10.0_0.4_3.0-6.5TeV-emfqcs/"),
    # modified for this example ---
    "db5": Path("./lhc_optics"),
    "optics2016": Path("./lhc_optics"),
    "optics2018": Path("./lhc_optics"),
    "external": Path("./external"),
    "wise": Path("./external/wise_2015"),
}


def pathstr(key: str, *args: str) -> str:
    """ Wrapper to get the path (as string! Because MADX wants strings)
    with the base from the dict ``PATHS``.

    Args:
        key (str): Key for the base-path in ``PATHS``.
        args (str): Path parts to attach to the base.

    Returns:
        str: Full path with the base from  given ``key``.
    """
    return str(PATHS[key].joinpath(*args))


def get_optics_path(name: str):
    """ Get optics by name, i.e. a collection of optics path-strings to the optics files.

     Args:
         name (str): Name for the optics.

    Returns:
        str: Path to the optics file.
     """
    optics_map = {
        'inj': pathstr("optics2018", "PROTON", "opticsfile.1"),
        'round3030': pathstr("optics2018", "PROTON", "opticsfile.22_ctpps2")
    }
    return optics_map[name]


def get_wise_path(seed: int):
    """ Get the wise errordefinition file by seed-number.

    Args:
        seed (int): Seed for the error realization.

    Returns:
        str: Path to the wise errortable file.
    """
    return pathstr('wise', f"WISE.errordef.{seed:04d}.tfs")


def drop_allzero_columns(df: TfsDataFrame) -> TfsDataFrame:
    """ Drop columns that contain only zeros, to save harddrive space.

    Args:
        df (TfsDataFrame): DataFrame with all data

    Returns:
        TfsDataFrame: DataFrame with only non-zero columns.
    """
    return df.loc[:, (df != 0).any(axis="index")]


def get_detuning_from_ptc_output(df: DataFrame, beam: int = None, log: bool = True) -> Dict[str, float]:
    """ Convert PTC amplitude detuning output to dict and log values.

    Args:
        df (DataFrame): DataFrame as given by PTC.
        beam (int): Beam used (for logging purposes only)
        log (bool): Print values to the logger

    Returns:
        dict[str, float]: Dictionary with entries 'X', 'Y', 'XY'
        with the values for the direct X, direct Y and cross Term respectively

    """
    map = {"X": "X10", "Y": "Y01", "XY": "X01"}
    results = {name: None for name in map.keys()}
    if log:
        LOG.info("Current Detuning Values" + ("" if not beam else f" in Beam {beam}"))
    for name, term in map.items():
        value = df.query(
            f'NAME == "ANH{term[0]}" and '
            f'ORDER1 == {term[1]} and ORDER2 == {term[2]} '
            f'and ORDER3 == 0 and ORDER4 == 0'
        )["VALUE"].to_numpy()[0]
        if log:
            LOG.info(f"  {name:<2s}: {value}")
        results[name] = value
    return results


@dataclass()
class Correction:
    """ DataClass to store correction data. """
    name: str
    df: TfsDataFrame
    cmd: str


#LHCBeam Dataclass -------------------------------------------------------------

@dataclass()
class LHCBeam:
    """ Object containing all the information about the machine setup and
    performing the MAD-X commands to run the simulation. """
    beam: int
    outputdir: Path
    xing: dict
    errors: dict
    optics: str
    correct_irnl: bool = True
    thin: bool = True
    seed: int = 1
    tune_x: float = 62.31
    tune_y: float = 60.32
    chroma: float = 3
    emittance: float = 7.29767146889e-09
    n_particles: float = 1.0e10   # number of particles in beam
    on_arc_errors: bool = False  # apply field errors to arcs
    # Placeholders (set in functions)
    df_twiss_nominal: TfsDataFrame = field(init=False)
    df_twiss_nominal_ir: TfsDataFrame = field(init=False)
    df_ampdet_nominal: TfsDataFrame = field(init=False)
    df_errors: TfsDataFrame = field(init=False)
    df_errors_ir: TfsDataFrame = field(init=False)
    correction: Correction = field(init=False)
    df_twiss_corrected: TfsDataFrame = field(init=False)
    df_ampdet_corrected: TfsDataFrame = field(init=False)
    # Constants
    ACCEL: ClassVar[str] = 'lhc'
    TWISS_COLUMNS: ClassVar[Sequence[str]] = tuple(['NAME', 'KEYWORD', 'S', 'X', 'Y', 'L', 'LRAD',
                                                    'BETX', 'BETY', 'ALFX', 'ALFY',
                                                    'DX', 'DY', 'MUX', 'MUY',
                                                    'R11', 'R12', 'R21', 'R22'] + get_k_strings())
    ERROR_COLUMNS: ClassVar[Sequence[str]] = tuple(["NAME", "DX", "DY"] + get_k_strings())

    # Init ---

    def __post_init__(self):
        """ Setup the MADX, output dirs and logging as well as additional instance parameters. """
        self.outputdir.mkdir(exist_ok=True, parents=True)
        self.madx = Madx(**cpymad_logging_setup(level=LOG_LEVEL,  # sets also standard loggers
                                                command_log=self.outputdir/'madx_commands.log',
                                                full_log=self.outputdir/'full_output.log'))
        self.logger = {key: logging.getLogger(key).handlers for key in ("", MADXOUT, MADXCMD)}  # save logger to reinstate later
        self.madx.globals.mylhcbeam = self.beam  # used in macros

        # Define Sequence to use
        self.seq_name, self.seq_file, self.bv_flag = get_lhc_sequence_filename_and_bv(self.beam)
        if self.correct_irnl and not self.thin:
            raise NotImplementedError("To correct IRNL errors a thin lattice is required.")

    # Output Helper ---

    def output_path(self, type_: str, output_id: str, dir_: Path = None, suffix: str = ".tfs") -> Path:
        """ Returns the output path for standardized tfs names in the default output directory.

        Args:
            type_ (str): Type of the output file (e.g. 'twiss', 'errors', 'ampdet')
            output_id (str): Name of the output (e.g. 'nominal')
            dir_ (Path): Override default directory.
            suffix (str): suffix of the output file.

        Returns:
            Path: Path to the output file
         """
        if dir_ is None:
            dir_ = self.outputdir
        return dir_ / f'{type_}.lhc.b{self.beam:d}.{output_id}{suffix}'

    def get_twiss(self, output_id=None, index_regex=r"BPM|M|IP", **kwargs) -> TfsDataFrame:
        """ Uses the ``twiss`` command to get the current optics in the machine
        as TfsDataFrame.

        Args:
            output_id (str): ID to use in the output (see ``output_path``).
                             If not given, no output is written.
            index_regex (str): Filter DataFrame index (NAME) by this pattern.

        Returns:
            TfsDataFrame: DataFrame containing the optics.
        """
        kwargs['chrom'] = kwargs.get('chrom', True)
        self.madx.twiss(sequence=self.seq_name, **kwargs)
        df_twiss = self.get_last_twiss(index_regex=index_regex)
        if output_id is not None:
            self.write_tfs(df_twiss, 'twiss', output_id)
        return df_twiss

    def get_last_twiss(self, index_regex=r"BPM|M|IP") -> TfsDataFrame:
        """ Returns the twiss table of the last calculated twiss.

        Args:
            index_regex (str): Filter DataFrame index (NAME) by this pattern.

        Returns:
            TfsDataFrame: DataFrame containing the optics.
        """
        return get_tfs(self.madx.table.twiss, columns=self.TWISS_COLUMNS, index_regex=index_regex)

    def get_errors(self, output_id: str = None, index_regex: str = "M") -> TfsDataFrame:
        """ Uses the ``etable`` command to get the currently assigned errors in the machine
        as TfsDataFrame.

        Args:
            output_id (str): ID to use in the output (see ``output_path``).
                             If not given, no output is written.
            index_regex (str): Filter DataFrame index (NAME) by this pattern.

        Returns:
            TfsDataFrame: DataFrame containing errors.
        """
        # As far as I can tell `only_selected` does not work with
        # etable and there is always only the selected items in the table
        # (jdilly, cpymad 1.4.1)
        self.madx.select(flag='error', clear=True)
        self.madx.select(flag='error', column=self.ERROR_COLUMNS)
        self.madx.etable(table='error')
        df_errors = get_tfs(self.madx.table.error, index_regex=index_regex, columns=self.ERROR_COLUMNS)
        if output_id is not None:
            self.write_tfs(df_errors, 'errors', output_id)
        return df_errors

    def get_ampdet(self, output_id: str) -> TfsDataFrame:
        """ Write out current amplitude detuning via PTC.

        Args:
            output_id (str): ID to use in the output (see ``output_path``).
                             If not given, no output is written.

        Returns:
            TfsDataFrame: Containing the PTC output data.
        """
        file = None
        if output_id is not None:
            file = self.output_path('ampdet', output_id)
            LOG.info(f"Calculating amplitude detuning for {output_id}.")
        df_ampdet = amplitude_detuning_ptc(self.madx, ampdet=2, chroma=4, file=file)
        get_detuning_from_ptc_output(df_ampdet, beam=self.beam)
        return df_ampdet

    def write_tfs(self, df: TfsDataFrame, type_: str, output_id: str):
        """ Write the given TfsDataFrame with the standardized name (see ``output_path``)
        and the index ``NAME``.

        Args:
            df (TfsDataFrame): DataFrame to write.
            type_ (str): Type of the output file (see ``output_path``)
            output_id (str): Name of the output (see ``output_path``)
        """
        tfs.write(self.output_path(type_, output_id), drop_allzero_columns(df), save_index="NAME")

    # Wrapper ---

    def log_orbit(self):
        """ Log the current orbit. """
        log_orbit(self.madx, accel=self.ACCEL)

    def closest_tune_approach(self, df: TfsDataFrame = None):
        """ Calculate and print out the closest tune approach from the twiss
        DataFrame given. If no frame is given, it gets the current twiss.

        Args:
            df (TfsDataFrame): Twiss DataFrame.
        """
        if df is None:
           df = self.get_twiss()
        df_coupling = coupling_via_cmatrix(df)
        closest_tune_approach(df_coupling, qx=self.tune_x, qy=self.tune_y)

    def correct_coupling(self):
        """ Correct the current coupling in the machine. """
        correct_coupling(self.madx,
                         accel=self.ACCEL, sequence=self.seq_name,
                         qx=self.tune_x, qy=self.tune_y,
                         dqx=self.chroma, dqy=self.chroma)

    def match_tune(self):
        """ Match the machine to the preconfigured tunes. """
        match_tune(self.madx,
                   accel=self.ACCEL, sequence=self.seq_name,
                   qx=self.tune_x, qy=self.tune_y,
                   dqx=self.chroma, dqy=self.chroma)

    def apply_measured_errors(self, *magnets: str):
        """ Apply the measured errors to the given magnets via Efcomp-files.

        Args:
            magnets (Sequence[str]): Names of the magnets to apply the errors to.
                                     (As in the Efcomp filenames).
        """
        for magnet in magnets:
            self.madx.call(pathstr('db5', 'measured_errors', f'Efcomp_{magnet}.madx'))

    def reinstate_loggers(self):
        """ Set the saved logger handlers to the current logger. """
        for name, handlers in self.logger.items():
            logging.getLogger(name).handlers = handlers

    def get_other_beam(self):
        """ Return the respective other beam number. """
        return 1 if self.beam == 4 else 4

    # Main ---

    def setup_machine(self):
        """ Nominal machine setup function.
        Initialized the beam and applies optics, crossing. """
        self.reinstate_loggers()
        madx = self.madx  # shorthand
        mvars = madx.globals  # shorthand

        # Load Macros
        madx.call(pathstr("optics2018", "toolkit", "macro.madx"))

        # Lattice Setup ---------------------------------------
        # Load Sequence
        madx.call(pathstr("optics2018", self.seq_file))

        # Slice Sequence
        if self.thin:
            mvars.slicefactor = 4
            madx.beam()
            madx.call(pathstr("optics2018", "toolkit", "myslice.madx"))
            madx.beam()
            madx.use(sequence=self.seq_name)
            madx.makethin(sequence=self.seq_name, style="teapot", makedipedge=True)

        # Cycling w.r.t. to IP3 (mandatory to find closed orbit in collision in the presence of errors)
        madx.seqedit(sequence=self.seq_name)
        madx.flatten()
        madx.cycle(start="IP3")
        madx.endedit()

        # Define Optics and make beam
        madx.call(get_optics_path(self.optics))
        if self.optics == 'inj':
            mvars.NRJ = 450.000  # not defined in injection optics.1 but in the others

        madx.beam(sequence=self.seq_name, bv=self.bv_flag,
                  energy="NRJ", particle="proton", npart=self.n_particles,
                  kbunch=1, ex=self.emittance, ey=self.emittance)

        # Setup Orbit
        orbit_vars = orbit_setup(madx, accel='lhc', **self.xing)

        madx.use(sequence=self.seq_name)

        # Save Nominal
        self.match_tune()
        self.df_twiss_nominal = self.get_twiss('nominal')
        self.df_ampdet_nominal = self.get_ampdet('nominal')
        self.log_orbit()

        # Save nominal optics in IR+Correctors for ir nl correction
        self.df_twiss_nominal_ir = self.get_last_twiss(index_regex="M(QS?X|BX|BRC|C[SOT]S?X)")
        self.write_tfs(self.df_twiss_nominal_ir, 'twiss', 'optics_ir')

    def apply_errors(self):
        """ Apply the errors onto the machine. The state is uncorrected afterwards. """
        self.reinstate_loggers()
        madx = self.madx  # shorthand

        if self.df_twiss_nominal is None:
            raise EnvironmentError("The machine needs to be setup first, before applying errors.")

        # Call error subroutines and measured error table for nominal LHC
        #
        # 'rotations_Q2_integral.tab', 'macro_error.madx' and 'Orbit_Routines.madx' are
        # called twice. It was like that in the mask I got from Ewen.
        # Possibly not neccessary. (jdilly, 2022-03-22)
        madx.call(file=pathstr('optics2016', 'measured_errors', 'Msubroutines.madx'))
        madx.readtable(file=pathstr('optics2016', 'measured_errors', 'rotations_Q2_integral.tab'))
        madx.call(file=pathstr('optics2016', 'errors', 'macro_error.madx'))  # some macros for error generation
        madx.call(file=pathstr('optics2016', 'toolkit', 'Orbit_Routines.madx'))
        madx.call(file=pathstr('optics2016', 'measured_errors', 'Msubroutines_new.madx'))  # think the new subroutines are only relevant for MSS - not used pre-2017 so shouldn't make a difference compared to old Msubroutines...
        madx.call(file=pathstr('optics2016', 'measured_errors', 'Msubroutines_MS_MSS_MO_new.madx'))
        madx.call(file=pathstr('optics2016', 'toolkit', 'Orbit_Routines.madx'))  # 2nd time
        madx.call(file=pathstr('optics2016', 'toolkit', 'SelectLHCMonCor.madx'))
        madx.readtable(file=pathstr('optics2016', 'measured_errors', 'rotations_Q2_integral.tab'))  # 2nd time
        madx.call(file=pathstr('optics2016', 'errors', 'macro_error.madx'))  # 2nd time

        # Apply magnetic errors -------------------------------
        switch_magentic_errors(madx, **self.errors)

        # Read WISE
        madx.readtable(file=get_wise_path(self.seed))

        # Apply errors to elements ---
        if self.on_arc_errors:
            self.apply_measured_errors('MB', 'MQ')

        self.apply_measured_errors(
            # IR Dipoles
            'MBXW',  # D1 in IP1 and IP5
            'MBRC',  # D2
            'MBX',  # D in IP2 and 8
            'MBRB',  # IP4
            'MBRS',  # IP4
            'MBW',  # IP7 and IP3
            # IR Quads
            'MQX',
            'MQY',
            'MQM',
            'MQMC',
            'MQML',
            'MQTL',
            'MQW',
        )

        # Save uncorrected
        if not self.correct_irnl:
            self.closest_tune_approach()
            self.correct_coupling()

        self.match_tune()
        df_twiss_uncorrected = self.get_twiss('uncorrected')
        df_ampdet_uncorrected = self.get_ampdet('uncorrected')
        self.df_errors = self.get_errors('all')
        self.closest_tune_approach(df_twiss_uncorrected)

        # Save errors to table to be used for correction ---------------------------
        self.df_errors_ir = self.get_errors('ir', index_regex=r"M([QB]X|BRC)")

    def apply_corrections(self):
        """ Assumes that ``self.corrections`` has been assigned and applies these.
        They are also written out for reference. Afterwards coupling is corrected
        and the twiss of the corrected machine is written out.
        Additional logging of the CTA and Orbit is done at the end.
        """
        self.reinstate_loggers()
        if not self.correct_irnl:
            raise ValueError("IRNL correction was not selected. Cannot apply correction!")

        if self.correction is None:
            raise ValueError("IRNL correction has not been set. Cannot apply correction!")

        correct_name = f'mcx_{self.correction.name}'
        write_command(self.output_path('settings', correct_name), self.correction.cmd)
        write_tfs(self.output_path('settings', correct_name), self.correction.df)

        # Apply correction
        self.madx.input(self.correction.cmd)

        # Correct Coupling
        self.closest_tune_approach()
        self.correct_coupling()

        # Save corrected
        self.match_tune()
        self.df_twiss_corrected = self.get_twiss('corrected')
        self.df_ampdet_corrected = self.get_ampdet('corrected')

        # Some logging for reference
        self.closest_tune_approach(self.df_twiss_corrected)
        self.log_orbit()

    def write_output_for_sixtrack(self):
        """ Writes the output for sixtrack. """
        self.reinstate_loggers()
        sixtrack_output(self.madx,
                        energy=self.madx.globals.nrj,
                        outputdir=self.outputdir)

    def exit(self):
        """ End attached cpymad MADX instance. """
        self.reinstate_loggers()
        self.madx.exit()


# Correction Wrapper -----------------------------------------------------------

def do_correction(lhc_beams: Sequence[LHCBeam],
                  rdts: Union[str, Sequence[str], Dict[str, Sequence[str]]],
                  rdts2: Union[Sequence[str], Dict[str, Sequence[str]]] = None,
                  feeddown: int = 0, iterations: int = 1) -> Correction:
    """ Calculate the IRNL corrections for the given beam(s).
    For a detailed description of input args, see the ``pylhc.irnl_rdt_correction``.

    Args:
        lhc_beams (Sequence[LHCBeam]): List of LHCBeam objects to use in correction.
        rdts (str, Sequence[str], dict[str, Sequence[str]]): Mapping of field orders to rdts to correct.
        rdts2 (Sequence[str], dict[str, Sequence[str]]): Mapping of field orders to rdts to correct in second optics.
        feeddown (int): Order of feeddown to calculate
        iterations (int): Number of iterations to do.

    Returns:
        Correction: The calculated correction
    """
    # reinstate all loggers
    logging.getLogger("").handlers = [h for lhc_beam in lhc_beams for h in lhc_beam.logger[""]]

    cmd_correction, df_correction = irnl_correct(
        # Correction setup for LHC ---
        beams=[lhc_beam.beam for lhc_beam in lhc_beams],
        optics=[lhc_beam.df_twiss_nominal_ir for lhc_beam in lhc_beams],
        errors=[lhc_beam.df_errors_ir for lhc_beam in lhc_beams],
        rdts=None if rdts == 'default' else rdts,
        rdts2=rdts2,
        accel='lhc',  # accelerator name
        feeddown=feeddown,  # order of feeddown to take into account
        iterations=iterations,  # number of correction iterations
        ignore_corrector_settings=True,  # all correctors are assumed unpowered
        ips=(1, 2, 5, 8),  # in which IPs to correct
        solver='lstsq',  # 'inv', 'linear' Solver to use
        ignore_missing_columns=False,  # True: if columns are missing, assume 0
    )
    return Correction(
        name=''.join(f"b{lhc_beam.beam}" for lhc_beam in lhc_beams),
        cmd=cmd_correction, df=df_correction)


# Main function ----------------------------------------------------------------

def main(outputdirs: Dict[int, Path],
         xing: dict = None,  # set to {'scheme': 'top'} below
         correct_beam: str = 'same',  # correct beam with corrections from itself
         errors: dict = None,  # set to {'default': True} below
         optics: str = 'round3030',  # 30cm round optics
         feeddown: int = 0,
         iterations: int = 1,
         rdts: Union[str, Sequence[str], Dict[str, Sequence[str]]] = 'default',  # uses default RDTs for lhc
         rdts2: Union[Sequence[str], Dict[str, Sequence[str]]] = None,  # use separate corrections per beam
         seed: int = 1,
         ):
    """ Main function to run this script.
    First sets up the LHC machine for the beams defined by the `outputdirs` dict.
    Then runs the IRNL correction and assig

    Args:
        outputdirs (dict): Mapping of beam-number to output directory. Defines which beams to run!
        xing (dict): Crossing scheme definition. See ``cpymad_lhc.ir_orbit.orbit_setup``
        correct_beam (str): How to correct:
                           ``Same`` assigns the corrections to the beam optics they are calculated from.
                           ``Other`` assigns them to the respective other one.
                           ``b#`` assigns the corrections from beam number # to all machines.
                           If ``rdts2`` are given there should be no difference, as all
                           corrections are the same (as they are calculated from both beam optics).
        errors (dict): Error definitions. See ``cpymad_lhc.general.switch_magnetic_errors``
        optics (str): Optics to use. See ``get_optics_path``.
        feeddown (int): Order of feeddown to calculate. See ``irnl_rdt_correction``.
        iterations (int): Number of correction iterations to do. See ``irnl_rdt_correction``.
        rdts (Dict[str, Sequence[str]]): Mapping of field orders to rdts to correct.
                                     See ``irnl_rdt_correction``.
        rdts2 (Dict[str, Sequence[str]]): Mapping of field orders to rdts to correct in second optics.
                                      See ``irnl_rdt_correction``.
                                      If this is given, the corrections are calculated from both beams.
        seed (int): Error realization seed for WISE tables. Between 1-60.

    """
    # Input Checks -------------------------------------------------------------
    if rdts2 is not None and len(outputdirs) != 2:
        raise ValueError("To use 'rdts2' you need to run with two beams/optics.")

    # set mutable defaults ----
    if xing is None:
        xing = {'scheme': 'top'}  # use top-energy crossing scheme

    if errors is None:
        errors = {f"AB{i}": True for i in range(3, 16)}  # activates default errors

    # Setup LHC for both beams -------------------------------------------------
    lhc_beams: Dict[int, LHCBeam] = {}
    for beam, outputdir in outputdirs.items():
        lhc_beam = LHCBeam(
            beam=beam, outputdir=outputdir,
            correct_irnl=rdts is not None,
            xing=xing, errors=errors, optics=optics,
            seed=seed,
        )
        lhc_beams[beam] = lhc_beam
        lhc_beam.setup_machine()
        lhc_beam.apply_errors()

    # IR Nonlinear Correction --------------------------------------------------
    if rdts is not None:
        if rdts2 is None:
            # calculate individually
            for lhc_beam in lhc_beams.values():
                correction = do_correction(
                    [lhc_beam], rdts=rdts, rdts2=rdts2,
                    feeddown=feeddown, iterations=iterations
                )

                # assign to whichever beam should be corrected with these
                if correct_beam == "same":
                    lhc_beams[lhc_beam.beam].correction = correction
                elif correct_beam == "other":
                    lhc_beams[lhc_beam.get_other_beam()].correction = correction
                else:
                    lhc_beams[int(correct_beam[-1])].correction = correction
        else:
            # correct with both optics
            correction = do_correction(
                list(lhc_beams.values()), rdts=rdts, rdts2=rdts2,
                feeddown=feeddown, iterations=iterations
            )

            # assign same correction to both
            for lhc_beam in lhc_beams.values():
                lhc_beam.correction = correction

        # apply corrections
        for lhc_beam in lhc_beams.values():
            lhc_beam.apply_corrections()

    # Write SixTrack output ----------------------------------------------------
    for lhc_beam in lhc_beams.values():
        lhc_beam.write_output_for_sixtrack()

    # End MAD-X instances ------------------------------------------------------
    for lhc_beam in lhc_beams.values():
        lhc_beam.exit()


if __name__ == '__main__':
    main({i: Path(f"OutputData/b{i}") for i in (1, 4)})
    # main({i: Path(f"OutputData/b{i}") for i in (1, 2)})
