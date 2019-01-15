import sys
import json_files_reader as jfr
import argparse
from nltk.corpus import wordnet as wn
import json
import os


def _load_semcor_sense_frequency_statistics():
    path = 'resource/sense_frequencies'

    sfs = {}
    with open(os.path.join(path, 'sfs_ita.json')) as si:
        sfs['ita'] = json.loads(si.read())

    with open(os.path.join(path, 'sfs_rom.json')) as si:
        sfs['rom'] = json.loads(si.read())

    return sfs


general_mfs_statistics = _load_semcor_sense_frequency_statistics()


def compute_mfs(word):
    """Gives MFS by excluding sense occurrences in the current text.

    :param word:
    :return:
    """
    if word.lang in general_mfs_statistics and word.lemma in general_mfs_statistics:
        # given the input lemma, for each sense s retrieves <sense, sum(occurrences in texts, excluded text)> pairs
        sid_scores = [(s, sum(general_mfs_statistics[word.lemma][s].values()) -
                       general_mfs_statistics[word.lemma][s].get(word.document, 0))
                      for s in general_mfs_statistics[word.lemma]]
        # assigns to sense the sense with highest number of occurrences
        sense = sorted(sid_scores, key=lambda x: x[1], reverse=True)[0][0]

        if sense is not None:
            return wn._synset_from_pos_and_offset(sense[-1], int(sense[:8]))

    return None


def get_mfs(word):
    if general_mfs_statistics:
        compute_mfs()
    else:
        return synset_lookup(word)[0]
    return set([])


def synset_lookup(word):
    if word.pos in ('a', 'r', 'v', 'n'):
        return set(wn.synsets(word.lemma, lang=word.lang, pos=word.pos))
    else:
        return set(wn.synsets(word.lemma, lang=word.lang))


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


def get_synset_in_overlap(overlap):
    assert len(overlap) == 1
    return get_offset(list(overlap)[0])


def get_offset(synset):
    return str(synset.offset()).zfill(8) + '_' + synset.pos()


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
    for lang in sorted(aligned_synset_bags, key=lambda k: len(aligned_synset_bags[k]), reverse=True):
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
    :param corpus_sense_frequencies:
    :return:
    """
    if len(overlap) == 1:
        assigned_sense = get_synset_in_overlap(overlap)
        assignment_type = 'disambiguated_by_msi'
    else:
        if corpus_sense_frequencies:
            frequent_sense_bag = get_frequent_sense(corpus_sense_frequencies, target_word)
            if overlap.intersection(frequent_sense_bag):
                overlap = overlap.intersection(frequent_sense_bag)
                if len(overlap) == 1:
                    import pdb;
                    pdb.set_trace()
                    assigned_sense = get_synset_in_overlap(overlap)
                    assignment_type = 'mfs_in_overlap'
                else:
                    import pdb;
                    pdb.set_trace()
                    # select sense with the highest frequency in frequent_sense_bag
                    relative_most_frequent_sense_in_overlap = []  # TODO
                    assigned_sense = relative_most_frequent_sense_in_overlap
                    assignment_type = 'mfs_in_overlap'  # TODO
        else:
            import pdb;
            pdb.set_trace()
            assigned_sense = get_mfs(target_word)  # TODO
            assignment_type = 'mfs'

    return assigned_sense, assignment_type


def get_aligned_words_synsets(word):
    aligned_synset_bags = {}
    for lang, aligned_word in word.alignments.items():
        aligned_synset_bags[lang] = synset_lookup(aligned_word)

    return aligned_synset_bags


def msi(multilingual_corpus, corpus_sense_frequencies=True):
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
                        aligned_synset_bags = get_aligned_words_synsets(word)
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
                  'Choose one beteeen "gs", "auto_grow", "auto_int", "sense", "all"')

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
