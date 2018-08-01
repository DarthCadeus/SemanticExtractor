import nltk
import pickle
nouns = {x.name().split('.', 1)[0] for x in nltk.corpus.wordnet.all_synsets('n')}
ns = open("../nouns", "wb")
pickle.dump(nouns, ns)
ns.close()
