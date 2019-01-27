import codecs
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

common_49 = ['a01', 'a11', 'a12', 'a13', 'a14', 'b13', 'b20', 'c01', 'c02', 'c04', 'd01', 'd03', 'e01', 'e04', 'e24', 'e29', 'f03', 'f10', 'f19', 'f43', 'g11', 'g15', 'h01', 'j01', 'j03', 'j04', 'j05', 'j10', 'j17', 'j22', 'j23', 'j37', 'j52', 'j53', 'j55', 'j57', 'j58', 'j60', 'k01', 'k02', 'k03', 'k05', 'k08', 'k10', 'k11', 'k13', 'k15', 'k18', 'k19']

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


def add_automatic_alignment_to_corpus(multilingual_corpus):
    align = codecs.open("../files/training/corpus/alignments/en_ro_align.align", "rb", "utf-8")
    aligned_corpus = multilingual_corpus.corpora['eng_sc']
    ron_corpus = multilingual_corpus.corpora['ron_sc']
    al_enro = {}
    count=0
    # {"r04": {"s_52%t_52_8": "t_52_5",
    for l in align:
        l = l.split()
        # sentence number is the second number
        id_text, source_sid = l[0][3:6], 's_'+ l[0].split("_")[-2]

        ron_lemma, ron_sense = l[2], l[4]
        target_lemma, target_sense = l[6], l[8]

        if id_text in aligned_corpus.documents:
            target_sentence = aligned_corpus.documents[id_text].sentences[source_sid]
            ron_sentence = ron_corpus.documents[id_text].sentences[source_sid]

            # found match w/ english
            current_word = ron_sentence.get_word_from_lemma_and_sense(ron_lemma, ron_sense)
            target_matched_word = target_sentence.get_word_from_lemma_and_sense(target_lemma, target_sense)

            if current_word and target_matched_word and current_word.sense == target_matched_word.sense:
                source_wid = current_word.id
                count += 1
                #print(id_text, f'{source_sid}%{source_wid}', target_matched_word.id)
                #print(current_word.lemma, current_word.sense, target_matched_word.lemma, target_matched_word.sense)
                if id_text in al_enro:
                    al_enro[id_text].update({f'{source_sid}%{source_wid}' : target_matched_word.id})
                else:
                    al_enro[id_text] = {f'{source_sid}%{source_wid}' : target_matched_word.id}

    #print(len(al_enro['a01']))

    with open('../alignments/ro2en.json', 'w') as so:
        json.dump(al_enro, so)
    return al_enro


def add_automatic_alignment_to_corpus_ita(multilingual_corpus):
    align = codecs.open("../files/training/corpus/alignments/en_ro_align_2_verified.align", "rb", "utf-8")
    aligned_corpus = multilingual_corpus.corpora['ita_sc']
    ron_corpus = multilingual_corpus.corpora['ron_sc']
    al_enro = {}
    count=0
    # {"r04": {"s_52%t_52_8": "t_52_5",
    for l in align:
        l = l.split()
        # sentence number is the second number
        id_text, source_sid = l[0][3:6], 's_'+ l[0].split("_")[-1]
        ron_lemma, ron_sense = l[2], l[4]
        target_lemma, target_sense = l[6], l[8]

        if id_text in aligned_corpus.documents:
            target_sentence = aligned_corpus.documents[id_text].sentences[source_sid]
            ron_sentence = ron_corpus.documents[id_text].sentences[source_sid]

            # found match w/ english
            current_word = ron_sentence.get_word_from_lemma_and_sense(ron_lemma, ron_sense)
            target_matched_word = target_sentence.get_word_from_lemma_and_sense(target_lemma, target_sense)

            if current_word and target_matched_word and current_word.sense == target_matched_word.sense:
                source_wid = current_word.id
                count += 1
                #print(id_text, f'{source_sid}%{source_wid}', target_matched_word.id)
                #print(current_word.lemma, current_word.sense, target_matched_word.lemma, target_matched_word.sense)
                if id_text in al_enro:
                    al_enro[id_text].update({f'{source_sid}%{source_wid}' : target_matched_word.id})
                else:
                    al_enro[id_text] = {f'{source_sid}%{source_wid}' : target_matched_word.id}

    #print(len(al_enro['a01']))

    with open('../alignments/ro2it.json', 'w') as so:
        json.dump(al_enro, so)
    return al_enro


