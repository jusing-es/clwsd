MSI employs statistics extracted from the SC corpora themselves. However, in order to avoid a positive bias, the disambiguation step takes one text at the time as input and, when resorting to SFS, it excludes the  frequency data computed over that text. 

See an example of accessing the Italian json file with key lemma "signore" (mister):

>>>dict_ita['signore']
{'06341340-n': {'n05': 2}, '10388440-n': {'k10': 1}, '09536363-n': {'f10': 1, 'k19': 4}, '10127273-n': {'l12': 1}, '10601451-n': {'n12': 1, 'k21': 3, 'p07': 4}}


