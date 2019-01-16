#!/usr/bin/env python
  # -*- coding: utf-8 -*-

# This script evaluates alignment accuracy of a number of aligners (Berkeley, fast-align and mGiza) given gold standard alignments.
#   Input files:
#    - file1 and file2 are the portion of source and target texts, sentence-aligned, for which we have GS alignments
#    - hand_al is the hand-made alignment for those GS sentences
#    - hand_ids of the aligned sentences
#
#      Ex. 
#     60284	60284
#     60745	60745
#     61794	61794
#
#    - all_ids with the id pairs of aligned sentences for the whole parallel text (NTUMC in our case)
#    Then, it takes as input 3 more files:
#    - B_all with the alignments given by Berkeley
#    - F_all with the alignments given by Fast-align
#    - G_all with the alignments given by Giza
#    Note that those three files must have the same number of lines as the whole parallel text
#    That is, if the aligner was fed with training data along with the target text, then only the alignments 
#    for the latter must be retrieved (see README)

#    The script finds the 35 GS sentences back in the alignment files built for the whole NTUMC,
#    by mapping ids to ids_all to find the line.
#    The script output the result of the comparison on the standard output. 
#    Optionally, it produces a file where all the alignments for the GS sentences (GS and automatically derived ones)
#    are printed out, for hand-checking purposes.

#    Example --> python compare_alignments.py ntumc/hand_ntumc_A ntumc/hand_ntumc_B ntumc/handmade_GS ntumc/handmade_GS_sentence_ids ntumc/ntumc_AB berkeley-output/training_ntumc.invert fastalign-output/full.ntumc.align mgiza-pharaoh/cmneng.cat -write

import codecs, sys, os
from ntumc_utilities import * #depends on ntumctk_utilities.f1(precision, recall)
from nltk.align import Alignment, AlignedSent
from itertools import izip
from collections import defaultdict as dd
import linecache

################################################################################
# READING ARGUMENTS (the data path)
# This script needs 2 arguments:
# mgiza_output_file starting_sid
################################################################################

if (len(sys.argv) >= 9): 
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    hand = sys.argv[3]
    ntumc_hand_ids = sys.argv[4]
    ntumc_all_ids = sys.argv[5]
    B_all = sys.argv[6]
    F_all = sys.argv[7]
    G_all = sys.argv[8]
    if (len(sys.argv) == 10):
       write = '-write'
    elif (len(sys.argv) == 9):
        write = ''
else:
    sys.stderr.write('You did not indicate the correct number of arguments: \n') 
    sys.stderr.write('1) source text for which there are Gold Standard alignments; \n') 
    sys.stderr.write('2) target text for which there are Gold Standard alignments (must be sentence-aligned to source text)\n') 
    sys.stderr.write('3) hand-made alignment for source and target text, in pharaoh format; \n') 
    sys.stderr.write('4) sentence id pairs of GS aligned sentences (as in NTUMC databases); \n') 
    sys.stderr.write('5) sentence id pairs of the parallel text (as in NTUMC databases) (ALL, not only for GS sentences); \n') 
    sys.stderr.write('6) alignments given by Berkeley for source and target texts (ALL); \n') 
    sys.stderr.write('7) alignments given by fast-align for source and target texts (ALL); \n') 
    sys.stderr.write('8) alignments given by mGiza for source and target texts (ALL). \n') 
    sys.stderr.write('You may provide a final argument -write so that GS alignments are printed out along with automatically-made alignments for comparison purposes.')
    sys.exit(1)

################################################################################
# Opening files related to GS
################################################################################

fileA = codecs.open(file1, encoding='utf-8', mode='r')
fileB = codecs.open(file2, encoding='utf-8', mode='r')
hand_al = codecs.open(hand, encoding='utf-8', mode='r')
hand_ids = codecs.open(ntumc_hand_ids, encoding='utf-8', mode='r')
all_ids = codecs.open(ntumc_hand_ids, encoding='utf-8', mode='r')

# Build AlignedSent objects for the GS sentences
als = []
for lineA, lineB, line_hand in izip(fileA, fileB, hand_al):
    #convert alignment in an Alignment object
    # first extract tuples in string format, then the actual tuples
    line_hand = [tuple([int(n) for n in t.split("-")]) for t in line_hand.strip().split(" ")]
    alignment = Alignment(line_hand)
    # create new AlignedSent
    s = AlignedSent(lineA.strip().split(" "), lineB.strip().split(" "), alignment)
    # append to als => this will provide the GS for sentence s
    als.append(s)

# open hand_ids
# for each hand_id, find corresponding line in all_ids

