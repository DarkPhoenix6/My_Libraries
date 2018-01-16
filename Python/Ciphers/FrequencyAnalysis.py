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
from Ciphers import CipherTools
from future import standard_library

standard_library.install_aliases()


class FrequencyAnalysis(object):
    def __init__(self):
        self.english_letter_freq = {'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75, 'S': 6.33,
                                    'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41,
                                    'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29, 'V': 0.98,
                                    'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07}
        self.letters = CipherTools.get_alphabet_upper()
        self.letters_occurring_order = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'

    def get_letter_count(self, message) -> dict:
        letter_count = CipherTools.get_alphabet_upper_dict()
        for l in message.upper():
            if l in self.letters:
                letter_count[l] += 1
        return letter_count

    @staticmethod
    def get_item_at_index_zero(x):
        return x[0]

    @staticmethod
    def get_item_at_index_one(x):
        return x[1]

    def get_frequency_order(self, message):
        """

        :param message: message to analyze
        :return: a string of the alphabet letters arranged in order of most frequently occurring in the message
        """

        letters_to_frequency = self.get_letter_count(message)
        frequency_to_letters = {}
        for l in self.letters:
            if letters_to_frequency[l] not in frequency_to_letters:
                frequency_to_letters[letters_to_frequency[l]] = [l]
            else:
                frequency_to_letters[letters_to_frequency[l]].append(l)

        for frequency in frequency_to_letters:
            frequency_to_letters[frequency].sort(key=self.letters_occurring_order.find, reverse=True)
            frequency_to_letters[frequency] = ''.join(frequency_to_letters[frequency])

        frequency_pairs = list(frequency_to_letters.items())
        frequency_pairs.sort(key=FrequencyAnalysis.get_item_at_index_zero, reverse=True)

        frequency_order = []
        for frequency_pair in frequency_pairs:
            frequency_order.append(frequency_pair[1])

        return ''.join(frequency_order)

    def english_frequency_match_score(self, message):
        frequency_order = self.get_frequency_order(message)
        match_score = 0

        for common_letter in self.letters_occurring_order[:6]:
            if common_letter in frequency_order[:6]:
                match_score += 1
        for uncommon_letter in self.letters_occurring_order[:-6]:
            if uncommon_letter in frequency_order[:-6]:
                match_score += 1

        return match_score