def add_automatic_alignment_to_corpus_jpn(multilingual_corpus):
    align = codecs.open('../files/training/corpus/jpn/a01.json', "rb", "utf-8")
    aligned_corpus = multilingual_corpus.corpora['eng_sc']
    ron_corpus = multilingual_corpus.corpora['jpn_sc']
    al_jp2en = {}
    count=0
    # {"r04": {"s_52%t_52_8": "t_52_5",
    for l in align:
        l = l.split()
        # sentence number is the second number
        id_text, source_sid = l[0][3:6], 's_'+ l[0].split("_")[-1]
        ron_lemma, ron_sense = l[2], l[4]
        target_lemma, target_sense = l[6], l[8]

        if id_text in aligned_corpus.documents:
            target_sentence = aligned_corpus.documents[id_text].sentences[source_sid]
            ron_sentence = ron_corpus.documents[id_text].sentences[source_sid]

            # found match w/ english
            current_word = ron_sentence.get_word_fron_lemma_and_sense(ron_lemma, ron_sense)
            target_matched_word = target_sentence.get_word_fron_lemma_and_sense(target_lemma, target_sense)

            if current_word and target_matched_word and current_word.sense == target_matched_word.sense:
                source_wid = current_word.id
                count += 1
                print(id_text, f'{source_sid}%{source_wid}', target_matched_word.id)
                print(current_word.lemma, current_word.sense, target_matched_word.lemma, target_matched_word.sense)
                if id_text in al_jp2en:
                    al_jp2en[id_text].update({f'{source_sid}%{source_wid}' : target_matched_word.id})
                else:
                    al_jp2en[id_text] = {f'{source_sid}%{source_wid}' : target_matched_word.id}

    #print(len(al_jp2en['a01']))

    with open('../alignments/2.json', 'w') as so:
        json.dump(al_jp2en, so)
    return al_jp2en


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
                                pos=doc[sent][token][2], upos=None, sense=doc[sent][token][3].replace('s', 'a'), external_sense=None,
                                document=doc_in.id, sentence=sentence_in.id, alignments={}, equivalent_wn_senses= [], msi_annotation=None)

                # change the lemma in generic placeholder if sense is location.n.01/group.n.01/person.n.01
                if word_in.sense in msi.generic_senses.keys():
                    word_in.lemma = msi.generic_senses[word_in.sense]

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
    ron_folder = '../files/training/corpus/rom'
    jpn_folder = '../files/training/corpus/jpn'
    with open(sys.argv[5]) as si:
        en2it_alignments = json.loads(si.read())

    eng_corpus = Corpus(id='eng_sc', title='English Semcor', lang=source_lang, documents={})
    ita_corpus = Corpus(id='ita_sc', title='Italian Semcor', lang=target_lang, documents={})
    ron_corpus = Corpus(id='ron_sc', title='ronanian Semcor', lang='ron', documents={}) #FIXME
    jpn_corpus = Corpus(id='jpn_sc', title='Japanese Semcor', lang='jpn', documents={}) #FIXME

    logger.info('starting')
    # load documents
    for doc in os.listdir(source_folder):
        if os.path.isfile(os.path.join(target_folder, doc)):
            #print(doc)
            eng_doc = load_document(source_lang, os.path.join(source_folder, doc))
            ita_doc = load_document(target_lang, os.path.join(target_folder, doc))
            ron_doc = load_document('ron', os.path.join(ron_folder, doc))
            jpn_doc = load_document_jpn('jpn', os.path.join(jpn_folder, doc))
            eng_corpus.add(eng_doc)
            ita_corpus.add(ita_doc)
            ron_corpus.add(ron_doc)
            jpn_corpus.add(jpn_doc)

    multilingual_corpus = MultilingualCorpus(id='MPC', title='Multilingual Parallel Corpus', corpora={},
                                             alignment_collector=AlignmentCollector())

    multilingual_corpus.add(jpn_corpus, eng_corpus, ita_corpus, ron_corpus)
    mc = multilingual_corpus
    ac = mc.alignment_collector
    add_alignments_to_corpus(en2it_alignments, multilingual_corpus, eng_corpus.id, ita_corpus.id)

    add_automatic_alignment_to_corpus(multilingual_corpus)
    add_automatic_alignment_to_corpus_ita(multilingual_corpus)

    with open('../alignments/ro2en.json', 'r') as si:
        ro2en_alignments = json.loads(si.read())

    add_alignments_to_corpus(ro2en_alignments, multilingual_corpus, ron_corpus.id, eng_corpus.id)

    with open('../alignments/ro2it.json', 'r') as si:
        ro2it_alignments = json.loads(si.read())

    add_alignments_to_corpus(ro2it_alignments, multilingual_corpus, ron_corpus.id, ita_corpus.id)

    with open('../alignments/en2jp_alignments_49.json', 'r') as si:
        en2jp_alignments = json.loads(si.read())

    add_alignments_to_corpus(en2jp_alignments, multilingual_corpus, eng_corpus.id, jpn_corpus.id)

    msi.apply_msi_to_corpus(multilingual_corpus, multilingual_corpus.languages, True)
    import pdb; pdb.set_trace()

    msi.evaluate_msi(multilingual_corpus)
    #print(render_multilingual_corpus(multilingual_corpus))
    #dump_multilingual_corpus_to_xml(multilingual_corpus)

