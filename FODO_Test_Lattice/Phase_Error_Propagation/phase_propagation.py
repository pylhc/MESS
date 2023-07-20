from dataclasses import dataclass, fields
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import pandas as pd
import tfs
from cpymad.madx import Madx
from matplotlib import colors as mc
from matplotlib import pyplot as plt
from uncertainties import ufloat

RNG = np.random.default_rng(27837)
FloatOrArray = Union[float, np.ndarray, pd.Series]


# Classes ----------------------------------------------------------------------

@dataclass 
class PropagableBoundaryConditions:
    """Store boundary conditions with error for propagating."""
    alpha: ufloat = None
    beta: ufloat = None

    @staticmethod
    def as_tuple(value: ufloat) -> Tuple[float, float]:
        return (value.nominal_value, value.std_dev)


@dataclass 
class MadXBoundaryConditions:
    """Store all boundary conditions for a Mad-X twiss."""
    alfx: float = None
    alfy: float = None
    betx: float = None
    bety: float = None
    dx: float = None
    dy: float = None
    dpx: float = None
    dpy: float = None
    wx: float = None
    wy: float = None
    dphix: float = None
    dphiy: float = None
    r11: float = None
    r12: float = None
    r21: float = None
    r22: float = None

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}


# Main -------------------------------------------------------------------------

def create_realizations(output: Path, n: int = 100) -> pd.DataFrame:
    """Main function to generate the phase advance realizations.
    The mean and std values are hardcoded and choosen to have a final phase advance 
    of around 0.25 (far away from 0.5) in units of 2 Pi.

    Args:
        output (Path): Path to save the output tfs-file.
        n (int, optional): Number of realizations to generate. Defaults to 100.
    """
    madx = generate_fodo()
    madx.twiss(chrom=True)

    x = PropagableBoundaryConditions(alpha=ufloat(-1.6, 0.002), beta=ufloat(3.467, 0.025))
    y = PropagableBoundaryConditions(alpha=ufloat(2.16, 0.002), beta=ufloat(7.14, 0.016))
    no_error = MadXBoundaryConditions(
        alfx=x.alpha.nominal_value, 
        betx=x.beta.nominal_value, 
        alfy=y.alpha.nominal_value, 
        bety=y.beta.nominal_value,
    )
    
    df_ref = generate_df(madx, sequence="fodo", boundary_conditions=no_error)
    
    df = pd.DataFrame()
    df["MUX"] = df_ref.mux
    df["PLUSX"] = propagate_with_plus(dphi=df_ref.mux, init=x)
    df["MINUSX"] = propagate_with_minus(dphi=df_ref.mux, init=x)
    
    df["MUY"] = df_ref.muy
    df["PLUSY"] = propagate_with_plus(dphi=df_ref.muy, init=y)
    df["MINUSY"] = propagate_with_minus(dphi=df_ref.muy, init=y)
    print(df_ref[["mux", "muy"]])

    for idx in range(n):
        with_error = MadXBoundaryConditions(
            alfx=get_realization(x.alpha),
            betx=get_realization(x.beta),
            alfy=get_realization(y.alpha),
            bety=get_realization(y.beta),
        )

        df_err = generate_df(madx, sequence="fodo", boundary_conditions=with_error)
        
        diff_x = (df_err.mux - df_ref.mux) % 1
        diff_y = (df_err.muy - df_ref.muy) % 1
        diff_x[diff_x > 0.5] -= 1
        diff_y[diff_y > 0.5] -= 1

        df[f"MADXX{idx:03d}"] = diff_x
        df[f"MADXY{idx:03d}"] = diff_y

    tfs.write(output, df, save_index="NAME")
    return df


# Helper ---

def generate_fodo(sequence: str ="fodo") -> Madx:
    """Generate a standard FODO sequence.
    
    Args:
        sequence (str): Sequence name.
    """
    madx = Madx()
    madx.beam()
    madx.globals["mqf.k1"] = 0.3037241107
    madx.globals["mqd.k1"] = -madx.globals["mqf.k1"]
    madx.input(f"""
    {sequence}: sequence, l=10, refer=entry;
    mqf: quadrupole, at=0, l=1, k1:=mqf.k1;
    dff: drift,      at=1, l=4;
    mqd: quadrupole, at=5, l=1, k1:=mqd.k1;
    dfd: drift,      at=6, l=4;
    endsequence;
    """)
    madx.use(sequence=sequence)
    return madx


