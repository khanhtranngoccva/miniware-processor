import re

import nltk
from nltk.corpus import words
from helpers.definition_helper import definition

try:
    english_words = set(words.words())
except LookupError:
    nltk.download('words')
    english_words = set(words.words())


@definition("English Corpus Words", "English")
def english_corpus(raw_string: str):
    res = []

    replaced = re.sub(r"[_\W]", " ", raw_string)
    groups = list(map(lambda obj: obj.span(), re.finditer(r"\S+", replaced)))

    styles = [
        re.compile(r"^[A-Z]?[a-z]+$"),
        re.compile(r"^[A-Z]+$")
    ]

    def match_style(string):
        for style in styles:
            if style.match(string) is not None:
                return True
        return False

    for group_start, group_end in groups:
        for i in range(group_start, group_end):
            for j in range(i, group_end + 1):
                if j - i < 3:
                    continue
                str_slice = replaced[i:j]
                if str_slice.lower() in english_words and match_style(str_slice):
                    res.append([i, j])

    return res


if __name__ == '__main__':
    input_str = '<requestedExecutionLevel level="asInvoker" />'
    res = english_corpus(input_str)
    for start, end in res:
        print(input_str[start:end])
