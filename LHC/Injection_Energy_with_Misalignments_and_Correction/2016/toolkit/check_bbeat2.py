#!/usr/bin/python

from pyoptics import *

from numpy import *

import sys

fn1=sys.argv[1]
fn2=sys.argv[2]

out={}
for beam in ['b1','b2']:
    t1=optics.open(fn1.replace('b1',beam))
    t2=optics.open(fn2.replace('b1',beam))
    for col in 'betx bety'.split():
        ref=t1[col]
        val=t2[col]
        err=abs(1-ref/val)
        out['%s_%serr'%(col,beam)]=err.max()
    for col in 'mux muy dx dy'.split():
        ref=t1[col]
        val=t2[col]
        out['%s_%serr'%(col,beam)]=abs(val-ref).max()
    for col in 'x y'.split():
        ref=t1[col]
        val=t2[col]
        out['co%s_%serr'%(col,beam)]=abs(val-ref).max()
    for col in 'q1 q2 dq1 dq2'.split():
        ref=t1.param[col]
        val=t2.param[col]
        out['%s_%serr'%(col,beam)]=abs(val-ref)
for row in map(None, *([iter(sorted(out.keys()))]*4)):
    for col in row:
      print "%-10s=%20.14f;"%(col,out[col])

