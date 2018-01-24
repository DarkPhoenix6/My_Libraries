from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import open
from builtins import str
from builtins import range
from builtins import object
from builtins import int
from builtins import bytes
from builtins import chr
from builtins import dict
from builtins import map
from builtins import input
# etc., as needed
from future import standard_library
standard_library.install_aliases()
from Ciphers.DetectEnglish import EnglishDict
import pprint


def get_word_pattern(word: str):
    word = word.upper()
    next_num = 0
    letter_numbers = {}
    word_pattern = []

    for letter in word:
        if letter not in letter_numbers:
            letter_numbers[letter] = str(next_num)
            next_num += 1
        word_pattern.append(letter_numbers[letter])
    return '.'.join(word_pattern)


def main():
    all_patterns = {}
    word_list = EnglishDict.load_dictionary_list()
    for word in word_list:
        pattern = get_word_pattern(word)
        if pattern not in all_patterns:
            all_patterns[pattern] = [word]
        else:
            all_patterns[pattern].append(word)
    fo = open('WordPatternsVar.py', 'w')
    fo.write('all_patterns = ')
    fo.write(pprint.pformat(all_patterns))


if __name__ == '__main__':
    main()
