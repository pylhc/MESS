## Model creation

Provides twiss files of a specific PETRA III model, to be used as input for the optics measurement codes.
After running, two twiss outputs are produced:

- a `twiss.dat` file containing only the optics functions at the BPMs,
- a `twiss_elements.dat` file which includes also optics functions at instruments and magnetic elements.

Optionally, an AC-Dipole element can be installed, in which case two additional files are produced, with the added suffix `_adt`.
These contain the optics function during forced excitation.

### Customizing

The script loads the PETRA III sequence and matches to the tunes specified with `Qx` and `Qy`, using all `qf` and `qd` quadrupoles.
The script provides the option to install an AC Dipole by setting the `ACD` variable to 1, which by default is not installed.
If the AC-Dipole is installed, it drives the beam to tunes specified with `ACQx` and `ACQy`.

If you intend to customize, check the following:

- Be sure to set `Qx` and `Qy` to your desired tune values.
- Be sure to enable AC-Dipole installation if needed, together with setting proper AC-Dipole tunes.
