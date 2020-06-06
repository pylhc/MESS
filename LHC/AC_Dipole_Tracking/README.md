Simple LHC tracking script with AC Dipole Excitation.
Tracking is done for LHC Beam 1, layout as of 2018 and with 2018 proton injection optics (`/afs/cern.ch/eng/lhc/optics/runII/2018`).

AC Dipole elements are installed on top of the MKA Kickers, and ramp up and flat top are set as is the case in the LHC.
Lattice is loaded and thin lens version is created to be used with MAD-X `TRACK` command.

Be sure to modify `DeltaQx` and `DeltaQy` to your desired tune separation values.