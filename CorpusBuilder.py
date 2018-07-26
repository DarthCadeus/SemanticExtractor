from nltk.corpus import brown
import random
categories = brown.categories()


def get_mixed(limit, number=False):
    source = categories
    if number:
        source = random.sample(source, number)
    try:
        return random.sample(list(brown.sents(categories=source)), limit)
    except ValueError:
        return list(brown.sents(categories=source))
