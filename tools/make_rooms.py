"""Construit les salles de nos îles à partir des plans texte de story/salles/*.txt.

Un plan décrit une salle du Réel (groupe 1, le « passé » d'Ages) :

    salle 9a decor 10        # salle 1:9a, décor (tileset) $10 = village du passé
    3b 3b 0c 0c 3b ...       # 8 lignes de 10 briques (numéros en hexadécimal)

Voir out/catalog/decor_XX.png (tools/catalog.py) pour les numéros des briques. Le script
écrit rooms/ages/small/roomGGSS.bin (GG = groupe de disposition du décor) et le décor de la
salle dans group1Tilesets.bin. Il retire aussi les objets d'Ages de ces salles (ennemis,
personnages) en les remplaçant par ceux de story/salles/objets.txt.

Usage : python tools/make_rooms.py
"""
import glob
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
TILESETS = os.path.join(DISASM, 'rooms', 'ages', 'group1Tilesets.bin')


def layout_group(tileset):
    lines = open(os.path.join(DISASM, 'data', 'ages', 'tilesets.s'), encoding='utf-8').read().split('\n')
    i = lines.index('\t; 0x%02x' % tileset)
    return int(lines[i + 5].replace('.db', '').split(',')[1].strip()[1:], 16)


def read_plans():
    plans = []
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
                cur = {'room': int(words[1], 16), 'tileset': int(words[3], 16), 'rows': [],
                       'where': '%s:%d' % (os.path.basename(path), n)}
                plans.append(cur)
                continue
            assert len(words) == 10, '%s:%d : 10 briques par ligne' % (path, n)
            cur['rows'].append([int(w, 16) for w in words])
    for p in plans:
        assert len(p['rows']) == 8, '%s : 8 lignes par salle' % p['where']
    return plans


def read_objects():
    objects, cur = {}, None
    for line in open(os.path.join(ROOT, 'story', 'salles', 'objets.txt'), encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith('salle'):
            cur = int(line.split()[1], 16)
            objects[cur] = []
        else:
            objects[cur].append(line.rstrip('\n'))
    return objects


def write_objects(rooms):
    """Nos salles ont leurs propres objets : on retire leurs étiquettes des données d'Ages
    (souvent partagées entre plusieurs salles) et on les redéfinit à la fin du fichier."""
    path = 'objects/ages/mainData.s'
    base = subprocess.run(['git', 'show', 'upstream/hack-base:' + path], cwd=DISASM,
                          capture_output=True, check=True).stdout.decode('utf-8')
    labels = {'group1Map%02xObjectData:' % r for r in rooms}
    lines = [l for l in base.split('\n') if l.strip() not in labels]
    objects = read_objects()
    out = ['', '; ' + '=' * 98,
           '; BALLADE: objets des salles de nos îles (générés par tools/make_rooms.py depuis',
           '; story/salles/objets.txt)', '; ' + '=' * 98]
    for r in sorted(rooms):
        out.append('group1Map%02xObjectData:' % r)
        out += objects.get(r, [])
        out.append('\tobj_End')
    with open(os.path.join(DISASM, path), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines).rstrip('\n') + '\n' + '\n'.join(out) + '\n')


def main():
    tilesets = bytearray(open(TILESETS, 'rb').read())
    write_objects([p['room'] for p in read_plans()])
    for p in read_plans():
        room, ts = p['room'], p['tileset']
        tilesets[room] = (tilesets[room] & 0x80) | ts
        path = os.path.join(DISASM, 'rooms', 'ages', 'small', 'room%02x%02x.bin' % (layout_group(ts), room))
        with open(path, 'wb') as f:
            f.write(bytes(b for row in p['rows'] for b in row))
    open(TILESETS, 'wb').write(tilesets)
    print('%d salles construites' % len(read_plans()))


main()
