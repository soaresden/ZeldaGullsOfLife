"""La table « salle -> île » des groupes 0 et 1 (le Songe a les mêmes numéros que le Réel).

Les îles sont voisines sur la carte d'Ages : par un bord, à pied ou à la nage, on passait d'une île
à l'autre (Denis : de Hameau-Grelot 1:32 vers le bas, on finissait dans la montagne de l'île des
Échos, 1:42). code/ages/balladeIslands.s refuse un changement d'écran vers une salle d'une autre
île (ou d'aucune) ; les îles ne se rejoignent qu'en Bateau-Rondin ou par les Arbres-Passages.

Une île = un plan story/salles/ile_*.txt (ses lignes « salle XX »), numérotées à partir de 1 ;
0 = aucune île.

Usage : python tools/make_islands.py   (build.sh)
Sortie : oracles-disasm/code/ages/balladeIslandTable.s (et les bords : edgeBlocked, edgeWater)
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
    blocked, water = edge_masks()
    for label, masks, what in (('edgeBlocked', blocked, 'un mur (collision $0f : Link y resterait coincé)'),
                               ('edgeWater', water, "l'eau profonde (collision $10 : sans les Palmes, il s'y noierait)")):
        lines += ['', "; Les bords : pour chaque groupe (0, 1), salle et direction (haut, droite, bas, gauche), les",
                  "; places du bord (colonne 0-9 ou rangée 0-7, un bit chacune) où l'on arriverait dans",
                  '; ' + what, label + ':']
        for g in range(2):
            for r in range(256):
                lines.append('\t.dw ' + ' '.join('$%04x' % m for m in masks[g][r]) + ' ; %d:%02x' % (g, r))
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    n = sum(bin(m).count('1') for g in blocked for r in g for m in r)
    print('îles : %d salles ; bords : %d places vers un mur -> %s' % (
        sum(1 for t in table if t), n, os.path.relpath(OUT, ROOT)))


def edge_masks():
    """Les places des bords qui mènent dans un mur ou dans l'eau de la salle d'à côté (Denis, 29/10 :
    « si on passe un écran en faisant une direction, on peut finir dans l'eau ou bloqué » : à la
    nage, il entrait dans le mur du bas de 1:99). Lues dans les vraies salles compilées
    (rooms/ages/small : le Songe, groupe 0, et le Réel, groupe 1, dans les fichiers 00 et 02)."""
    disasm = os.path.join(ROOT, 'oracles-disasm')
    collisions = {}

    def tiles(g, r):
        p = os.path.join(disasm, 'rooms', 'ages', 'small', 'room%02x%02x.bin' % ((0, 2)[g], r))
        data = open(p, 'rb').read() if os.path.exists(p) else b''
        return data if len(data) == 80 else None

    def collision(g, r):
        decor = tilesets[g][r] & 0x7f
        if decor not in collisions:
            collisions[decor] = open(os.path.join(disasm, 'tileset_layouts_expanded', 'ages',
                                                  'tilesetCollisions%02x.bin' % decor), 'rb').read()
        return collisions[decor]

    tilesets = [open(os.path.join(disasm, 'rooms', 'ages', 'group%dTilesets.bin' % g), 'rb').read() for g in range(2)]
    # (salle d'à côté, les places de son bord à elle)
    sides = [(-16, [(7, j) for j in range(10)]), (1, [(i, 0) for i in range(8)]),
             (16, [(0, j) for j in range(10)]), (-1, [(i, 9) for i in range(8)])]
    blocked = [[[0] * 4 for _ in range(256)] for _ in range(2)]
    water = [[[0] * 4 for _ in range(256)] for _ in range(2)]
    for g in range(2):
        for r in range(256):
            for d, (move, places) in enumerate(sides):
                n = r + move
                if not 0 <= n < 256 or (move == 1 and r % 16 == 15) or (move == -1 and r % 16 == 0):
                    continue
                t = tiles(g, n)
                if t is None:
                    continue
                c = collision(g, n)
                for p, (y, x) in enumerate(places):
                    v = c[t[y * 10 + x]]
                    if v == 0x0f:
                        blocked[g][r][d] |= 1 << p
                    elif v == 0x10:
                        water[g][r][d] |= 1 << p
    return blocked, water


if __name__ == '__main__':
    main()
