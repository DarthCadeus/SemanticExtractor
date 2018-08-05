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
from termcolor import colored

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")

def extract_1(tagged_corpus):
    global TIER
    TIER = 2.1
    # from now on, these will be using a more concise method
    sentence = {
        "sbj_toi": False,
        "sbj_dt": None,
        "sbj_att": [],
        "sbj_adt": [],
        "sbj": None,
        "sbj_tpa": [],
        "pdt": None,
        "obj_toi": False,
        "obj_cmp": False, # is complement?
        "obj_dt": None,
        "obj_att": [],
        "obj_adt": [],
        "obj": None,
        "obj_tpa": []
    }
    for word in tagged_corpus:
        if word[0].lower() == "to":
            if sentence["sbj"] and sentence["pdt"] and not sentence["obj"]:
                sentence["obj_toi"] = True
            elif not sentence["sbj"]:
                sentence["sbj_toi"] = True
        if word[1] == "DT":
            if sentence["pdt"] and not sentence["obj_toi"]:
                sentence["obj_dt"] = word
            elif not sentence["sbj_toi"]:
                sentence["sbj_dt"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "r":
            if sentence["pdt"]:
                if not sentence["obj_toi"]:
                    if sentence["obj_att"]:
                        closest = sentence["obj_att"][len(obj_att)-1]
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
                        closest = sentence["sbj_att"][len(sbj_att)-1]
                        if closest[1] is None:
                            closest[0].append(word)
                        else:
                            sentence["sbj_att"].append([[word], None])
                    else:
                        sentence["sbj_att"].append([[word], None])
                else:
                    if sentence["sbj"]:
                        sentence["sbj_tpa"].append(word)
        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
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
            # if sentence["obj_cmp"] is not False, which is its default value
            # then the predicate has to have been found already
            # making checking for sentence["pdt"] unnecessary.
            sentence["obj"] = word  # this could work ...
            res = utils.deep_in(sentence["obj_att"], word)
            if res:
                sentence["obj_att"].remove(res)
        if NLP.Converter.penn_to_wn(word[1]) == "n" or \
                word[1] == "PRP" or word[0].lower() == "it" or \
                word[1] == "VBG" or \
                NLP.Determiner.is_gerund(word[0]):
            # subjects have to appear before objects
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
                elif not sentence["sbj_toi"]:
                    sentence["sbj"] = word
        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word  # the all important line
                # this is what tier 2.1 is all about
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word
    return sentence  # much more concise!


def extract_2(tagged_corpus):
    global TIER
    TIER = 2.2
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
        "disagree": False
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

        if NLP.Converter.penn_to_wn(word[1]) == "a" or word[1] == "PRP$":
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
                elif not sentence["sbj_toi"]:
                    sentence["sbj"] = word

        if NLP.Converter.penn_to_wn(word[1]) == "v" and \
                word[1] != "VBG":
            if sentence["sbj_toi"] and not sentence["sbj"]:
                sentence["sbj"] = word
            elif not sentence["pdt"]:
                sentence["pdt"] = word
                if not sentence["sbj"]:
                    return {
                        "sbj": None,
                        "pdt": None
                    }  # so that the error will be noted and passed over
                # will first do some basic determination based on plurality tags
                if sentence["sbj"][1] in ["NNS", "NNPS"] and word[1] == "VBZ":
                    sentence["disagree"] = True
                if word[0].lower() in ["am", "is", "are", "was", "were", "be", "been"]:
                    sentence["obj_cmp"] = True
            elif sentence["obj_toi"] and not sentence["obj"]:
                sentence["obj"] = word
    return sentence

def process_2_1(sentence, tagged_corpus):
    # adding another part for the first time
    # if possible, integrate this into the main loop
    if sentence["pdt"] is None:  # try to re-cast this
        possibles = []


        for word_index in range(len(tagged_corpus)):
            word = tagged_corpus[word_index]
            if word[1] == "NNS":
                word_processed = (NLP.inflect.singular_noun(word[0]), "NN")
                obj = EC.Container(word=word, word_processed=word_processed, trd_p=True, index=word_index)
            else:
                word_processed = word
                obj = EC.Container(word=word, word_processed=word_processed, index=word_index)

            if word_processed[0] in NLP.wordtags and NLP.wordtags[word_processed[0]].index("VERB") < 3:
                possibles.append(obj)


        for possibility in possibles:
            tagged_alternative = copy.deepcopy(tagged_corpus)
            tag = "VB"
            if hasattr(possibility, "trd_p"):
                tag = "VBZ"
            tagged_alternative[possibility.index] = (possibility.word[0], tag)
            if possibility.index == 0:
                continue
            elif not utils.deep_in(tagged_alternative[:possibility.index], "n", key=NLP.Converter.penn_to_wn):
                print(tagged_alternative)
                continue
            new_sentence = extract_2(tagged_alternative)
            if utils.verify(new_sentence):
                yield new_sentence


corpora = [
"This command updates the index",
"The \"index\" holds a snapshot of the content of the working tree"
]
start_time = time.time()
tagger = NLP.Basic(st)
tagged_group = [tagger.tag(x) for x in corpora]

if __name__ == '__main__':
    print(f"Tagging complete in {time.time()-start_time}")
    for tagged_index in range(len(tagged_group)):
        tagged = tagged_group[tagged_index]
        plt.figure(tagged_index+1)
        print("TAGGED:", tagged)
        extracted = extract_2(tagged)
        if not utils.verify(extracted):
            print(colored("CHECKING ALTS", "red"))
            all_extracted = list(process_2_1(extracted, tagged))
            for i in all_extracted:
                print(colored(i, "green"))
                graph = to_graph.to_graph(i, TIER, True)
        else:
            print(extracted)
            graph = to_graph.to_graph(extracted, TIER, True)  # display is integrated
        print("==========")
    print(f"TIME: {time.time() - start_time} for a count of {len(corpora)}")
    plt.show()
    # plt.savefig(f"tier {TIER if TIER != 0 else 'UNDEFINED'}.png")
