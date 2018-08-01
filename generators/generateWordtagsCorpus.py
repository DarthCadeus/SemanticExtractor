import nltk
import sys
import pickle
wordtags = nltk.ConditionalFreqDist((w.lower(), t)
                                    for w, t in
                                    nltk.corpus.brown.tagged_words(tagset="universal"))
print(sys.getsizeof(wordtags))
new_tags = {}
for word in wordtags:
    r = sorted(wordtags[word], key=wordtags[word].get, reverse=True)
    if "VERB" in r:
        if r.index("VERB") < 10:
            new_tags[word] = r
print(sys.getsizeof(new_tags))
wdtb = open("../wordtags", "wb")
pickle.dump(new_tags, wdtb)
wdtb.close()
