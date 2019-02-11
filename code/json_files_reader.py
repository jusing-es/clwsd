import json
import os
import sys
from pathlib import Path
from shared_reader_utils import generic_senses, show_supported_languages, common_49
from corpus import Corpus, Document, Sentence, Word, MultilingualCorpus
from corpus import Alignment, AlignmentCollector
from nltk.corpus import wordnet as wn
import logging

logger = logging.getLogger(__name__)


def folder_instructions():
    print("""
    Expected folder structure for a multilingual corpus in English (eng), Italian (ita), Romanian (rom) and Japanese (jpn):
    corpus/
          eng/
            a01.json
            a02.json
            ...
          ita/
            a01.json
            a02.json
            ...
          rom/
            a01.json
            a02.json
            ...
          jpn/
            a01.json
            a02.json
            ...
          alignments/
             Expected in the following format:
             eng2ita.json
             eng2rom.json
             eng2jpn.json
             ita2eng.json
             ...
    """)

def load_document(source_lang, path):
    with open(path) as si:
        doc = json.loads(si.read())
        doc_id = Path(path).stem
        doc_in = Document(id=doc_id, lang=source_lang, sentences={})
        for sent in sorted(doc, key=lambda x: int(x.split("_")[1])):
            sentence_in = Sentence(id=sent, document=doc_in.id, tokens={}, text='')
            raw_text = []
            for token in sorted(doc[sent], key=lambda x: int(x.split("_")[1]+x.split("_")[2])):
                word_in = Word(id=token, lang=doc_in.lang, surface_form=doc[sent][token][0], lemma=doc[sent][token][1],
                                pos=doc[sent][token][2], upos=None, sense=doc[sent][token][3].replace('s', 'a'), external_sense=None,
                                document=doc_in.id, sentence=sentence_in.id, alignments={}, equivalent_wn_senses= [], msi_annotation=None)

                # change the lemma in generic placeholder if sense is location.n.01/group.n.01/person.n.01
                if word_in.sense in generic_senses.keys():
                    word_in.lemma = generic_senses[word_in.sense]

                raw_text.append(word_in.surface_form)
                sentence_in.add(word_in)
            assert len(sentence_in.tokens) == len(doc[sent])
            sentence_in.text = ' '.join(raw_text)
            doc_in.add(sentence_in)
    return doc_in


def load_document_jpn(source_lang, path):
    # re-read jpn corpus so that sids are sids and not paragraphs sids
    with open(path) as si:
        doc = json.loads(si.read())
        doc_id = Path(path).stem
        doc_in = Document(id=doc_id, lang=source_lang, sentences={})
        for sent in sorted(doc, key=lambda x: int(x.split("_")[1])):
            sentence_in = Sentence(id=sent, document=doc_in.id, tokens={}, text='') #FIXME sentence id and doc_id uniformare
            raw_text = []
            for token in doc[sent]:
                sense, external_sense, equivalent_wn_synsets = None, None, []
                if doc[sent][token]['semcor_tag']:
                    sense = doc[sent][token]['semcor_tag']
                if doc[sent][token]['jwn_annotation']:
                    external_sense = doc[sent][token]['jwn_annotation']
                if doc[sent][token]['equivalent_esc_synsets']:
                    equivalent_wn_synsets = doc[sent][token]['equivalent_esc_synsets']

                word_in = Word(id=token, lang=doc_in.lang,
                               surface_form=' '.join((i['lemma'] for i in doc[sent][token]['components'])),
                               lemma=doc[sent][token]['lemma'],
                               pos=doc[sent][token]['pos'][-1], upos=None, sense=sense, external_sense=external_sense,
                               document=doc_in.id, sentence=sentence_in.id,
                               equivalent_wn_senses = equivalent_wn_synsets,
                               alignments={}, msi_annotation=None)
                raw_text.append(word_in.surface_form)
                sentence_in.add(word_in)
            assert len(sentence_in.tokens) == len(doc[sent])
            sentence_in.text = ' '.join(raw_text)
            doc_in.add(sentence_in)
    return doc_in


