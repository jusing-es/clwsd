import sys
import json_files_reader as jfr
import argparse
from nltk.corpus import wordnet as wn
import json

general_mfs_statistics = {} #load TODO

def get_mfs(word):
    if general_mfs_statistics:
        pass
    else:
        pass
    return set([])

def synset_lookup(word):
    if word.pos in ('a', 'r', 'v', 'n'):
        return set([wn.synsets(word.lemma, lan=word.get_lang(), pos=word.pos)])
    else:
        return set([wn.synsets(word.lemma, lan=word.get_lang())])


def get_frequent_sense(sense_frequencies, word):
    pass


def assign_sense(target_word, assigned_sense, contributing_languages, assignment_type):
    """

    :param target_word:
    :param assigned_sense:
    :param contributing_languages:
    :param assignment_type:
    :return:
    """
    target_word.add_msi_annotation(assigned_sense, list(contributing_languages), assignment_type)


def perform_intersection(target_word, aligned_synset_bags):
    """

    :param target_word:
    :param aligned_synset_bags:
    :return:
    """

    target_synsets = synset_lookup(target_word)

    overlap = target_synsets
    contributing_languages = set()
    # start overlapping from the most populated synset_bag
    for lang in sorted(aligned_synset_bags,key=lambda k: len(aligned_synset_bags[k]), reverse=True):
        if overlap.intersection(aligned_synset_bags[lang]):
            overlap = overlap.intersection(aligned_synset_bags[lang])
            contributing_languages.add(lang)
        else:
            # don't perform intersection if the overlap leads to an empty set
            continue

    return overlap, contributing_languages

def make_decision(target_word, overlap, corpus_sense_frequencies=None):
    """Works with the current overlap set

    :param target_word:
    :param overlap:
    :param general_mfs_statistics:
    :param corpus_sense_frequencies:
    :return:
    """

    assigned_sense = None
    assignment_type = None

    if len(overlap) == 1:
        assigned_sense = list(overlap)[0]
        assignment_type = 'disambiguated_by_msi'
    else:
        if corpus_sense_frequencies:
            frequent_sense_bag = get_frequent_sense(corpus_sense_frequencies, target_word)
            if overlap.intersection(frequent_sense_bag):
                overlap = overlap.intersection(frequent_sense_bag)
                if len(overlap) == 1:
                    assigned_sense = list(overlap)[0]
                    assignment_type = 'mfs_in_overlap'
                else:
                    # select sense with the highest frequency in frequent_sense_bag
                    relative_most_frequent_sense_in_overlap = [] #TODO
                    assigned_sense = relative_most_frequent_sense_in_overlap
                    assignment_type = 'mfs_in_overlap'
        else:
            assigned_sense = get_mfs(target_word) #TODO
            assignment_type= 'mfs'

    return assigned_sense, assignment_type


def msi(multilingual_corpus, corpus_sense_frequencies=None):
    """

    :param multilingual_corpus:
    :param sense_frequencies:
    :return:
    """
    for _, corpus in multilingual_corpus.corpora.items():
        for _, document in corpus.documents.items():
            for _, sentence in document.sentences.items():
                for _, word in sentence.tokens.items():
                    if word.sense and word.alignments and not word.msi_annotation:
                        aligned_synset_bags = {}
                        for lang, aligned_word in word.alignments.items():
                            aligned_synset_bags[lang] = synset_lookup(aligned_word)

                        overlap, contributing_languages = perform_intersection(word, aligned_synset_bags)
                        assigned_sense, assignment_type = make_decision(word, overlap, corpus_sense_frequencies)
                        assign_sense(word, assigned_sense, contributing_languages, assignment_type)


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
