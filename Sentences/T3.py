TIER = 0
DEBUG = True
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
import copy
import nltk
from termcolor import colored
from T2 import process_2_1

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")


def extract_1(tagged_corpus):
    global TIER
    TIER = 3.1
    sentence = {
        "sbj_toi": False,
        "sbj_dt": None,
        "sbj_att": [],
        "sbj_adt": [],
        "sbj": None,
        "sbj_tpa": [],
        "pdt": None,
        "obj_toi": False,
        "obj_cmp": False,
        "obj_dt": None,
        "obj_att": [],
        "obj_adt": [],
        "obj": None,
        "obj_tpa": [],
        "pss_vce": False,  # passive voice
        "svb_dis": False,  # subject-verb disagreement
        "spn_dis": False,  # subject pronoun nominative disagreement
        "opn_dis": False,
        "err": False
    }
    for word in tagged_corpus:
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[0].lower() in ["a", "the"]:
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_adt"] or sentence["obj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                if sentence["sbj_adt"] or sentence["sbj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["obj_att"].append([[word], None])
                    else:
                        sentence["obj_att"].append([[word], None])
                else:
                    if sentence["obj"]:
                        sentence["obj_tpa"].append(word)
            else:
                if not sentence["sbj_toi"]:
                    if sentence["sbj_att"]:
                        closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["sbj_att"].append([[word], None])
                    else:
                        sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$" or word[1] == "CD":
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_att"]:
                    closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["obj_att"].append([[], word])
                else:
                    sentence["obj_att"].append([[], word])
            elif not sentence["sbj_toi"]:
                if sentence["sbj_att"]:
                    closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["sbj_att"].append([[], word])
                else:
                    sentence["sbj_att"].append([[], word])

        if sentence["obj_cmp"] and NLP.Converter.penn_to_wn(word[1]) == "a":
            sentence["obj"] = word
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)

        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not sentence["pdt"] and not sentence["sbj_toi"]:
                    if sentence["sbj"]:
                        sentence["sbj_adt"].append(sentence["sbj"])
                        sentence["sbj"] = word
                    else:
                        sentence["sbj"] = word
                elif not sentence["obj_toi"]:
                    if sentence["obj"]:
                        if not sentence["obj_cmp"]:
                            sentence["obj_adt"].append(sentence["obj"])
                        sentence["obj"] = word
                    else:
                        sentence["obj"] = word
            else:
                if sentence["pdt"] and not sentence["obj_toi"]:
                    sentence["obj"] = word
                    if word[1] == "PRP" and word[0].lower() in ["he", "she", "they"]:
                        sentence["opn_dis"] = True
                        sentence["err"] = True
                elif not sentence["sbj_toi"]:
                    if word[1] == "PRP" and word[0].lower() in ["him", "her", "them"]:
                        sentence["spn_dis"] = True
                        sentence["err"] = True
                    sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["obj_cmp"] and word[1] == "VBN":
                sentence["obj_cmp"] = False
                sentence["pss_vce"] = True
                sentence["pdt"] = word
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word
    return sentence


