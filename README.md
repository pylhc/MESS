

# <img src="https://raw.githubusercontent.com/pylhc/pylhc.github.io/master/docs/assets/logos/OMC_logo.svg" height="28"> MESS - MAD-X Example Study Scripts

This repository is a collection of MAD-X scripts used for various studies in the optics measurements and corrections group (OMC).

### Getting Started

The scripts can be browsed via github or the full repository can be obtained either via `git clone https://github.com/pylhc/MESS.git` or downloading the zipped repository.

### Prerequisites

To run the scripts, [MAD-X](https://mad.web.cern.ch/mad/) is required. If not otherwise stated, all scripts have been tested using MAD-X > 5.05.02.

### Documentation

- Each script directory contains a ``README``, outlining the basic functionality and notes on possible pitfalls.
- Excessive use of comments in the MAD-X scripts itself is encouraged.
- General documentation of the OMC-Teams software on <https://twiki.cern.ch/twiki/bin/view/BEABP/OMC>.

### Maintainability

- The main scripts should be named ``job.madx`` and placed in an accordingly named directory in the directory tree.
- Supporting files should be uploaded in the script directory. Links to external afs directories should be avoided as files might be modified there or removed.
- Running with the minimum amount of unavoidable MAD-X errors is prefered.

## Studies

- *LHC* - The flagship collider of the 21st century
    - *Coupling RDT Bump* - Creates closed coupling bumps in the LHC IR2 and Arc12.
    - *Sextupole RDT Bump* - Creates closed sextupole RDT bump in Arc12.
    - *Injectionenergy with misaligments and correction* - Realistic model of the LHC at injection energy with misaligments and nonlinear correction.
    - *Kmod simulation* - Simulating K-Modulation in one Q1 quadrupole.
    - *Tracking with ACD* - Setup for AC-dipole in LHC and subsequent tracking
- *FODO Testlattice* - Small FODO lattice for benchmarking theories and scripts
    - *Lattice Setup* - Setting up basic lattice and return twiss.
    - *Phase Trombone* - Setting up basic lattice, match tunes via a phase trombone and return twiss.
- *PETRA3* - PETRA III, DESY's brilliant X-ray light source
    - *Model Creation* - Creates model twiss files with AC-dipole and tune selection.

## Authors

* **pyLHC/OMC-Team** - *Working Group* - [pyLHC](https://github.com/orgs/pylhc/teams/omc-team)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
