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


def decrypt_shift(in_str: str):

    a = split_string(in_str)
    for i in range(26):
        c = caesar_cipher(a, i)
        print(c)


def caesar_cipher(in_str, shift_amount):
    d = get_alphabet()
    c = str(shift_amount) + ": "
    for h in in_str:
        for j in h:
            c += d[(d.find(j.lower()) + shift_amount) % 26]
        c += " "
    return c


a = enum_alphabet()


in_1 = 'tq esle hld ecfp sp xfde slgp qpwe esle sp slo wzde esp zwo hlcx hzcwo, alto l strs actnp qzc wtgtyr ezz ' \
       'wzyr htes l dtyrwp ocplx. sp xfde slgp wzzvpo fa le ly fyqlxtwtlc dvj esczfrs qctrsepytyr wplgpd lyo ' \
       'dstgpcpo ld sp qzfyo hsle l rczepdbfp estyr l czdp td lyo szh clh esp dfywtrse hld fazy esp dnlcnpwj ncplepo ' \
       'rcldd. l yph hzcwo, xlepctlw hteszfe mptyr cplw, hspcp azzc rszded, mcplestyr ocplxd wtvp ltc, ' \
       'octqepo qzceftezfdwj lmzfe...wtvp esle ldspy, qlyeldetn qtrfcp rwtotyr ezhlco stx esczfrs esp lxzcaszfd ecppd.'

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


for i in a:
    print(i)

d = get_alphabet()
b = "tq esle hld ecfp"
decrypt_shift(in_1)

in_1_dec = caesar_cipher(split_string(in_1), 15)
print(in_1_dec)
decrypt_shift(in_2)

print(count_letters(split_string(in_2)))
