"""Teste chaque niveau du jeu en passant par le menu de test caché (tools/debug_menu.py).

Pour chaque île construite et chaque moment (Plage, Ville, Donjon, M-boss, Boss, Fin) : depuis le
démarrage, HAUT tenu 5 s à l'écran titre, nouvelle partie, le menu, puis on vérifie l'arrivée
(la salle, les objets, les drapeaux) et on joue un petit bout (le boss parle, la fin commence...).
Vérifie aussi que le menu reste caché : sans le code, la partie commence sur la plage, et HAUT
tenu 2 secondes ne suffit pas.

Usage : python tools/test_niveaux.py DOSSIER_CAPTURES [ÎLE...]   (ROM=chemin pour une autre ROM)
Écrit DOSSIER/NOM.png pour chaque niveau et DOSSIER/planche.png (toutes les captures).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import (BOSS_KEYS, ESSENCES, INV_A, INV_B, ISLANDS, LANGUAGE, MAX_HEALTH, STEPS,
                        Game)

OUT = sys.argv[1]
ONLY = [int(a) for a in sys.argv[2:]]
os.makedirs(OUT, exist_ok=True)

TREASURE_SWORD, TREASURE_HARP = 0x05, 0x11
ENDING = 0xcdf4           # wBalladeEnding : le tour du village (fin du chapitre 1)
RHYTHM_TEST = 0xcded      # wBalladeRhythmTest
INTERACTIONS = range(0xd2, 0xe0)
ENEMIES = range(0xd0, 0xe0)
INTERAC_MARINE = 0xe7

errors, shots = [], []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)


def interaction_present(g, ident):
    return any(g.m[h * 256 + 0x41] == ident and g.m[h * 256 + 0x40] for h in INTERACTIONS)


def enemy_ids(g):
    return {g.m[h * 256 + 0x81] for h in ENEMIES if g.m[h * 256 + 0x80]}


def shoot(g, name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def run(island, step, lang='fr'):
    """Une partie neuve jusqu'au niveau ; renvoie le jeu (à arrêter)."""
    g = Game()
    g.level(island, step, lang)
    print('--- %d. %s / %s : salle %d:%02x' % ((island, ISLANDS[island - 1], step) + g.where()))
    return g


def equipped(g, treasure):
    return treasure in (g.m[INV_A], g.m[INV_B])


# ---------------------------------------------------------------------------------------------
# 1. L'île de la Brume
# ---------------------------------------------------------------------------------------------
def brume():
    g = run(1, 'Plage')
    check(g.where() == (1, 0xaa), '1.Plage : la plage du réveil (1:aa)')
    check(not g.has(TREASURE_SWORD), '1.Plage : pas encore d\'épée')
    g.w(240)
    check(interaction_present(g, INTERAC_MARINE), '1.Plage : Marine arrive')
    shoot(g, '1_plage', '1. Plage')
    g.stop()

    g = run(1, 'Ville')
    check(g.where() == (1, 0x9b), '1.Ville : la place de Port-Veille (1:9b)')
    check(g.has(TREASURE_SWORD) and equipped(g, TREASURE_SWORD), '1.Ville : l\'épée, sur A ou B')
    check(g.m[LANGUAGE] == 1, '1.Ville : le jeu est en français')
    g.hold('select', 60)    # Select maintenu : Marine parle depuis la tunique
    check(g.wait_text(60), '1.Ville : Select maintenu -> Marine parle')
    g.w(60)
    shoot(g, '1_ville', '1. Ville')
    g.wait_no_text(900) or [g.press('a', 30) for _ in range(6)]
    g.wait_no_text(300)
    g.press('select', 40)   # Select court : la carte
    shoot(g, '1_carte', '1. La carte (Select)')
    g.stop()

    g = run(1, 'Donjon')
    check(g.where() == (4, 0x24), '1.Donjon : le hall du Phare (4:24)')
    g.w(120)
    shoot(g, '1_donjon', '1. Donjon')
    g.stop()

    g = run(1, 'M-boss')
    check(g.where() == (4, 0x18), '1.M-boss : la salle du Ghini géant (4:18)')
    check(g.has(TREASURE_HARP), '1.M-boss : la Lanterne')
    g.w(120)
    shoot(g, '1_mboss', '1. M-boss')
    check(len(enemy_ids(g)) > 0, '1.M-boss : le mini-boss est là')
    g.stop()

    g = run(1, 'Boss')
    check(g.where() == (4, 0x12), '1.Boss : la galerie, sous la porte de Jack (4:12)')
    check(g.m[BOSS_KEYS] & 0x02, '1.Boss : la clé du boss')
    for _ in range(40):
        g.hold('up', 16)
        if g.where() == (4, 0x13):
            break
    g.hold('up', 30)
    check(g.where() == (4, 0x13), '1.Boss : Link entre chez Jack (4:13)')
    check(g.wait_text(400), '1.Boss : Jack menace')
    g.w(90)
    shoot(g, '1_boss', '1. Boss : Jack')
    g.stop()

    g = run(1, 'Fin')
    check(g.m[ESSENCES] & 0x01, '1.Fin : l\'essence du Phare')
    check(g.m[MAX_HEALTH] == 16, '1.Fin : 4 cœurs (un réceptacle de plus)')
    check(g.wait_text(300), '1.Fin : Marine parle sur le cap')
    shoot(g, '1_fin_cap', '1. Fin : sur le cap')
    for _ in range(60):
        if g.m[ENDING]:
            break
        g.press('a', 20)
    check(g.m[ENDING], '1.Fin : le tour du village commence')
    g.settled()
    g.w(120)
    shoot(g, '1_fin', '1. Fin : le tour du village')
    g.stop()