def extract_2(tagged_corpus):
    global TIER
    TIER = 3.2
    sentence = {
        "sbj_toi": False,
        "sbj_dt": None,
        "sbj_att": [],
        "sbj_adt": [],
        "sbj": None,
        "sbj_tpa": [],
        "pdt": None,
        "pdt_ptc": [],  # predicate particles
        "obj_toi": False,
        "obj_cmp": False,
        "obj_dt": None,
        "obj_att": [],
        "obj_adt": [],
        "obj": None,
        "obj_tpa": [],
        "pss_vce": False,  # passive voice
        "svb_dis": False,  # subject-verb disagreement
        "spn_dis": False,  # subject pronoun nominative disagreement
        "opn_dis": False,
        "err": False
    }
    for word in tagged_corpus:
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[0].lower() in ["a", "the"]:
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_adt"] or sentence["obj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                if sentence["sbj_adt"] or sentence["sbj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["obj_att"].append([[word], None])
                    else:
                        sentence["obj_att"].append([[word], None])
                else:
                    if sentence["obj"]:
                        sentence["obj_tpa"].append(word)
            else:
                if not sentence["sbj_toi"]:
                    if sentence["sbj_att"]:
                        closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["sbj_att"].append([[word], None])
                    else:
                        sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$" or word[1] == "CD":
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_att"]:
                    closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["obj_att"].append([[], word])
                else:
                    sentence["obj_att"].append([[], word])
            elif not sentence["sbj_toi"]:
                if sentence["sbj_att"]:
                    closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["sbj_att"].append([[], word])
                else:
                    sentence["sbj_att"].append([[], word])

        if sentence["obj_cmp"] and NLP.Converter.penn_to_wn(word[1]) == "a":
            sentence["obj"] = word
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)

        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not sentence["pdt"] and not sentence["sbj_toi"]:
                    if sentence["sbj"]:
                        sentence["sbj_adt"].append(sentence["sbj"])
                        sentence["sbj"] = word
                    else:
                        sentence["sbj"] = word
                elif not sentence["obj_toi"]:
                    if sentence["obj"]:
                        if not sentence["obj_cmp"]:
                            sentence["obj_adt"].append(sentence["obj"])
                        sentence["obj"] = word
                    else:
                        sentence["obj"] = word
            else:
                if sentence["pdt"] and not sentence["obj_toi"]:
                    sentence["obj"] = word
                    if word[1] == "PRP" and word[0].lower() in ["he", "she", "they"]:
                        sentence["opn_dis"] = True
                        sentence["err"] = True
                elif not sentence["sbj_toi"]:
                    if word[1] == "PRP" and word[0].lower() in ["him", "her", "them"]:
                        sentence["spn_dis"] = True
                        sentence["err"] = True
                    sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["obj_cmp"] and word[1] == "VBN":
                sentence["obj_cmp"] = False
                sentence["pss_vce"] = True
                sentence["pdt"] = word
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word

        if word[1] == "RP":
            if not sentence["obj_cmp"]:
                sentence["pdt_ptc"].append(word)

    return sentence


def extract_3(tagged_corpus):
    global TIER
    TIER = 3.3
    sentence = EC.SentenceResult()
    mark = False
    for word in tagged_corpus:
        if word[0].lower() == "by":
            mark = True
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[0].lower() in ["a", "the", "an"]:
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_adt"] or sentence["obj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                if sentence["sbj_adt"] or sentence["sbj_att"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_dtr"] and not mark:  # the same thing
                    sentence["pdt_ptc"].append(word)
                elif not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["obj_att"].append([[word], None])
                    else:
                        sentence["obj_att"].append([[word], None])
                else:
                    if sentence["obj"]:
                        sentence["obj_tpa"].append(word)
            else:
                if not sentence["sbj_toi"]:
                    if sentence["sbj_att"]:
                        closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["sbj_att"].append([[word], None])
                    else:
                        sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$" or word[1] == "CD":
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_att"]:
                    closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["obj_att"].append([[], word])
                else:
                    sentence["obj_att"].append([[], word])
            elif not sentence["sbj_toi"]:
                if sentence["sbj_att"]:
                    closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["sbj_att"].append([[], word])
                else:
                    sentence["sbj_att"].append([[], word])

        if sentence["obj_cmp"] and NLP.Converter.penn_to_wn(word[1]) == "a":
            sentence["obj"] = word
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)

        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not sentence["pdt"] and not sentence["sbj_toi"]:
                    if sentence["sbj"]:
                        sentence["sbj_adt"].append(sentence["sbj"])
                        sentence["sbj"] = word
                    else:
                        sentence["sbj"] = word
                elif not sentence["obj_toi"]:
                    if sentence["obj"]:
                        if not sentence["obj_cmp"]:
                            sentence["obj_adt"].append(sentence["obj"])
                        sentence["obj"] = word
                    else:
                        sentence["obj"] = word
            else:
                if sentence["pdt"] and not sentence["obj_toi"]:
                    sentence["obj"] = word
                    if word[1] == "PRP" and word[0].lower() in ["he", "she", "they", "I"]:
                        sentence["opn_dis"] = True
                        sentence["err"] = True
                elif not sentence["sbj_toi"]:
                    if word[1] == "PRP" and word[0].lower() in ["him", "her", "them", "me"]:
                        sentence["spn_dis"] = True
                        sentence["err"] = True
                    sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["obj_cmp"] and word[1] == "VBN":
                sentence["obj_cmp"] = False
                sentence["pss_vce"] = True
                sentence["pdt"] = word
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if (sentence["sbj"][1] in ["NN", "NNP"] or sentence["sbj"][0].lower() in ["he", "she", "it"]) and word[1] == "VB":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word

        if word[1] == "RP":
            if not sentence["obj_cmp"]:
                sentence["pdt_ptc"].append(word)

    # will be more readable to leave this switch outside the main loop
    if sentence["pss_vce"]:
        sentence.swap()
        if not sentence["sbj"]:
            sentence["sbj"] = EC.Pointer("&any")

    return sentence


