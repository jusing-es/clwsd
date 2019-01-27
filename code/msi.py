import re
import sys
from pprint import pprint
#import json_files_reader as jfr
import xml_file_reader as xr
import argparse
import nltk.corpus
from nltk.corpus import wordnet as wn
import json
import os
from collections import defaultdict, Counter

general_mfs_statistics = None

# senses for generic location, group and person
generic_senses = {'00007846-n': 'person',
                  '00031264-n': 'group',
                  '00027167-n': 'location'}

missing_lemmas_recap = {'eng' : Counter(),
                        'ita' : Counter(),
                        'ron' : Counter(),
                        'jpn': Counter()
                        }

def add_to_missing_lemmas_recap(word):
    try:
        translation = f"{word.alignments['eng'].lemma}"
        sense = f"{word.alignments['eng'].sense}"
    except KeyError:
        translation = ''
        sense = ''
    missing_lemmas_recap[word.lang][f'{word.lemma}${word.pos}${translation}${sense}'] += 1

def dump_missing_lemmas_recap():
    for lang in missing_lemmas_recap:
        with open(f'../resources/missing_senses/{lang}_semcor.txt', 'w', encoding='utf8') as so:
            for item in missing_lemmas_recap[lang]:
                lemma, pos, translation, suggested_sense = item.split("$")
                so.write(f'{lemma}\t{pos}\t{missing_lemmas_recap[lang][item]}\t{translation}\t{suggested_sense}\n')

def _load_corpora_sense_frequency_statistics(languages):
    def _load_wn_glosses_eng_sense_frequency_statistics():
        path = '../resources/sense_frequencies'
        with open(os.path.join(path, 'sfs_eng_wn_glosses.json')) as si:
            sfs = json.loads(si.read())

        return sfs

    def _load_semcor_sense_frequency_statistics(lang):
        path = '../resources/sense_frequencies'
        sfs = {}
        if lang == 'ita':
            with open(os.path.join(path, 'sfs_ita.json')) as si:
                sfs = json.loads(si.read())
        elif lang == 'rom':
            with open(os.path.join(path, 'sfs_rom.json')) as si:
                sfs = json.loads(si.read())

        return sfs

    sfs = {}
    if 'eng' in languages:
        sfs['eng'] = _load_wn_glosses_eng_sense_frequency_statistics()
    if 'ita' in languages:
        sfs['ita'] = _load_semcor_sense_frequency_statistics(lang='ita')
    if 'rom' in languages:
        sfs['rom'] = _load_semcor_sense_frequency_statistics(lang='rom')

    return sfs

def get_relative_frequent_senses(word):
    """Gives relative MFS by excluding sense occurrences in the current text.

    :param word:
    :returns list:
    """
    rfss = []
    if word.lang in general_mfs_statistics and word.lang in ('ita', 'rom'):
        if word.lemma in general_mfs_statistics[word.lang]:
            # given the input lemma, for each sense s retrieves <sense, sum(occurrences in texts, excluded text)> pairs
            sid_scores = [(s, sum(general_mfs_statistics[word.lang][word.lemma][s].values()) -
                           general_mfs_statistics[word.lang][word.lemma][s].get(word.document, 0))
                          for s in general_mfs_statistics[word.lang][word.lemma]]
            # first one is the sense with highest number of occurrences
            rfss = sorted(sid_scores, key=lambda x: x[1], reverse=True)
            # scores not needed
            if rfss and isinstance(rfss[0], tuple):
                rfss = [i for (i, j) in sorted(sid_scores, key=lambda x: x[1], reverse=True)]

    elif word.lang in general_mfs_statistics and word.lang == 'eng':
        if word.lemma + '-' + word.pos in general_mfs_statistics[word.lang]:
            rfss = general_mfs_statistics[word.lang][word.lemma + '-' + word.pos]

    try:
        rfss = [i.replace('-s', '-a') for i in rfss]
    except:
        import pdb; pdb.set_trace()
    return rfss


def offset_to_synset(offset_pos):
    return wn._synset_from_pos_and_offset(offset_pos[-1], int(offset_pos[:8]))


def get_mfs_offset(word):
    """ Returns list

    :param word:
    :return:
    """
    if synset_lookup(word):
        return [get_offset(synset_lookup(word)[0])]
    return []


def synset_lookup(word):
    if word.lemma in generic_senses.values():
        return wn.synsets(word.lemma, pos='n', lang='eng')
    if re.match(r'^\d+?$', word.lemma):
        return wn.synsets(word.lemma, pos=word.pos, lang='eng')
    try:
        if word.pos in ('a', 'r', 'v', 'n', 's'):
            return wn.synsets(word.lemma, lang=word.lang, pos=word.pos)
        else:
            return wn.synsets(word.lemma, lang=word.lang)
    except:
        import pdb; pdb.set_trace()

