"""
For dealing with Tier 1 sentences
Tier 1 sentences, as in the most basic sentences
consisting only of a subject, predicate, and object
See the wiki! https://github.com/DarthCadeus/SemanticExtractor/wiki/Sentence-Tiers
"""
import sys
sys.path.append("..")
import utils
import NLPExtension as NLP
import ExtractorClasses as EC

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")


corpus = "He eats hamburgers"
tagged = NLP.Basic(st).tag(corpus)


# Tier 1.1
def extract1_1(tagged_corpus):
    sbj = None
    pdt = None
    obj = None
    for word in tagged_corpus:
        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            # subjects have to appear before objects
            if not sbj:
                sbj = word
            else:
                obj = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            pdt = word
    return sbj, pdt, obj


if __name__ == '__main__':
    print("TAGGED:", tagged)
    print(extract1_1(tagged))
