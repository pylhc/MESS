# LHC Example Tracking Script

Tracking is done for LHC Beam 1, layout as of Run II 2018 and with 2018 flat-top optics with telescopic squeeze (as from `/afs/cern.ch/eng/lhc/optics/runII/2018`).
Specifically, this is `beta*_IP1/2/5/8 = 0.300/10.000/0.300/3.000` (Q6@300A).

Lattice is loaded and thin lens version is created to be used with MAD-X `TRACK` command.
Some tiny amount of coupling is introduced, then tunes and chroma are rematched.
Observation points are defined and a single particle is tracked for 1023 turns.

A singe resulting file for the tracking is output, named `trackone`.

This script is a companion to the example walkthrough for `omc3` analysis on the OMC website and should run as is.
