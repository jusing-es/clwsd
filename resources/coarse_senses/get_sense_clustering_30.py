import nltk
from nltk.corpus import wordnet as wn
import json

f = open('sense_clusters-21.senses', 'r')
lines = f.readlines()

sense_list = []

for l in lines:
    keys = l.strip().split(" ")
    slist=[]
    for k in keys:
        try:
            offset = wn.lemma_from_key(k).synset().offset()
            pos = wn.lemma_from_key(k).synset().pos()
        except nltk.corpus.reader.wordnet.WordNetError as e:
            continue
        slist.append(str(offset).zfill(8)+'-'+pos)
    sense_list.append(slist)

# This produces 29,974 clusters
with open('sense_clustering_30.json', 'w') as outfile:
     json.dump(sense_list, outfile)

d = {}

# This produces clusters for 44,741 keys
for elenco in sense_list:
    for item in elenco:
        d[item] = elenco

with open('sense_clustering_dict.json', 'w') as outfile:
    json.dump(d, outfile)


