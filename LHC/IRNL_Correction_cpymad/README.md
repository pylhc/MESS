# Nonlinear correction for LHC

This is a `cpymad` example to setup the LHC with errors and then correct the 
errors in the IRs with the nonlinear correction package.

## Run

The main file is `run.py` which can be run with python 3.7 with the necessary packages installed (see chapter **Setup**).

### Paths

All necessary files to run the example are within this folder, and one can even loop over the 60 different seeds.
If you want to run different setups, you need to set the `PATHS` variables and maybe add some additional optics 
identifiers in `get_optics_path`. 
Both of them are at the top of the file.

## Output

Output is written into `OutputData` folder with `b#` subfolders.
The files directly produced by this script follow the naming convention 
`prefix.machine.beam.stage_id.suffix`.
`machine` is here always `lhc` and the suffix mostly `.tfs`.

There are four different data types identified by their `prefix`:
- `twiss`: Classic madx output files from the `twiss` command (actually written by `tfs-pandas`)
- `errors`: Table of the errors in the machine as from madx `esave` command (actually written by `tfs-pandas`)
- `ampdet`: Amplitude Detuning data as written by PTC.
- `settings`: These are the settings used for the corrector powering.
  `.madx` contains the MADX commands and can be called directly from madx.
  `.tfs` sorts the same data into a nice table.
  This file will also contain an identifier from which beam-optics these corrections were calculated after the `mcx_`.

In there tfs files represent the data at different `stages` of the machine:

 - **nominal**: the virgin machine after loading sequence, applying optics and applying crossing scheme
 - **optics_ir**: as above but only for elements in the IR, as used for correction.
   This file is not needed for correction as the dataframe is passed on in memory.
 - **uncorrected**: after errors are applied
 - **corrected**: after the errors are corrected in the IR (only present if `rdts` are supplied or set to default).

Additionally there is the output as used by `SixTrack` (the `.fc` files).   
Further there are `.log` files that contain either the `full_output` or just the commands as passed on to MADX.
The latter could be used to run with `madx`, but will not produce any output (apart from the `sixtrack` files).


## Setup

Python 3.7+ is required and the dependencies can be installed from the `requirements.txt`. 
This file contains the exact versions this script has been tested with, but it might run with newer
versions as well.



