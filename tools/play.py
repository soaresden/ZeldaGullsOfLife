"""Joue la ROM dans PyBoy sans fenêtre et prend des captures d'écran.

Usage : python tools/play.py SCENARIO DOSSIER_CAPTURES
SCENARIO : suite de commandes séparées par des espaces :
  wN       avancer de N images        a b start select up down left right : appuyer
  sNOM     capture NOM.png            pN : appuyer A toutes les 20 images pendant N images
Le son doit être émulé (sinon le jeu boucle après le logo Capcom).
"""
import os
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    script, outdir = sys.argv[1].split(), sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
    pb.set_emulation_speed(0)
    for cmd in script:
        if cmd[0] == 'w':
            pb.tick(int(cmd[1:]), True)
        elif cmd[0] == 's' and cmd not in ('start', 'select'):
            pb.screen.image.save(os.path.join(outdir, cmd[1:] + '.png'))
        elif cmd[0] == 'p' and cmd[1:].isdigit():
            for _ in range(int(cmd[1:]) // 20):
                pb.button('a', 3)
                pb.tick(20, True)
        else:
            pb.button(cmd, 3)
            pb.tick(4, True)
    pb.stop(save=False)


main()
