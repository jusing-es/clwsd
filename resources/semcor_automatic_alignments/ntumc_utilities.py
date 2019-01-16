#!/usr/bin/env python
  # -*- coding: utf-8 -*-

# This file collects few scripts that are used in the alignment pipeline to populate NTUMC with word alignments.
# To use these functions, just write "from ntumc_utilities import *" at the top of your python script.

import os, errno, subprocess
import re

def get_file_length(file_path):
    try:
        file_length = int(subprocess.check_output("wc -l < {0}".format(file_path), shell=True))
    except subprocess.CalledProcessError, e:
        file_length = "(unknown)"
    return file_length

def check_path_exists(path):
    ''' Check if a directory exists; if not, create it (used by giza2pharaoh.py)'''
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return path

def convert_string(a):
    ''' Convert from list of tuples to str line (used by giza2pharaoh.py)
    Ex. input: [(0, 0), (1, 1), (2, 2), (5, 3), (5, 4), (5, 5)]
    Ex. output: '0-0 1-1 2-2 5-3 5-4 5-5 '''
    line=''
    for (s,t) in a:
        line += "{0}-{1} ".format(s, t)
    return line.strip()

def process_lines(lines):
    ''' Convert from GIZA format to Pharaoh one sentence pair at the time (used by giza2pharaoh.py)
    Ex. input: NULL ({ 7 }) He ({ 1 }) or ({ 2 }) I ({ 3 }) am ({ }) to ({ }) shovel ({ 4 5 6 }) the ({ }) snow. ({ })
    Ex. output (EN -> ZH): [(1, 1), (2, 2), (3, 3), (6, 4), (6, 5), (6, 6)] 
    (Actual) output: [(0, 0), (1, 1), (2, 2), (5, 3), (5, 4), (5, 5)] '''
    # get sid from first line
    sid = int(lines[0].split(" ")[3][1:-1])
    score = float(lines[0].split(" ")[-1])
    pattern = re.compile('{ ([0-9]*\s)*}')

    # find groups matching the pattern
    # ex. given NULL ({ 2 7 17 18 24 }) 这些 ({ 1 3 }) 疑惑 ({ 4 5 6 8 9 10 11 12 }) 在 ({ }) 要求 ({ }) 刷新 ({ 13 14 15 16 19 }) 
    # 政治 ({ 20 }) 的 ({ }) 狂热 ({ }) 国民 ({ }) 面前 ({ }) 黯然失色 ({ 21 22 23 }) ， ({ }) 走红运 ({ 25 26 }) 的 ({ }) 他 ({ }) 
    # 登上 ({ }) 最高 ({ }) 权力 ({ 27 }) 宝座 ({ }) 。 ({ 28 }) 
    # returns ['2 7 17 18 24', '1 3', '4 5 6 8 9 10 11 12', '', '', '13 14 15 16 19', '20', '', '', '', '', '21 22 23', '', 
    # '25 26', '', '', '', '', '27', '', '28']

    tgt=[]
    for m in re.finditer(pattern, lines[2]):
        tgt.append(m.group(0)[1:-1].strip())

    # NULL at index 0
    alignments = []
    for l in range(len(tgt))[1:]: # leaves out the NULL alignments
        if tgt[l] is not '':
            if len(tgt[l].split(" ")) > 1:
                for e in tgt[l].split(" "):
                    alignments.append((l, int(e)))
            else:      
                alignments.append((l, int(tgt[l])))
    # subtract 1 to all alignments as they start from 0
    alignments = [(s-1,t-1) for (s,t) in alignments]
    # prepend SID and confidence score
    # ex (1, 1), (2, 2), (5, 3), (5, 4), (5, 5)
    #   becomes [18, 0.32, [(1, 1), (2, 2), (5, 3), (5, 4), (5, 5)]], so alignments[2] = list of alignments
    alignments = [sid, score] + [alignments]
    return alignments

def f1(precision, recall):
    ''' Compute F-measure score from precision and recall (used by compare_alignments.py)'''
    return 2*precision*recall/(precision+recall)

