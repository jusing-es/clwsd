import json
from render2xml import render_monolingual_corpus, render_multilingual_corpus

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
