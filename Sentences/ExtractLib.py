"""
Distribution version
v.0.1
Using t.3.7 & t.3.6 & p.2.2.1
"""

import sys
sys.path.append("..")
import utils
import NLPExtension as NLP
import ExtractorClasses as EC
import to_graph
import networkx as nx
import copy
import time
import copy
import nltk
from termcolor import colored
from ImportSource import ltpc, lths

def extract(corpus, graph=True, debug=False):
    wb = EC.NoStdout() if not debug else EC.YesStdout()
    with wb:
        tokenized_corpus = NLP.Basic.tokenize(corpus)
        tagged_corpus = nltk.pos_tag(tokenized_corpus)
        function = lths
        processor = ltpc

        extracted = function(tagged_corpus, tokenized_corpus)

        if not utils.verify(extracted):
            alt_extraction = function(tagged_corpus, tokenized_corpus, force=True)
            if type(alt_extraction) == dict:
                pass
            else:
                if alt_extraction():
                    if not graph:
                        return alt_extraction
                    return to_graph.to_graph(alt_extraction, 3.7)
            all_extracted = list(processor(extracted, tagged_corpus))
            if not graph:
                print("Okay")
                return all_extracted
            graph = []
            for i in all_extracted:
                graph.append(to_graph.to_graph(i, 3.7))
        else:
            if not graph:
                print("Me too")
                return extracted
            graph = to_graph.to_graph(extracted, 3.7)
        return graph
