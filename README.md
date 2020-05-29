

# <img src="https://twiki.cern.ch/twiki/pub/BEABP/Logos/OMC_logo.png" height="28"> MAD-X Example Studies

This repository is a collection of MAD-X scripts used for various studies in the optics measurements and corrections group (OMC).

### Getting Started

The scripts can be browsed via github or the full repository can be obtained either via `git clone https://github.com/pylhc/PyLHC.git` or downloading as a zip-file.

### Prerequisites

To run the scripts, [MAD-X](https://mad.web.cern.ch/mad/) is required. All scripts have been tested using MAD-X > 5.05.02.



### Documentation

- Each script directory contains a ``README``, outlining the basic functionality and notes on possible pitfalls.
- Excessive use of comments in the MAD-X scripts itself is encouraged.
- General documentation of the OMC-Teams software on <https://twiki.cern.ch/twiki/bin/view/BEABP/OMC>.

### Maintainability

- The main scripts should be named ``job.madx`` and placed in accordingly named directory in the directory tree.
- Supporting files should be uploaded in the script directory. Links to external afs directories should be avoided as files might be modified there or removed.
- Running with the minimum amount of unavoidable MAD-X errors is prefered.


## Studies

- *LHC* - The flagship collider of the 21st century
    - *Coupling RDT Bump* - Creates closed coupling bumps in the LHC IR2 and Arc12.
    - *Sextupole RDT Bump* - Creates closed sextupole RDT bump in Arc12.
    - *Injectionenergy with misaligments and correction* - Realisitc model of the LHC at injection energy with misaligments and nonlinear correction.
    - *Kmod simulation* - Simulating K-Modulation in one Q1 quadrupole.
    - *Tracking with ACD* - Setup for AC-dipole in LHC and subsequent tracking
- *FODO Testlattice* - Small FODO lattice for benchmarking theories and scripts.
    - *Lattice setup* - Setting up basic lattice and return twiss.


## Authors

* **pyLHC/OMC-Team** - *Working Group* - [pyLHC](https://github.com/orgs/pylhc/teams/omc-team)

<!--
## License
This project is licensed under the  License - see the [LICENSE.md](LICENSE.md) file for details
-->