## LHC script to create model with AC Dipole.

Model is created for LHC Beam 1, layout as of Run II 2018 and with 2018 flat-top optics with telescopic squeeze (see `/afs/cern.ch/eng/lhc/optics/runII/2018`).
Specifically, this is `beta*_IP1/2/5/8 = 0.300/10.000/0.300/3.000` (Q6@300A).

AC Dipole elements are installed on top of the MKA Kickers as matrix elements, so that their effect is taken into account on the TWISS functions.
All MAD-X output will be located in a newly created `Outputdata` folder.

### Customizing

If ran as is, the AC Dipole will give tune separation of `DeltaQx = -0.01` and `DeltaQy = 0.012`.
If you intend to customize, check the following:

- Be sure to set `DeltaQx` and `DeltaQy` to your desired tune separation values (lines 33-34).
- Be sure to setup desired crossing scheme, separation bumps etc (lines 86-95).
- Any other change that fits your case study (calling a different `opticsfile`, including macros etc).

### Caveats

- Installing the AC dipole element requires a `SEQEDIT` command, after which the `USE` command needs to be called again.
Beware that the `USE` command reloads a sequence and erases previously defined errors or orbit correction: these will have to be defined again.