def generate_df(madx: Madx, sequence: str, boundary_conditions: MadXBoundaryConditions = None) -> pd.DataFrame:
    """Generate a dataframe with Mad-X twiss and the given boundary conditions.
    
    Args:
        madx (Madx): Mad-X cpymad object.
        sequence (str): Sequence name.
        boundary_conditions (MadXBoundaryConditions): Boundary conditions.
    """
    if boundary_conditions is None:
        boundary_conditions = MadXBoundaryConditions()

    madx.use(sequence=sequence)
    madx.twiss(sequence=sequence, chrom=True, **boundary_conditions.as_dict())
    return madx.table.twiss.dframe().copy()



# Propagate Errors -------------------------------------------------------------

def propagate_with_minus(dphi: FloatOrArray, init: PropagableBoundaryConditions):
    """Phase error propagation as given in Eq. (2) of the paper,
    but the first plus sign replaced with a minus sign.

    Args:
        dphi (FloatOrArray): Phase advance(s). 
        init (PropagableBoundaryConditions): Initial conditions.

    Returns:
        FloatOrArray: Phase error at the given phase advance(s).
    """
    alpha, erralpha = init.as_tuple(init.alpha)
    beta, errbeta = init.as_tuple(init.beta)

    res = np.sqrt(
        (
                (((np.cos(4 * np.pi * dphi) - 1) * alpha) - 
                 (np.sin(4 * np.pi * dphi))
                 ) * 0.5 * errbeta/beta
        ) ** 2 +
        ((np.cos(4*np.pi*dphi) - 1) * 0.5 * erralpha) ** 2
    ) / (2*np.pi)
    return res

def propagate_with_plus(dphi: FloatOrArray, init: PropagableBoundaryConditions) -> FloatOrArray:
    """Phase error propagation as given in Eq. (2) of the paper.

    Args:
        dphi (FloatOrArray): Phase advance(s). 
        init (PropagableBoundaryConditions): Initial conditions.

    Returns:
        FloatOrArray: Phase error at the given phase advance(s).
    """
    alpha, erralpha = init.as_tuple(init.alpha)
    beta, errbeta = init.as_tuple(init.beta)

    res = np.sqrt(
        (
                (((np.cos(4 * np.pi * dphi) - 1) * alpha) + 
                 (np.sin(4 * np.pi * dphi))
                 ) * 0.5 * errbeta/beta
        ) ** 2 +
        ((np.cos(4 * np.pi*dphi) - 1) * 0.5 * erralpha) ** 2
    ) / (2*np.pi)
    return res



# Random Generators ------------------------------------------------------------


def get_realization(value: ufloat) -> float:
    """Generate a single realization from a gaussian distribution, given 
    the mean and standard deviation.

    Args:
        value (ufloat): The mean and standard deviation of the distribution as 
                        a uncertainty object.

    Returns:
        float: The generated realization.
    """
    return RNG.normal(loc=value.nominal_value, scale=value.std_dev)


# Plotting --------------------------------------------------------------------- 


def plot_realizations(saved_realizations: Union[Path, pd.DataFrame], element: str, bins=20):
    """Plot the generated realizations to compare with the analytical propagation.

    Args:
        saved_realizations (Union[Path, pd.DataFrame]): The generated realizations.
        element (str): Element at which to plot the error on the phase advances.
        bins (int, optional): Number of histogram bins. Defaults to 20.
    """
    try:
        df = tfs.read(saved_realizations, index="NAME")
    except TypeError:
        df = saved_realizations

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    cmap = plt.get_cmap("Set1")
    color_madx = cmap.colors[2]
    color_prop_plus = cmap.colors[0]
    color_prop_minus = cmap.colors[1]

    for ax, plane in zip(axs, ("X", "Y")):
        columns = df.columns.str.match(f"MADX{plane}\d+")
        madx_res = df.loc[element, columns]
        ax.hist(
                madx_res,
                histtype='stepfilled',
                bins=bins,
                color=(*mc.to_rgb(color_madx), 0.1),
                edgecolor=color_madx,
                label="MAD-X",
                density=True,
            )
        ax.axvline(
            madx_res.std(),
            color=color_madx,
            linestyle='--',
            label="_MADX_MEAN",
        )
        ax.axvline(
            df.loc[element, f"PLUS{plane}"],
            color=color_prop_plus,
            linestyle='-',
            label="Plus",
        )
        ax.axvline(
            df.loc[element, f"MINUS{plane}"],
            color=color_prop_minus,
            linestyle='-',
            label="Minus",
        )
        ax.legend(
            bbox_to_anchor=(1, 1.01), 
            loc='lower right', 
            fancybox=False, 
            shadow=False, 
            frameon=False, 
            ncol=3
        )
        ax.set_xlabel(fr"$\Delta\phi_{plane}$")
        ax.set_ylabel("Density")
    


if __name__ == "__main__":
    output = Path("delta_phase_propagation.tfs")
    create_realizations(output, n=1000)
    plot_realizations(output, element="#e", bins=100)
    plt.show()
