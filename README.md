# Semantic Extractor
Used to extract the meaning of a corpus of Natural Language text. Read the wiki for more information.

# Files
This is **not** yet a python package, so do not try to install it.
## root
The files that are directly in the directory include,
### CorpusBuilder.py
Used to create a large random corpora from nltk's brown corpus in _nltk.corpus.brown_ for testing.
### ExtractorClasses.py
Defines all the classes (e.g. class `Entity`, class `Pointer` ...) to contain the different elements
### NLPExtension.py
Extends nltk by wrapping some of its functions that are used regularly.
### SemanticExtraction.py
**DEPRECATED**
Extracts Entities and their Relationships
### SemanticTest.py
**DEPRECATED**
Tests the extract function in SemanticExtraction.py for multiple times and outputs a testlog in the form of a plain text file
### utils.py
Some basic utilities that extend both python native data structures and the structures in SemanticExtraction.py
### nouns
A _pickled_ file containing a list of English nouns. Pickled to save time, and generated with a generator file, "GenerateNouns.py"
### stanfordPOSTagger
**DEPRECATED**
Another _pickled_ file containing the Stanford POS tagger. Originally conceived as a work around to making every user download the Stanford POS tagger library and add it to CLASSPATH, deprecated after finding that this approach does not work.
### wordtags
Similar to nouns and is a _pickled_ file, contains a dictionary of English words with their POS tags. Only used by is_gerund.
***
If you have security concerns about pickled files, then generate them using the files in generators. Which generates which should be self-evident from the name
