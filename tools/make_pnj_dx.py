"""Les habitants de nos îles avec des dessins de PNJ de Link's Awakening DX (Denis : « utilise aussi
des designs de PNJ de DX », à la place des villageois d'Ages mal choisis : le meunier qui était
l'ado, le roi, le père...). Des gens de Mabe qui marchent dans les quatre directions, pris dans le
désassemblage de DX (LADX-Disassembly-main/src/gfx/characters ; une bande = 8 sprites de 8 x 16,
deux voisins font un 16 x 16 ; pixels 0 transparent, 85/170/255 = couleurs 1/2/3 : noir, la couleur
de l'habit, la peau, comme les palettes 0-3 des sprites d'Ages).

Chaque feuille (oracles-disasm/gfx_compressible/ages/spr_ballade_pnj_N.png, 128 x 16) porte deux
habitants rangés comme les villageois d'Ages (tuiles $00 et $10) : de face, de dos, de profil vers
la gauche, de profil en marchant. Les animations des habitants (interactione8Animations) retournent
ces images pour l'autre pas et l'autre côté. Aperçu : art/pnj_dx.png. Sans le désassemblage de DX,
les feuilles déjà dans le dépôt servent.

Usage : python tools/make_pnj_dx.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DX = os.path.join(ROOT, 'LADX-Disassembly-main', 'src', 'gfx', 'characters')
OUT = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages', 'spr_ballade_pnj_%d.png')
PREVIEW = os.path.join(ROOT, 'art', 'pnj_dx.png')
WALK = ((0, 1), (2, 3), (4, 5), (6, 7))       # face, dos, profil, profil un pas
NO_BACK = ((0, 1), (0, 1), (4, 5), (6, 7))    # pas de dos dans DX : de face
# (nom, fichier, bande, poses) ; deux par feuille, la feuille n est le header $eb + n
SHEETS = [
    [('le garçon', 'oam_npc_3.cgb.png', 39, WALK),
     ('la fille', 'oam_npc_3.cgb.png', 19, WALK)],
    [('le petit', 'oam_npc_1.cgb.png', 8, WALK),
     ('le gamin à la mèche', 'oam_npc_1.cgb.png', 3, WALK)],
    [('la dame', 'oam_npc_2.cgb.png', 7, WALK),
     ("l'homme", 'oam_npc_1.cgb.png', 4, WALK)],
    [("l'homme aux cheveux fous", 'oam_npc_1.cgb.png', 6, WALK),
     ("l'homme aux cheveux en pétard", 'oam_npc_2.cgb.png', 27, NO_BACK)],
]
# Les palettes 0-3 des sprites d'Ages (standardSpritePaletteData), pour l'aperçu
PREVIEW_PALS = [[(255, 255, 255), (0, 0, 0), main, (248, 208, 136)]
                for main in ((16, 168, 64), (24, 128, 248), (248, 8, 40), (248, 120, 8))]


def main():
    if not os.path.isdir(DX):
        print('pnj DX : pas de désassemblage de DX, les feuilles spr_ballade_pnj_* restent telles quelles')
        return
    files = {}
    prev = Image.new('RGB', (128, 16 * len(SHEETS)), (255, 255, 255))
    for s, people in enumerate(SHEETS):
        out = Image.new('P', (128, 16), 0)
        out.putpalette([0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255] + [0] * 756)
        for p, (name, fname, band, poses) in enumerate(people):
            im = files.setdefault(fname, Image.open(os.path.join(DX, fname)).convert('L'))
            for n, pair in enumerate(poses):
                for half, sprite in enumerate(pair):
                    for x in range(8):
                        for y in range(16):
                            v = im.getpixel((sprite * 8 + x, band * 16 + y))
                            out.putpixel((p * 64 + n * 16 + half * 8 + x, y), {0: 0, 85: 1, 170: 2, 255: 3}[v])
        out.save(OUT % (s + 1))
        for x in range(128):
            for y in range(16):
                prev.putpixel((x, s * 16 + y), PREVIEW_PALS[(s * 2 + x // 64) % 4][out.getpixel((x, y))])
        print('pnj DX : %s -> %s' % (', '.join(p[0] for p in people), os.path.relpath(OUT % (s + 1), ROOT)))
    prev.resize((512, 64 * len(SHEETS)), Image.NEAREST).save(PREVIEW)


if __name__ == '__main__':
    main()