def assign_sense(target_word, assigned_sense, contributing_languages, assignment_type, comments=None):
    """

    :param target_word:
    :param assigned_sense:
    :param contributing_languages:
    :param assignment_type:
    :return:
    """
    target_word.add_msi_annotation(assigned_sense, list(contributing_languages), assignment_type, comments)


def get_only_element_in_overlap(overlap):
    try:
        assert len(overlap) == 1
    except AssertionError as e:
        raise e
    return list(overlap)[0]


def get_offset(synset):
    try:
        return str(synset.offset()).zfill(8) + '-' + synset.pos().replace('s', 'a')
    except nltk.corpus.reader.wordnet.WordNetError as e:
        print(e)
        import pdb; pdb.set_trace()


def resort_to_mfs(target_word, overlap):
    """

    :param target_word:
    :param overlap:
    :return:
    """
    mfs = get_mfs_offset(target_word)
    overlap = overlap.intersection(mfs)
    if len(overlap) == 1:
        assigned_sense = get_only_element_in_overlap(overlap)
        assignment_type = 'mfs_in_overlap'
    else:
        assert set(mfs).issubset((map(get_offset, synset_lookup(target_word))))
        if len(mfs) == 0:
            import pdb; pdb.set_trace()
        # check if it was part of the original set
        try:
            assigned_sense = get_only_element_in_overlap(mfs)
        except AssertionError:
            import pdb; pdb.set_trace()
            assigned_sense = None
        assignment_type = 'mfs'

    return assigned_sense, assignment_type


def make_decision(target_word, overlap, corpus_sense_frequencies=False):
    """Works with the current overlap set

    :param target_word:
    :param overlap:
    :param corpus_sense_frequencies:
    :return:
    """
    if len(overlap) == 1:
        assigned_sense = get_only_element_in_overlap(overlap)
        assignment_type = 'disambiguated_by_msi'
    else:
        if corpus_sense_frequencies:
            frequent_sense_bag = get_relative_frequent_senses(target_word)
            if overlap.intersection(frequent_sense_bag):
                overlap = overlap.intersection(frequent_sense_bag)
                """If resorting to SFS statistics leads to an overlap containing one sense, 
                the word is disambiguated (mfs_in_overlap); if the overlap still results in more 
                than one sense, the most frequent one among the ones left is selected (rmfs_within_overlap). """
                if len(overlap) == 1:
                    assigned_sense = get_only_element_in_overlap(overlap)
                    assignment_type = 'mfs_in_overlap'
                else:
                    # select sense with the highest frequency in frequent_sense_bag
                    assigned_sense = frequent_sense_bag[0]
                    assignment_type = 'rmfs_within_overlap'
            else:
                assigned_sense, assignment_type = resort_to_mfs(target_word, overlap)
        else:
            assigned_sense, assignment_type = resort_to_mfs(target_word, overlap)

    return assigned_sense, assignment_type

def print_recap_for_table(recap):
    d= {'eng' : [],
        'ita' : [],
        'ron' : [],
        'jpn': []
        }
    with open('results.txt', 'w') as so:
        for lang in recap:
            so.write(f"\t{lang}\t\t\t\t\n")
            d[lang].append(f"doc_id\tMSI Precision\tMFS Precision\tCoarse MSI Precision\tCoarse MFS Precision\tCoverage\n")
            for column in sorted(recap[lang]):
                if column not in ('contributing_languages', 'aligned_languages'):
                    d[lang].append(f"{column}\t{recap[lang][column]['precision']}\t{recap[lang][column]['precision_mfs']}\t"
                         f"{recap[lang][column]['precision_coarse']}\t{recap[lang][column]['precision_coarse_mfs']}\t"
                         f"{recap[lang][column]['coverage']}\n")
        import pdb; pdb.set_trace()


def perform_intersection(target_word, possible_target_synsets, aligned_synset_bags):
    """Be aware: compares offsets interally.

    :param target_word:
    :param aligned_synset_bags:
    :return:
    """
    overlap = possible_target_synsets.copy()
    contributing_languages = set()
    # start overlapping from the most populated synset_bag
    for lang in sorted(aligned_synset_bags, key=lambda k: len(aligned_synset_bags[k]), reverse=True):
        # don't perform intersection if that leaves the set with no one of the target synsets left
        # it may happen, because other wordnets are more developed - but it's important that the annotation is covered
        # in the target's language WN
        if overlap.intersection(aligned_synset_bags[lang]) and possible_target_synsets.intersection(
                aligned_synset_bags[lang]):
            overlap = overlap.intersection(aligned_synset_bags[lang])
            contributing_languages.add(lang)
        else:
            # don't perform intersection if the overlap leads to an empty set
            continue

    return overlap, contributing_languages


