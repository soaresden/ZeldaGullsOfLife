"""Dessine la carte de l'archipel des Sans-Sommeil et le plan de l'île de la Brume.

Sortie : docs/carte_archipel.png

Usage : python tools/make_map.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = 'C:/Windows/Fonts/'
W, H = 1700, 960
SEA = (46, 104, 170)
SEA_LIGHT = (86, 150, 205)
SAND = (236, 214, 150)
INK = (40, 28, 20)
PAPER = (244, 232, 200)


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


TITLE = font('georgiab.ttf', 44)
NAME = font('georgiab.ttf', 21)
SMALL = font('georgiai.ttf', 16)
CELL = font('georgia.ttf', 15)
CELLB = font('georgiab.ttf', 15)

# Les îles : nom, sous-titre (rêve perdu / donjon), centre, rayon, couleur, icône
ISLANDS = [
    ('1. Île de la Brume', 'Le Repos · Phare Éteint', (190, 640), 70, (96, 160, 90), 'phare'),
    ('2. Hameau-Grelot', 'Le Jeu · Coffre à Jouets', (420, 760), 55, (120, 176, 96), 'jouet'),
    ('3. Lagune des Serments', "L'Amour · Récif Murmurant", (700, 700), 62, (90, 170, 150), 'coquillage'),
    ('4. Mont-Braise', 'La Création · Forge Endormie', (860, 470), 66, (140, 110, 80), 'volcan'),
    ('5. Île des Échos', 'Le Souvenir · Cathédrale des Échos', (760, 230), 58, (110, 120, 140), 'cloche'),
    ('6. Nid des Vents', 'La Liberté · Spirale Céleste', (470, 165), 50, (150, 190, 120), 'nuage'),
    ('7. Île du Grand Sommeil', 'Le Réveil · Palais Givré', (180, 300), 64, (200, 220, 235), 'flocon'),
    ('8. Œil de l\'Insomnis', 'Tour Sans-Nuit', (480, 470), 40, (70, 60, 90), 'oeil'),
]


def blob(cx, cy, r, seed, n=48):
    rnd = random.Random(seed)
    phases = [rnd.uniform(0, math.tau) for _ in range(4)]
    pts = []
    for i in range(n):
        a = math.tau * i / n
        k = 1 + 0.16 * math.sin(3 * a + phases[0]) + 0.10 * math.sin(5 * a + phases[1]) \
            + 0.06 * math.sin(8 * a + phases[2])
        pts.append((cx + math.cos(a) * r * k, cy + math.sin(a) * r * k * 0.8))
    return pts


def scaled(pts, cx, cy, f):
    return [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in pts]


def draw_icon(d, kind, x, y):
    if kind == 'phare':
        d.polygon([(x - 8, y + 22), (x + 8, y + 22), (x + 5, y - 14), (x - 5, y - 14)], fill=(245, 245, 240), outline=INK)
        for yy in (y - 4, y + 10):
            d.rectangle([x - 7, yy, x + 7, yy + 4], fill=(200, 50, 50))
        d.rectangle([x - 7, y - 24, x + 7, y - 14], fill=(90, 90, 90), outline=INK)
        d.polygon([(x - 9, y - 24), (x + 9, y - 24), (x, y - 34)], fill=(200, 50, 50), outline=INK)
    elif kind == 'jouet':
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(230, 80, 80), outline=INK, width=2)
        d.line([x - 14, y, x + 14, y], fill=(250, 220, 90), width=4)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(250, 240, 200), outline=INK)
    elif kind == 'coquillage':
        for i in range(5):
            a = math.pi * (0.15 + 0.175 * i)
            d.line([x, y + 12, x - math.cos(a) * 18, y + 12 - math.sin(a) * 22], fill=INK, width=2)
        d.chord([x - 18, y - 12, x + 18, y + 26], 180, 360, outline=INK, width=2)
        d.ellipse([x - 4, y + 8, x + 4, y + 16], fill=(250, 200, 210), outline=INK)
    elif kind == 'volcan':
        d.polygon([(x - 26, y + 18), (x + 26, y + 18), (x + 8, y - 16), (x - 8, y - 16)], fill=(110, 80, 60), outline=INK)
        d.polygon([(x - 8, y - 16), (x + 8, y - 16), (x + 4, y - 4), (x - 4, y - 4)], fill=(240, 110, 40))
        for i, (dx, dy) in enumerate(((-6, -26), (4, -34), (-2, -44))):
            d.ellipse([x + dx - 6, y + dy - 6, x + dx + 6, y + dy + 6], fill=(150, 150, 150))
    elif kind == 'cloche':
        d.chord([x - 16, y - 18, x + 16, y + 14], 180, 360, fill=(210, 170, 70), outline=INK, width=2)
        d.rectangle([x - 16, y - 2, x + 16, y + 10], fill=(210, 170, 70), outline=INK)
        d.ellipse([x - 4, y + 8, x + 4, y + 16], fill=INK)
    elif kind == 'nuage':
        for dx, dy, r in ((-12, 0, 11), (0, -8, 13), (13, 0, 11), (0, 4, 12)):
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(255, 255, 255))
    elif kind == 'flocon':
        for i in range(3):
            a = math.pi * i / 3
            dx, dy = math.cos(a) * 18, math.sin(a) * 18
            d.line([x - dx, y - dy, x + dx, y + dy], fill=(60, 110, 170), width=3)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(60, 110, 170))
    elif kind == 'oeil':
        d.rectangle([x - 9, y - 30, x + 9, y + 16], fill=(50, 40, 70), outline=(20, 10, 30))
        d.ellipse([x - 9, y - 26, x + 9, y - 14], fill=(250, 220, 90))
        d.ellipse([x - 3, y - 23, x + 3, y - 17], fill=(160, 30, 60))


def draw_archipelago(img):
    d = ImageDraw.Draw(img)
    # Mer : vaguelettes
    rnd = random.Random(7)
    for _ in range(420):
        x, y = rnd.randrange(20, 1040), rnd.randrange(90, H - 30)
        d.arc([x, y, x + 14, y + 8], 200, 340, fill=SEA_LIGHT, width=2)
    # Routes du Bateau-Rondin (pointillés)
    order = [ISLANDS[i][2] for i in range(7)] + [ISLANDS[7][2]]
    for (x1, y1), (x2, y2) in zip(order, order[1:]):
        steps = int(math.hypot(x2 - x1, y2 - y1) / 14)
        for s in range(0, steps, 2):
            a, b = s / steps, (s + 1) / steps
            # léger arc
            off = math.sin(math.pi * a) * 30
            nx, ny = -(y2 - y1), (x2 - x1)
            ln = math.hypot(nx, ny) or 1
            p1 = (x1 + (x2 - x1) * a + nx / ln * off, y1 + (y2 - y1) * a + ny / ln * off)
            off2 = math.sin(math.pi * b) * 30
            p2 = (x1 + (x2 - x1) * b + nx / ln * off2, y1 + (y2 - y1) * b + ny / ln * off2)
            d.line([p1, p2], fill=(250, 240, 200), width=3)
    # Îles
    for i, (name, sub, (cx, cy), r, green, icon) in enumerate(ISLANDS):
        pts = blob(cx, cy, r, seed=i * 13 + 5)
        if icon == 'nuage':
            # île flottante : son ombre sur la mer
            d.ellipse([cx - r, cy + r * 0.9, cx + r, cy + r * 1.3], fill=(36, 84, 140))
        d.polygon(scaled(pts, cx, cy, 1.18), fill=SEA_LIGHT)
        d.polygon(pts, fill=SAND, outline=INK)
        d.polygon(scaled(pts, cx, cy, 0.78), fill=green)
        draw_icon(d, icon, cx, cy - 6)
        tw = d.textlength(name, font=NAME)
        ty = cy + r * 0.95 + 8
        d.text((cx - tw / 2 + 1, ty + 1), name, font=NAME, fill=(20, 40, 70))
        d.text((cx - tw / 2, ty), name, font=NAME, fill=(255, 250, 230))
        sw = d.textlength(sub, font=SMALL)
        d.text((cx - sw / 2, ty + 25), sub, font=SMALL, fill=(230, 240, 250))
    # Le Bateau-Rondin, au départ
    x, y = 300, 560
    d.rounded_rectangle([x - 22, y - 6, x + 22, y + 6], radius=6, fill=(150, 100, 50), outline=INK)
    d.text((x - 50, y + 10), 'Bateau-Rondin', font=SMALL, fill=(255, 250, 230))
    # Rose des vents
    cx, cy = 980, 800
    for a, l in ((0, 'N'), (90, 'E'), (180, 'S'), (270, 'O')):
        ra = math.radians(a - 90)
        d.polygon([(cx, cy), (cx + math.cos(ra - 0.25) * 18, cy + math.sin(ra - 0.25) * 18),
                   (cx + math.cos(ra) * 46, cy + math.sin(ra) * 46),
                   (cx + math.cos(ra + 0.25) * 18, cy + math.sin(ra + 0.25) * 18)], fill=PAPER, outline=INK)
        d.text((cx + math.cos(ra) * 60 - 6, cy + math.sin(ra) * 60 - 10), l, font=NAME, fill=PAPER)


# Plan de l'île de la Brume : 4 x 4 écrans (None = la mer)
BRUME = [
    [None, ('Falaises nord', 'chemin du phare'), ('Cap du Phare', 'entrée du donjon 1'), None],
    [('Bois de la Brume', 'brouillard ; passage par le Songe'), ('Sentier des falaises', 'ennemis, éboulis'),
     ('Rochers aux mouettes', 'cœur caché'), None],
    [('Le Ponton', 'Bateau-Rondin (après le phare)'), ('Port-Veille ouest', "l'auberge : dormir = Songe"),
     ('Port-Veille, la place', 'le puits, les insomniaques'), ('Plage est', 'les enfants qui ne jouent plus')],
    [None, ('Plage du réveil', 'Marine arrive (fait)'), ('Port de pêche', 'le vieux pêcheur'), None],
]
CELL_COLORS = {
    'Plage': (236, 214, 150), 'Port': (214, 190, 150), 'Falaises': (170, 150, 120), 'Cap': (170, 150, 120),
    'Bois': (110, 150, 100), 'Sentier': (150, 170, 110), 'Rochers': (180, 170, 150), 'Le Ponton': (190, 160, 120),
}


def draw_plan(img, x0, y0):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 - 20, y0 - 80, W - 30, H - 30], radius=16, fill=PAPER, outline=INK, width=3)
    d.text((x0, y0 - 66), "Île de la Brume : jusqu'au premier donjon", font=font('georgiab.ttf', 25), fill=INK)
    d.text((x0, y0 - 34), 'Chaque case = un écran du jeu (10 x 8 tuiles)', font=SMALL, fill=INK)
    cw, ch = 138, 116
    for r, row in enumerate(BRUME):
        for c, cell in enumerate(row):
            x, y = x0 + c * cw, y0 + r * ch
            if cell is None:
                d.rectangle([x, y, x + cw, y + ch], fill=SEA_LIGHT, outline=(60, 110, 160))
                for k in range(3):
                    d.arc([x + 30 + k * 30, y + 50, x + 50 + k * 30, y + 62], 200, 340, fill=PAPER, width=2)
                continue
            title, note = cell
            color = next((v for k, v in CELL_COLORS.items() if title.startswith(k)), (200, 190, 160))
            d.rectangle([x, y, x + cw, y + ch], fill=color, outline=INK, width=2)
            yy = y + 8
            for line in wrap(d, title, CELLB, cw - 14):
                d.text((x + 7, yy), line, font=CELLB, fill=INK)
                yy += 18
            yy += 4
            for line in wrap(d, note, CELL, cw - 14):
                d.text((x + 7, yy), line, font=CELL, fill=(60, 45, 30))
                yy += 17
    # Le parcours
    steps = ['1. Réveil sur la plage, Marine se glisse dans la tunique',
             "2. Port-Veille : personne ne dort ; l'aubergiste prête un lit",
             '3. Dans le Songe, Marine redevient humaine ; un pont de rêve',
             '   traverse la brume vers le sentier des falaises',
             '4. Le Phare Éteint : la Lanterne des Songes, le Veilleur Creux',
             '5. Premier couplet de la chanson de Marine ; le Ponton s\'ouvre']
    yy = y0 + 4 * ch + 22
    for s in steps:
        d.text((x0, yy), s, font=CELL, fill=INK)
        yy += 21


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    img = Image.new('RGB', (W, H), SEA)
    d = ImageDraw.Draw(img)
    draw_archipelago(img)
    d.text((40, 24), 'Archipel des Sans-Sommeil', font=TITLE, fill=(255, 250, 230))
    d.text((44, 76), 'The Legend of Zelda: Gulls of Life', font=font('georgiai.ttf', 20), fill=(230, 240, 250))
    draw_plan(img, 1090, 130)
    out = os.path.join(ROOT, 'docs', 'carte_archipel.png')
    img.save(out)
    print('->', os.path.relpath(out, ROOT))


main()
