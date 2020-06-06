import sys
sys.path.append("/afs/cern.ch/eng/sl/lintrack/Beta-Beat.src/Python_Classes4MAD")
import string
import os
import shutil
import stat
import re
import math
from numpy import *
from datetime import datetime
import csv
import atexit
from operator import itemgetter
import random
from metaclass import *



trim=[]
thisfile='./output/dqmin.final.trim.dat'
rdat=open(thisfile,'r')
for line in rdat.readlines():
    var=str(line.partition('=')[2].strip().strip(';').strip())
    try:
        val=float(var)
    except:
        continue
    trim.append(val)
rdat.close()


maddq=[]
thisfile='./output/dqmin.final.deltaq.mad.dat'
rdat=open(thisfile,'r')
for line in rdat.readlines():
    var=str(line.partition('=')[2].strip().strip(';').strip())
    try:
        val=float(var)
    except:
        continue
    maddq.append(val)
rdat.close()

'''
ptcdq=[]
thisfile='./output/dqmin.ptc.final.deltaq.dat'
rdat=open(thisfile,'r')
for line in rdat.readlines():
    var=str(line.partition('=')[2].strip().strip(';').strip())
    try:
        val=float(var)
    except:
        continue
    ptcdq.append(val)
rdat.close()
'''



wout=open('data.dqminscan.dat','w')
csvwout=csv.writer(wout,delimiter=' ')
for i in range(len(trim)):
    data=[trim[i],maddq[i]]
    csvwout.writerow(data)
wout.close()



sortmad=sorted(maddq)
dqminmad=sortmad[0]

'''
sortptc=sorted(ptcdq)
dqminptc=sortptc[0]
'''

print '\n\n DQmin via madx scan = '+str(dqminmad)
#print '\n\n DQmin via PTC scan  = '+str(dqminptc)

wout=open('data.dqmin.dat','w')
wout.write('DQmin via madx scan = '+str(dqminmad)+'\n')
#wout.write('DQmin via PTC scan  = '+str(dqminptc))
wout.close()

sys.exit()
