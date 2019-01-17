import json
import serialization

def decoder(some_dict):
    if set(some_dict.keys()) == set(["__class__", "__args__", "__kw__"]):
        class_ = eval(some_dict['__class__'])
        return class_(*some_dict['__args__'], **some_dict['__kw__'])
    else:
        return some_dict

class MultilingualCorpus(object):
    __slots__ = ['id', 'title', 'languages', 'corpora', 'alignment_collector']
    def __init__(self, id, title, languages=[], corpora={}, alignment_collector=None):
        self.id = id
        self.title = title
        self.languages = languages
        self.corpora = corpora
        self.alignment_collector = alignment_collector

    def __len__(self):
        return len(self.corpora)

    def __getitem__(self, key):
        return self.corpora[key]

    def add(self, *args):
        for corpus in args:
            assert isinstance(corpus, Corpus)
            if corpus.id not in self.corpora:
                self.corpora[corpus.id] = corpus
                self.languages.append(corpus.lang)
                for _, document in corpus.documents.items():
                    document.multilingual_corpus = self

    def set_alignment_collector(self, alignment_collector):
        assert isinstance(alignment_collector, AlignmentCollector)
        self.alignment_collector = alignment_collector

    def add_document_alignment(self, doc_id, *args):
        """Adds alignment to Corpus' alignment collector """
        if self.alignment_collector:
            for alignment in args:
                self.alignment_collector.add_document_alignment(doc_id, alignment)

    def add_alignment(self, *args):
        """Adds alignment to Corpus' alignment collector """
        if self.alignment_collector:
            for alignment in args:
                self.alignment_collector.add(alignment)

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'id': self.id,
                           'title' : self.title,
                           'languages' : self.languages,
                           'corpora': self.corpora,
                           'alignment_collector': self.alignment_collector},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)

    @staticmethod
    def loads(data_json):
        return json.loads(data_json, object_hook=decoder)


class Corpus(object):
    __slots__ = ['id', 'title', 'lang', 'documents']
    def __init__(self, id, title, lang, documents={}):
        self.id = id
        self.title = title
        self.lang = lang
        self.documents = documents

    # def __repr__(self):
    #     return json.dumps(self.__dict__, default=serialization.pretty_print)

    def __getitem__(self, key):
        return self.documents[key]

    def __len__(self):
        return len(self.documents)

    def __eq__(self, other):
        return self.id == other.id and self.title == other.title and self.lang == other.lang \
               and self.documents == other.documents

    def add(self, document):
        assert isinstance(document, Document)
        self.documents[document.id] = document
        document.corpus = self

    def get_words(self):
        words={}
        for doc in self.documents:
            for sent in doc.sentences:
                words = {**words, **sent.tokens}
        return words


    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'id': self.id,
                           'title': self.title,
                           'lang': self.lang,
                           'documents' : self.documents},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)

    @staticmethod
    def loads(data_json):
        return json.loads(data_json, object_hook=decoder)


class Document(object):
    __slots__ = ['id', 'lang', 'sentences', 'corpus', 'multilingual_corpus']

    def __init__(self, id, lang, sentences={}, corpus=None, multilingual_corpus=None):
        self.id = id
        self.lang = lang
        self.sentences = sentences
        self.corpus = None
        self.multilingual_corpus = None

    # def __repr__(self):
    #     return json.dumps(self.__dict__, default=serialization.pretty_print)

    def __getitem__(self, key):
        return self.sentences[key]

    def get_word(self, sid, wid):
        try:
            return self.sentences[sid].tokens[wid]
        except KeyError:
            # s_7%t_7_13 : t_7_14 is for grammatical words, for instance
            return None

    def __len__(self):
        return len(self.sentences)

    def add(self, sentence):
        assert isinstance(sentence, Sentence)
        self.sentences[sentence.id] = sentence

    def add_alignment(self, alignment):
        """Adds alignment to Corpus' alignment collector """
        if self.multilingual_corpus:
            self.multilingual_corpus.alignment_collector.add(alignment)

    # doesn't dump corpus / alignments
    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'id': self.id,
                           'lang': self.lang,
                           'sentences': self.sentences},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)

    @staticmethod
    def loads(data_json):
        return json.loads(data_json, object_hook=decoder)