alignments_ids=[]
for ids in hand_ids:
    all_ids = codecs.open(ntumc_all_ids, encoding='utf-8', mode='r')
    for num, line in enumerate(all_ids):
        if ids == line:
           alignments_ids.append(num+1)
           break

# loops over the alignment ids to find the alignments in the aligner outputs 
# saves the alignment_error_rate for each sentence

if write=='-write':
    comparison = codecs.open('compare_alignments.txt', encoding='utf-8', mode='w')

scores = {'berkeley' : dd(lambda : 0), 'fastalign' : dd(lambda : 0), 'mgiza' : dd(lambda : 0)}

for num, alid in enumerate(alignments_ids):
    # read alignments in the format 1-0 3-1 3-2 3-3 3-4 3-5, by exploiting the line number l
    al_B = linecache.getline(B_all, alid)
    al_F = linecache.getline(F_all, alid)
    al_G = linecache.getline(G_all, alid)
    # get alignments in the format [(1, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)]
    # required for comparison with Alignment objects

    if al_B != '\n':
        al_B = [tuple([int(n) for n in t.split("-")]) for t in al_B.strip().split(" ")]
    else:
        al_B = set()
    if al_F != '\n':
        al_F = [tuple([int(n) for n in t.split("-")]) for t in al_F.strip().split(" ")]
    else:
        al_F = set()
    if al_G != '\n':
        al_G = [tuple([int(n) for n in t.split("-")]) for t in al_G.strip().split(" ")]
    else:
        al_G = set()

    al_B = AlignedSent(als[num].words, als[num].mots, al_B)
    al_F = AlignedSent(als[num].words, als[num].mots, al_F)
    al_G = AlignedSent(als[num].words, als[num].mots, al_G)

    scores['berkeley']['aer'] += al_B.alignment_error_rate(als[num])
    scores['berkeley']['precision'] += al_B.precision(als[num])
    scores['berkeley']['recall'] += al_B.recall(als[num])

    scores['fastalign']['aer'] += al_F.alignment_error_rate(als[num])
    scores['fastalign']['precision'] += al_F.precision(als[num])
    scores['fastalign']['recall'] += al_F.recall(als[num])

    scores['mgiza']['aer'] += al_G.alignment_error_rate(als[num])
    scores['mgiza']['precision'] += al_G.precision(als[num])
    scores['mgiza']['recall'] += al_G.recall(als[num])

    if write == '-write':
        print >>comparison, 'GS:', (als[num].alignment)
        print >>comparison, 'B:', al_B.precision(als[num]), convert_string(al_B.alignment)
        print >>comparison, 'F:', al_F.precision(als[num]), convert_string(al_F.alignment)
        print >>comparison, 'G:', al_G.precision(als[num]), convert_string(al_G.alignment)
        print >>comparison, '\n'

if write == '-write':
    comparison.close()
    print "File compare_alignments.txt created"

# Print the scores
#https://docs.python.org/3/library/string.html#formatspec

#{:>12} arranges 12-char width per field, * 4 fields
#{:>12.2f} combines two format options, width allocated + format for floats
# *scores unpacking argument sequence
headers_format = "{:>12}"*(len(scores['berkeley'].keys())+1)
row_format = "{:>12}"+"{:>12.2f}"*(len(scores['berkeley'].keys()))
print headers_format.format("",*scores['berkeley'].keys())
for aligner in scores.keys():
    values = [score/num for score in [scores[aligner].values()][0]]
    print row_format.format(aligner,*values)

print "Average error rates: Berkeley {0:.2f}, Fast-align {1:.2f}, mGiza {2:.2f}".format(scores['berkeley']['aer']/num, scores['fastalign']['aer']/num, scores['mgiza']['aer']/num)
print "Average precision scores: Berkeley {0:.2f}, Fast-align {1:.2f}, mGiza {2:.2f}".format(scores['berkeley']['precision']/num, scores['fastalign']['precision']/num, scores['mgiza']['precision']/num) 
print "Average recall scores: Berkeley {0:.2f}, Fast-align {1:.2f}, mGiza {2:.2f}".format(scores['berkeley']['recall']/num, scores['fastalign']['recall']/num, scores['mgiza']['recall']/num)
print "Average F-measure scores: Berkeley {0:.2f}, Fast-align {1:.2f}, mGiza {2:.2f}".format(f1(scores['berkeley']['precision']/num, scores['berkeley']['recall']/num), f1(scores['fastalign']['precision']/num, scores['fastalign']['recall']/num), f1(scores['mgiza']['precision']/num, scores['mgiza']['recall']/num))

