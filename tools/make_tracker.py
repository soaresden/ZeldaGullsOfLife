"""La liste des coffres du jeu pour l'écran de progression (balladeObjects.progressTracker).

Les coffres de la Ballade sont les entrées commentées de data/ages/chestData.s (les autres sont des
restes d'Ages, dans des salles où l'on ne va pas), sauf les coffres d'Ages modifiés pour retirer
leurs anneaux au hasard (« plus d'anneaux au hasard »). Un coffre ouvert met le drapeau $20 de sa
salle : on écrit (groupe, salle) pour chacun, sans doublon. Les trésors flottants de la Fosse (vue de
côté) sont des lignes en commentaire marquées « trésor flottant » : comptées, mais sans coffre (le
jeu poserait un coffre ouvert à leur place).

Usage : python tools/make_tracker.py   (build.sh)
Sortie : oracles-disasm/code/ages/balladeTrackerChests.s
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')


def chests():
    group, out = None, []
    for line in open(os.path.join(DISASM, 'data', 'ages', 'chestData.s'), encoding='utf-8'):
        m = re.match(r'chestGroup(\d)Data:', line)
        if m:
            group = int(m.group(1))
            continue
        m = re.match(r'\s+(;?)m_ChestData \$(\w\w), \$(\w\w), (\w+)\s*(;.*)?$', line)
        if not m or not m.group(5) or "plus d'anneaux au hasard" in m.group(5):
            continue
        if m.group(1) and 'trésor flottant' not in m.group(5):
            continue
        key = (group, int(m.group(3), 16))
        if key not in out:
            out.append(key)
    return out


def main():
    rooms = chests()
    lines = ['; Généré par tools/make_tracker.py (ne pas modifier à la main) : les coffres de la Ballade',
             '; (groupe, salle), pour l\'écran de progression (balladeObjects.progressTracker).',
             '.define BALLADE_TRACKER_CHESTS %d' % len(rooms), '', 'progressTrackerChests:']
    lines += ['\t.db $%02x, $%02x' % r for r in rooms]
    path = os.path.join(DISASM, 'code', 'ages', 'balladeTrackerChests.s')
    open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('progression : %d coffres -> %s' % (len(rooms), os.path.relpath(path, ROOT)))


if __name__ == '__main__':
    main()
