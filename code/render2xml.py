from jinja2 import Environment, FileSystemLoader
import pathlib


def render_monolingual_corpus(corpus):
    path = pathlib.Path(__file__).parents[1]
    env = Environment(loader=FileSystemLoader(str(path / 'templates')))
    template = env.get_template('corpus.xml')
    for key, doc in corpus.documents.items():
        for sid, sent in doc.sentences.items():
            print(key, sid, len(doc[sid]))
    data = template.render({'corpus': corpus})

    data = """<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Corpus SYSTEM "../../NTUMC/ntumc.dtd">\n""" \
           + data

    return data

def render_multilingual_corpus(multicorpus):
    path = pathlib.Path(__file__).parents[1]
    env = Environment(loader=FileSystemLoader(str(path / 'templates')))
    template = env.get_template('multilingual_corpus.xml')
    # for key, doc in corpus.documents.items():
    #     for sid, sent in doc.sentences.items():
    #         print(key, sid, len(doc[sid]))
    data = template.render({'multicorpus': multicorpus})

    data = """<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Corpus SYSTEM "../../NTUMC/ntumc.dtd">\n""" \
           + data

    return data
