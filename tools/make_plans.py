"""Dessine les plans des îles 2 à 8 et la forme de leurs donjons, d'après story/iles.md.

Lit les blocs ```ile N``` (une ligne = une rangée d'écrans, cases séparées par « | », « ~ » = la
mer, « * » = le ciel) et ```donjon N``` (E entrée, B boss, M mini-boss, C objet, K clé du boss, # salle, . rien,
1-5 = étages de la tour). Le titre de l'île vient du titre « ## N. Nom · Rêve » du fichier.

Sortie : docs/iles_plans.png

Usage : python tools/make_plans.py
"""
import os
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = 'C:/Windows/Fonts/'
INK = (40, 28, 20)
PAPER = (244, 232, 200)
SEA = (86, 150, 205)
BG = (46, 104, 170)
LAND = [(170, 200, 130), (200, 180, 140), (225, 205, 150)]
ROOM = {'E': ((96, 160, 90), 'entrée'), 'B': ((200, 60, 60), 'boss'), 'M': ((230, 140, 60), 'mini-boss'),
        'C': ((240, 200, 70), 'objet'), 'K': ((150, 120, 200), 'clé du boss'), '#': ((214, 196, 156), 'salle')}


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


TITLE = font('georgiab.ttf', 40)
NAME = font('georgiab.ttf', 22)
SUB = font('georgiai.ttf', 16)
CELL = font('georgia.ttf', 13)
SMALL = font('georgiai.ttf', 14)
ROOMF = font('georgiab.ttf', 13)


def read():
    text = open(os.path.join(ROOT, 'story', 'iles.md'), encoding='utf-8').read()
    titles = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
              for m in re.finditer(r'^## (\d)\. ([^·\n]+)·\s*(.+)$', text, re.M)}
    blocks = {}
    for m in re.finditer(r'^```(ile|donjon) (\d)\n(.*?)^```', text, re.M | re.S):
        rows = [[c.strip() for c in line.split('|')] for line in m.group(3).strip('\n').split('\n')]
        blocks[(m.group(1), int(m.group(2)))] = rows
    return titles, blocks


def wrap(d, txt, width):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if d.textlength(test, font=CELL) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_island(d, rows, x0, y0, w, h):
    n_rows, n_cols = len(rows), max(len(r) for r in rows)
    cw, ch = w / n_cols, h / n_rows
    for r, row in enumerate(rows):
        for c, name in enumerate(row):
            box = [x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw, y0 + (r + 1) * ch]
            if name == '~':
                d.rectangle(box, fill=SEA, outline=(70, 130, 190))
                for k in range(3):
                    xx = box[0] + cw * (0.25 + 0.25 * k)
                    d.arc([xx - 6, box[1] + ch / 2 - 3, xx + 6, box[1] + ch / 2 + 5], 200, 340, fill=(240, 248, 255), width=2)
                continue
            if name == '*':
                d.rectangle(box, fill=(196, 226, 248), outline=(170, 205, 235))
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                for ox, oy, rr in ((-12, 4, 9), (0, -2, 12), (13, 4, 9)):
                    d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=(255, 255, 255))
                continue
            fill = LAND[(r + c) % 3]
            if 'Lagune' in name or 'Lac ' in name:
                fill = (120, 200, 200)
            if 'Bateau' in name:
                fill = (205, 170, 120)
            if any(k in name for k in ('Donjon', 'Coffre', 'Récif Murmurant', 'Forge', 'Cathédrale', 'Nid (', 'Palais', 'Tour', 'Grotte de la Boîte')):
                fill = (235, 190, 110)
            d.rectangle(box, fill=fill, outline=INK, width=2)
            lines = wrap(d, name, cw - 10)
            ty = box[1] + (ch - 15 * len(lines)) / 2
            for line in lines:
                d.text(((box[0] + box[2]) / 2, ty), line, font=CELL, fill=INK, anchor='ma')
                ty += 15


