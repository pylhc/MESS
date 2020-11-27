## Model creation

The scripts in the folder `modelcreation` provide twiss files of specific PETRA III models

`p3.madx` is a template file.
Before running, the following variables have to be set:

**natural tunes**:
- `--Iqx--` hor integer tune
- `--Iqy--` ver integer tune
- `--qx--`  hor fractional tune
- `--qy--`  ver fractional tune

where nominal tunes lie around `Qx=37.14` and `Qy=30.31`. 

**driven tunes**
- `--dqx--`  hor fractional tune
- `--dqy--`  ver fractional tune

The ideal way to set these values is to use `p3.madx` as mask and replace the given values using
e.g. python.
