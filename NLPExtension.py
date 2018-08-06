import time
from nltk.corpus import wordnet
from nltk import word_tokenize
import inflect
import pickle
from termcolor import colored
inflect = inflect.engine()
ns = open("nouns", "rb")
# nouns
nouns = pickle.load(ns)
ns.close()
# this gives a sort of general tagging
wordtags = pickle.load(open("wordtags", "rb"))

class Converter:
    def __init__(self):
        pass

    @staticmethod
    def penn_to_wn(tag):
        if tag in ['JJ', 'JJR', 'JJS']:
            return "a"
        elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:
            return "n"
        elif tag in ['RB', 'RBR', 'RBS']:
            return "r"
        elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            return "v"
        return None

    @staticmethod
    def penn_base_form(tag):
        if tag in ["JJ", "JJR", "JJS", "PDT", "PRP$"]:
            return "des"

    @staticmethod
    def to_sbj(pronoun):
        return {
            "them": "they",
            "her": "she",
            "him": "he",
            "us": "we"
        }.get(pronoun, pronoun)


class Determiner:
    def __init__(self):
        pass

    @staticmethod
    def is_gerund(word, threshold=3):
        try:
            ref = wordtags[word]
            if word.endswith("ing") and ref.index("VERB") < threshold:
                return True
            return False
        except ValueError:
            return None
        except KeyError:
            return None

    @staticmethod
    def is_plural(word):
        return not bool(inflect.singular_noun(word))

    @staticmethod
    def cross_reference(word, ref):
        try:
            return wordnet.synsets(word)[0].pos()
        except IndexError:
            if word in ref:
                return ref[word]
        return


class Extracter:
    def __init__(self):
        pass

    @staticmethod
    def extract_tokens(sentence):
        return list(map(lambda x: x[1], sentence))

    @staticmethod
    def extract_core_pattern(tokens):
        return list(filter(lambda x: True if x == "v" or x == "n" or x == "adj" else False, tokens))

    @staticmethod
    def extract_lemmatized_words(lemmatized_text):
        return list(map(lambda x: x[0], lemmatized_text))


class Partitioner:
    def __init__(self):
        pass

    @staticmethod
    def punctuation_partition(tokens, just_words=False):
        part = []
        if type(tokens[0]) is tuple:
            for t in tokens:
                if t[0] == ",":
                    yield part
                    part = []
                else:
                    part.append(t if just_words else t[0])
            yield part
        else:
            for t in tokens:
                if t == ",":
                    yield part
                    part = []
                else:
                    part.append(t)
            yield part


class Processor:
    def __init__(self):
        pass

    @staticmethod
    def process_raw_tokens(tokens):
        for t in tokens:
            yield Converter.penn_to_wn(t)

    @staticmethod
    def process_tokens(tokenized_text):
        for sent in tokenized_text:
            for group in sent:
                yield (group[0], Converter.penn_to_wn(group[1]), group[1])


class NoTaggerFound(Exception):
    pass


class InvalidCorpus(Exception):
    pass


# for basic usage
class Basic:
    def __init__(self, tagger=None):
        self.tagger = tagger

    @staticmethod
    def tokenize(corpus):
        return word_tokenize(corpus)

    def tag(self, tkn_corpus, tagger=None):
        if type(tkn_corpus) == str:
            tkn_corpus = Basic.tokenize(tkn_corpus)  # sort of sugar. Integrated into tagger comes the
            # word tokenizer
        if self.tagger:
            return self.tagger(tkn_corpus)
        if tagger:
            return tagger(tkn_corpus)
        raise NoTaggerFound("This may come as a surprise, but POS taggers are a prerequisite"
                            "for POS tagging! Pass a tagger with Basic(tagger) or pass it as the"
                            "second argument in the function. ")
