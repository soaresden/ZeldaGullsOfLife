"""Vérifie les bords entre les salles de l'île : on ne doit jamais pouvoir entrer dans un mur.

Le piège : un buisson coupable à l'épée (ou une case libre) au bord d'une salle, en face d'un
rocher ou d'un arbre dans la salle voisine. Link coupe le buisson, passe, et se retrouve coincé
dans le rocher. Avec --fix, ces cases deviennent un buisson épais qu'on ne coupe pas (décor de
la plage) ; le script recommence jusqu'à ce qu'il n'y ait plus rien à corriger.

Usage : python tools/check_edges.py [--fix] [PLAN]   (par défaut : story/salles/ile_brume.txt ;
ex. story/salles/ile_grelot.txt)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = ([os.path.abspath(a) for a in sys.argv[1:] if not a.startswith('--')]
        or [os.path.join(ROOT, 'story', 'salles', 'ile_brume.txt')])[0]
COLLISIONS = os.path.join(ROOT, 'oracles-disasm', 'tileset_layouts_expanded', 'ages',
                          'tilesetCollisions%02x.bin')
SWORD_CUTTABLE = {0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca}   # buissons (breakableTiles.s, modes 1 à 6)
SOLID = {0x18: '4e', 0x7b: 'f7'}   # par décor : brique pleine, qu'on ne coupe pas


def load():
    rooms, cur = {}, None
    lines = open(PLAN, encoding='utf-8').read().split('\n')
    for n, line in enumerate(lines):
        m = re.match(r'salle (\w+) decor (\w+)', line)
        if m:
            cur = int(m.group(1), 16)
            rooms[cur] = {'decor': int(m.group(2), 16), 'rows': [], 'lines': []}
        elif cur is not None and re.match(r'^[0-9a-f]{2}( [0-9a-f]{2}){9}$', line.strip()):
            rooms[cur]['rows'].append(line.split())
            rooms[cur]['lines'].append(n)
    return lines, rooms


def edges(r):
    """(voisine, cases de mon bord, cases du bord d'en face)"""
    side = [(i, 9) for i in range(8)], [(i, 0) for i in range(8)]
    top = [(0, j) for j in range(10)], [(7, j) for j in range(10)]
    return ((r + 1, side[0], side[1]), (r - 1, side[1], side[0]),
            (r + 16, top[1], top[0]), (r - 16, top[0], top[1]))


def problems(rooms):
    col = {r: open(COLLISIONS % i['decor'], 'rb').read() for r, i in rooms.items()}
    out = []
    for r, info in sorted(rooms.items()):
        for nb, mine, theirs in edges(r):
            if nb not in rooms:
                continue
            for (a, b), (c, d) in zip(mine, theirs):
                t, u = int(info['rows'][a][b], 16), int(rooms[nb]['rows'][c][d], 16)
                passable = col[r][t] == 0 or t in SWORD_CUTTABLE
                # l'eau ($10) n'est pas un piège : Link s'y noie et revient au bord
                blocked = col[nb][u] not in (0, 0x10) and u not in SWORD_CUTTABLE
                if passable and blocked:
                    out.append((r, a, b, nb))
    return out


def main():
    fix = '--fix' in sys.argv
    lines, rooms = load()
    seen = set()
    while True:
        found = [p for p in problems(rooms) if p[:3] not in seen]
        if not found:
            break
        for r, a, b, nb in found:
            seen.add((r, a, b))
            tile = rooms[r]['rows'][a][b]
            print('salle %02x ligne %d colonne %d : %s mène dans un mur de la salle %02x' % (r, a, b, tile, nb))
            if fix and rooms[r]['decor'] in SOLID:
                rooms[r]['rows'][a][b] = SOLID[rooms[r]['decor']]
        if not fix:
            break
    if fix:
        for info in rooms.values():
            for n, row in zip(info['lines'], info['rows']):
                lines[n] = ' '.join(row)
        open(PLAN, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    left = problems(rooms)
    print('ok' if not left else '%d case(s) à revoir' % len(left))
    sys.exit(1 if left else 0)


main()
