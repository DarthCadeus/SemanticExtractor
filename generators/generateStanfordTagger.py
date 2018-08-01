from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger("english-bidirectional-distsim.tagger")

import pickle
stp = open("../stanfordPOSTagger", "wb")
pickle.dump(st, stp)
stp.close()
