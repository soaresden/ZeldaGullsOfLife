"""La table « salle -> île » des groupes 0 et 1 (le Songe a les mêmes numéros que le Réel).

Les îles sont voisines sur la carte d'Ages : par un bord, à pied ou à la nage, on passait d'une île
à l'autre (Denis : de Hameau-Grelot 1:32 vers le bas, on finissait dans la montagne de l'île des
Échos, 1:42). code/ages/balladeIslands.s refuse un changement d'écran vers une salle d'une autre
île (ou d'aucune) ; les îles ne se rejoignent qu'en Bateau-Rondin ou par les Arbres-Passages.

Une île = un plan story/salles/ile_*.txt (ses lignes « salle XX »), numérotées à partir de 1 ;
0 = aucune île.

Usage : python tools/make_islands.py   (build.sh)
Sortie : oracles-disasm/code/ages/balladeIslandTable.s
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'oracles-disasm', 'code', 'ages', 'balladeIslandTable.s')


def main():
    table = [0] * 256
    names = []
    for n, path in enumerate(sorted(glob.glob(os.path.join(ROOT, 'story', 'salles', 'ile_*.txt'))), 1):
        names.append('%d %s' % (n, os.path.basename(path)[4:-4]))
        for line in open(path, encoding='utf-8'):
            m = re.match(r'salle ([0-9a-f]{2})\b', line)
            if m:
                room = int(m.group(1), 16)
                assert table[room] in (0, n), 'salle %02x dans deux îles' % room
                table[room] = n
    lines = ['; Généré par tools/make_islands.py (ne pas modifier à la main) : l\'île de chaque salle des',
             '; groupes 0 et 1 (0 = aucune) : ' + ', '.join(names) + '.',
             'islandOfRoom:']
    for row in range(16):
        lines.append('\t.db ' + ' '.join('$%02x' % table[row * 16 + x] for x in range(16)) +
                     ' ; $%x0' % row)
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('îles : %d salles -> %s' % (sum(1 for t in table if t), os.path.relpath(OUT, ROOT)))


if __name__ == '__main__':
    main()
