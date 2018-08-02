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
import time

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")


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
                        obj_adt.append(obj)
                        obj = word
                    else:
                        obj = word
            else:
                if pdt:
                    obj = word
                else:
                    obj = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            pdt = word  # the all important line
    return sbj_dt, sbj_att, sbj_adt, sbj, pdt, obj_dt, obj_att, obj_adt, obj


# Tier 1.4
def extract_4(tagged_corpus):
    global TIER
    TIER = 1.4
    sbj_toi = False
    sbj_dt = None
    sbj_att = []
    sbj_adt = []
    sbj = None
    pdt = None
    obj_toi = False
    obj_dt = None
    obj_att = []
    obj_adt = []
    obj = None
    for word in tagged_corpus:
        if word[0].lower() == "to":
            print(sbj, pdt, obj)
            if sbj and pdt and not obj:
                obj_toi = True
            elif not sbj:
                sbj_toi = True
        if word[1] == "DT":
            if pdt and not obj_toi:
                obj_dt = word
            elif not sbj_toi:
                sbj_dt = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if pdt and not obj_toi:
                if obj_att:
                    closest = obj_att[len(obj_att)-1]
                    if closest[1] is None:
                        closest[0].append(word)
                    else:
                        obj_att.append([[word], None])
                else:
                    obj_att.append([[word], None])
            elif not sbj_toi:
                if sbj_att:
                    closest = sbj_att[len(sbj_att)-1]
                    if closest[1] is None:
                        closest[0].append(word)
                    else:
                        sbj_att.append([[word], None])
                else:
                    sbj_att.append([[word], None])
        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
            if pdt and not obj_toi:
                if obj_att:
                    closest = obj_att[len(obj_att)-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        obj_att.append([[], word])
                else:
                    obj_att.append([[], word])
            elif not sbj_toi:
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
                if not pdt and not sbj_toi:
                    if sbj:
                        sbj_adt.append(sbj)
                        sbj = word
                    else:
                        sbj = word
                elif not obj_toi:
                    if obj:
                        obj_adt.append(obj)
                        obj = word
                    else:
                        obj = word
            else:
                if pdt and not obj_toi:
                    obj = word
                elif not sbj_toi:
                    sbj = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sbj_toi and not sbj:
                sbj = word
            elif not pdt:
                pdt = word  # the all important line
            elif obj_toi and not obj:
                obj = word
    return sbj_dt, sbj_att, sbj_adt, sbj, pdt, obj_dt, obj_att, obj_adt, obj, \
            sbj_toi, obj_toi


# Tier 1.5
def extract_5(tagged_corpus):
    global TIER
    TIER = 1.5
    sbj_toi = False
    sbj_dt = None
    sbj_att = []
    sbj_adt = []
    sbj = None
    sbj_tpa = []  # to-infinitive post adverbs
    pdt = None
    obj_toi = False
    obj_dt = None
    obj_att = []
    obj_adt = []
    obj = None
    obj_tpa = []
    for word in tagged_corpus:
        if word[0].lower() == "to":
            print(sbj, pdt, obj)
            if sbj and pdt and not obj:
                obj_toi = True
            elif not sbj:
                sbj_toi = True
        if word[1] == "DT":
            if pdt and not obj_toi:
                obj_dt = word
            elif not sbj_toi:
                sbj_dt = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if pdt:
                if not obj_toi:
                    if obj_att:
                        closest = obj_att[len(obj_att)-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            obj_att.append([[word], None])
                    else:
                        obj_att.append([[word], None])
                else:
                    if obj:
                        obj_tpa.append(word)
            else:
                if not sbj_toi:
                    if sbj_att:
                        closest = sbj_att[len(sbj_att)-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sbj_att.append([[word], None])
                    else:
                        sbj_att.append([[word], None])
                else:
                    if sbj:
                        sbj_tpa.append(word)
        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
            if pdt and not obj_toi:
                if obj_att:
                    closest = obj_att[len(obj_att)-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        obj_att.append([[], word])
                else:
                    obj_att.append([[], word])
            elif not sbj_toi:
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
                if not pdt and not sbj_toi:
                    if sbj:
                        sbj_adt.append(sbj)
                        sbj = word
                    else:
                        sbj = word
                elif not obj_toi:
                    if obj:
                        obj_adt.append(obj)
                        obj = word
                    else:
                        obj = word
            else:
                if pdt and not obj_toi:
                    obj = word
                elif not sbj_toi:
                    sbj = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sbj_toi and not sbj:
                sbj = word
            elif not pdt:
                pdt = word  # the all important line
            elif obj_toi and not obj:
                obj = word
    return sbj_dt, sbj_att, sbj_adt, sbj, sbj_tpa, pdt, obj_dt, obj_att, obj_adt, obj, \
            obj_tpa, sbj_toi, obj_toi


corpus = "She sent him a gift"
tagged = NLP.Basic(st).tag(corpus)

if __name__ == '__main__':
    print("TAGGED:", tagged)
    start_time = time.time()
    extracted = extract_5(tagged)
    print(extracted)
    graph = to_graph.to_graph(extracted, TIER, True)
    print(graph.number_of_nodes())
    nx.draw(graph, with_labels=True, node_size=600)
    # plt.savefig(f"tier {TIER if TIER != 0 else 'UNDEFINED'}.png")
    print(f"TIME: {time.time() - start_time}")
