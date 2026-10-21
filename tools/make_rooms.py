"""Construit les salles de nos îles à partir des plans texte de story/salles/*.txt.

Un plan décrit une salle :

    salle 9a decor 10        # salle 1:9a (le Réel), décor (tileset) $10 = village du passé
    salle 0:8a decor 7d      # salle 0:8a (le Songe), décor $7d = village du Songe
    3b 3b 0c 0c 3b ...       # 8 lignes de 10 briques (numéros en hexadécimal)

    decor 2:9e 7f copie 3:9e # changer le décor d'une salle et reprendre la disposition d'une autre

Le Songe (groupe 0, le « présent » d'Ages) reprend automatiquement chaque salle du Réel avec le
décor bleuté correspondant (voir SONGE ci-dessous et tools/make_songe.py), sauf si un plan
« salle 0:XX » la redessine. Chaque salle du Songe (groupes 0 et 2) reçoit l'ondulation de
l'écran (INTERAC_BALLADE_DREAM_FX), sauf les intérieurs : leurs longs scripts tournent dans
la mémoire que la vague réécrit.

Voir out/catalog/decor_XX.png (tools/catalog.py) pour les numéros des briques. Le script
écrit rooms/ages/small/roomGGSS.bin (GG dépend du groupe : voir LAYOUT_GROUP) et les décors dans
groupNTilesets.bin. Il retire aussi les objets d'Ages de nos salles et les remplace par ceux de
story/salles/objets.txt.

Usage : python tools/make_rooms.py
"""
import glob
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
SONGE = {0x10: 0x7d, 0x18: 0x7e, 0x7b: 0x7c, 0x1e: 0x06, 0x13: 0x07, 0x1a: 0x08}   # décor du Réel -> décor du Songe
DREAM_FX = '\tobj_Interaction INTERAC_BALLADE_DREAM_FX $00'


def tilesets_path(group):
    return os.path.join(DISASM, 'rooms', 'ages', 'group%dTilesets.bin' % group)


# Dans hack-base, le fichier de disposition dépend du groupe de la salle, pas du décor
# (code/bank0.s, @getLayoutGroup) : rooms/ages/small/roomGGSS.bin avec GG = LAYOUT_GROUP[groupe]
# Groupes 4 et 5 (donjons) : grandes salles de 15 x 11 briques, rangées sur 16 colonnes.
LAYOUT_GROUP = {0: 0x00, 1: 0x02, 2: 0x01, 3: 0x03, 4: 0x04, 5: 0x05}
LARGE = (4, 5)


def room_size(group):
    return (15, 11) if group in LARGE else (10, 8)


def room_file(group, room):
    return os.path.join(DISASM, 'rooms', 'ages', 'large' if group in LARGE else 'small',
                        'room%02x%02x.bin' % (LAYOUT_GROUP[group], room))


def parse_room(name):
    """« 9a » -> (1, 0x9a) ; « 0:8a » -> (0, 0x8a)."""
    if ':' in name:
        g, r = name.split(':')
        return int(g), int(r, 16)
    return 1, int(name, 16)


def read_plans():
    plans, decors = [], {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'story', 'salles', '*.txt'))):
        if os.path.basename(path) == 'objets.txt':
            continue
        cur = None
        for n, line in enumerate(open(path, encoding='utf-8'), 1):
            line = line.split('#')[0].strip()
            if not line:
                continue
            words = line.split()
            if words[0] == 'salle':
                cur = {'key': parse_room(words[1]), 'tileset': int(words[3], 16), 'rows': [],
                       'flags': words[4:], 'where': '%s:%d' % (os.path.basename(path), n)}
                plans.append(cur)
                continue
            if words[0] == 'decor':
                # « decor 2:9e 7f copie 3:9e » : même disposition qu'une autre salle
                copy = parse_room(words[4]) if len(words) > 4 and words[3] == 'copie' else None
                decors[parse_room(words[1])] = (int(words[2], 16), copy)
                continue
            w, h = room_size(cur['key'][0])
            assert len(words) == w, '%s:%d : %d briques par ligne' % (path, n, w)
            cur['rows'].append([int(w, 16) for w in words])
    for p in plans:
        h = room_size(p['key'][0])[1]
        assert len(p['rows']) == h, '%s : %d lignes par salle' % (p['where'], h)
    # Le Songe : copie de chaque salle du Réel qui n'est pas redessinée
    drawn = {p['key'] for p in plans}
    for p in list(plans):
        g, r = p['key']
        if g == 1 and (0, r) not in drawn:
            plans.append({'key': (0, r), 'tileset': SONGE[p['tileset']], 'rows': p['rows'],
                          'where': p['where'] + ' (Songe)'})
    return plans, decors


