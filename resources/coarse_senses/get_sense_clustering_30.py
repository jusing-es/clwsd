import nltk
from nltk.corpus import wordnet as wn
import json

f = open('sense_clusters-21.senses', 'r')
lines = f.readlines()

list = []

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
    list.append(slist)

with open('sense_clustering_30.json', 'w') as outfile:
     json.dump(list, outfile)

#29,974 clusters

##Usage example
#with open('sense_clustering_30.json') as data:
#    clustering = json.load(data)

## say the synset found through SI is 'reject.v.04', but the gold standard has 'condemn.v.01' 
#attempted_offset = '00796976-v'
#correct_offset = '01774799-v'

#cluster = [items for items in clustering if attempted_offset in items]
#if correct_offset in cluster:
     ## consider attempted_offset correct
