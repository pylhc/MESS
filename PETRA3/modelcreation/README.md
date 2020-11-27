## Model creation

Provides twiss files of a specific PETRA III model, to be used as input for the optics measurement codes.
After running, two twiss files are produced, `twiss.dat` containing only the optics functions at the
BPMs, and `twiss_elements.dat` which includes also optics functions at instruments and magnetic elements.
Optinally, an AC-Dipole element can be installed, in which case two additional files are produced, with the added
suffix `_adt`. These contain the optics function during forced excitation.

### Customizing

The script loads the PETRA III sequence and matches to the tunes specified with `Qx` and `Qy`, using all `qf` and `qd` quadrupoles.
The script provides the option to install an AC-Dipole using `ACD=1;`, which by default is not installed.
If the AC-Dipole is installed, it runs with frequencies specified with `ACQx` and `ACQy`.

If you intend to customize, check the following:

- Be sure to set `Qx` and `Qy` to your desired tune values.
- Be sure to enable AC-Dipole installation if needed, together with setting proper AC-Dipole tunes.
