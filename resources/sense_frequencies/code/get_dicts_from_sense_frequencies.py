import json
pairs =json.load(open('glosses_frequencies.json'))

g = open("sense_frequency_wn_glosses.tab", "wb")
# build sense frequency dictionary
sf_dict = {}
for pair in pairs:
    lemma, offset, pos = pair[0], pair[1], pair[1][-1]
    if lemma+'-'+pos in sf_dict:
        if offset in sf_dict[lemma+'-'+pos]:
            sf_dict[lemma+'-'+pos][offset] += 1
        else:
            sf_dict[lemma+'-'+pos][offset] = 1
    else:
        sf_dict[lemma+'-'+pos] = {offset : 1}
#build mfs dictionary
mfs = {}
for k, v in sf_dict.items():
   # print synsets in decreasing frequency order
   # ex 
   # acompaniament [(u'07031752-n\n', 1)]
   # spatiu [(u'00028651-n\n', 15), (u'08652970-n\n', 5), (u'13910384-n\n', 1)]
   # muncitor [(u'09632518-n\n', 7), (u'10241300-n\n', 3), (u'10791221-n\n', 1)]
   # sort dictionary according to values to have synsets in decreasing order of frequency
   v = sorted(v.items(), key=lambda x : x[1], reverse=True)
   # write in output file; lemma and synsets in decreasing order of frequency
   g.write("%s\t%s\n" % (k,"\t".join([a for (a,b) in v])))
   mfs[k] = [c for (c,d) in v]

g.close()

with open('sense_frequencies_sorted_wn_glosses.json','w') as out:
    json.dump(a,out)



