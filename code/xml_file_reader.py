import sys
from lxml import etree
from corpus import Corpus, Document, Sentence, Word, MultilingualCorpus
from corpus import Alignment, AlignmentCollector


class InvalidMultilingualCorpusException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

def load_multilingualcorpus_from_xml(xml_file):
    tree = etree.parse(open(xml_file))

    root = tree.getroot()

    if root.attrib['linguality'] != 'multilingual':
        raise InvalidMultilingualCorpusException("Attribute linguality's value is not 'multilingual' ")
    mc = MultilingualCorpus(id=root.attrib['corpusID'], title=root.attrib['title'], languages=[], corpora={}, alignment_collector=None)

    dict_docs = {}
    dict_alignments = {}
    for element in root.getchildren():
        if element.tag == 'Document':

            doc_element = Document(id=element.attrib['title'], lang=element.attrib['language'],
                                   sentences={}, corpus=None, multilingual_corpus=mc)

            for sent in element.getchildren():
                sent_element = Sentence(id=sent.attrib['sid'], document=doc_element, tokens={}, text=None)

                for word in sent.getchildren():
                    #     __slots__ = ['id', 'document', 'lang', 'surface_form', 'lemma', 'pos', 'upos', 'sense', 'msi_annotation', 'sentence', 'alignments']
                    word_element = Word(id=word.attrib['wid'], document=doc_element, lang=doc_element.lang,
                                        surface_form=word.attrib['surface_form'],
                                        lemma= word.attrib['lemma'],
                                        pos=word.attrib['pos'],
                                        sense=None)
                    concepts = sent.findall(f'Concept[@wid="{word_element.id}"]')
                    if concepts:
                        for concept in concepts:
                            if concept.getchildren():
                                import pdb; pdb.set_trace()
                                word.msi_annotation = ''

                            word.sense = concept.attrib['synset_tag']

            # add document to dictionary to create object Corpus when done
            dict_docs[element.attrib['language']] = dict_docs.get(element.attrib['language'], []) \
                                                    + [doc_element]

        elif element.tag == 'Alignment':
            for alignment in alignment.getchildren():

                if alignment.tag == 'DocAlignment':
                    aligned_docs = alignment.attrib['docID'].split()
                    for doc in aligned_docs:
                        for target in aligned_docs:
                            if doc == target:
                                continue
                            source_doc_alignment = Alignment(type='document', source_id=doc, target_id=target, origin='manual')
                            mc.add_document_alignment(doc, source_doc_alignment)

                elif alignment.tag == 'SentAlignment':

                    source_sent_alignment = Alignment(type='sentence', source_id=source_doc.lang + '_' + source_sent,
                                                      target_id=target_doc.lang + '_' + target_sent, origin='manual')
                    target_sent_alignment = Alignment(type='sentence', source_id=target_doc.lang + '_' + target_sent,
                                                      target_id=source_doc.lang + '_' + source_sent, origin='manual')

                    mc.add_alignment(source_sent_alignment, target_sent_alignment)

                elif alignment.tag == 'WordAlignment':

                    source_word_alignment = Alignment(type='word', source_id=source_doc.lang + '_' + source_wid,
                                                      target_id=target_doc.lang + '_' + target_wid, origin='manual')
                    target_word_alignment = Alignment(type='word', source_id=target_doc.lang + '_' + target_wid,
                                                      target_id=source_doc.lang + '_' + source_wid, origin='manual')

                    mc.add_alignment(source_word_alignment, target_word_alignment)
                    # add alignments to Word objects
                    source_word = source_doc.get_word(source_sid, source_wid)
                    target_word = target_doc.get_word(source_sid, target_wid)

                    if source_word and target_word:  # FIXME necessary as long as I don't have also the grammatical words as well
                        source_word.add_alignment(target_lang, target_word)
                        target_word.add_alignment(source_lang, source_word)

                elif alignment.tag == 'ConceptAlignment':
                            source_concept_alignment = Alignment(type='concept',
                                                                 source_id=source_doc.lang + '_' + source_wid.replace(
                                                                     "t", "c"),
                                                                 target_id=target_doc.lang + '_' + target_wid.replace(
                                                                     "t_", "c_"), origin='manual')
                            target_concept_alignment = Alignment(type='concept',
                                                                 source_id=target_doc.lang + '_' + target_wid.replace(
                                                                     "t", "c"),
                                                                 target_id=source_doc.lang + '_' + source_wid.replace(
                                                                     "t_", "c_"), origin='manual')

                            mc.add_alignment(source_concept_alignment, target_concept_alignment)

                """
                    <Alignment>
                        {% for doc_id, doc_alignments in multicorpus.alignment_collector.documents.items() -%}
                        <DocAlignment docID="{{doc_alignments|join(' ')}}"/>
                        {% endfor -%}
                        {% for source_id, sent_alignments in multicorpus.alignment_collector.sentences.items() -%}
                            {% for target_alignment in sent_alignments -%}
                            <SentAlignment sid_from="{{source_id}}" sid_to="{{target_alignment.target_id}}" type="{{target_alignment.origin}}"/>
                            {% endfor -%}
                        {% endfor -%}
                        {% for source_id, word_alignments in multicorpus.alignment_collector.words.items() -%}
                            {% for target_alignment in word_alignments -%}
                            <WordAlignment wid_from="{{source_id}}" wid_to="{{target_alignment.target_id}}" type="{{target_alignment.origin}}"/>
                            {% endfor -%}
                        {% endfor -%}
                        {% for source_id, concept_alignments in multicorpus.alignment_collector.concepts.items() -%}
                            {% for target_alignment in concept_alignments -%}
                            <ConceptAlignment cid_from="{{source_id}}" cid_to="{{target_alignment.target_id}}" type="{{target_alignment.origin}}"/>
                            {% endfor -%}
                        {% endfor -%}
                    </Alignment>
                </Corpus>
                """

    corpus_id = 1
    for lang, documents in dict_docs.items():
        corpus_object = Corpus(id=f'c{corpus_id}', title='', lang=lang, documents=documents)
        mc.add(corpus_object)
        corpus_id += 1

    return mc

if __name__ == '__main__':
    load_multilingualcorpus_from_xml(sys.argv[1])