def get_aligned_words_synsets(word):
    """Returns bag of offsets

    :param word:
    :return:
    """
    aligned_synset_bags = {}
    for lang, aligned_word in word.alignments.items():
        aligned_synset_bags[lang] = set(map(get_offset, synset_lookup(aligned_word)))

    # take advantage of the further alignments of the only aligned word
    if len(word.alignments) == 1:
        only_aligned_word = word.alignments[lang]
        for other_lang, aligned_word in only_aligned_word.alignments.items():
            if other_lang not in (only_aligned_word.lang, word.lang):
                aligned_synset_bags[other_lang] = set(map(get_offset, synset_lookup(aligned_word)))

    return aligned_synset_bags


def evaluate_msi(multilingual_corpus):
    """"""

    with open('../resources/coarse_senses/sense_clustering_dict.json') as infile:
        coarse_senses_dict = json.loads(infile.read())

    recap = {lang : defaultdict(lambda: 0) for lang in multilingual_corpus.languages}
    for _, corpus in multilingual_corpus.corpora.items():
        recap[corpus.lang]['contributing_languages'] = Counter()
        recap[corpus.lang]['aligned_languages'] = Counter()
        for doc_id, document in corpus.documents.items():
            recap[corpus.lang][doc_id] = defaultdict(lambda: 0)
            for _, sentence in document.sentences.items():
                for _, word in sentence.tokens.items():
                    if word.sense and word.alignments:
                        recap[corpus.lang][doc_id]['counts'] += 1

                        mfs = get_mfs_offset(word)
                        if mfs:
                            mfs = get_only_element_in_overlap(mfs)
                            if mfs == word.sense:
                                recap[corpus.lang][doc_id]['mfs_match'] += 1
                            else:
                                recap[corpus.lang][doc_id]['mfs_mismatch'] += 1
                                if mfs in coarse_senses_dict and word.sense in coarse_senses_dict[mfs]:
                                    recap[corpus.lang][doc_id]['coarse_mfs_match'] += 1

                        rmfs = get_relative_frequent_senses(word)
                        if rmfs:
                            rmfs = rmfs[0]
                            if rmfs == word.sense:
                                recap[corpus.lang][doc_id]['rmfs_match'] += 1
                            else:
                                recap[corpus.lang][doc_id]['rmfs_mismatch'] += 1
                                if rmfs in coarse_senses_dict and word.sense in coarse_senses_dict[rmfs]:
                                    recap[corpus.lang][doc_id]['coarse_rmfs_match'] += 1

                        if word.msi_annotation:
                            if word.msi_annotation.assigned_sense == word.sense:
                                recap[corpus.lang][doc_id]['match'] += 1
                                recap[corpus.lang][doc_id][word.msi_annotation.assignment_type] += 1
                                recap[corpus.lang]['contributing_languages'][len(word.msi_annotation.contributing_languages)] += 1
                                recap[corpus.lang]['aligned_languages'][len(word.alignments)] += 1
                            elif word.msi_annotation.assigned_sense is None:
                                recap[corpus.lang][doc_id][word.msi_annotation.assignment_type] += 1
                            elif word.msi_annotation.assigned_sense and word.sense \
                                    and word.msi_annotation.assigned_sense != word.sense \
                                    and re.match(r'\d{8}-[avrn]', word.msi_annotation.assigned_sense):
                                recap[corpus.lang][doc_id]['mismatch'] += 1
                                if word.msi_annotation.assigned_sense in coarse_senses_dict \
                                    and word.sense in coarse_senses_dict[word.msi_annotation.assigned_sense]:
                                    recap[corpus.lang][doc_id]['coarse_match'] += 1
                                else:
                                    recap[corpus.lang][doc_id]['coarse_mismatch'] += 1

                                #print(word.sense, word.lemma, word.msi_annotation.assigned_sense, coarse_senses_dict.get(word.msi_annotation.assigned_sense, []))

            assert recap[corpus.lang][doc_id]['mismatch'] + recap[corpus.lang][doc_id]['no_sense'] + recap[corpus.lang][doc_id]['match'] == recap[corpus.lang][doc_id]['counts']
            assert recap[corpus.lang][doc_id]['coarse_mismatch'] + recap[corpus.lang][doc_id]['coarse_match'] + recap[corpus.lang][doc_id]['no_sense'] + recap[corpus.lang][doc_id]['match'] == recap[corpus.lang][doc_id]['counts']


            # content words (that had sense) with alignments, excluding those not having a sense in WN 3.0
            number_annotable_words = recap[corpus.lang][doc_id]['counts'] - recap[corpus.lang][doc_id]['no_sense']

            # estimate on words that had sense (non necessarily alignment)
            number_content_words = document.number_content_words_in_document()

            recap[corpus.lang][doc_id]['precision'] = round(recap[corpus.lang][doc_id]['match'] / number_annotable_words, 3)

            recap[corpus.lang][doc_id]['precision_mfs'] = round(recap[corpus.lang][doc_id]['mfs_match'] / number_annotable_words, 3)

            recap[corpus.lang][doc_id]['precision_coarse'] = round((recap[corpus.lang][doc_id]['coarse_match'] + recap[corpus.lang][doc_id]['match']) / number_annotable_words, 3)

            recap[corpus.lang][doc_id]['precision_coarse_mfs'] = round((recap[corpus.lang][doc_id]['mfs_match'] + recap[corpus.lang][doc_id]['coarse_mfs_match']) / number_annotable_words, 3)

            recap[corpus.lang][doc_id]['coverage'] = round(number_annotable_words / number_content_words, 3)

    from pprint import pprint
    pprint(recap)
    print_recap_for_table(recap)


