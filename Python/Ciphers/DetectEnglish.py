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
from Ciphers.CipherTools import *
from future import standard_library

standard_library.install_aliases()


class EnglishDict(object):

    @staticmethod
    def load_dictionary(eng_dictionary='dictionary.txt') -> dict:
        dict_file = open(eng_dictionary)
        english_words = {}
        for w in dict_file.read().split('\n'):
            english_words[w] = None
        dict_file.close()
        return english_words

    @staticmethod
    def load_dictionary_list(eng_dictionary='dictionary.txt') -> list:
        dict_file = open(eng_dictionary)
        english_words = []
        for w in dict_file.read().split('\n'):
            english_words.append(w)
        dict_file.close()
        return english_words


class DetectEnglish(object):
    def __init__(self):
        self.uppercase_letters = get_alphabet_upper()
        self.alphabet_and_space = self.uppercase_letters + get_alphabet() + " \t\n"
        self.english_dict = EnglishDict.load_dictionary()

    def get_english_count(self, message: str):
        message = self.remove_non_letters(message.upper())
        possible_words = message.split()

        if is_empty(possible_words):
            return 0.0
        else:
            matches = 0
            for w in possible_words:
                if w in self.english_dict:
                    matches += 1
            return float(matches) / len(possible_words)

    def remove_non_letters(self, message) -> str:
        letters_only = []
        for character in message:
            if character in self.alphabet_and_space:
                letters_only.append(character)
        return ''.join(letters_only)

    def is_english(self, message, word_percent=20, letter_percent=85):
        """

        :param message:
        :param word_percent: the percentage of words that must exist in the english dictionary
        :param letter_percent: the percentage of letters that must be in the alphabet
        :return:
        """
        words_match = self.get_english_count(message) * 100 >= word_percent
        num_letters = len(self.remove_non_letters(message))
        message_letters_percent = float(num_letters) / len(message) * 100
        letters_match = message_letters_percent >= letter_percent
        return words_match and letters_match
