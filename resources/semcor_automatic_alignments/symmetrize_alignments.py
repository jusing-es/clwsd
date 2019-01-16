#!/usr/bin/env python
  # -*- coding: utf-8 -*-

# This script takes as input the Source-Target and the Target-Source alignments produced by Fast-align and intersects them.
# Note that it is not necessary to invert the alignments from the T-S to perform intersection, as fast-align takes care of that internally.
# Produces one file with the alignments common to both S-T and T-S directions.

import codecs, os, sys
from itertools import izip
from ntumc_utilities import *

################################################################################
# READING ARGUMENTS 
# This script needs 2 arguments:
# forward.align reverse.align
################################################################################

if (len(sys.argv) != 4): 
    sys.stderr.write('You did not indicate the correct number of arguments: \n') 
    sys.stderr.write('1) forward alignment \n') 
    sys.stderr.write('2) reverse alignment\n') 
    sys.stderr.write('3) type of set operation: "union" or "intersect" \n') 
    sys.exit(1)
else:
    forward = sys.argv[1]
    reverse = sys.argv[2]
    operation = sys.argv[3]

################################################################################
# OPEN INPUT FILES AND PROCESS IT, WRITE OUTPUT FILES
################################################################################

F = codecs.open(forward, encoding='utf-8', mode='r')
R = codecs.open(reverse, encoding='utf-8', mode='r')

basename = os.path.basename(forward)
output = codecs.open(basename+'.'+operation, encoding='utf-8', mode='w')

for f , r in izip(F, R):
    f = [tuple([int(n) for n in t.split("-")]) for t in f.strip().split(" ")]
    r = [tuple([int(n) for n in t.split("-")]) for t in r.strip().split(" ")]
    if operation == 'union':
        print >>output, convert_string(set(f) | set(r))
    elif operation == 'intersect':
        print >>output, convert_string(set(f) & set(r))
    else:
        print "Invalid operation: {0}".format(operation)

output.close()
print "File {0}.{1} created.".format(basename, operation)