# Donjons : un octet par salle dans rooms/ages/groupNDungeonProperties.bin
# (constants/common/dungeonRoomProperties.s) : les ouvertures pour la mini-carte, coffre, boss, noir
WALLS = {0xb0, 0xb1, 0xb2, 0xb3, 0xb8, 0xb9, 0xba, 0xbb}
DARK, BOSS, CHEST = 0x80, 0x40, 0x20


def dungeon_property(p):
    rows = p['rows']
    middle = [rows[0][7], rows[5][14], rows[10][7], rows[5][0]]   # haut, droite, bas, gauche
    prop = sum(1 << i for i, t in enumerate(middle) if t not in WALLS)
    if any(0xf1 in row for row in rows):
        prop |= CHEST
    if 'boss' in p['flags']:
        prop |= BOSS
    if 'sombre' in p['flags']:
        prop |= DARK
    return prop


def read_objects():
    objects, cur = {}, None
    for line in open(os.path.join(ROOT, 'story', 'salles', 'objets.txt'), encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith('salle'):
            cur = parse_room(line.split()[1])
            # Une salle écrite deux fois : la 2e liste remplacerait la 1re sans rien dire
            assert cur not in objects, 'objets.txt : la salle %s apparaît deux fois' % line.split()[1]
            objects[cur] = []
        else:
            objects[cur].append(line.rstrip('\n'))
    return objects


def write_objects(keys):
    """Nos salles ont leurs propres objets : on retire leurs étiquettes des données d'Ages
    (souvent partagées entre plusieurs salles) et on les redéfinit à la fin du fichier."""
    path = 'objects/ages/mainData.s'
    base = subprocess.run(['git', 'show', 'upstream/hack-base:' + path], cwd=DISASM,
                          capture_output=True, check=True).stdout.decode('utf-8')
    objects = read_objects()
    keys = sorted(set(keys) | set(objects))
    labels = {'group%dMap%02xObjectData:' % k for k in keys}
    lines = [l for l in base.split('\n') if l.strip() not in labels]
    out = ['', '; ' + '=' * 98,
           '; BALLADE: objets des salles de nos îles (générés par tools/make_rooms.py depuis',
           '; story/salles/objets.txt)', '; ' + '=' * 98]
    for k in keys:
        out.append('group%dMap%02xObjectData:' % k)
        out += objects.get(k, [])
        if k[0] == 0 and not os.environ.get('BALLADE_SANS_ONDULATION'):
            out.append(DREAM_FX)
        out.append('\tobj_End')
    with open(os.path.join(DISASM, path), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines).rstrip('\n') + '\n' + '\n'.join(out) + '\n')


def main():
    plans, decors = read_plans()
    tilesets = {g: bytearray(open(tilesets_path(g), 'rb').read()) for g in range(6)}
    write_objects([p['key'] for p in plans] + list(decors))
    for p in plans:
        (g, r), ts = p['key'], p['tileset']
        tilesets[g][r] = (tilesets[g][r] & 0x80) | ts
        # Grandes salles : 16e colonne de remplissage à 0, comme les salles d'Ages
        pad = [0] if g in LARGE else []
        with open(room_file(g, r), 'wb') as f:
            f.write(bytes(b for row in p['rows'] for b in row + pad))
    for (g, r), (ts, copy) in decors.items():
        tilesets[g][r] = (tilesets[g][r] & 0x80) | ts
        if copy:
            with open(room_file(g, r), 'wb') as f:
                f.write(open(room_file(*copy), 'rb').read())
    for g, t in tilesets.items():
        open(tilesets_path(g), 'wb').write(t)
    for g in LARGE:
        path = os.path.join(DISASM, 'rooms', 'ages', 'group%dDungeonProperties.bin' % g)
        props = bytearray(open(path, 'rb').read())
        for p in plans:
            if p['key'][0] == g:
                props[p['key'][1]] = dungeon_property(p)
        open(path, 'wb').write(props)
    print('%d salles construites (Réel et Songe)' % len(plans))


main()