def extract_4(tagged_corpus):
    global TIER
    TIER = 3.4
    sentence = EC.SentenceResult()
    mark = False
    for word in tagged_corpus:
        if word[0].lower() == "by":
            mark = True
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[0].lower() in ["a", "the", "an"]:
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_adt"] or sentence["obj_att"]:
                    print("determiner too late error")
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                if sentence["sbj_adt"] or sentence["sbj_att"]:
                    print("determiner too late error (subject)")
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_dtr"] and not mark:  # the same thing
                    sentence["pdt_ptc"].append(word)
                elif not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["obj_att"].append([[word], None])
                    else:
                        sentence["obj_att"].append([[word], None])
                else:
                    if sentence["obj"]:
                        sentence["obj_tpa"].append(word)
            else:
                if not sentence["pss_vce"] and sentence["sbj"]:
                    sentence["pdt_ptc"].append(word)
                if not sentence["sbj_toi"]:
                    if not sentence["pdt"]:
                        if sentence["sbj_att"]:
                            closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                            if closest[1] is None:
                                closest[0].append(word)
                            else:
                                sentence["sbj_att"].append([[word], None])
                        else:
                            sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$" or word[1] == "CD":
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_att"]:
                    closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["obj_att"].append([[], word])
                else:
                    sentence["obj_att"].append([[], word])
            elif not sentence["sbj_toi"] and not sentence["pdt"]:
                if sentence["sbj_att"]:
                    closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["sbj_att"].append([[], word])
                else:
                    sentence["sbj_att"].append([[], word])

        if sentence["obj_cmp"] and (NLP.Converter.penn_to_wn(word[1]) == "a" or NLP.Converter.penn_to_wn(word[1]) == "r"):
            sentence["obj"] = word
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)

        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not sentence["pdt"] and not sentence["sbj_toi"]:
                    if sentence["sbj"]:
                        sentence["sbj_adt"].append(sentence["sbj"])
                        sentence["sbj"] = word
                    else:
                        sentence["sbj"] = word
                elif not sentence["obj_toi"]:
                    if sentence["obj"]:
                        if not sentence["obj_cmp"]:
                            sentence["obj_adt"].append(sentence["obj"])
                        sentence["obj"] = word
                    else:
                        sentence["obj"] = word
            else:
                if sentence["pdt"] and not sentence["obj_toi"]:
                    sentence["obj"] = word
                    if word[1] == "PRP" and word[0].lower() in ["he", "she", "they", "I"]:
                        sentence["opn_dis"] = True
                        sentence["err"] = True
                elif not sentence["sbj_toi"]:
                    if word[1] == "PRP" and word[0].lower() in ["him", "her", "them", "me"]:
                        sentence["spn_dis"] = True
                        sentence["err"] = True
                    sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["obj_cmp"] and word[1] == "VBN":
                sentence["obj_cmp"] = False
                sentence["pss_vce"] = True
                sentence["pdt"] = word
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    print("subjectless predicate error")
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if (sentence["sbj"][1] in ["NN", "NNP"] or sentence["sbj"][0].lower() in ["he", "she", "it"]) and word[1] == "VB":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word

        if word[1] == "RP":
            if not sentence["obj_cmp"]:
                sentence["pdt_ptc"].append(word)

    # placing apposition detection outside the main loop will also be clearer and more efficient, and do it before the swap
    if sentence["sbj"][1] == "NNP":  # appositions only apply to proper nouns currently, because most are named entities
        for adt in sentence["sbj_adt"][::-1]:
            if adt[1] == "NNP":
                sentence["sbj_adt"].remove(adt)
                sentence["sbj"] = (adt[0] + " " + sentence["sbj"][0], "NNP")
            else:
                break

    if sentence["obj"]:
        if sentence["obj"][1] == "NNP":  # appositions only apply to proper nouns currently, because most are named entities
            for adt in sentence["obj_adt"][::-1]:
                if adt[1] == "NNP":
                    sentence["obj_adt"].remove(adt)
                    sentence["obj"] = (adt[0] + " " + sentence["obj"][0], "NNP")
                else:
                    break

    # remove those adjective phrases in attributes that have no body, just adverbs
    for char in sentence["sbj_att"]:
        if char[1] is None:
            sentence["sbj_att"].remove(char)
    for char in sentence["obj_att"]:
        if char[1] is None:
            sentence["obj_att"].remove(char)

    # will be more readable to leave this switch outside the main loop
    if sentence["pss_vce"]:
        sentence.swap()
        if not sentence["sbj"]:
            sentence["sbj"] = EC.Pointer("&any")


    return sentence