def draw_dungeon(d, rows, x0, y0, size):
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            if k == '.':
                continue
            box = [x0 + c * size, y0 + r * size, x0 + (c + 1) * size - 3, y0 + (r + 1) * size - 3]
            if k.isdigit():
                d.rectangle(box, fill=(110, 90, 140), outline=INK, width=2)
                d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), k, font=ROOMF, fill=(255, 250, 230), anchor='mm')
                continue
            d.rectangle(box, fill=ROOM.get(k, ROOM['#'])[0], outline=INK, width=2)
            if k != '#':
                d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), k, font=ROOMF, fill=INK, anchor='mm')


def main():
    titles, blocks = read()
    islands = sorted(n for kind, n in blocks if kind == 'ile')
    pw, ph, gap = 820, 330, 24
    cols = 2
    rows_n = (len(islands) + cols) // cols
    W = 40 + cols * pw + (cols - 1) * gap + 40
    H = 120 + rows_n * (ph + gap) + 20
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Les îles de l'archipel : les plans", font=TITLE, fill=(255, 250, 230))
    d.text((42, 74), 'Chaque case = un écran (10 x 8 tuiles) ; à droite, la forme du donjon sur la carte',
           font=SUB, fill=(225, 235, 250))
    for i, n in enumerate(islands):
        px, py = 40 + (i % cols) * (pw + gap), 120 + (i // cols) * (ph + gap)
        d.rounded_rectangle([px, py, px + pw, py + ph], 16, fill=PAPER, outline=INK, width=3)
        name, dream = titles.get(n, ('Île %d' % n, ''))
        d.text((px + 18, py + 12), '%d. %s' % (n, name), font=NAME, fill=INK)
        d.text((px + 18, py + 40), dream, font=SUB, fill=INK)
        isl = blocks[('ile', n)]
        draw_island(d, isl, px + 18, py + 70, 540, ph - 90)
        dj = blocks.get(('donjon', n))
        if dj:
            size = min(34, int(min((pw - 600) / max(len(r) for r in dj), (ph - 110) / len(dj))))
            dw = size * max(len(r) for r in dj)
            dx = px + 580 + (pw - 600 - dw) / 2
            d.text((px + 580 + (pw - 600) / 2, py + 70), 'Le donjon', font=SMALL, fill=INK, anchor='ma')
            draw_dungeon(d, dj, dx, py + 96, size)
    # Légende des salles, dans la dernière case libre
    if len(islands) % cols:
        px, py = 40 + (pw + gap), 120 + (len(islands) // cols) * (ph + gap)
        d.rounded_rectangle([px, py, px + pw, py + ph], 16, fill=PAPER, outline=INK, width=3)
        d.text((px + 18, py + 14), 'Légende des donjons', font=NAME, fill=INK)
        for j, (k, (color, label)) in enumerate(ROOM.items()):
            yy = py + 56 + j * 32
            d.rectangle([px + 24, yy, px + 52, yy + 28], fill=color, outline=INK, width=2)
            if k != '#':
                d.text((px + 38, yy + 14), k, font=ROOMF, fill=INK, anchor='mm')
            d.text((px + 66, yy + 5), label, font=CELL, fill=INK)
        yy = py + 56 + len(ROOM) * 32
        d.rectangle([px + 24, yy, px + 52, yy + 28], fill=(110, 90, 140), outline=INK, width=2)
        d.text((px + 38, yy + 14), '1', font=ROOMF, fill=(255, 250, 230), anchor='mm')
        d.text((px + 66, yy + 5), 'étage de la Tour Sans-Nuit (la musique gagne un instrument par étage)', font=CELL, fill=INK)
        d.text((px + 24, py + ph - 26), 'Source : story/iles.md (tools/make_plans.py)', font=SMALL, fill=INK)
    dst = os.path.join(ROOT, 'docs', 'iles_plans.png')
    im.save(dst)
    print('->', os.path.relpath(dst, ROOT))


main()
