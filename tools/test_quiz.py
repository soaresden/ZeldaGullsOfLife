"""Test du quiz de Marine sur Cocolint (idée de Denis) : à l'auberge, juste après les photos.
- une première fois avec une erreur : « Tu as oublié des choses... On recommencera ! » ;
- en revenant à l'auberge : tout juste (le Village des Animaux, il plonge, Richard, le Coq
  Volant, sa mère : pas notée, Mario) : la blague de Tarkin, sa tirade, puis le bisou
  (GLOBALFLAG_BALLADE_QUIZ, les cœurs pleins).
Usage : python tools/test_quiz.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, HEALTH, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
GLOBALFLAG_BALLADE_PHOTOS, GLOBALFLAG_BALLADE_QUIZ = 0x5b, 0x5c
ANSWERS = [(2, 3), (1, 3), (0, 3), (0, 3), (1, 2), (0, 3)]   # (le bon choix, le nombre de choix)
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


def quiz(answers, shots_prefix=None):
    check(g.wait_text(300), "Marine : « On va voir si tu te souviens de Cocolint... »")
    for n, (option, count) in enumerate(answers):
        g.text_through(4)
        g.choose(option, count)
        if shots_prefix and n in (0, 5):
            g.w(30)
            shoot('%s_q%d' % (shots_prefix, n + 1), 'Question %d' % (n + 1))


g.level(5, 'Fin')
for _ in range(20):
    g.text_through()
    g.w(20)
g.m[GLOBAL_FLAGS + GLOBALFLAG_BALLADE_PHOTOS // 8] |= 1 << (GLOBALFLAG_BALLADE_PHOTOS % 8)
g.m[HEALTH] = 4

# Avec une erreur (le morse : il a dansé)
g.warp(3, 0x9e, 0x57)
wrong = list(ANSWERS)
wrong[1] = (0, 3)
quiz(wrong)
for _ in range(40):
    g.text_through()
    g.w(10)
check(not g.global_flag(GLOBALFLAG_BALLADE_QUIZ), 'une erreur : pas de bisou')

# Tout juste
g.warp(3, 0x9e, 0x57)
quiz(ANSWERS, 'z')
g.text_through(4)
check(g.wait_text(200), 'la blague de Tarkin, la tirade')
for _ in range(60):
    if g.global_flag(GLOBALFLAG_BALLADE_QUIZ) and g.m[TEXT_ACTIVE]:
        break
    g.press('a', 6)
    g.w(10)
g.w(40)
shoot('z_bisou', '*Smack!*')
check(g.global_flag(GLOBALFLAG_BALLADE_QUIZ), 'tout juste : le bisou (GLOBALFLAG_BALLADE_QUIZ)')
check(g.m[HEALTH] == g.m[MAX_HEALTH], 'les cœurs pleins')
for _ in range(10):
    g.text_through()
    g.w(10)
g.warp(3, 0x9e, 0x57)
g.w(200)
check(not g.m[TEXT_ACTIVE], 'le quiz ne revient plus')

sheet(shots, os.path.join(OUT, 'quiz.png'), cols=3)
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
