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
from Ciphers.DetectEnglish import DetectEnglish
from Ciphers.FrequencyAnalysis import FrequencyAnalysis
from future import standard_library

standard_library.install_aliases()
import itertools
import re


class VigenereCipher(object):

    @staticmethod
    def encrypt(message, key):
        return VigenereCipher.translate_message(message, key, 'encrypt')

    @staticmethod
    def decrypt(message, key):
        return VigenereCipher.translate_message(message, key, 'decrypt')

    @staticmethod
    def translate_message(message: str, key: str, mode: str):
        alphabet = get_alphabet_upper()
        translated = []
        i = 0  # key Index
        key = key.upper()
        len1 = len(alphabet)
        key_len = len(key)
        for j in message:  # loop through each character in the message
            num = VigenereCipher.find_symbol(alphabet, j)
            if num != -1:  # -1 means j.upper() was not found in alphabet
                if mode == 'encrypt':
                    num += alphabet.find(key[i])  # add if encrypting
                elif mode == 'decrypt':
                    num -= alphabet.find(key[i])  # subtract if decrypting

                num %= len1  # handle the potential wrap-around

                if j.isupper():
                    translated.append(alphabet[num])
                elif j.islower():
                    translated.append(alphabet[num].lower())
                i += 1
                if i == key_len:
                    i = 0
            else:
                # The character was not in alphabet, so add it to translated as it is.
                translated.append(j)
        return ''.join(translated)

    @staticmethod
    def find_symbol(alphabet, j):
        return alphabet.find(j.upper())


