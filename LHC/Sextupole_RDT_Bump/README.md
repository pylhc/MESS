Script to create a closed sextupole RDT bump in Arc12.
LHC Beam 1 is used, layout as of 2018 and with 2018 proton injection optics (`/afs/cern.ch/eng/lhc/optics/runII/2018`).

Lattice is loaded and two sextupole elements are modified to individually power them later.
All other sextupoles are turned off using the modified opticsfile.
RDT are then extracted using the PTC_TWISS trackRDT option.