def harness_5(tagged_corpus, untagged):
    global TIER
    if tagged_corpus[::-1][0][0] == "!":  # take out the first item of the last item in the corpus
        print("Imperative")
        comparison = extract_4(tagged_corpus)
        if type(comparison) == EC.SentenceResult:
            if comparison():  # this is okay because my __call__ method is set to verify self
                print("not Imperative after all")
                return comparison
        # It is now definitely imperative
        # to make it complete, insert the subject "You"
        # currently this cannot handle cases with let, of course
        untagged.insert(0, "You")
        tagged_corpus = nltk.pos_tag(untagged)
        extracted = extract_4(tagged_corpus)
        TIER = 3.5 if 3.5 > TIER else TIER
        return extracted
    extracted = extract_4(tagged_corpus)
    TIER = 3.5 if 3.5 > TIER else TIER  # make sure the correct Tier is registered
    return extracted


def harness_6(tagged_corpus, untagged, force=False):
    global TIER
    if tagged_corpus[::-1][0][0] == "!" or force:  # take out the first item of the last item in the corpus
        if not force:
            comparison = extract_7(tagged_corpus)
            if type(comparison) == EC.SentenceResult:
                if comparison():  # this is okay because my __call__ method is set to verify self
                    return comparison
        # It is now definitely imperative
        # to make it complete, insert the subject "You"
        # currently this cannot handle cases with let, of course
        if tagged_corpus[0][0].lower() in ["let"]:
            untagged.pop(0)
            if tagged_corpus[1][0].lower() == "'s":
                untagged.insert(0, "We")
            non_std = True
        else:
            untagged.insert(0, "You")
        tagged_corpus = nltk.pos_tag(untagged)
        extracted = extract_7(tagged_corpus, True)
        if type(extracted) == dict:
            return extracted
        else:
            extracted.imp = True
        TIER = 3.6 if 3.6 > TIER else TIER
        return extracted
    extracted = extract_7(tagged_corpus)
    TIER = 3.6 if 3.6 > TIER else TIER # make sure the correct Tier is registered
    return extracted


