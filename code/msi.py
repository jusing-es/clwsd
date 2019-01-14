import sys
import getopt
import argparse
from nltk.corpus import wordnet as wn
import json


def folder_instructions():
    print("""
    Expected folder structure for a multilingual corpus in English (eng), Italian (ita), Romanian (rom) and Japanese (jpn):
    corpus/
          eng/
            corpus.json
          ita/
            corpus.json
          rom/
            corpus.json
          jpn/
            corpus.json
          alignments/
             eng2ita.json
             eng2rom.json
             eng2jpn.json
             ita2eng.json
             ita2rom.json
             ita2jpn.json
             rom2eng.json
             rom2ita.json
             rom2jpn.json
             jpn2eng.json
             jpn2ita.json
             jpn2rom.json
    """)

def msi(*args, **kwargs):
    import pdb; pdb.set_trace()

    source_corpus = kwargs.pop('eng')
    target_corpus = kwargs.pop('ita')
    if kwargs:
        raise TypeError('Unepxected kwargs provided: %s' % list(kwargs.keys()))

def read_input_files(input_folder, langs):

    # print(f'Input languages are {", ".join(langs)}')
    # print(f'Word alignment choice is {alignment}')

    with open('../files/training/corpus/eng/a01.json', 'r') as si:
        eng = json.loads(si.read())

    with open('../files/training/corpus/ita/a01.json', 'r') as si:
        ita = json.loads(si.read())

    msi(l1=eng, l2=ita)

if __name__ == "__main__":

    usage = "Correct usage: python msi.py -i <path_to_input_folder> [-s]"
    parser = argparse.ArgumentParser(description="Performs Multilingual Sense Intersection ")
    parser.add_argument("-i", "--input_folder", help="")
    parser.add_argument("-l", "--languages", help="""Indicate valid ISO-639-2 language codes. 
                                                   Input corpora must be in languages having a wordnet in 
                                                   Open Multilingual Wordnet.
                                                   """)
    parser.add_argument("-f", "--sense_frequencies", default=None)

    parser.add_argument("-a", "--automatic_alignments", help="Path to alignments folder.", default=None)

    options = parser.parse_args()

    if options.languages and options.input_folder:
        langs = options.languages.split("_")
        if set(langs).issubset(wn.langs()) is not True:
            print(f"""Admitted languages are: {wn.langs()}""")
            folder_instructions()
            sys.exit()

        if options.automatic_alignments not in ["gs", "auto_grow", "auto_int", "sense", "all"]:
            print('Word alignment choice not valid. '
                  'Choose one betweeen "gs", "auto_grow", "auto_int", "sense", "all"')

        if options.input_folder:
            read_input_files(options.input_folder, langs)

            if options.sense_frequencies:
                print("External sense frequencies enabled...")
                pass

        print("Starting MSI...")
    else:
        print(f"""Admitted languages are: {wn.langs()}""")
        folder_instructions()
        sys.exit()
