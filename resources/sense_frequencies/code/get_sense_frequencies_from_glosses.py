from lxml import etree
import nltk
from nltk.corpus import wordnet as wn
import glob
import json

path='/home/giulia/lexical_resources/WordNet-3.0 gloss corpus/glosstag/merged/*.xml'
 
files = glob.glob(path)
pairs=[]

for f in files:
    tree=etree.parse(f)
    # get sensekeys contained in sk elements (the glosses' terms)
    sks= tree.findall('.//keys/sk')
    for sk in sks:    
        try:
            pairs.append([sk.text.split("%")[0], str(wn.lemma_from_key(sk.text).synset().offset()).zfill(8)+'-'+wn.lemma_from_key(sk.text).synset().pos()])
        except nltk.corpus.reader.wordnet.WordNetError as e: 
            #No synset found for key 'annoying%3:00:00:disagreeable:00' -> because 3 is actually 5 (satellite adjectives)
            sk.text = sk.text.replace('%3:','%5:')
            pairs.append([sk.text.split("%")[0], str(wn.lemma_from_key(sk.text).synset().offset()).zfill(8)+'-'+wn.lemma_from_key(sk.text).synset().pos()])
    # get sensekeys of terms in glosses ("id" elements with "sk" attributes)
    ids = tree.findall('.//id[@sk]')
    for ide in ids:
        temp = ide.attrib['sk']
        if temp == 'purposefully_ignored%0:00:00::':
            continue
        try:
            pairs.append([temp.split("%")[0], str(wn.lemma_from_key(temp).synset().offset()).zfill(8)+'-'+wn.lemma_from_key(temp).synset().pos()])
        except nltk.corpus.reader.wordnet.WordNetError as e: 
            #No synset found for key 'annoying%3:00:00:disagreeable:00' -> because 3 is actually 5 (satellite adjectives)
            temp = temp.replace('%3:','%5:')
            pairs.append([temp.split("%")[0], str(wn.lemma_from_key(temp).synset().offset()).zfill(8)+'-'+wn.lemma_from_key(temp).synset().pos()])

#produce output file

with open('glosses_frequencies.json','w') as out:
    json.dump(a,out)