def add_alignments_to_corpus(alignments, multilingual_corpus, source_corpus_id, target_corpus_id):

    for doc_in in alignments:
        if doc_in in common_49:
            source_doc = multilingual_corpus[source_corpus_id][doc_in]
            target_doc = multilingual_corpus[target_corpus_id][doc_in]
            source_doc_alignment = Alignment(type='document', source_id=source_doc.lang + '_' + source_doc.id,
                                      target_id=target_doc.lang + '_' + target_doc.id, origin='manual')

            multilingual_corpus.add_document_alignment(doc_in, source_doc_alignment)

            sent_pairs = set()
            for sentid in alignments[doc_in]:
                source_sid, source_wid = sentid.split("%")
                target_wid = alignments[doc_in][sentid]
                source_word_alignment = Alignment(type='word', source_id=source_doc.lang + '_' + source_wid,
                                                 target_id= target_doc.lang+ '_' + target_wid, origin='manual')
                target_word_alignment = Alignment(type='word', source_id=target_doc.lang + '_' + target_wid,
                                                  target_id=source_doc.lang + '_' + source_wid, origin='manual')

                multilingual_corpus.add_alignment(source_word_alignment, target_word_alignment)
                # add alignments to Word objects

                source_word = source_doc.get_word(source_sid, source_wid)
                target_word = target_doc.get_word(source_sid, target_wid)

                if source_word and target_word: #FIXME necessary as long as I don't have also the grammatical words as well
                    source_word.add_alignment(target_word.lang, target_word)
                    target_word.add_alignment(source_word.lang, source_word)
                    if source_word.sense and target_word.sense and source_word.sense == target_word.sense:
                        source_concept_alignment = Alignment(type='concept', source_id=source_doc.lang + '_' + source_wid.replace("t", "c"),
                                                          target_id=target_doc.lang + '_' + target_wid.replace("t_", "c_"), origin='manual')
                        target_concept_alignment = Alignment(type='concept', source_id=target_doc.lang + '_' + target_wid.replace("t", "c"),
                                                          target_id=source_doc.lang + '_' + source_wid.replace("t_", "c_"), origin='manual')

                        multilingual_corpus.add_alignment(source_concept_alignment, target_concept_alignment)

                if (source_sid, source_sid) not in sent_pairs:
                    sent_pairs.add((source_sid, source_sid))

            for source_sent, target_sent in sent_pairs:
                source_sent_alignment = Alignment(type='sentence', source_id=source_doc.lang + '_' + source_sent,
                                                 target_id= target_doc.lang+ '_' + target_sent, origin='manual')
                target_sent_alignment = Alignment(type='sentence', source_id=target_doc.lang + '_' + target_sent,
                                                  target_id=source_doc.lang + '_' + source_sent, origin='manual')

                multilingual_corpus.add_alignment(source_sent_alignment, target_sent_alignment)


def input_languages_are_valid(langs):
    for lang in langs:
        if lang not in wn.langs():
            show_supported_languages(lang)
            return False
    return True


def verify_as_many_folders_as_languages(corpus_folder_tree, langs):
    return set(corpus_folder_tree) == set(langs)


def verify_alignments_folder(alignments_folder_tree, langs):
    for lang_pair in os.listdir(alignments_folder_tree):
         if not set(lang_pair.split('.json')[0].split('2')).issubset(langs):
             return False
    return True


def read_input_files(input_folder, langs):

    contents_input_folder = os.listdir(input_folder)

    # check folder structure is consistent with expected input
    try:
        assert os.path.exists(os.path.join(input_folder, 'corpus'))
        assert os.path.exists(os.path.join(input_folder, 'alignments'))
        assert input_languages_are_valid(langs)

        corpus_folder_tree = os.listdir(os.path.join(input_folder, 'corpus'))
        assert verify_as_many_folders_as_languages(corpus_folder_tree, langs)

        alignments_folder_tree = os.path.join(input_folder, 'alignments')
        assert verify_alignments_folder(alignments_folder_tree, langs)

    except AssertionError:
        folder_instructions()
        sys.exit(1)

    eng_corpus = Corpus(id='eng_sc', title='English Semcor', lang='eng', documents={})
    ita_corpus = Corpus(id='ita_sc', title='Italian Semcor', lang='ita', documents={})
    ron_corpus = Corpus(id='ron_sc', title='ronanian Semcor', lang='ron', documents={})
    jpn_corpus = Corpus(id='jpn_sc', title='Japanese Semcor', lang='jpn', documents={})

    corpora = [eng_corpus, ita_corpus, jpn_corpus, ron_corpus]

    eng_folder = os.path.join(input_folder, 'corpus', 'eng')
    ita_folder = os.path.join(input_folder, 'corpus', 'ita')
    ron_folder = os.path.join(input_folder, 'corpus', 'ron')
    jpn_folder = os.path.join(input_folder, 'corpus', 'jpn')

    folders = [eng_folder, ita_folder, jpn_folder, ron_folder]

    langs.sort()

    logger.info('starting')
    # load documents
    for source_corpus, source_lang, source_folder in zip(corpora, langs, folders):
        for doc in os.listdir(source_folder):
            if source_lang == 'jpn':
                doc = load_document_jpn(source_lang, os.path.join(source_folder, doc))
            else:
                doc = load_document(source_lang, os.path.join(source_folder, doc))
            source_corpus.add(doc)

    multilingual_corpus = MultilingualCorpus(id='MPC', title='Multilingual Parallel Corpus', corpora={},
                                             alignment_collector=AlignmentCollector())

    multilingual_corpus.add(jpn_corpus, eng_corpus, ita_corpus, ron_corpus)
    mc = multilingual_corpus
    ac = mc.alignment_collector

    for alignment_pair in os.listdir(alignments_folder_tree):
        source_lang, target_lang = alignment_pair.split(".json")[0].split("2")
        source_corpus_id = [c.id for c in corpora if c.lang == source_lang][0]
        target_corpus_id = [c.id for c in corpora if c.lang == target_lang][0]

        with open(os.path.join(alignments_folder_tree, alignment_pair), 'r') as si:
            alignments = json.loads(si.read())
            add_alignments_to_corpus(alignments, multilingual_corpus, source_corpus_id, target_corpus_id)

    for corpusid in mc.corpora:
        for doc in mc[corpusid].documents:
            for sent in mc[corpusid][doc].sentences:
                if corpusid != 'jpn_sc':
                    assert len(mc[corpusid][doc][sent]) == mc[corpusid][doc][sent].number_content_words()

        # content words in JPN_SC are those with a link to ESC, so much fewer than the actual annotated words
        if corpusid != 'jpn_sc':
            assert mc[corpusid][doc].number_content_words_in_document() == sum([len(mc[corpusid][doc][sent]) for sent in mc[corpusid][doc].sentences])

    return multilingual_corpus