def check_for_named_entities(word):
    # overlap fails if annotation is in English and corpus in language other than English
    if word.lemma in ('group', 'location', 'person', 'grand_jury') and word.lang != 'eng':
        return wn.synsets(word.lemma, pos='n')
    elif re.match(r'^\d+?$', word.lemma):
        return wn.synsets(word.lemma)


def is_multiword(lemma):
    return '_' in lemma

def apply_msi_to_corpus(multilingual_corpus, langs, use_sense_frequencies=False):
    """

    :param multilingual_corpus:
    :param corpus_sense_frequencies:
    :return:
    """
    if use_sense_frequencies:
        global general_mfs_statistics
        general_mfs_statistics = _load_corpora_sense_frequency_statistics(langs)
        print("External sense frequencies enabled...")

        corpus_sense_frequencies = True
    for _, corpus in multilingual_corpus.corpora.items():
        for _, document in corpus.documents.items():
            for _, sentence in document.sentences.items():
                for _, word in sentence.tokens.items():
                    if word.sense and word.alignments and not word.msi_annotation:
                        aligned_synset_bags = get_aligned_words_synsets(word)
                        target_synsets = set(map(get_offset, synset_lookup(word)))
                        if not target_synsets:
                            if check_for_named_entities(word):
                                target_synsets = set(map(get_offset, check_for_named_entities(word)))
                            else:
                                if word.lang == 'jpn' and word.equivalent_wn_senses:
                                    target_synsets = set(word.equivalent_wn_senses)
                                else:
                                    """
                                    possible cases:
                                        if (word.lang =='ita' and word.sense and not target_synsets) 
                                        or is_multiword(word.lemma) 
                                        or (word.lang == 'jpn' and not word.equivalent_wn_senses):
                                    """
                                    assigned_sense = None
                                    assignment_type = 'no_sense'
                                    add_to_missing_lemmas_recap(word)
                                    assign_sense(word, assigned_sense, set(word.alignments.keys()), assignment_type)
                                    continue
                        overlap, contributing_languages = perform_intersection(word, target_synsets, aligned_synset_bags)
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
        #
        # if options.json_input_folder:
        #     try:
        #         multilingual_corpus = jfr.read_input_files(options.json_input_folder, langs)
        #     except BaseException as e:
        #         jfr.folder_instructions()
        #
        # elif options.xml_input_file:
        #     multilingual_corpus = xr.load_multilingualcorpus_from_xml(options.xml_input_file)
        # else:
        #     print('Valid input formats are XML compliant to NTUMC DTD or input folder with json files as below')
        #     jfr.folder_instructions()
        #     sys.exit()

        if options.automatic_alignments and \
                options.automatic_alignments not in ["gs", "auto_grow", "auto_int", "sense", "all"]:
            print('Word alignment choice not valid. Choose one beteeen "gs", "auto_grow", "auto_int", "sense", "all"')

        if options.sense_frequencies:
            use_general_mfs_statistics = True
        else:
            use_general_mfs_statistics = False

        apply_msi_to_corpus(multilingual_corpus, langs, use_general_mfs_statistics)
        print("Starting MSI...")

    elif options.languages and options.xml_input_file:
        pass
    else:
        print(f"""Admitted languages are: {wn.langs()}""")
        sys.exit()