"""Les marques de l'après-jeu sur la carte (Select) : ce qui reste à trouver (Denis : « post game,
faudrait que tu affiches comme on a fait pour la ROM combined, les quarts de cœur qui sont sur la
map, les anneaux aussi ; et les coffres manquants »). code/ages/balladeMapMarks.s les dessine.

Une marque par sorte (0 quart de cœur, 1 anneau, 2 coffre) et par case de la carte (la salle du
groupe 1 : dehors, ou l'entrée du donjon / de la grotte / de la maison) : elle s'affiche si l'une
des choses de cette case reste à prendre (l'octet qui le dit et son masque : pris, le bit est mis).
- Les quarts de cœur et les anneaux : la liste ci-dessous (voir CLAUDE.md, « Les cœurs »).
- Les coffres : ceux de l'écran de progression (code/ages/balladeTrackerChests.s,
  tools/make_tracker.py ; le drapeau $20 de leur salle) ; dans un donjon (data/ages/dungeonData.s,
  dungeonLayouts.s), la case de son entrée.

Usage : python tools/make_map_marks.py   (build.sh, après make_tracker.py)
Sortie : oracles-disasm/code/ages/balladeMapMarksTable.s
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
FLAGS = {0: 'wGroup0RoomFlags', 1: 'wGroup1RoomFlags', 2: 'wGroup0RoomFlags', 3: 'wGroup1RoomFlags',
         4: 'wGroup4RoomFlags', 5: 'wGroup5RoomFlags'}

# Les quarts de cœur : la case, l'octet, le masque, ce que c'est
HEARTS = [
    (0xac, 'wGroup1RoomFlags+$ac', '$80', 'le Creuse-Rubis, en Difficile'),
    (0xac, 'wGroup5RoomFlags+$ea', '$80', 'le Mamono, en Dur sans être blessé'),
    (0xac, 'wGroup5RoomFlags+$ee', '$80', 'le 2e Labyrinthe des Lynels'),
    (0x74, 'wGroup1RoomFlags+$74', '$40', 'la carte au trésor'),
    (0x62, 'wGroup0RoomFlags+$62', '$20', 'la grand-mère de Noé (le Songe)'),
    (0xb3, 'wGroup1RoomFlags+$b3', '$02', 'la chanteuse du Grand Sommeil'),
    (0x17, 'wGroup5RoomFlags+$d2', '$20', 'la Fosse de Bulle, à 3 m'),
    (0x20, 'wGroup1RoomFlags+$20', '$20', 'Tic et Tac (les cinq cachettes)'),
    (0x12, 'wBoughtShopItems2', '$40', 'la boutique de Pépin'),
    (0x89, 'wGroup1RoomFlags+$89', '$40', 'enterré au milieu du motif'),
]
# Les anneaux : la case, l'anneau, ce que c'est
RINGS = [
    (0xac, 'POWER_RING_L1', 'le 1er Labyrinthe des Lynels'),
    (0x20, 'ARMOR_RING_L1', 'Tic et Tac'),
    (0xac, 'CHARGE_RING', 'le Mamono'),
    (0xac, 'BALLADE_CAMELEON_RING', 'le Creuse-Rubis'),
    (0x5c, 'BALLADE_EASTER_RING', 'Marine, sur son île'),
]
# L'entrée de chaque donjon (son numéro -> la case dehors)
ENTRANCES = {0x01: 0x7b, 0x02: 0x21, 0x03: 0x36, 0x04: 0x0a, 0x05: 0x42, 0x06: 0x48, 0x07: 0xb2,
             0x08: 0xc9, 0x09: 0x17, 0x0b: 0x60}
# Les grottes et les salles hors donjon (groupe, salle) -> la case dehors
OTHERS = {(5, 0xb0): 0x32, (5, 0xb1): 0x27, (5, 0xb2): 0x28}


def dungeon_rooms():
    """(groupe, salle) -> le numéro du donjon, d'après dungeonData.s et dungeonLayouts.s"""
    data = open(os.path.join(DISASM, 'data', 'ages', 'dungeonData.s'), encoding='utf-8').read()
    layouts = open(os.path.join(DISASM, 'data', 'ages', 'dungeonLayouts.s'), encoding='utf-8').read()
    rooms = {}
    for m in re.finditer(r'^dungeonData([0-9a-f]{2}):\n(?:\s*;.*\n)*\s+m_DungeonData >wGroup(\d)RoomFlags, \$\w\w, (\w+)',
                         data, re.M):
        index, group, label = int(m.group(1), 16), int(m.group(2)), m.group(3)
        start = re.search(r'^%s:' % label, layouts, re.M)
        if not start:
            continue
        body = layouts[start.end():]
        nxt = re.search(r'^\w+:', body, re.M)
        body = body[:nxt.start()] if nxt else body
        for b in re.findall(r'\$([0-9a-f]{2})', body):
            rooms.setdefault((group, int(b, 16)), index)
    return rooms


def chests():
    text = open(os.path.join(DISASM, 'code', 'ages', 'balladeTrackerChests.s'), encoding='utf-8').read()
    return [(int(g, 16), int(r, 16)) for g, r in re.findall(r'\.db \$(\w\w), \$(\w\w)', text)]


def main():
    rooms = dungeon_rooms()
    marks = {}      # (sorte, case) -> [(octet, masque, ce que c'est)]
    for square, addr, mask, what in HEARTS:
        marks.setdefault((0, square), []).append((addr, mask, what))
    for square, ring, what in RINGS:
        marks.setdefault((1, square), []).append(('wRingsObtained+(%s>>3)' % ring, '1<<(%s&7)' % ring, what))
    missing = []
    for g, r in chests():
        if g in (0, 1):
            square = r
        elif (g, r) in OTHERS:
            square = OTHERS[(g, r)]
        elif (g, r) in rooms and rooms[(g, r)] in ENTRANCES:
            square = ENTRANCES[rooms[(g, r)]]
        else:
            missing.append('%d:%02x' % (g, r))
            continue
        marks.setdefault((2, square), []).append(('%s+$%02x' % (FLAGS[g], r), '$20', 'le coffre de %d:%02x' % (g, r)))
    assert not missing, 'coffres sans case sur la carte : %s' % missing
    lines = ["; Généré par tools/make_map_marks.py (ne pas modifier à la main) : les marques de l'après-jeu",
             '; sur la carte (code/ages/balladeMapMarks.s). Une marque : la sorte (0 quart de cœur, 1 anneau,',
             "; 2 coffre), la case, le nombre de choses ; puis chaque chose : l'octet qui dit si elle est prise",
             "; (.dw), son masque (.db). La marque s'affiche si l'une d'elles reste à prendre.", 'mapMarks:']
    for (kind, square), items in sorted(marks.items()):
        lines.append('\t.db $%02x, $%02x, %d' % (kind, square, len(items)))
        for addr, mask, what in items:
            lines.append('\t.dw %s' % addr)
            lines.append('\t.db %s ; %s' % (mask, what))
    lines.append('\t.db $ff')
    path = os.path.join(DISASM, 'code', 'ages', 'balladeMapMarksTable.s')
    open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print("carte de l'après-jeu : %d marques (%d quarts, %d anneaux, %d coffres) -> %s" % (
        len(marks), len(HEARTS), len(RINGS), len(chests()), os.path.relpath(path, ROOT)))


if __name__ == '__main__':
    main()
