## LHC tracking script with AC Dipole Excitation.

Tracking is done for LHC Beam 1, layout as of Run II 2018 and with 2018 flat-top optics with telescopic squeeze (see `/afs/cern.ch/eng/lhc/optics/runII/2018`).
Specifically, this is `beta*_IP1/2/5/8 = 0.300/10.000/0.300/3.000` (Q6@300A).

AC Dipole elements are installed on top of the MKA Kickers.
Lattice is loaded and thin lens version is created to be used with MAD-X `TRACK` command.
The AC Dipole ramp up and flat top are set as is the case in the LHC: 2000 turns of ramp-up, 6600 turns of flattop kick, 2000 turns of ramp-down.

All MAD-X output will be located in a newly created `Outputdata` folder.

### Customizing

If ran as is, the AC Dipole will give tune separation of `DeltaQx = -0.01` and `DeltaQy = 0.012`, and will kick to an amplitude of 1 sigma.
All BPMs are defined as observation points for the tracking, in order to have detailed orbit data across the machine.
If you intend to customize, check the following:

- Be sure to set `DeltaQx` and `DeltaQy` to your desired tune separation values (lines 40-41).
- Be sure to setup desired crossing scheme, separation bumps etc (lines 125-134).
- Be sure to setup your observation point(s) on line 282 (for instance, `OBSERVE, place=BPM.21R8.B1;`).
- Be sure to set the desired `SIGMAX` and `SIGMAY` kick amplitudes (lines 237-238).
- Any other change that fits your case study (calling a different `opticsfile`, including macros etc).