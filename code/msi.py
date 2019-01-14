import sys
import json_files_reader as jfr
import argparse
from nltk.corpus import wordnet as wn
import json



def msi(multilingual_corpus, sense_frequencies=False):
    for _, corpus in multilingual_corpus.corpora.items():
        for _, document in corpus.documents.items():
            for _, sentence in document.sentences.items():
                for _, word in sentence.tokens.items():
                    if word.sense and word.alignments:
                        import pdb; pdb.set_trace()






def show_supported_languages(input_lang):
    print(wn.langs())
    sys.exit(f'{input_lang} is not supported by Wordnet.')


if __name__ == "__main__":

    usage = "Correct usage: python msi.py -i <path_to_input_folder> [-s]"
    parser = argparse.ArgumentParser(description="Performs Multilingual Sense Intersection ")
    parser.add_argument("-i", "--json_input_folder", help="")
    parser.add_argument("-x", "--xml_input_file", help="")
    parser.add_argument("-l", "--languages", help="""Indicate valid ISO-639-2 language codes. 
                                                   Input corpora must be in languages having a wordnet in 
                                                   Open Multilingual Wordnet.
                                                   """)
    parser.add_argument("-f", "--sense_frequencies", default=None)

    parser.add_argument("-a", "--automatic_alignments", help="Path to alignments folder.", default=None)

    options = parser.parse_args()

    if options.languages and options.json_input_folder:
        langs = options.languages.split("_")
        if set(langs).issubset(wn.langs()) is not True:
            print(f"""Admitted languages are: {wn.langs()}""")
            jfr.folder_instructions()
            sys.exit()

        if options.automatic_alignments not in ["gs", "auto_grow", "auto_int", "sense", "all"]:
            print('Word alignment choice not valid. '
                  'Choose one betweeen "gs", "auto_grow", "auto_int", "sense", "all"')

        if options.input_folder:
            source, target = jfr.read_input_files(options.input_folder, langs)
            msi()
            if options.sense_frequencies:
                print("External sense frequencies enabled...")
                pass

        print("Starting MSI...")
    elif options.languages and options.xml_input_file:
        pass
    else:
        print(f"""Admitted languages are: {wn.langs()}""")
        sys.exit()
