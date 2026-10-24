"""Tarkin (le père de Marine) avec son vrai sprite de Link's Awakening DX (Denis : « il aurait fallu
récupérer son sprite ! le voir de dos »). Les poses de Tarin dans le désassemblage de DX
(LADX-Disassembly-main/src/gfx/characters ; une bande = 8 sprites de 8 x 16, deux voisins font un
16 x 16 ; pixels 0 transparent, 85/170/255 = couleurs 1/2/3 de la palette, comme nos feuilles) :
- oam_npc_2.cgb.png, bande 44 : de face, de dos, de profil, de profil en marchant
  (TarinBeekeeperSpriteVariants, src/code/entities/07_tarinbeekeeper.asm) ;
- oam_npc_1.cgb.png, bande 14 : de face (dedans), endormi (le torse), de profil (dedans).
Sa palette de DX (PAL2 : noir, rouge, peau) : paletteDataTarkin (PALH_TARKIN).

Écrit oracles-disasm/gfx_compressible/ages/spr_ballade_tarkin.png (8 images de 16 x 16 ; l'image n
prend les tuiles 4n à 4n+3) et l'aperçu art/tarkin.png. Sans le désassemblage de DX, les fichiers
déjà dans le dépôt servent.

Usage : python tools/make_tarkin.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DX = os.path.join(ROOT, 'LADX-Disassembly-main', 'src', 'gfx', 'characters')
OUT = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages', 'spr_ballade_tarkin.png')
PREVIEW = os.path.join(ROOT, 'art', 'tarkin.png')
# (fichier, bande, sprite de gauche) ; le sprite de droite est le suivant
POSES = [
    ('oam_npc_2.cgb.png', 44, 0),   # 0. de face
    ('oam_npc_2.cgb.png', 44, 2),   # 1. de dos
    ('oam_npc_2.cgb.png', 44, 4),   # 2. de profil (vers la gauche)
    ('oam_npc_2.cgb.png', 44, 6),   # 3. de profil, un pas
    ('oam_npc_1.cgb.png', 14, 0),   # 4. de face (dedans)
    ('oam_npc_1.cgb.png', 14, 2),   # 5. endormi (le torse)
    ('oam_npc_1.cgb.png', 14, 4),   # 6. de profil (dedans)
]
# PAL2 de DX (noir, rouge, peau), pour l'aperçu
PREVIEW_PAL = [(255, 255, 255), (0, 0, 0), (248, 8, 40), (248, 184, 136)]


def main():
    if not os.path.isdir(DX):
        print('tarkin : pas de désassemblage de DX, spr_ballade_tarkin.png reste tel quel')
        return
    sheets = {}
    out = Image.new('P', (128, 16), 0)
    out.putpalette([0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255] + [0] * 756)
    for n, (name, band, sprite) in enumerate(POSES):
        im = sheets.setdefault(name, Image.open(os.path.join(DX, name)).convert('L'))
        for x in range(16):
            for y in range(16):
                v = im.getpixel((sprite * 8 + x, band * 16 + y))
                out.putpixel((n * 16 + x, y), {0: 0, 85: 1, 170: 2, 255: 3}[v])
    out.save(OUT)
    prev = Image.new('RGB', (128, 16))
    for x in range(128):
        for y in range(16):
            prev.putpixel((x, y), PREVIEW_PAL[out.getpixel((x, y))])
    prev.resize((512, 64), Image.NEAREST).save(PREVIEW)
    print('tarkin : %d poses -> %s' % (len(POSES), os.path.relpath(OUT, ROOT)))


if __name__ == '__main__':
    main()
