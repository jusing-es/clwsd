from nltk.corpus import wordnet as wn

# senses for generic location, group and person
generic_senses = {'00007846-n': 'person',
                  '00031264-n': 'group',
                  '00027167-n': 'location'}

common_49 = ['a01', 'a11', 'a12', 'a13', 'a14', 'b13', 'b20', 'c01', 'c02', 'c04', 'd01', 'd03', 'e01', 'e04', 'e24', 'e29', 'f03', 'f10', 'f19', 'f43', 'g11', 'g15', 'h01', 'j01', 'j03', 'j04', 'j05', 'j10', 'j17', 'j22', 'j23', 'j37', 'j52', 'j53', 'j55', 'j57', 'j58', 'j60', 'k01', 'k02', 'k03', 'k05', 'k08', 'k10', 'k11', 'k13', 'k15', 'k18', 'k19']


def show_supported_languages(input_lang):
    print(wn.langs())
    sys.exit(f'{input_lang} is not supported by Wordnet.')