class Sentence(object):
    __slots__ = ['id', 'document', 'tokens', 'text']
    def __init__(self, id, document, tokens={}, text=''):
        self.id = id
        self.document = document
        self.tokens = tokens
        self.text = text

    # def __repr__(self):
    #     return json.dumps(self.__dict__, default=serialization.pretty_print)

    def __getitem__(self, key):
        return self.tokens[key]

    def __len__(self):
        return len(self.tokens)

    def add(self, word):
        assert isinstance(word, Word)
        self.tokens[word.id] = word

    def add_alignment(self, alignment):
        """Adds alignment to Corpus' alignment collector """
        if self.document.multilingual_corpus:
            self.document.multilingual_corpus.alignment_collector.add(alignment)

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'id': self.id,
                           'document': self.document,
                           'tokens': self.tokens,
                           'text': self.text},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)

    @staticmethod
    def loads(data_json):
        return json.loads(data_json, object_hook=decoder)

class Word(object):
    __slots__ = ['id', 'document', 'lang', 'surface_form', 'lemma', 'pos', 'upos', 'sense', 'msi_annotation', 'sentence', 'alignments']
    def __init__(self, document, id, lang, surface_form, lemma, pos=None, upos=None, sense=None, msi_annotation=None, alignments={}, sentence=None):
        self.document = document
        self.id = id
        self.lang = lang
        self.surface_form = surface_form
        self.lemma = lemma
        self.pos = pos
        self.upos = pos
        self.sense = sense
        self.msi_annotation = msi_annotation
        self.sentence = sentence
        self.alignments = alignments

    def add_alignment(self, target_lang, target_word):
        self.alignments[target_lang] = target_word

    def has_alignment(self, lang):
        """
        Just checks for alignment - doesn't know if the aligned word is annotated with sense!
        :param lang:
        :return:
        """
        if lang in self.alignments:
            return self.alignments[lang]
        else:
            return None

    def add_msi_annotation(self, assigned_sense, contributing_languages, assignment_type, comments=None):
        self.msi_annotation = MsiAnnotation(assigned_sense, contributing_languages, assignment_type, comments)

    def to_string(self):
        return json.dumps(self.__dict__, default=serialization.pretty_print)

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'id': self.id,
                           'document': self.document,
                           'lang' : self.lang,
                            'surface_form' : self.surface_form,
                            'lemma' : self.lemma,
                            'pos' : self.pos,
                            'sense' : self.sense,
                            'msi_annotation' : self.msi_annotation,
                            'sentence' : self.sentence,
                            'alignments' : self.alignments},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)


class MsiAnnotation(object):
    __slots__ = ['assigned_sense', 'contributing_languages', 'assignment_type', 'comments']

    possible_assignment_types = ('mfs_in_overlap', 'disambiguated_by_msi', 'mfs',
                                 'rmfs_within_overlap', 'no_sense')

    def __init__(self, assigned_sense, contributing_languages, assignment_type, comments=None):
        self.assigned_sense = assigned_sense
        self.contributing_languages = contributing_languages
        assert assignment_type in MsiAnnotation.possible_assignment_types
        self.assignment_type = assignment_type
        self.comments = comments

    def to_string(self):
        return json.dumps(self.__dict__, default=serialization.pretty_print)

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'assigned_sense': self.assigned_sense,
                           'contributing_languages': self.contributing_languages,
                           'assignment_type': self.assignment_type,
                           'comments' : self.comments},
                '__args__': []}

    def dumps(self):
        return json.dumps(self, indent=4, default=serialization.encoder)


