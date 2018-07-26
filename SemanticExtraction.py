"""
TODOS: implement the evalby attribute (out of self.attribute)
"""

import time
start_time = time.clock()
import pickle
import NLPExtension as NLP
import ExtractorClasses as EC
import utils
import copy

stp = open("stanfordPOSTagger", "rb")
st = pickle.load(stp)  # the POS tagger
stp.close()


def get_to_inf_actions(tg_corpus):
    for tgi in range(0, len(tg_corpus) - 1):  # skip the last word
        tg = tg_corpus[tgi]
        if tg[0].lower() == "to" and \
                NLP.Converter.penn_to_wn(tg_corpus[tgi + 1][1]) == "v" and \
                NLP.Converter.penn_to_wn(tg_corpus[tgi - 1][1]) != "n":
            yield EC.Action(tg_corpus[tgi+1][0], tgi+1, tag=tg_corpus[tgi+1][1])


def get_pointers(tg_corpus):
    for tgi in range(len(tg_corpus)):
        tg = tg_corpus[tgi]
        if tg[1] == "PRP" or (tg[0] in ["this", "that"] and tg[1] in ["DT"]):
            yield EC.Pointer(tg[0], index=tgi)


def get_nouns_gerunds(tg_corpus):
    for tgi in range(len(tg_corpus)):
        tg = tg_corpus[tgi]
        if tg[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            if NLP.Determiner.is_gerund(tg[0]):
                yield EC.Action(tg[0], index=tgi)
            else:
                yield EC.Entity(tg[0], index=tgi)
        elif tg[1] == "VBG":  # I literally did not include this
            yield EC.Action(tg[0], index=tgi)


def create_entities(tg_corpus):
    ret = list(get_nouns_gerunds(tg_corpus))
    ret.extend(get_pointers(tg_corpus))
    ret.extend(get_to_inf_actions(tg_corpus))
    return ret


def get_front_des(idx, tg_corpus, entity_indices):
    if idx == 0 or idx is None:
        return False
    cur = idx-1
    ret = []
    while cur not in entity_indices and cur >= 0 and \
            (tg_corpus[cur][1] in ['JJ', 'JJR', 'JJS'] or
             tg_corpus[cur][0] in [",", "and"]):
        if tg_corpus[cur][1] in ['JJ', 'JJR', 'JJS']:
            ret.append(EC.Characteristic(tg_corpus[cur][0], cur))
        cur -= 1
    return ret


def get_trailing_des(idx, tg_corpus, entity_indices):
    if idx is None:
        return False
    indicators = ["am", "is", "are", "was", "were", "be", "been", "being",
                  "seem", "seemed", "seems"
                  "appear", "appeared", "appears"
                  "become", "became", "becomes"
                  "get", "got", "gotten", "gets"
                  "look", "looked", "looks",
                  "feel", "felt", "feels"
                  "sound", "sounds", "sounded"
                  "smell", "smells", "smelled", "smelt"  # might get trouble with that
                  ]
    length = len(tg_corpus)
    cur = 0
    while cur < length:
        if tg_corpus[cur][1] not in \
                ['JJ', 'JJR', 'JJS',  # adj
                 'NN', 'NNS', 'NNP', 'NNPS',  # noun
                 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'  # verb
                 ]:  # filter out all noise
            tg_corpus[cur] = None
        cur += 1
    if idx == length-2:
        return False
    cur = idx+1
    ret = []
    while tg_corpus[cur] is None:
        cur += 1
        if cur >= length:
            return []
    if tg_corpus[cur][0] not in indicators:
        return []
    while True:
        if tg_corpus[cur] is None:
            cur += 1
            if cur >= length:
                return []
            continue
        if tg_corpus[cur][0] in indicators:
            cur += 1
            if cur >= length:
                return []
        else:
            break
    while cur not in entity_indices and \
            tg_corpus[cur][1] in ['JJ', 'JJR', 'JJS']:
        ret.append(EC.Characteristic(tg_corpus[cur][0], cur))
        cur += 1
        while tg_corpus[cur] is None:
            cur += 1
        if cur >= length:
            break
    return ret


def get_all_des(ents, ents_idx, tg_corpus):
    for ent in ents:
        tagged2 = copy.deepcopy(tg_corpus)
        tagged3 = copy.deepcopy(tg_corpus)
        or2 = copy.copy(ents_idx)
        or3 = copy.copy(ents_idx)
        des = get_front_des(ent.index, tagged2, or2)
        if not des:
            des = []
        trailing = get_trailing_des(ent.index, tagged3, or3)
        if trailing:
            des.extend(trailing)
        yield des


def get_trailing_targ(idx, tg_corpus, tg_idx, ents):
    # TODO: generate tg_idx from entities
    if type(utils.getEntityByIndex(idx, ents)) != EC.Action:
        return None
    length = len(tg_corpus)
    cur = 0
    while cur < length:
        if (NLP.Converter.penn_to_wn(tg_corpus[cur][1]) not in
                ["a", "n", "v"] and tg_corpus[cur][0].lower() != "and"):
            if tg_corpus[cur][1] not in ["PRP", "IN"]:  # filter out all noise
                tg_corpus[cur] = None
        cur += 1
    if idx == length-1:
        return False
    cur = idx+1
    ret = []
    while True:
        if cur >= length:
            break
        if tg_corpus[cur] is None:
            cur += 1
            continue
        if not ((cur in tg_idx and type(utils.getEntityByIndex(cur, ents)) != EC.Action)
                or tg_corpus[cur][0].lower() == "and"):
            break
        ret.append(utils.getEntityByIndex(cur, ents))
        cur += 1
    return ret


def add_target(ents, tg_corpus):
    # scan for any non Action entity objects
    nonacts = list(filter(lambda x: type(x) != EC.Action, ents))

    if not nonacts:
        return ents

    entity_indices = list(map(lambda x: x.index, ents))

    for e in ents:
        if type(e) is EC.Action:
            yield list(filter(lambda x: False if x is None else True,
                              get_trailing_targ(idx=e.index,
                                                tg_idx=copy.copy(entity_indices),
                                                tg_corpus=copy.deepcopy(tg_corpus),
                                                ents=ents)))


def extract_relations(tg_corpus, entity_indices, characteristic_indices):
    for g in range(len(tg_corpus)):
        if g in entity_indices or g in characteristic_indices \
                or tg_corpus[g][1] not in \
                ['JJ', 'JJR', 'JJS',  # adj
                 'NN', 'NNS', 'NNP', 'NNPS',  # noun
                 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # verb
                 'RB', 'RBR', 'RBS'  # adverb
                 ] \
                or tg_corpus[g][1] in ['RB', 'RBR', 'RBS']:
            tg_corpus[g] = None
    partitioned = list(utils.partition(tg_corpus, None))
    return [EC.Relation(x[:len(x)-1], x[len(x)-1][0]) for x in partitioned]  # TODO: add index support


def construct_graph(entities, entity_indices, relations, relation_indices):
    graph = EC.CorpusGraph(sorted(entities, key=lambda x: x.index))
    enti = sorted(copy.copy(entity_indices))
    for i in range(len(enti)-1):
        c = list(utils.correspond((enti[i], enti[i+1]), relation_indices))
        if c:
            r = utils.getRelationByIndex(relations, c[0])
        else:
            continue
        n1 = graph.getNodeById(i)
        n2 = graph.getNodeById(i+1)
        graph.linkEntities(n1, n2, r)
    return graph


def extract(cps, cpm=False):
    if not cpm:
        with open(cps, "r") as cpsc:
            corpus = cpsc.read().replace("\n", "")
    else:
        corpus = cps
    tagged = NLP.Basic(st).tag(corpus)  # the tagger will do the tokenization
    print("tagged corpus: ", tagged)
    entities = create_entities(tagged)
    entity_index = list(map(lambda x: x.index, entities))
    characterizations = list(get_all_des(entities, entity_index, tagged))
    for chari in range(len(characterizations)):
        entities[chari].attributes = characterizations[chari]
    targets = list(add_target(entities, tagged))
    actions = list(filter(lambda x: True if type(x) == EC.Action else False, entities))
    for targ in range(len(targets)):
        actions[targ].target = targets[targ]
    utils.printl(entities)
    # characterizations index
    raw_characterizations = utils.flatten(characterizations)
    characterizations_indices = list(map(lambda x: x.index, raw_characterizations))
    relations = extract_relations(copy.deepcopy(tagged), entity_index, characterizations_indices)
    relation_index = list(map(lambda x: x.index, relations))
    utils.printl(relations)
    return construct_graph(entities, entity_index, relations, relation_index)


if __name__ == "__main__":
    image = extract("corpus.txt")
    print(image.draw(None, None, force_ascii=True))