class CrackVigenere(FrequencyAnalysis):
    def __init__(self, silent_mode=False, number_most_freq_letters=4, max_key_length=16):
        FrequencyAnalysis.__init__(self)
        self.detect_english = DetectEnglish()
        self.silent_mode = silent_mode
        self.number_most_freq_letters = number_most_freq_letters
        self.max_key_length = max_key_length
        self.non_letters_pattern = re.compile('[^A-Z]')

    def find_repeat_sequences(self, message):
        message = self.non_letters_pattern.sub('', message.upper())

        sequence_spacings = {}
        # iterate through looking for patterns with length from 3 to 5
        for seq_len in range(3, 6):
            for seq_start in range(len(message) - seq_len):
                sequence = message[seq_start:seq_start + seq_len]

                # look for pattern in rest of message
                for i in range(seq_start + seq_len, len(message) - seq_len):
                    if message[i:i + seq_len] == sequence:
                        if sequence not in sequence_spacings:
                            sequence_spacings[sequence] = []

                        # Append the spacing distance between the sequence and the repeated sequence
                        # to the dict entry for that sequence
                        sequence_spacings[sequence].append(i - seq_start)
        return sequence_spacings

    @memoize
    def get_useful_factors(self, number):
        if number < 2:
            # no useful factors
            return []

        factors = []

        for i in range(2, self.max_key_length + 1):
            if (number % i) == 0:
                factors.append(i)
                factors.append(int(number / i))
            if 1 in factors:
                factors.remove(1)
            return list(set(factors))

    def get_most_common_factors(self, sequence_factors):
        factor_counts = {}
        for sequence in sequence_factors:
            factor_list = sequence_factors[sequence]
            for factor in factor_list:
                if factor not in factor_counts:
                    factor_counts[factor] = 0
                factor_counts[factor] += 1

        factors_by_count = []
        for factor in factor_counts:
            if factor <= self.max_key_length:
                # only factors less than or equal to the max key size
                factors_by_count.append((factor, factor_counts[factor]))

        factors_by_count.sort(key=CrackVigenere.get_item_at_index_one, reverse=True)
        return factors_by_count

    def kasiski_examination(self, ciphertext):
        repeated_sequence_spacings = self.find_repeat_sequences(ciphertext)

        sequence_factors = {}
        for sequence in repeated_sequence_spacings:
            sequence_factors[sequence] = []
            for spacing in repeated_sequence_spacings[sequence]:
                sequence_factors[sequence].extend(self.get_useful_factors(spacing))

        factors_by_count = self.get_most_common_factors(sequence_factors)
        likely_key_lengths = []
        for two_int_tuple in factors_by_count:
            likely_key_lengths.append(two_int_tuple[0])

        return likely_key_lengths

    def get_nth_subkey_letters(self, n, key_length, message):
        message = self.non_letters_pattern.sub('', message)

        i = n - 1
        letters = []
        while i < len(message):
            letters.append(message[i])
            i += key_length
        return ''.join(letters)

    def attempt_hack_with_key_of_length_n(self, ciphertext, n, encryption_break_dict_orig: dict):
        """

        :param ciphertext:
        :param n: most likely key length
        :param encryption_break_dict_orig:
        :return:
        """
        encryption_break_dict = {}
        ciphertext_upper = ciphertext.upper()
        all_frequency_scores = []
        for nth in range(1, n + 1):
            nth_letters = self.get_nth_subkey_letters(nth, n, ciphertext_upper)
            frequency_scores = []
            for poss_key in self.letters:
                decrypted_text = VigenereCipher.decrypt(nth_letters, poss_key)
                key_and_frequency_match_tuple = (poss_key, self.english_frequency_match_score(decrypted_text))
                frequency_scores.append(key_and_frequency_match_tuple)

            frequency_scores.sort(key=self.get_item_at_index_one, reverse=True)

            all_frequency_scores.append(frequency_scores[:self.number_most_freq_letters])

        for indexes in itertools.product(range(self.number_most_freq_letters), repeat=n):
            poss_key = ''
            for i in range(n):
                poss_key += all_frequency_scores[i][indexes[i]][0]

            decrypted_text = VigenereCipher.decrypt(ciphertext_upper, poss_key)

            if self.detect_english.is_english(decrypted_text):
                original_case = []
                for i in range(len(ciphertext)):
                    if ciphertext[i].isupper():
                        original_case.append(decrypted_text[i].upper())
                    else:
                        original_case.append(decrypted_text[i].lower())

                decrypted_text = ''.join(original_case)
                CrackVigenere.add_to_enc_break_dict(encryption_break_dict, poss_key, decrypted_text, 200)
        return dict(encryption_break_dict, **encryption_break_dict_orig)

    def hack_vigenere(self, ciphertext):
        """

        :param ciphertext:
        :return:
        """
        encryption_break_dict = {}
        all_likely_key_lengths = self.kasiski_examination(ciphertext)

        for key_length in all_likely_key_lengths:
            encryption_break_dict = self.attempt_hack_with_key_of_length_n(ciphertext, key_length, encryption_break_dict)

        print(encryption_break_dict)

        if is_empty(encryption_break_dict):
            print('Unable to hack message with likely key length(s). Brute forcing key length...')


    @staticmethod
    def dictionary_attack(cipher_text):
        encryption_break_dict = {}
        detect_english = DetectEnglish()
        for w in detect_english.english_dict:
            decrypted_text = VigenereCipher.decrypt(cipher_text, w)
            if detect_english.is_english(decrypted_text, word_percent=40):
                CrackVigenere.add_to_enc_break_dict(encryption_break_dict, w, decrypted_text)
        return encryption_break_dict

    @staticmethod
    def add_to_enc_break_dict(break_dict, key, dec_message, message_len_to_show=100):
        break_dict[key] = dec_message[:message_len_to_show]


