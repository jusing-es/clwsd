import json
import logging
import os
from pathlib import Path
import sys
from render2xml import render_monolingual_corpus, render_multilingual_corpus
from nltk.corpus import wordnet as wn
from pprint import pprint
import msi

from corpus import Corpus, Document, Sentence, Word, MultilingualCorpus
from corpus import Alignment, AlignmentCollector

logger = logging.getLogger(__name__)

def add_alignments_to_corpus(alignments, multilingual_corpus):
    #TODO
    #FIXME alignment_collector should be a variable of CorpusCollector

    doc_id = 'a01'
    json_alignments = alignments['a01']


    source_doc = multilingual_corpus['eng_sc']['a01']
    target_doc = multilingual_corpus['ita_sc']['a01']
    source_doc_alignment = Alignment(type='document', source_id=source_doc.lang + '_' + source_doc.id,
                              target_id=target_doc.lang + '_' + target_doc.id, origin='manual')

    multilingual_corpus.add_document_alignment(doc_id, source_doc_alignment)

    sent_pairs = set()
    for sentid in json_alignments:
        source_sid, source_wid = sentid.split("%")
        target_wid = json_alignments[sentid]
        source_word_alignment = Alignment(type='word', source_id=source_doc.lang + '_' + source_wid,
                                         target_id= target_doc.lang+ '_' + target_wid, origin='manual')
        target_word_alignment = Alignment(type='word', source_id=target_doc.lang + '_' + target_wid,
                                          target_id=source_doc.lang + '_' + source_wid, origin='manual')

        multilingual_corpus.add_alignment(source_word_alignment, target_word_alignment)
        # add alignments to Word objects

        source_word = source_doc.get_word(source_sid, source_wid)
        target_word = target_doc.get_word(source_sid, target_wid)

        if source_word and target_word: #FIXME necessary as long as I don't have also the grammatical words as well
            source_word.add_alignment(target_lang, target_word)
            target_word.add_alignment(source_lang, source_word)
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


def choose_majority_tag(word):
    #iterates over self.annotations
    pass


def dump_to_file(corpus):
    with open (f'{corpus.title}.json', 'w') as so:
      json.dumps(corpus.to_json())

def dump_monolingual_corpus_to_xml(corpus):
    data = render_monolingual_corpus(corpus)
    with open(corpus.lang + '.xml', 'w') as so:
        so.write(data)
    print('File', corpus.lang + '.xml', 'created')

def dump_multilingual_corpus_to_xml(corpus):
    data = render_multilingual_corpus(corpus)
    with open(corpus.id + '.xml', 'w') as so:
        so.write(data)
    print('File', corpus.id + '.xml', 'created')

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
                                pos=doc[sent][token][2], upos=None, sense=doc[sent][token][3].replace('s', 'a'),
                                document=doc_in.id, sentence=sentence_in.id, alignments={}, msi_annotation=None)
                raw_text.append(word_in.surface_form)
                sentence_in.add(word_in)
            assert len(sentence_in.tokens) == len(doc[sent])
            sentence_in.text = ' '.join(raw_text)
            doc_in.add(sentence_in)
    return doc_in



if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit("Invalid number of arguments")
    source_lang= sys.argv[1]
    target_lang=sys.argv[2]
    if source_lang not in wn.langs():
        msi.show_supported_languages(source_lang)
    if target_lang not in wn.langs():
        msi.show_supported_languages(target_lang)

    source_folder = sys.argv[3]
    target_folder = sys.argv[4]
    with open(sys.argv[5]) as si:
        json_alignments = json.loads(si.read())

    source_corpus = Corpus(id='eng_sc', title='English Semcor', lang=source_lang, documents={})
    target_corpus = Corpus(id='ita_sc', title='Italian Semcor', lang=target_lang, documents={})
    logger.info('starting')
    # load documents
    for doc in os.listdir(source_folder):
        if os.path.isfile(os.path.join(target_folder, doc)):
            source_doc = load_document(source_lang, os.path.join(source_folder, doc))
            target_doc = load_document(target_lang, os.path.join(target_folder, doc))
            source_corpus.add(source_doc)
            target_corpus.add(target_doc)

    multilingual_corpus = MultilingualCorpus(id='MPC', title='Multilingual Parallel Corpus', corpora={},
                                             alignment_collector=AlignmentCollector())
    multilingual_corpus.add(source_corpus, target_corpus)
    alignments = add_alignments_to_corpus(json_alignments, multilingual_corpus)

    msi.apply_msi_to_corpus(multilingual_corpus, multilingual_corpus.languages, True)
    msi.evaluate_msi(multilingual_corpus)
    #print(render_multilingual_corpus(multilingual_corpus))
    #dump_multilingual_corpus_to_xml(multilingual_corpus)

