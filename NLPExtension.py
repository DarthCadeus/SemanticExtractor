import time
start_time = time.clock()
print("loading NLP Extension... ")
from nltk.corpus import wordnet
from nltk import word_tokenize
import inflect
import utils
import pickle
from termcolor import colored
inflect = inflect.engine()
print(colored(f"-importing completed in {time.clock() - start_time} seconds", "red"))
# corpus_root = '/usr/share/dict'
# wordlists = PlaintextCorpusReader(corpus_root, '.*')
# print(colored(f"-wordlists read in {time.clock() - start_time} seconds", "red"))
# english_vocab = set(w.lower() for w in words.words())
# print(colored(f"-English vocab constructed in {time.clock() - start_time} seconds", "red"))
ns = open("nouns", "rb")
# this gives a sort of general tagging
nouns = pickle.load(ns)
ns.close()
print(colored(f"-nouns loaded from nouns in {time.clock() - start_time} seconds", "red"))
# this gives a sort of general tagging
wordtags = pickle.load(open("wordtags", "rb"))
print(colored(f"-wordtags loaded in {time.clock() - start_time} seconds", "red"))


class Converter:
    def __init__(self):
        pass

    @staticmethod
    def penn_to_wn(tag):
        # if tag == "NNS":
        #     return "n"
        if tag in ['JJ', 'JJR', 'JJS']:
            return "a"
        elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:
            return "n"
        elif tag in ['RB', 'RBR', 'RBS']:
            return "r"
        elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            return "v"
        return None


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

    # @staticmethod
    # def unusual_words(text):
    #     text_vocab = set(w.lower() for w in text if w.isalpha())
    #     unusual = text_vocab.difference(english_vocab)
    #     return sorted(unusual)

    @staticmethod
    def cross_reference(word, ref):
        try:
            return wordnet.synsets(word)[0].pos()
        except IndexError:
            if word in ref:
                return ref[word]
        return

    @staticmethod
    def recognize_repetitive_pattern(tokens):
        # get rid of all connectives
        # this is not best form, but still
        tokens_processed = tokens
        if not tokens:
            return False
        try:
            tokens_processed.remove("CC")
        except ValueError:
            pass
        tokens_processed = list(Processor.process_raw_tokens(tokens_processed))
        # merge the two, to keep the wn when there is an option
        # leave the others untouched
        tokens_processed = list(map(lambda x, y: x if x else y, tokens_processed, tokens))
        # partition the list based on the punctuation
        tokens_processed_partitioned = list(Partitioner.punctuation_partition(tokens_processed))
        tokens_processed_partitioned_extracted = list(
            map(lambda x: Extracter.extract_core_pattern(x), tokens_processed_partitioned))
        sentence_patterns = {}
        for part in tokens_processed_partitioned_extracted:
            pattern = ",".join(part)
            if pattern not in sentence_patterns:
                sentence_patterns[pattern] = 1
            else:
                sentence_patterns[pattern] += 1
        # filter out the items with just one appearance: they cannot show a pattern
        # I suppose I am not the best fighter on the readibility front
        sentence_patterns = dict(list(map(lambda x: (x, sentence_patterns[x]),
                                          list(filter(lambda x: sentence_patterns[x] > 1, sentence_patterns)))))

        if len(sentence_patterns) == 0:
            return False  # cannot contain a repititive pattern

        largest = utils.dict_max(sentence_patterns)
        if len(sentence_patterns) == 1:
            pass
        else:
            # detect if there is an obvious pattern
            # evaluate the overall percentage in the partition
            pct = sentence_patterns[largest] / sum(list(sentence_patterns.values()))
            if pct < 0.3:
                return False

        idcs = list(utils.findall(largest.split(","), tokens_processed_partitioned_extracted))
        all_matches = list(utils.getall(idcs, tokens_processed_partitioned))
        return all_matches, idcs


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

    # @staticmethod
    # def tokenize_sentence(sentence_text):
    #     for sent in sentence_text:
    #         yield nltk.pos_tag(nltk.word_tokenize(sent))

    # @staticmethod
    # def lemmatize(processed_text):
    #     result = []
    #     for g_index in range(0, len(processed_text)):
    #         group = processed_text[g_index]
    #         if group[1] is None:
    #             continue
    #         result.append((nltk.stem.wordnet.WordNetLemmatizer().lemmatize(group[0], group[1]), g_index))
    #     return result

    # @staticmethod
    # def lemmatize_singly(raw_words, ref):
    #     for word in raw_words:
    #         t = Determiner.cross_reference(word, ref)
    #         if t:
    #             res = nltk.stem.wordnet.WordNetLemmatizer().lemmatize(word, t)
    #             if res == word:
    #                 # attempt other ones
    #                 if word.endswith("ing"):
    #                     resv = nltk.stem.wordnet.WordNetLemmatizer().lemmatize(word, "v")
    #                     if resv != word:
    #                         yield resv
    #                         continue
    #                 elif word.endswith("s"):
    #                     if inflect.singular_noun(word) in english_vocab:
    #                         yield inflect.singular_noun(word)
    #                         continue
    #             yield res


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
            return self.tagger.tag(tkn_corpus)
        if tagger:
            return tagger.tag(tkn_corpus)
        raise NoTaggerFound("This may come as a surprise, but POS taggers are a prerequisite"
                            "for POS tagging! Pass a tagger with Basic(tagger) or pass it as the"
                            "second argument in the function. ")


print(colored(f"-Classes defined in {time.clock() - start_time} seconds", "red"))

if __name__ == "__main__":
    print(Determiner.is_gerund("eating"))