def extract_7(tagged_corpus, special=False):
    global TIER
    TIER = 3.7
    sentence = EC.SentenceResult()
    mark = False
    for word in tagged_corpus:
        if word[0].lower() == "by":
            mark = True
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[0].lower() in ["a", "the", "an"]:
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_adt"] or sentence["obj_att"]:
                    print("determiner too late error")
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                if sentence["sbj_adt"] or sentence["sbj_att"]:
                    print("determiner too late error (subject)")
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_dtr"] and not mark and not sentence["obj_adt"] and not sentence["obj_att"] and not sentence["obj"]:  # the same thing
                    sentence["pdt_ptc"].append(word)
                elif not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["obj_att"].append([[word], None])
                    else:
                        sentence["obj_att"].append([[word], None])
                else:
                    if sentence["obj"]:
                        sentence["obj_tpa"].append(word)
            else:
                if not sentence["pss_vce"] and sentence["sbj"]:
                    sentence["pdt_ptc"].append(word)
                if not sentence["sbj_toi"]:
                    if not sentence["pdt"]:
                        if sentence["sbj_att"]:
                            closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                            if closest[1] is None:
                                closest[0].append(word)
                            else:
                                sentence["sbj_att"].append([[word], None])
                        else:
                            sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$" or word[1] == "CD":
            if sentence["pdt"] and not sentence["obj_toi"]:
                if sentence["obj_att"]:
                    closest = sentence["obj_att"][len(sentence["obj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["obj_att"].append([[], word])
                else:
                    sentence["obj_att"].append([[], word])
            elif not sentence["sbj_toi"] and not sentence["pdt"]:
                if sentence["sbj_att"]:
                    closest = sentence["sbj_att"][len(sentence["sbj_att"])-1]
                    if closest[1] is None:
                        closest[1] = word
                    else:
                        sentence["sbj_att"].append([[], word])
                else:
                    sentence["sbj_att"].append([[], word])

        if sentence["obj_cmp"] and (NLP.Converter.penn_to_wn(word[1]) == "a" or NLP.Converter.penn_to_wn(word[1]) == "r"):
            sentence["obj"] = word
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)

        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            if NLP.Converter.penn_to_wn(word[1]) == "n":
                if not sentence["pdt"] and not sentence["sbj_toi"]:
                    if sentence["sbj"]:
                        sentence["sbj_adt"].append(sentence["sbj"])
                        sentence["sbj"] = word
                    else:
                        sentence["sbj"] = word
                elif not sentence["obj_toi"]:
                    if sentence["obj"]:
                        if not sentence["obj_cmp"]:
                            sentence["obj_adt"].append(sentence["obj"])
                        sentence["obj"] = word
                    else:
                        sentence["obj"] = word
            else:
                if sentence["pdt"] and not sentence["obj_toi"]:
                    sentence["obj"] = word
                    if word[1] == "PRP" and word[0].lower() in ["he", "she", "they", "I"]:
                        sentence["opn_dis"] = True
                        sentence["err"] = True
                elif not sentence["sbj_toi"]:
                    if word[1] == "PRP" and word[0].lower() in ["him", "her", "them", "me"]:
                        if not special:
                            sentence["spn_dis"] = True
                            sentence["err"] = True
                        else:
                            sentence["sbj"] = (NLP.Converter.to_sbj(word[0]), word[1])
                    else:
                        sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["obj_cmp"] and word[1] == "VBN":
                sentence["obj_cmp"] = False
                sentence["pss_vce"] = True
                sentence["pdt"] = word
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    print("subjectless predicate error")
                    print("tgd", tagged_corpus)
                    print("stc", sentence)
                    return {
                        "sbj": None,
                        "pdt": None
                    }
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if (sentence["sbj"][1] in ["NN", "NNP"] or sentence["sbj"][0].lower() in ["he", "she", "it"]) and word[1] == "VB":
                    sentence["svb_dis"] = True
                    sentence["err"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word

        if word[1] == "RP":
            if not sentence["obj_cmp"]:
                sentence["pdt_ptc"].append(word)

    # placing apposition detection outside the main loop will also be clearer and more efficient, and do it before the swap
    if sentence["sbj"][1] == "NNP":  # appositions only apply to proper nouns currently, because most are named entities
        for adt in sentence["sbj_adt"][::-1]:
            if adt[1] == "NNP":
                sentence["sbj_adt"].remove(adt)
                sentence["sbj"] = (adt[0] + " " + sentence["sbj"][0], "NNP")
            else:
                break

    if sentence["obj"]:
        if sentence["obj"][1] == "NNP":  # appositions only apply to proper nouns currently, because most are named entities
            for adt in sentence["obj_adt"][::-1]:
                if adt[1] == "NNP":
                    sentence["obj_adt"].remove(adt)
                    sentence["obj"] = (adt[0] + " " + sentence["obj"][0], "NNP")
                else:
                    break

    # remove those adjective phrases in attributes that have no body, just adverbs
    for char in sentence["sbj_att"]:
        if char[1] is None:
            sentence["sbj_att"].remove(char)
    for char in sentence["obj_att"]:
        if char[1] is None:
            sentence["obj_att"].remove(char)

    # will be more readable to leave this switch outside the main loop
    if sentence["pss_vce"]:
        sentence.swap()
        if not sentence["sbj"]:
            sentence["sbj"] = EC.Pointer("&any")


    return sentence


corpora = [
    "Open my recent files!"
]
start_time = time.time()

tokenized_corpora = [NLP.Basic.tokenize(x) for x in corpora]
tagged_group = nltk.pos_tag_sents(tokenized_corpora)

if __name__ == '__main__':
    function = harness_6
    processor = process_2_1
    print(f"Tagging complete in {time.time()-start_time}")
    for tagged_index in range(len(tagged_group)):
        tagged = tagged_group[tagged_index]
        plt.figure(tagged_index+1)
        print("TAGGED:", tagged)
        extracted = function(tagged, tokenized_corpora[tagged_index])
        print(extracted)
        if not utils.verify(extracted):
            print(colored("CHECKING ALTS", "red"))
            alt_extraction = function(tagged, tokenized_corpora[tagged_index], force=True)
            all_extracted = list(processor(extracted, tagged))
            for i in all_extracted:
                print(colored(i, "green"))
                graph = to_graph.to_graph(i, TIER, True)
        else:
            graph = to_graph.to_graph(extracted, TIER, True)  # display is integrated
            pass
        print("==========")
    print(f"TIME: {time.time() - start_time} for a count of {len(corpora)}")
    plt.show()
    # plt.savefig(f"tier {TIER if TIER != 0 else 'UNDEFINED'}.png")
