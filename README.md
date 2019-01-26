# clwsd
# Cross Lingual Word Sense Disambiguation with WordNets

Implementation of Multilingual Sense Intersection (MSI), as described in Bond and Bonansinga (2015) and Bonansinga and Bond (2016).
## Getting Started

More information will come.

* ```core.py```: contains the JSON reader and XML reader 
* ```corpus.py```: contains the classes used by the other scripts
* ```msi.py```: performs MSI

### Installing

Required modules are listed in ```requirements.txt```. 

To get started, (optionally) activate a brand new Python 3.6+ virtual environment and install with ```pip```:

```
pip install < requirements.txt
```

## Todo List

- [x] Write module to dump ```Corpus```/```MultilingualCorpus``` object to XML 
- [x] Monolingual corpus template, compliant to NTUMC.dtd
- [x] Multilingual corpus template, compliant to NTUMC.dtd
- [x] Loaded sample multilingual corpus for document ```a01``` in English and Italian (cfr. ```examples\MPC.xml```)
- [x] basic MSI on EN-IT and evaluation
- [x] include support for external sense frequencies
- [x] include automatic alignments for each language pair
- [x] Load sample corpus with also Romanian and Japanese texts
- [x] Load sample corpus for SemCor document ```a01``` for all languages (```eng ita rom jpn```) with also MSI annotations
- [x] MSI code porting to Python3.7
- [x] Write JSON reader for MSI
- [x] Write XML reader for MSI

## Related projects


* [NTUMC](https://github.com/lmorgadodacosta/NTUMC) - 
NTUMC Multilingual Corpus, including XML and SQLITE schemas and conversion tools


## Publications

* **Giulia Bonansinga and Francis Bond** (2016) *Multilingual Sense Intersection in a Parallel Corpus with Diverse Language Families.* 
In Proceedings of the Eighth Global WordNet Conference, Bucharest. pp 44–49. [PDF](http://gwc2016.racai.ro/proceedings.html)
* **Francis Bond and Giulia Bonansinga** (2015) *Exploring Cross-Lingual Sense Mapping in a Multilingual Parallel Corpus.* 
In Second Italian Computational Linguistics Conference, Trento. [PDF](http://compling.hss.ntu.edu.sg/pdf/2015-clic-exploring-xling.pdf)


See also the list of [contributors](https://github.com/jusing-es/clwsd/graphs/contributors) who participated in this project.

## License

This project is licensed under ... TODO License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you to Francis Bond, Luis Morgado da Costa, Tuan Anh Le and Tommaso Petrolito for their help and suggestions.
