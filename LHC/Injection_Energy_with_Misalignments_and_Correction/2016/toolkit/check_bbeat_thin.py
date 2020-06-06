#!/usr/bin/python

import sys

import numpy as np

from pyoptics import *

fn1=sys.argv[1]
fn2=sys.argv[2]

def get_idxfrom_names(t,names):
    lookup=dict([(b,a) for a,b in enumerate(t.name)])
    return [lookup[n] for n in names if n in lookup]

def get_idxfrom_names2(t1,t2):
    idx1=t1.l==0
    names=t1.name[idx1]
    id1=np.in1d(t1.name,names)
    id2=np.in1d(t2.name,names)
    return id1,id2

out={}
for beam in ['b1','b2']:
    t1=optics.open(fn1.replace('b1',beam)).cycle('IP1',True)
    t2=optics.open(fn2.replace('b1',beam)).cycle('IP1',True)
    idx1,idx2=get_idxfrom_names2(t1,t2)
    #idx1=t1.l==0
    #idx2=get_idxfrom_names(t2,t1.name[idx1])
    #name2=t2.name[idx2]
    #idx1=get_idxfrom_names(t1,t2.name[idx2])
    #if len(t1.name[idx1])!=len(t2.name[idx2]):
    #    print "Not matching sequences"
    for col in 'betx bety'.split():
        ref=t1[col][idx1]
        val=t2[col][idx2]
        err=abs(1-ref/val)
        idxmax=err.argmax()
        out['%s_%serr'%(col,beam)]=err[idxmax],t1.name[idx1][idxmax]
    for col in 'mux muy dx dy'.split():
        ref=t1[col][idx1]
        val=t2[col][idx2]
        err=abs(val-ref)
        idxmax=err.argmax()
        out['%s_%serr'%(col,beam)]=err[idxmax],t1.name[idx1][idxmax]
    for col in 'x y'.split():
        ref=t1[col][idx1]
        val=t2[col][idx2]
        err=abs(val-ref)
        idxmax=err.argmax()
        out['%s_%serr'%(col,beam)]=err[idxmax],t1.name[idx1][idxmax]
    for col in 'q1 q2 dq1 dq2'.split():
        ref=t1.param[col]
        val=t2.param[col]
        err=abs(val-ref)
        out['%s_%serr'%(col,beam)]=err,''
for row in map(None, *([iter(sorted(out.keys()))]*4)):
    for col in row:
      val,name=out[col]
      print "%-10s=%20.14f; !%s"%(col,val,name)

