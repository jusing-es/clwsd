import sys
import json_files_reader as jfr
import xml_file_reader as xr
import argparse
from nltk.corpus import wordnet as wn
import json
import os


def _load_corpora_sense_frequency_statistics(languages):
    def _load_wn_glosses_eng_sense_frequency_statistics():
        path = '../resources/sense_frequencies'

        with open(os.path.join(path, 'sfs_eng_wn_glosses.json')) as si:
            sfs['eng'] = json.loads(si.read())

        return sfs

    def _load_semcor_sense_frequency_statistics(lang):
        path = '../resources/sense_frequencies'

        if lang == 'ita':
            with open(os.path.join(path, 'sfs_ita.json')) as si:
                sfs = json.loads(si.read())

        elif lang == 'rom':
            with open(os.path.join(path, 'sfs_rom.json')) as si:
                sfs = json.loads(si.read())

        return sfs


    sfs ={}
    if 'eng' in languages:
        sfs['eng'] = _load_wn_glosses_eng_sense_frequency_statistics()
    if 'ita' in languages:
        sfs['ita'] = _load_corpora_sense_frequency_statistics(lang='ita')
    if 'rom' in languages:
        sfs['rom'] = _load_corpora_sense_frequency_statistics(lang='rom')


def compute_rmfs(word):
    """Gives relative MFS by excluding sense occurrences in the current text.

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
    if synset_lookup(word):
        return synset_lookup(word)[0]
    return set()

def synset_lookup(word):
    if word.pos in ('a', 'r', 'v', 'n'):
        return set(wn.synsets(word.lemma, lang=word.lang, pos=word.pos))
    else:
        return set(wn.synsets(word.lemma, lang=word.lang))


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
                """If resorting to SFS statistics leads to an overlap containing one sense, 
                the word is disambiguated (mfs_in_overlap); if the overlap still results in more 
                than one sense, the most frequent one among the ones left is selected (rmfs_within_overlap). """
                if len(overlap) == 1:
                    import pdb;
                    pdb.set_trace()
                    assigned_sense = get_synset_in_overlap(overlap)
                    assignment_type = 'mfs_in_overlap'
                else:
                    import pdb;
                    pdb.set_trace()
                    # select sense with the highest frequency in frequent_sense_bag
                    assigned_sense = frequent_sense_bag[0]
                    assignment_type = 'rmfs_within_overlap'
        else:
            mfs = get_mfs(target_word)
            overlap = overlap.intersection(mfs)
            if len(overlap) == 1:
                assigned_sense = get_synset_in_overlap(overlap)
                assignment_type = 'mfs_in_overlap'
            else:
                assert mfs.issubset(synset_lookup(target_word))
                # check if it was part of the original set
                import pdb; pdb.set_trace()
                assigned_sense = mfs
                assignment_type = 'mfs'

    return assigned_sense, assignment_type


def perform_intersection(target_word, aligned_synset_bags):
    """

    :param target_word:
    :param aligned_synset_bags:
    :return:
    """
    target_synsets = synset_lookup(target_word)

    overlap = target_synsets
    possible_target_synsets = target_synsets
    contributing_languages = set()
    # start overlapping from the most populated synset_bag
    for lang in sorted(aligned_synset_bags, key=lambda k: len(aligned_synset_bags[k]), reverse=True):
        # don't perform intersection if that leaves the set with no one of the target synsets left
        # it may happen, because other wordnets are more developed - but it's important that the annotation is covered
        # in the target's language WN
        if overlap.intersection(aligned_synset_bags[lang]) and possible_target_synsets.intersection(aligned_synset_bags[lang]):
            overlap = overlap.intersection(aligned_synset_bags[lang])
            contributing_languages.add(lang)
        else:
            # don't perform intersection if the overlap leads to an empty set
            continue

    return overlap, contributing_languages


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

    if options.languages:
        langs = options.languages.split("_")
        if set(langs).issubset(wn.langs()) is not True:
            print(f"""Admitted languages are: {wn.langs()}""")
            sys.exit()

        if options.json_input_folder:

            try:
                multilingual_corpus = jfr.read_input_files(options.json_input_folder, langs)
            except:
                jfr.folder_instructions()

        elif options.xml_input_file:
                multilingual_corpus = xr.load_multilingualcorpus_from_xml(options.xml_input_file)
        else:
            print('Valid input formats are XML compliant to NTUMC DTD or input folder with json files as below')
            jfr.folder_instructions()
            sys.exit()

        if options.automatic_alignments and \
                options.automatic_alignments not in ["gs", "auto_grow", "auto_int", "sense", "all"]:
            print('Word alignment choice not valid. Choose one beteeen "gs", "auto_grow", "auto_int", "sense", "all"')

       if options.sense_frequencies:
            general_mfs_statistics = _load_corpora_sense_frequency_statistics(langs)
            print("External sense frequencies enabled...")
       else:
           general_mfs_statistics = None

    msi(multilingual_corpus, )
        print("Starting MSI...")

    elif options.languages and options.xml_input_file:
        pass
    else:
        print(f"""Admitted languages are: {wn.langs()}""")
        sys.exit()
