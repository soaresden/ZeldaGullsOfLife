"""Le miroir de Marine (l'Easter Egg) devient la porte tournante de Link's Awakening DX (Denis : « les
portes qui vont que dans un sens de DX, pour le miroir de Marine »). Avec la bague, Link le pousse :
le panneau tourne avec lui et il passe de l'autre côté (balladeObjects.easterMirror).

Les images viennent de la planche de Link de DX (LADX-Disassembly-main/src/gfx/characters/
oam_link_2.cgb.png ; les poses LINK_ANIMATION_STATE_REVOLVING_DOOR_1-5, tuiles $ea-$fa de
LinkAnimationStateTable, src/code/bank20.asm), mises aux trois couleurs du miroir (la palette 6 des
sprites, PALH_TERRIER : k noir, r gris acier, w la vitre cyan). Link, dans la vitre, devient un
reflet ; derrière le panneau de biais, le passage secret est noir. La face du miroir (la vitre et
son reflet, à la place de la flèche de DX) est dessinée à la main.

Écrit art/miroir.txt (si le désassemblage de DX est là ; sinon le fichier déjà dans le dépôt sert).

Usage : python tools/make_miroir.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DX = os.path.join(ROOT, 'LADX-Disassembly-main', 'src', 'gfx', 'characters', 'oam_link_2.cgb.png')
OUT = os.path.join(ROOT, 'art', 'miroir.txt')

# La face, à la main : le cadre d'acier, la vitre cyan, un reflet en biais
FACE = """\
kkkkkkkkkkkkkkkk
krrrrrrrrrrrrrrk
krkkkkkkkkkkkkrk
krkwwwwwwwwwwkrk
krkwrwwwwwwwwkrk
krkwwrwwwwwwwkrk
krkwwwrwwwwwwkrk
krkwwwwwwwwrwkrk
krkwwwwwwwrwwkrk
krkwwwwwwrwwwkrk
krkwwwwwwwwwwkrk
krkwwwwwwwwwwkrk
krkkkkkkkkkkkkrk
krrrrrrrrrrrrrrk
kkkkkkkkkkkkkkkk
.kkkkkkkkkkkkkk.""".split('\n')

# Les poses de DX : (tuile gauche, tuile droite, la droite en miroir), et ce que devient le blanc
POSES = [
    ('Link pousse le panneau (un reflet dans la vitre)', 0xea, 0xec, False, 'w'),
    ('Link aplati, le panneau tourne avec lui', 0xee, 0xf0, False, 'w'),
    ('le panneau de biais : derrière, le passage noir', 0xf2, 0xf4, False, 'k'),
    ("le panneau de biais, de l'autre côté", 0xf8, 0xfa, False, 'k'),
]


def dx_frames():
    from PIL import Image
    im = Image.open(DX).convert('L')

    def tile(t):
        r, c = divmod(t // 2, 8)
        return im.crop((c * 8, r * 16, c * 8 + 8, r * 16 + 16))

    out = []
    for label, a, b, flip, white in POSES:
        f = Image.new('L', (16, 16))
        f.paste(tile(a), (0, 0))
        tb = tile(b)
        if flip:
            tb = tb.transpose(Image.FLIP_LEFT_RIGHT)
        f.paste(tb, (8, 0))
        m = {0: 'k', 85: 'r', 170: 'w', 255: white}
        out.append((label, [''.join(m[f.getpixel((x, y))] for x in range(16)) for y in range(16)]))
    return out


def main():
    if not os.path.exists(DX):
        print('miroir : pas de désassemblage de DX, art/miroir.txt reste tel quel')
        return
    frames = [('la face du miroir (au repos, et au milieu du tour)', FACE)] + dx_frames()
    lines = ['# Le miroir de Marine, la porte tournante de Link\'s Awakening DX (tools/make_miroir.py : les',
             '# poses de DX aux couleurs du miroir ; la face à la main). Une image 16 x 16 par pose ; l\'image',
             '# n prend les tuiles 4n à 4n+3 (spr_ballade_miroir.png). Palette 6 des sprites (PALH_TERRIER) :',
             '# . transparent  k noir  r gris acier  w la vitre cyan.']
    for n, (label, rows) in enumerate(frames):
        lines += ['#', '# %d. %s' % (n, label)] + rows
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('miroir : %d images -> art/miroir.txt' % len(frames))


if __name__ == '__main__':
    main()
