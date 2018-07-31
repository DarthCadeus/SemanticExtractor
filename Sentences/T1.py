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


corpus = "His constant hammering was annoying"
tagged = NLP.Basic(st).tag(corpus)


# Tier 1.1
def extract_1(tagged_corpus):
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


# Tier 1.2
def extract_2(tagged_corpus):
    sbj_dt = None
    sbj_att = []
    sbj = None
    pdt = None
    obj = None
    obj_dt = None
    obj_att = []
    for word in tagged_corpus:
        if word[1] == "DT":
            if sbj:
                obj_dt = word
            else:
                sbj_dt = word
        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
            if sbj:
                obj_att.append(word)
            else:
                sbj_att.append(word)
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
    return sbj_dt, sbj_att, sbj, pdt, obj_dt, obj_att, obj



if __name__ == '__main__':
    print("TAGGED:", tagged)
    print(extract_2(tagged))
