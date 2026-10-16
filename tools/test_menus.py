"""Test des menus graphiques dans les deux langues (PyBoy) : captures de chaque écran.

Usage : python tools/test_menus.py DOSSIER_CAPTURES [fr|en] [ROM]
Nouvelle partie, choix de la langue sur la plage, menu de sauvegarde (Start+Select),
« sauver et quitter », écran du choix du fichier (langue retenue), Game Over.
"""
import os
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
LANG = sys.argv[2] if len(sys.argv) > 2 else 'fr'
ROM = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'out', 'gulls_of_life.gbc')
os.makedirs(OUT, exist_ok=True)
pb = PyBoy(ROM, window='null', sound_emulated=True)
pb.set_emulation_speed(0)
n = [0]


def w(k):
    pb.tick(k, True)


def press(b, k=4):
    pb.button(b, 3)
    w(k)


def shot(name):
    pb.screen.image.save(os.path.join(OUT, '%02d_%s.png' % (n[0], name)))
    n[0] += 1


def start_select():
    pb.button_press('start')
    pb.button_press('select')
    w(6)
    pb.button_release('start')
    pb.button_release('select')


# Choix du fichier, nouvelle partie, nom (film passé, écran titre, Start)
w(900)
press('start', 150)
press('start', 60)
shot('fichiers')
press('a', 60)
shot('nouvelle_partie')
press('a', 80)
shot('nom')
for c in 'a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
# La question de la langue
for i in range(300):
    w(4)
    if pb.memory[0xcba0]:
        break
w(120)
if LANG == 'en':
    press('down', 20)
press('a', 60)
print('langue', pb.memory[0xc62a])
# La scène de la plage
for i in range(300):
    w(30)
    if pb.memory[0xcba0]:
        press('a', 4)
    elif pb.memory[0xcc8a] == 0 and i > 20:
        break
w(60)
shot('en_jeu')
# Menu de sauvegarde
start_select()
w(120)
shot('sauvegarde')
press('down', 20)
shot('sauvegarde_bas')
press('down', 20)
press('a', 60)
# « Sauver et quitter » relance le jeu : logo, film, écran titre, puis le choix du fichier
w(900)
press('start', 150)
press('start', 60)
shot('fichiers_retour')
press('a', 60)
shot('fichier_choisi')
for i in range(20):
    press('a', 30)
w(200)
shot('reprise')
# Inventaire (trois pages, Select pour changer)
press('start', 90)
for i in range(3):
    shot('inventaire%d' % i)
    press('select', 60)
press('start', 90)
# Game Over
pb.memory[0xc6aa] = 0
w(500)
shot('game_over')
press('down', 20)
shot('game_over_bas')
pb.stop(save=False)
