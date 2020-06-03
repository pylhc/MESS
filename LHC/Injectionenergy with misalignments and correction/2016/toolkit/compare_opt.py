#!/usr/bin/python



def compare_optics(t1,t2,prratio=1.00001,prdiff=1e-12):
  v1=None
  v2=None
  diff=[]
  ratio=[]
  all_keys=set(t1._keys()+t2._keys())
  for k in all_keys:
      try:
        v2=t2._data[k]
      except KeyError:
        print "%s not found in %s"%(k,t1)
        continue
      try:
        v1=t1._data[k]
      except KeyError:
        print "%s not found in %s"%(k,t2)
        continue
      if type(v1) is float  and type(v2) is float:
          if abs(v1)<1e-7 or abs(v2)<1e-7:
              df=abs(v1-v2)
              if df>0:
                diff.append( ( abs(v1-v2) ,k))
          else:
              r=abs(v1/v2)
              if r<1:
                  r=1/r
              if r>1:
                ratio.append( (r,k) )
  diff.sort()
  diff.reverse()
  ratio.sort()
  ratio.reverse()

  rmax=ratio and ratio[0] or (1,'none')
  dmax=diff  and diff[0] or (0,'none')

  if len(diff)>0 and len(ratio)>0:
      print "ratio %10.3e %s, diff %10.3e %s"%(rmax+dmax)
  if len(ratio)>0:
  #  print "name                 value1     value2      ratio"
    for v,k in ratio:
      if v> prratio:
         print "%-20s %10.3e %10.3e %10.3e"%(k,t1[k],t2[k],v)
      else:
         break
  if len(diff)>0:
  #  print "name                 value1     value2      diff"
    for v,k in diff:
      if v> prdiff:
         print "%-20s %10.3e %10.3e %10.3e"%(k,t1[k],t2[k],v)
      else:
         break
  return ratio,diff

if __name__=='__main__':
  import sys
  from pyoptics import madlang
  fn1=sys.argv[1]
  fn2=sys.argv[2]

  prratio=1.00001;
  prdiff=1e-12;

  if len(sys.argv)>3:
      prratio=float(sys.argv[3])
  if len(sys.argv)>4:
      prdiff=float(sys.argv[4])

  t1=madlang.open(fn1)
  t2=madlang.open(fn2)
  compare_optics(t1,t2,prratio,prdiff)