class AlignmentCollector(object):
    __slots__ = ['documents', 'sentences', 'words', 'concepts']
    def __init__(self, documents={}, sentences={}, words={}, concepts={}):
        self.documents = documents
        self.sentences = sentences
        self.words = words
        self.concepts = concepts

    def add_document_alignment(self, doc_id, alignment):
        """Adds alignment to the proper subcollector. Duplicates (same type, source_id, target_id, origin) are skipped.

        :param alignment:
        :return:
        """
        assert isinstance(alignment, Alignment) and alignment.type == 'document'
        if doc_id in self.documents.keys():
            if alignment.source_id not in self.documents[doc_id]:
                self.documents[doc_id].append(alignment.source_id)
            if alignment.target_id not in self.documents[doc_id]:
                self.documents[doc_id].add(alignment.target_id)
        else:
            self.documents[doc_id] = set([alignment.source_id, alignment.target_id])

    def add(self, alignment):
        """Adds alignment to the proper subcollector. Duplicates (same type, source_id, target_id, origin) are skipped.

        :param alignment:
        :return:
        """
        assert isinstance(alignment, Alignment)
        if alignment.type == 'sentence' and alignment not in self.sentences.get(alignment.source_id, []):
            self.sentences[alignment.source_id] = self.sentences.get(alignment.source_id, []) + [alignment]
        elif alignment.type == 'word'  and alignment not in self.words.get(alignment.source_id, []):
            self.words[alignment.source_id] = self.words.get(alignment.source_id, []) + [alignment]
        elif alignment.type == 'concept'  and alignment not in self.concepts.get(alignment.source_id, []):
            self.concepts[alignment.source_id] = self.concepts.get(alignment.source_id, []) + [alignment]

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'documents': self.documents,
                           'sentences': self.sentences,
                           'words': self.words,
                           'concepts': self.concepts},
                '__args__': []}


class Alignment(object):
    __slots__ = ['type', 'source_id', 'target_id', 'origin']
    def __init__(self, type, source_id, target_id, origin):
        self.type = type
        self.source_id = source_id
        self.target_id = target_id
        self.origin = origin

        @property
        def type(self):
            return self._type

        @type.setter
        def type(self, t):
            if t not in ('document', 'sentence', 'word'):
                raise Exception("Alignment must be type document/sentence/word.")
            self._type = t

        @property
        def origin(self):
            return self._origin

        @type.setter
        def origin(self, t):
            if t not in ('manual', 'automatic'):
                raise Exception("Alignment attribute origin can only be manual/automatic.")
            self._origin = t

    def __eq__(self, other):
        if self.type == other.type and self.source_id == other.source_id and self.target_id == other.target_id and self.origin == other.origin:
            return True
        else:
            return False

    def to_json(self):
        return {'__class__': self.__class__.__name__,
                '__kw__': {'type': self.type,
                           'source_id': self.source_id,
                           'target_id': self.target_id,
                           'origin' : self.origin},
                '__args__': []}


