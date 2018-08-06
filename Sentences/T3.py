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

corpora = [
    "This command updates the index",
    "The index is updated by this command"
]
start_time = time.time()

# tagger = NLP.Basic(nltk.pos_tag_sents)
# tagged_group = [tagger.tag(x) for x in corpora]
# print(tagger.)
tokenized_corpora = [NLP.Basic.tokenize(x) for x in corpora]
tagged_group = nltk.pos_tag_sents(tokenized_corpora)

if __name__ == '__main__':
    print(f"Tagging complete in {time.time()-start_time}")
    for tagged_index in range(len(tagged_group)):
        tagged = tagged_group[tagged_index]
        plt.figure(tagged_index+1)
        print("TAGGED:", tagged)
        extracted = extract_3(tagged)
        print(extracted)
        if not utils.verify(extracted):
            print(colored("CHECKING ALTS", "red"))
            all_extracted = list(process_2_1(extracted, tagged))
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
