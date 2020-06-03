#!/usr/bin/python

from pyoptics import *
import pyoptics.madlang as mad

import sys
import re

fn=sys.argv[1]

p=mad.open(fn)
#print fn

reg=re.compile(r'kq(1?[0-9]).*b1')

data=[]
for k in p._keys():
  res=reg.match(k)
  if res:
      b1=p[k]
      b2=p[k[:-1]+'2']
      data.append((abs(b1/b2),b1,b2,k))

scale=23348
data.sort()
for r,b1,b2,k in data:
    if r<0.5 or r>2:
        print "%-30s %-10s %6.3g %6.3g %6.3g"%(fn,k,r, b1*scale,b2*scale)