# ---------------------------------------------------------------------------------------------
# 2. Hameau-Grelot
# ---------------------------------------------------------------------------------------------
GLOBALFLAG_BALLADE_ISLAND3 = 0x52
ENDING = 0xcdf4


def grelot():
    g = run(2, 'Plage')
    check(g.where() == (1, 0x31), '2.Plage : la jetée de Hameau-Grelot (1:31)')
    check(g.global_flag(0x50) and g.global_flag(0x51), '2.Plage : le Bateau-Rondin, Hameau-Grelot repéré')
    check(g.has(0x12), '2.Plage : le Carnet des Rêves')
    check(g.wait_text(200), '2.Plage : Marine parle en arrivant')
    g.w(40)
    shoot(g, '2_plage', '2. Plage : la jetée')
    g.stop()

    g = run(2, 'Ville')
    check(g.where() == (1, 0x11), '2.Ville : la place du Grelot (1:11)')
    g.w(60)
    shoot(g, '2_ville', '2. Ville : la place')
    g.stop()

    g = run(2, 'Donjon')
    check(g.where() == (4, 0x39), "2.Donjon : l'entrée du Coffre à Jouets (4:39)")
    check(g.has(0x03), '2.Donjon : les bombes')
    check(g.wait_text(200), '2.Donjon : le nom du donjon')
    g.w(40)
    shoot(g, '2_donjon', '2. Donjon : le Coffre à Jouets')
    g.stop()

    g = run(2, 'M-boss')
    check(g.where() == (4, 0x2d), '2.M-boss : devant le volet du Soldat de Plomb (4:2d)')
    check(g.has(0x06), '2.M-boss : le boomerang')
    check(g.go('left', (4, 0x2c)), '2.M-boss : le volet est ouvert')
    g.hold('left', 20)
    check(g.wait_text(300), '2.M-boss : le Soldat de Plomb parle')
    g.w(40)
    shoot(g, '2_mboss', '2. M-boss : le Soldat de Plomb')
    g.stop()

    g = run(2, 'Boss')
    check(g.where() == (4, 0x2e), "2.Boss : l'antichambre (4:2e)")
    check(g.m[BOSS_KEYS] & 0x04, '2.Boss : la clé du boss')
    g.stand(5, 4, y_first=True)
    g.stand(1, 4)
    check(g.go('up', (4, 0x2b)), "2.Boss : l'échelle mène à Pantin-Sans-Fil")
    check(g.wait_text(200), '2.Boss : Pantin-Sans-Fil menace')
    g.w(40)
    shoot(g, '2_boss', '2. Boss : Pantin-Sans-Fil')
    g.stop()

    g = run(2, 'Fin')
    check(g.where() == (3, 0x21), '2.Fin : chez Lila (3:21)')
    check(g.m[ESSENCES] & 0x02, "2.Fin : l'essence du Coffre à Jouets")
    check(g.wait_text(300), '2.Fin : Lila se réveille')
    g.w(40)
    shoot(g, '2_fin_lila', '2. Fin : Lila se réveille')
    for _ in range(80):
        g.press('a', 20)
        if g.where() == (1, 0x11):
            break
    g.settled()
    check(g.where() == (1, 0x11), '2.Fin : la place du Grelot')
    check(g.wait_text(300), '2.Fin : les enfants jouent')
    g.w(40)
    shoot(g, '2_fin_place', '2. Fin : les enfants jouent')
    for _ in range(80):
        if g.global_flag(GLOBALFLAG_BALLADE_ISLAND3) and g.m[ENDING] == 0:
            break
        g.press('a', 20)
    check(g.global_flag(GLOBALFLAG_BALLADE_ISLAND3), '2.Fin : Marine repère la Lagune des Serments')
    g.w(60)
    shoot(g, '2_fin_suite', '2. Fin : à suivre')
    g.text_through()
    g.stop()


