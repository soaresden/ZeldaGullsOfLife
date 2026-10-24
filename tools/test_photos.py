"""Test des photos de Cocolint (idée de Denis) : une fois le chapitre 5 fini, à l'auberge (3:9e),
l'aubergiste n'est pas là et Marine envoie Link dormir (« en face à face ») ; le lit, l'auberge du
Songe (2:9e) : Marine humaine fouille ses poches (« J'AI TROUVÉ ÇA DANS TES POCHES ! ») ; les trois
vraies photos de Link's Awakening DX (la chute, Tarkin et Bow Wow, la falaise), en plein écran avec
sa réplique ; puis retour à l'auberge du Songe et le quiz ; une seule fois (GLOBALFLAG_BALLADE_PHOTOS).
Usage : python tools/test_photos.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CUTSCENE_INDEX = 0xc2ef
TEXT_INDEX = 0xcba2
INTERAC_BALLADE_NPC = 0xe8
DREAM_INN_FLAGS = 0xc79e          # les drapeaux de la salle 2:9e (le câlin vu : $40)
GLOBALFLAG_BALLADE_PHOTOS = 0x5b
GLOBALFLAG_BALLADE_PHOTOS_HINT = 0x64
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


g.level(5, 'Fin')
for _ in range(20):
    g.text_through()
    g.w(20)
check(not g.global_flag(GLOBALFLAG_BALLADE_PHOTOS), 'pas encore de photos')
# La fin du chapitre passée, dehors, Marine le dit une fois (Denis) : « Link... on peut revenir à
# l'auberge ? J'ai quelque chose à te dire... »
said = g.global_flag(GLOBALFLAG_BALLADE_PHOTOS_HINT)
for _ in range(60):
    if said:
        break
    g.w(10)
    if g.m[TEXT_ACTIVE]:
        shoot('p00_auberge', "Marine : on peut revenir à l'auberge ?")
    said = g.global_flag(GLOBALFLAG_BALLADE_PHOTOS_HINT)
    g.text_through()
check(said, "Marine : « Link... on peut revenir à l'auberge ? »")
g.warp(3, 0x9e, 0x57)
check(g.wait_text(200) and g.m[TEXT_INDEX] == 0x7b, "l'auberge : « en face à face... va dormir ! »")
g.w(30)
shoot('p00_dormir', 'Va dormir !')
innkeeper = [s for s in range(0xd0, 0xe0)
             if g.m[(s << 8) + 0x40] and g.m[(s << 8) + 0x41] == INTERAC_BALLADE_NPC and g.m[(s << 8) + 0x42] == 0]
check(not innkeeper, "l'aubergiste n'est pas là")
g.text_through()
# (le câlin de la première nuit est déjà passé)
g.m[DREAM_INN_FLAGS] |= 0x40
# Le lit : en poussant contre l'oreiller (à pied : en revenant dans la salle, Marine
# le redirait)
g.goto(None, 0x68)          # (par la colonne 6 : la commode bloque la 7)
g.goto(0x18, None)
g.goto(None, 0x78)
# (l'épée est sur A : Link pousse contre le lit, comme dans Ages)
g.hold('right', 130)
for _ in range(150):
    g.w(6)
    if g.where() == (2, 0x9e):
        break
    if g.m[TEXT_ACTIVE]:
        g.press('a', 2)
g.settled()
check(g.where() == (2, 0x9e), "Link dort : l'auberge du Songe (2:9e)")
check(g.wait_text(200) and g.m[TEXT_INDEX] == 0x7c, 'Marine humaine : « fais voir tes poches ! »')
g.text_through()
g.w(30)
shoot('p00_fouille', 'Elle fouille')
check(g.wait_text(200) and g.m[TEXT_INDEX] == 0xe8, "« J'AI TROUVÉ ÇA DANS TES POCHES ! »")
g.w(30)
shoot('p00_poche', "J'ai trouvé ça dans tes poches !")
g.text_through()
check(g.wait_until(lambda: g.m[CUTSCENE_INDEX] == 0x22, 300), 'la cinématique des photos')
for n, (name, label) in enumerate((('p01_chute', 'On ne parle PAS de celle-là'),
                                   ('p02_tarkin', 'Papa ! Et Bow Wow !'),
                                   ('p03_falaise', 'Qui a pris cette photo ?!'))):
    check(g.wait_text(400), 'photo %d : la réplique de Marine' % (n + 1))
    g.w(150)
    shoot(name, label)
    g.text_through()
check(g.wait_until(lambda: g.m[CUTSCENE_INDEX] == 0x01 and g.where() == (2, 0x9e), 600),
      "retour à l'auberge du Songe (2:9e)")
g.settled()
check(g.wait_text(200) and g.m[TEXT_INDEX] == 0xee, "le quiz : « on va voir si tu te souviens de tout ! »")
g.w(30)
shoot('p04_retour', "On va voir si tu te souviens de tout !")
check(g.global_flag(GLOBALFLAG_BALLADE_PHOTOS), 'les photos ont été vues (GLOBALFLAG_BALLADE_PHOTOS)')
# Une seule fois (ensuite, à l'auberge du Songe, c'est le quiz de Marine : tools/test_quiz.py)
g.warp(2, 0x9e, 0x17)
again = False
for _ in range(40):
    g.text_through(4)
    g.w(10)
    again = again or g.m[CUTSCENE_INDEX] == 0x22
check(not again, 'une seule fois')

sheet(shots, os.path.join(OUT, 'photos.png'), cols=3)
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