m = 'tkg kcl sgzgj gzgs hggs pn lncsgt bvyy fspvy cqpgj kgj qcpkgj csl bnpkgj lvgl, pknfuk tvw nj gvukp pvbgt c ' \
    'egcj tkg ogsp pn pnos ns tcpfjlce, vs pkg ocuns, vs c bcvy-njlgj ljgtt csl kgj hcjg qggp qycp vs pkg ocuns ' \
    'hgl csl kgj tkngt ojcaagl vs c avgig nq acagj hgtvlg kgj ns pkg tgcp. tkg onfyl afp ns pkg tkngt xftp ' \
    'hgqnjg pkg ocuns jgcikgl pnos. cqpgj tkg unp pn hg c hvu uvjy tkg onfyl ctm kgj qcpkgj pn tpna pkg ocuns cp ' \
    'pkg glug nq pnos csl tkg onfyl ugp lnos csl ocym. tkg onfyl snp pgyy kgj qcpkgj oke tkg ocspgl pn ocym vs ' \
    'vstpgcl nq jvlvsu. kg pknfukp pkcp vp oct hgicftg nq pkg tbnnpk tpjggpt, pkg tvlgocymt. hfp vp oct hg icftg ' \
    'tkg hgyvgzgl pkcp pkg agnayg okn tco kgj csl oknb tkg acttgl ns qnnp onfyl hgyvgzg pkcp tkg yvzgl vs pkg ' \
    'pnos pnn. okgs tkg oct pogyzg egcjt nyl kgj qcpkgj csl bnpkgj lvgl vs pkg tcbg tfbbgj, vs c ynu knftg nq ' \
    'pkjgg jnnbt csl c kcyy, ovpknfp tijggst, vs c jnnb yvukpgl he c hfutovjygl mgjntgsg ycba, pkg scmgl qynnj ' \
    'onjs tbnnpk ct nyl tvyzgj he scmgl qggp. tkg oct pkg enfsugtp yvzvsu ikvyl. kgj bnpkgj lvgl qvjtp. tkg tcvl, ' \
    'pcmg icjg nq aco. ygsc lvl tn. pkgs nsg lce kgj qcpkgj tcvl, enf un pn lncsgt bvyy ovpk bimvsyge. enf ugp ' \
    'jgcle pn un, hg jgcle okgs kg inbgt. pkgs kg lvgl. bimvsyge, pkg hjnpkgj, cjjvzgl vs c ocuns. pkge hfjvgl ' \
    'pkg qcpkgj vs c ujnzg hgkvsl c infspje ikfjik nsg cqpgjsnns, ovpk c avsg kgcltpnsg. pkg sgwp bnjsvsu tkg ' \
    'lgacjpgl qnjgzgj, pknfuk vp vt anttvhyg pkcp tkg lvl snp msno pkvt cp pkg pvbg, vs pkg ocuns ovpk bimvsyge, ' \
    'qnj lncsgt bvyy. pkg ocuns oct hnjjnogl csl pkg hjnpkgj kcl ajnbvtgl pn jgpfjs vp he svukpqcyy. pkg hjnpkgj ' \
    'onjmgl vs pkg bvyy. cyy pkg bgs vs pkg zvyycug. onjmgl vs pkg bvyy nj qnj vp. vp oct ifppvsu avsg. vp kcl ' \
    'hggs pkgjg tgzgs egcjt csl vs tgzgs egcjt bnjg vp onfyl lgtpjne cyy pkg pvbhgj ovpkvs vpt jgcik. pkgs tnbg ' \
    'nq pkg bcikvsgje csl bntp nq pkg bgs okn jcs vp csl gwvtpgl hgicftg nq csl qnj vp onfyl hg ynclgl nspn ' \
    'qjgvukp icjt csl bnzgl coce. hfp tnbg nq pkg bcikvsgje onfyl hg ygqp, tvsig sgo avgigt infyl cyocet hg ' \
    'hnfukp ns pkg vstpcyybgsp aycs-ucfsp, tpcjvsu, bnpvnsygtt okggyt jvtvsu qjnb bnfslt nq hjvim jfhhyg csl ' \
    'jcuugl ogglt ovpk c rfcyvpe ajnqnfslye ctpnsvtkvsu, csl ufppgl hnvygjt yvqpvsu pkgvj jftpvsu csl fstbnmvsu ' \
    'tpcimt ovpk cs cvj tpfhhnjs, hcqqygl csl hgbftgl fans c tpfbaanimgl tigsg nq ajnqnfsl csl agcigqfy ' \
    'lgtnycpvns, fsaynogl, fspvyygl, ufppvsu tynoye vspn jgl csl iknmgl jczvsgt hgsgcpk pkg ynsu rfvgp jcvst nq ' \
    'cfpfbs csl pkg ucyynavsu qfje nq zgjscy grfvsnwgt. pkgs pkg kcbygp okvik cp vpt hgtp lce kcl hnjsg sn scbg ' \
    'yvtpgl ns antpnqqvig lgacjpbgsp csscyt onfyl snp sno gzgs hg jgbgbhgjgl he pkg knnmonjbjvllgs kgvjtcp-ycjug ' \
    'okn afyygl pkg hfvylvsut lnos csl hfjvgl pkgb vs innmtpnzgt csl ovspgj ujcpgt. '

# crack_dict = CrackVigenere.dictionary_attack(m)
# print(crack_dict)

crack_ven = CrackVigenere()
crack_ven.hack_vigenere(m)