# class DocAlignment(object):
#     __slots__ = ['source_doc_id', 'target_doc_ids', 'sentence_alignments']
#     def __init__(self, source_lang, source_doc_id, target_lang, target_doc_id, sentence_alignments={}):
#         self.source_doc_id = source_lang + '_' + source_doc_id
#         self.target_doc_ids = [target_lang + '_' + target_doc_id]
#         self.sentence_alignments = sentence_alignments
#
#     def add_aligned_document(self, ):
#         self.target_doc_ids
#
#     def add(self, sent_alignment):
#         # has to be loaded in both directions
#         assert isinstance(sent_alignment, SentAlignment)
#         self.sentence_alignments[sent_alignment.source_sent] = sent_alignment
#
#     # def has_alignment(self, source_word, target_lang):
#     #     assert source_word.document == self.source_doc
#     #     assert target_lang == self.target_lang
#     #     if source_word.sentence in self.sentence_alignments and source_word.id in self.sentence_alignments[source_word.sentence]:
#     #         return self.sentence_alignments[source_word.sentence]
#     #     return None
#
#
# class SentAlignment(object):
#     __slots__ = ['source_sent_id', 'target_sent_id', 'word_alignments', 'concept_alignments']
#     def __init__(self, source_sent, target_sent, word_alignments={}, concept_alignments={}):
#         self.source_sent_id = source_sent.document.lang + '_' + source_sent.id
#         self.target_sent_id = target_sent.document.lang + '_' + target_sent.id
#         self.word_alignments = word_alignments
#         self.concept_alignments = concept_alignments
#
#     def add_word_alignment(self, alignment):
#         assert isinstance(alignment, WordAlignment)
#         self.word_alignments[alignment.source_word] = alignment
#
#     def add_concept_alignment(self, alignment):
#         assert isinstance(alignment, ConceptAlignment)
#         self.concept_alignments[alignment.source_word] = alignment

# class WordAlignment(object):
#     __slots__ = ['source_word', 'target_word']
#     def __init__(self, source_word, target_word):
#         self.source_word = source_word
#         self.target_word = target_word
#
class ConceptAlignment(object):
    __slots__ = ['source_word', 'target_word']
    def __init__(self, source_word, target_word):
        self.source_word = source_word
        self.target_word = target_word

if __name__ == '__main__':
    doc = Document(id='ciao', lang='eng')
    sent = Sentence(id='a', document=doc.id)
    doc.add(sent)
    print(sent.dumps())
    print(doc.dumps())
    corpus = Corpus(id='c1', title='title', lang='eng')
    corpus.add(doc)
    print(corpus.dumps())
    word = Word(document=doc.id, id='a_1_5', surface_form='a', lemma='', sentence=sent.id)
    sent.add(word)
    word = Word(document=doc.id, id='a_1_3', surface_form='a', lemma='', sentence=sent.id)
    sent.add(word)
    msi = MsiAnnotation(assigned_sense='00000000-n', contributing_languages=4, assignment_type='disambiguated_by_msi')
    word = Word(document=doc.id, id='a_12_3', surface_form='a', lemma='', sentence=sent.id, msi_annotation=msi)
    sent.add(word)

    corpus2 = Corpus(id='c2', title='title', lang='ita')
    lr = MultilingualCorpus(id='semcor', title='MPC', languages=[])
    lr.add(corpus, corpus2)
    print(len(lr))

    ac = AlignmentCollector()
    lr.set_alignment_collector(ac)
    alignment = Alignment(type='document', source_id='eng_da01', target_id='ita_da01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='document', source_id='eng_da01', target_id='rom_da01', origin='manual')
    ac.add(alignment)
    alignment2 = Alignment(type='document', source_id='eng_da01', target_id='rom_da01', origin='manual')

    ac.add(alignment)

    alignment = Alignment(type='document', source_id='eng_da01', target_id='jpn_da01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='document', source_id='ita_da01', target_id='rom_da01', origin='manual')
    ac.add(alignment)

    alignment = Alignment(type='sentence', source_id='eng_sa01', target_id='ita_sa01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='sentence', source_id='eng_sa01', target_id='rom_sa01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='sentence', source_id='eng_sa01', target_id='jpn_sa01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='sentence', source_id='ita_sa01', target_id='rom_sa01', origin='manual')
    ac.add(alignment)

    alignment = Alignment(type='word', source_id='eng_w01', target_id='ita_w01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='word', source_id='eng_w01', target_id='rom_w01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='word', source_id='eng_w01', target_id='jpn_w01', origin='manual')
    ac.add(alignment)
    alignment = Alignment(type='word', source_id='eng_w01', target_id='jpn_w01', origin='manual')
    ac.add(alignment) # this doesn't get added (correctly)

    print(corpus.dumps())

    print(word)
    print(doc)
    print(corpus)
    print(lr.dumps())
