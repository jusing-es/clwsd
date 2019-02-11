# clwsd
# Cross Lingual Word Sense Disambiguation with WordNets

Implementation of Multilingual Sense Intersection (MSI), as described in Bond and Bonansinga (2015) and Bonansinga and Bond (2016).

## Installing

Required modules are listed in ```requirements.txt```. 

To get started, (optionally) activate a brand new Python 3.6+ virtual environment and install with ```pip```:

```
pip install < requirements.txt
```
## Getting Started

### Launch MSI yourself


* ```json_file_reader.py```: contains the JSON reader 
* ```corpus.py```: contains the classes used by the other scripts
* ```msi.py```: performs MSI

MSI has been performed on the Multilingual Parallel Corpus (MPC).
To carry out it yourself, clone the project, install the dependencies and run:

```
cd clwsd/code/
python msi.py -i ../files/json_files -l eng_ita_jpn_ron -f -e -d
```

The above command:
 - performs MSI on MPC (serialized in the json files contained in ```files/json_files```);
 - works with English, Italian, Japanese and Romanian;
 - sense frequencies are enabled;
 - evaluation is performed and printed to the standard output;
 - the result of MSI annotation is dumped to an XML file.

Parameters:

* ```-i, --json_input_folder```: accepts as input a folder structured as in ```files/json_files``` 
* ```-x, --xml_input_file```: accepts a compliant XML as input
* ```-l --languages```: lists the languages involved. Indicate valid ISO-639-2 language codes separated by _. Input corpora must be in languages having a wordnet in the Open Multilingual Wordnet.
* ```-f, --sense_frequencies```: enables sense frequencies
* ```-e, --evaluate```: outputs evaluation results (verbose)
* ```-d, --dump_xml_corpus```: produce the XML output corpus

### Or follow the demo in the Python notebook:

* run 
```pip install jupyter``` and then type
```jupyter notebook```

* this will make Jupyter available in localhost: go to  ```http://localhost:8888``` and open the notebook ```MSI_demo.ipynb```

* just read and enjoy... or run each step yourself!

## Todo List

- [x] Monolingual corpus template, compliant to NTUMC.dtd
- [x] Multilingual corpus template, compliant to NTUMC.dtd
- [x] Loaded sample multilingual corpus based on MPC (content words only)
- [x] MSI evaluation
- [x] include support for external sense frequencies
- [x] include automatic alignments for each language pair
- [x] JSON and XML reader for MSI
- [x] Tutorial through a Python notebook: ```code/MSI_demo.ipynb```

## Related projects


* [NTUMC](https://github.com/lmorgadodacosta/NTUMC) - 
NTUMC Multilingual Corpus, including XML and SQLITE schemas and conversion tools


## Publications

* **Giulia Bonansinga and Francis Bond** (2016) *Multilingual Sense Intersection in a Parallel Corpus with Diverse Language Families.* 
In Proceedings of the Eighth Global WordNet Conference, Bucharest. pp 44–49. [PDF](http://gwc2016.racai.ro/proceedings.html)
* **Francis Bond and Giulia Bonansinga** (2015) *Exploring Cross-Lingual Sense Mapping in a Multilingual Parallel Corpus.* 
In Second Italian Computational Linguistics Conference, Trento. [PDF](http://compling.hss.ntu.edu.sg/pdf/2015-clic-exploring-xling.pdf)
* **Giulia Bonansinga** (2019) *Cross-lingual Word Sense Annotation with Multilingual WordNets*. Unpublished Master's Thesis in Digital Humanities, University of Pisa.


See also the list of [contributors](https://github.com/jusing-es/clwsd/graphs/contributors) who participated in this project.

## License

You may use, copy, modify and distribute this code for any purpose without any fee, so long as you keep it under the same license. See the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you to Francis Bond, Luis Morgado da Costa, Tuan Anh Le and Tommaso Petrolito for their help and suggestions.
