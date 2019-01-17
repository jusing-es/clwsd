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
    import pdb; pdb.set_trace()

    if root.attrib['linguality'] != 'multilingual':
        raise InvalidMultilingualCorpusException("Attribute linguality's value is not 'multilingual' ")
    mc = MultilingualCorpus(id=root.attrib['corpusID'], title=root.attrib['title'], languages=[], corpora={}, alignment_collector=None)

    dict_docs = {}
    for doc in root.getchildren():

        doc_element =

        """
        class Corpus(object):
    __slots__ = ['id', 'title', 'lang', 'documents']

    def __init__(self, id, lang, sentences={}, corpus=None, multilingual_corpus=None):
        self.id = id
        self.lang = lang
        self.sentences = sentences
        self.corpus = None
        self.multilingual_corpus = None


        """

        # add document to dictionary to create object Corpus when done
        dict_docs[doc.attrib['language']] =


    """
    <Corpus corpusID="{{multicorpus.id}}" title="{{multicorpus.title}}" linguality="multilingual">
        {% for _, corpus in multicorpus.corpora.items() -%}
            {% for key, doc in corpus.documents.items() -%}
            <Document docID="{{doc.lang + '_' + doc.id}}" doc="text" language="{{doc.lang}}" title="{{key}}">
                {% for sid, sent in doc.sentences.items() -%}
                <Sentence sid="{{doc.lang + '_' +sid}}" sent="{{sent.text}}">
                    {% for wid, word in sent.tokens.items() -%}
                    <Word wid="{{doc.lang + '_' + wid}}" pos="{{word.pos}}" lemma="{{word.lemma}}" surface_form="{{word.surface_form}}"/>
                    {% endfor -%}
                    {% for wid, word in sent.tokens.items() if word.sense -%}
                    <Concept cid="{{(doc.lang + '_' + wid).replace('t_', 'c_')}}" wid="{{doc.lang + '_' + wid}}" synset_tag="{{word.sense}}" clemma="{{word.lemma}}"/>
                     {% if word.msi_annotation and word.msi_annotation.assigned_sense -%}
                    <Concept cid="{{(doc.lang + '_' + 'msi' + '_' + wid).replace('t_', 'c_')}}" wid="{{doc.lang + '_' + wid}}" synset_tag="{{word.msi_annotation.assigned_sense}}" clemma="{{word.lemma}}">
                        <Tag category="msi_annotation" value="{{word.msi_annotation.assigned_sense}}" />
                    </Concept>
                     {% endif -%}
                    {% endfor -%}
                </Sentence>
                {% endfor -%}
            </Document>
            {% endfor -%}
        {% endfor -%}
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
    return mc

if __name__ == '__main__':
    load_multilingualcorpus_from_xml(sys.argv[1])