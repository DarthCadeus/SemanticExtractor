"""
For dealing with Tier 1 sentences
Tier 1 sentences, as in the most basic sentences
consisting only of a subject, predicate, and object
See the wiki! https://github.com/DarthCadeus/SemanticExtractor/wiki/Sentence-Tiers
"""
TIER = 0
import sys
sys.path.append("..")
import utils
import NLPExtension as NLP
import ExtractorClasses as EC
import to_graph
import networkx as nx
import matplotlib.pyplot as plt
import copy

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")


corpus = "His constant hammering was annoying"
tagged = NLP.Basic(st).tag(corpus)


# Tier 1.1
def extract_1(tagged_corpus):
    global TIER
    TIER = 1.1
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
    global TIER
    TIER = 1.2
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


# Tier 1.3
def extract_3(tagged_corpus):
    global TIER
    TIER = 1.3
    sbj_dt = None
    sbj_att = []
    sbj_adt = []
    sbj = None
    pdt = None
    obj = None
    obj_dt = None
    obj_att = []
    obj_adt = []
    for word in tagged_corpus:
        if word[1] == "DT":
            if pdt:
                obj_dt = word
            else:
                sbj_dt = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if pdt:
                if obj_att:
                    closest = obj_att[len(obj_att)-1]
                    if closest[1] is None:
                        closest[0].append(word)
                    else:
                        obj_att.append([[word], None])
                else:
                    obj_att.append([[word], None])
            else:
                if sbj_att:
                    closest = sbj_att[len(sbj_att)-1]
                    if closest[1] is None:
                        closest[0].append(word)
                    else:
                        sbj_att.append([[word], None])
                else:
                    sbj_att.append([[word], None])
        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
            if pdt:
                if obj_att:
                    closest = obj_att[len(obj_att)-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        obj_att.append([[], word])
                else:
                    obj_att.append([[], word])
            else:
                if sbj_att:
                    closest = sbj_att[len(sbj_att)-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sbj_att.append([[], word])
                else:
                    sbj_att.append([[], word])
        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            # subjects have to appear before objects
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not pdt:
                    if sbj:
                        sbj_adt.append(sbj)
                        sbj = word
                    else:
                        sbj = word
                else:
                    if obj:
                        sbj_adt.append(obj)
                        obj = word
                    else:
                        obj = word
            else:
                if pdt:
                    obj = word
                else:
                    sbj = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            pdt = word  # the all important line
    return sbj_dt, sbj_att, sbj_adt, sbj, pdt, obj_dt, obj_att, obj_adt, obj

if __name__ == '__main__':
    print("TAGGED:", tagged)
    extracted = extract_3(tagged)
    print(extracted)
    graph = to_graph.to_graph(extracted, TIER, True)
    print(graph.number_of_nodes())
    nx.draw(graph, with_labels=True, node_size=600)
    plt.savefig(f"tier {TIER if TIER != 0 else 'UNDEFINED'}.png")
