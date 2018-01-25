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
from builtins import list
from builtins import tuple
# etc., as needed
from future import standard_library

standard_library.install_aliases()
from Ciphers import SubstitutionCipher
from Ciphers import CipherTools
from Ciphers import WordPatterns
from Ciphers.DetectEnglish import DetectEnglish
import os
import re
import sys
import copy
import pprint
if not os.path.exists('WordPatternsVar.py'):
    WordPatterns.main()
from Ciphers import WordPatternsVar
ALPHABET_UPPER = CipherTools.get_alphabet_upper()

detect_english = DetectEnglish
NON_LETTERS_OR_SPACE_PATTERN = re.compile('[^A-Z\s]')


def get_blank_cipher_mapping():
    map_dict = {}
    for i in ALPHABET_UPPER:
        map_dict[i] = []
    return map_dict


def add_letters_to_mapping(letter_mapping, cipherword, candidate):
    letter_mapping2 = copy.deepcopy(letter_mapping)
    for i in range(len(cipherword)):
        if candidate[i] not in letter_mapping2[cipherword[i]]:
            letter_mapping2[cipherword[i]].append(candidate[i])
    return letter_mapping2


def intersect_mappings(map_a, map_b):
    intersected_mappings = get_blank_cipher_mapping()
    for letter in ALPHABET_UPPER:

        if CipherTools.is_empty(map_a[letter]):
            intersected_mappings[letter] = copy.deepcopy(map_b[letter])
        elif CipherTools.is_empty(map_b[letter]):
            intersected_mappings[letter] = copy.deepcopy(map_a[letter])
        else:
            for mapped_letter in map_a[letter]:
                if mapped_letter in map_b[letter]:
                    intersected_mappings[letter].append(mapped_letter)

    return intersected_mappings


def remove_solved_letters_from_mapping(letter_mapping):
    letter_map = copy.deepcopy(letter_mapping)
    loop_again = True
    while loop_again:
        loop_again = False

        solved_letters = []
        for cipher_letter in ALPHABET_UPPER:
            if len(letter_map[cipher_letter]) == 1:
                solved_letters.append(letter_map[cipher_letter][0])

        for cipher_letter in ALPHABET_UPPER:
            for s in solved_letters:
                if len(letter_map[cipher_letter]) != 1 and s in letter_map[cipher_letter]:
                    letter_map[cipher_letter].remove(s)
                    if len(letter_map[cipher_letter]) == 1:
                        loop_again = True
    return letter_map


def crack_sub(message):
    intersected_map = get_blank_cipher_mapping()
    cipher_word_list = NON_LETTERS_OR_SPACE_PATTERN.sub('', message.upper()).split()
    for cipher_word in cipher_word_list:
        new_map = get_blank_cipher_mapping()
        word_pattern = WordPatterns.get_word_pattern(cipher_word)
        if word_pattern not in WordPatternsVar.all_patterns:
            continue

        for candidate in WordPatternsVar.all_patterns[word_pattern]:
            new_map = add_letters_to_mapping(new_map, cipher_word, candidate)

        intersected_map = intersect_mappings(intersected_map, new_map)

    return remove_solved_letters_from_mapping(intersected_map)

def decrypt_with_letter_mapping(ciphertext, letter_mapping):
    key = ['x'] * len(ALPHABET_UPPER)
    for cipher_letter in ALPHABET_UPPER:
        if len(letter_mapping[cipher_letter]) == 1:
            key_index = ALPHABET_UPPER.find(letter_mapping[cipher_letter][0])
            key[key_index] = cipher_letter
        else:
            ciphertext = ciphertext.replace(cipher_letter.lower(), '_')
            ciphertext = ciphertext.replace(cipher_letter.upper(), '_')
    key = ''.join(key)
    return SubstitutionCipher.decrypt(ciphertext, key), key


def dec_2(ciphertext, key:str):
    letters = CipherTools.get_alphabet_upper()
    for cipher_letter in ALPHABET_UPPER:
        if key.find(cipher_letter) != -1:
            pass
        else:
            print(cipher_letter)
            ciphertext = ciphertext.replace(cipher_letter.lower(), '_')
            ciphertext = ciphertext.replace(cipher_letter.upper(), '_')
    print(ciphertext)
    return SubstitutionCipher.decrypt(ciphertext, key)


if __name__ == '__main__':
    in_2 = 'tkg kcl sgzgj gzgs hggs pn lncsgt bvyy fspvy cqpgj kgj qcpkgj csl bnpkgj lvgl, pknfuk tvw nj gvukp pvbgt c ' \
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

    print(sys.getsizeof(in_2))
    print(sys.getsizeof(WordPatternsVar.all_patterns))
    # cipher_mapping = crack_sub(in_2)
    # print('cipher_ mapping: ')
    # pprint.pprint(cipher_mapping)
    print('Original ciphertext:')
    print(in_2)
    print()
    key = 'CHILGQUKVXMYBSNARJTPFZOWED'
    pt = dec_2(in_2, key)
    # pt, new_key = decrypt_with_letter_mapping(in_2, cipher_mapping)
    print(pt)
    print(key)


