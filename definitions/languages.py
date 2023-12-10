import re

import nltk
from nltk.corpus import words
from definition_helper import definition

try:
    english_words = set(words.words())
except LookupError:
    nltk.download('words')
    english_words = set(words.words())


@definition("English Corpus Words", "English")
def english_corpus(raw_string: str):
    res = []

    r1 = re.compile(
        # Camel case
        r"(?<=[a-z])(?=[A-Z])"
        # Dealing with non-word characters
        r"|[\W_]"
    )

    tokens = r1.split(raw_string)

    for token in tokens:
        # Avoid 1-letter words qualifying
        if len(token) < 4:
            continue
        if token.lower() in english_words or token in english_words:
            res.append(token)

    return res


if __name__ == '__main__':
    print(english_corpus("ThisIs_A,Word"))