# ---------------------------------------------------------------------------------------------
# 8. L'Œil de l'Insomnis : 5F de la Tour Sans-Nuit, devant l'Insomnis (le boss en rythme)
# ---------------------------------------------------------------------------------------------
def oeil():
    g = run(8, 'Boss')
    check(g.where() == (5, 0xcb), '8.Boss : 5F de la Tour Sans-Nuit (5:cb)')
    g.route((5, 7), (5, 1))
    check(g.go('left', (5, 0xcc)), "8.Boss : l'Insomnis (5:cc)")
    g.w(200)
    check(g.m[0xcdec] >= 1, '8.Boss : le boss en rythme commence')   # wBalladeRhythmStage
    shoot(g, '8_boss', "8. Boss : l'Insomnis")
    g.stop()


# ---------------------------------------------------------------------------------------------
# Le menu lui-même
# ---------------------------------------------------------------------------------------------
def menu():
    # Sans le code : la plage, comme un joueur normal
    g = Game()
    g.title()
    g.new_game()
    check(g.where() == (1, 0xaa), 'sans le code : la partie commence sur la plage')
    g.stop()

    # HAUT tenu 2 secondes seulement : rien
    g = Game()
    g.title()
    g.secret(120)
    g.new_game()
    check(g.where() == (1, 0xaa), 'HAUT tenu 2 s : rien (la plage)')
    g.stop()

    # Une île pas encore construite : un son d'erreur, on revient au choix de l'île
    g = Game()
    g.title()
    g.secret()
    g.new_game()
    check(g.where() == (3, 0x9f), 'avec le code : la salle du menu (3:9f)')
    g.choose(0, 2)
    g.choose(7, 8)                     # île 8
    g.choose(3, 4)                     # Fin : pas encore construite (l'épilogue)
    check(g.wait_text(120), 'île pas construite : le menu redemande l\'île')
    g.w(90)
    shoot(g, '0_menu', 'Le menu (île ?)')
    g.choose(0, 8)                     # île 1
    g.island_step('Ville')
    g.arrive()
    check(g.where() == (1, 0x9b), 'puis île 1, Ville : la place (1:9b)')
    g.stop()


def sheet():
    """Planche de toutes les captures, avec leur nom."""
    if not shots:
        return
    cols = 4
    rows = (len(shots) + cols - 1) // cols
    W, H = 160 * 2, 144 * 2 + 18
    img = Image.new('RGB', (W * cols, H * rows), (16, 16, 32))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14)
    except OSError:
        f = ImageFont.load_default()
    for k, (path, label) in enumerate(shots):
        x, y = (k % cols) * W, (k // cols) * H
        img.paste(Image.open(path).resize((320, 288), Image.NEAREST), (x, y + 18))
        d.text((x + 4, y + 1), label, font=f, fill='white')
    img.save(os.path.join(OUT, 'planche.png'))
    print('->', os.path.join(OUT, 'planche.png'))


TESTS = {0: menu, 1: brume, 2: grelot, 8: oeil}
for k, t in TESTS.items():
    if not ONLY or k in ONLY:
        t()
sheet()
print('\n%d erreur(s)' % len(errors) if errors else '\nTout est bon.')
for e in errors:
    print('  -', e)
sys.exit(1 if errors else 0)
