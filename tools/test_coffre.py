"""Test du Coffre à Jouets (donjon 2), joué de bout en bout comme un joueur, depuis le menu de
test caché (2. Donjon) : les Zols et la petite clé 1, la porte à clé du hall, les soldats et le
Boomerang-Toupie, le grelot (Marine porte une bombe, le pont, la petite clé 2), le cristal touché
au boomerang (le volet du mini-boss), le Soldat de Plomb et la clé du boss, la porte du boss,
l'échelle de Pantin-Sans-Fil : Marine lui fait avaler des bombes ; l'essence dans l'antichambre.

Seule triche : les ennemis ordinaires et le mini-boss sont retirés, et Link garde sa vie pleine.

Usage : python tools/test_coffre.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import BOMBS, BOSS_KEYS, ESSENCES, HEALTH, MAX_HEALTH, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
ENEMY_HEAD_THWOMP = 0x79
INTERAC_ESSENCE = 0x7f
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(2))
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def protected(frames):
    """Pendant le combat : Link reste invincible (les boules de feu le feraient lâcher sa bombe)."""
    def cond():
        g.m[0xd02b] = 0x10         # w1Link.invincibilityCounter
        g.m[HEALTH] = g.m[MAX_HEALTH]
        return False
    g.wait_until(cond, frames)


def button(item):
    """Le bouton (A ou B) où est rangé un objet ; sinon le mettre sur A."""
    if g.m[0xc688] == item:
        return 'b'
    g.m[0xc689] = item
    return 'a'


g.level(2, 'Donjon')
check(g.where() == (4, 0x39), "l'entrée du Coffre à Jouets (4:39)")
check(g.wait_text(200), "le nom du donjon s'affiche")
g.w(30)
shoot('c01_entree', 'Niveau 2 : le Coffre à Jouets')
g.text_through()

# Les Zols (ouest) : battus, la petite clé tombe
g.stand(5, 3)
check(g.go('left', (4, 0x37)), 'à l\'ouest : les Zols (4:37)')
shoot('c02_zols', 'Les Zols')
g.clear_enemies()
g.w(120)
g.stand(5, 7)
g.w(60)
check(g.small_keys(2) == 1, 'la petite clé 1 (%d)' % g.small_keys(2))
g.stand(5, 12)
check(g.go('right', (4, 0x39)), 'retour à l\'entrée')

# La porte à clé du nord : le hall
g.stand(2, 7)
check(g.go('up', (4, 0x33)), 'la porte à clé mène au hall (4:33)')
shoot('c03_hall', 'Le hall')
g.clear_enemies()

# Ouest : les soldats (32), puis le Boomerang-Toupie (31)
g.stand(5, 7, y_first=True)
g.stand(5, 3)
check(g.go('left', (4, 0x32)), "à l'ouest du hall (4:32)")
g.clear_enemies()
g.stand(5, 3)
check(g.go('left', (4, 0x31)), 'la salle du boomerang (4:31)')
g.stand(5, 10)
g.w(60)
shoot('c04_soldats', 'Le volet se ferme : des soldats')
check(g.tile(0x5e) == 0x79, 'le volet de droite est fermé (%02x)' % g.tile(0x5e))
g.clear_enemies()
g.w(120)
check(g.tile(0x57) == 0xf1, 'le coffre apparaît')
check(g.open_chest(5, 7), 'coffre ouvert : le Boomerang-Toupie')
check(g.has(0x06), 'Link a le boomerang')
shoot('c05_boomerang', 'Le Boomerang-Toupie')
g.stand(5, 12)
check(g.go('right', (4, 0x32)), 'retour vers le hall')
g.stand(5, 12)
check(g.go('right', (4, 0x33)), 'le hall')

# Est : le grelot (34) ; Marine porte une bombe par-dessus le gouffre
g.stand(5, 12)
check(g.go('right', (4, 0x34)), "à l'est : le grelot (4:34)")
check(g.wait_text(120), 'Marine remarque le grelot')
g.text_through()
shoot('c06_grelot', 'Encore un grelot !')
full_life()
g.stand(5, 5)
g.face('right')
slot = button(0x03)
g.tap(slot, 30)               # une bombe au-dessus de la tête
g.press('select', 10)
g.w(150)
check(g.room_flags(4, 0x34) & 0x40, 'le grelot a sonné')
check(g.tile(0x56) == 0xa0 and g.tile(0x59) == 0xa0, 'le pont traverse le gouffre')
shoot('c07_pont', 'Le pont')
g.route((5, 11))              # par le pont
check(g.open_chest(2, 12), 'coffre ouvert : la petite clé 2')
check(g.small_keys(2) == 1, 'la petite clé 2')
g.stand(5, 11, y_first=True)
g.route((5, 3))
check(g.go('left', (4, 0x33)), 'retour au hall')

# La porte à clé du nord de 32 : le cristal (2d)
g.stand(5, 3)
check(g.go('left', (4, 0x32)), "à l'ouest du hall")
g.stand(5, 7, y_first=True)
g.stand(2, 7)
check(g.go('up', (4, 0x2d)), 'la porte à clé mène au cristal (4:2d)')
g.clear_enemies()
shoot('c08_cristal', 'Le cristal, au fond')
check(g.tile(0x50) == 0x7b, 'le volet du mini-boss est fermé (%02x)' % g.tile(0x50))
# Le boomerang vers le cristal (ligne 2, colonne 3), depuis l'autre bord du gouffre (colonne 7)
g.stand(5, 8, y_first=True)
g.stand(2, 8)
g.goto(None, 0x78)
g.face('left')
slot = button(0x06)
g.press(slot, 60)
g.w(60)
shoot('c09_boomerang', 'Le boomerang touche le cristal')
check(g.tile(0x50) != 0x7b, "le volet du mini-boss s'ouvre (%02x)" % g.tile(0x50))

# Le Soldat de Plomb (2c) : l'Armos Warrior ; battu, la clé du boss
g.stand(5, 7, y_first=True)
g.stand(5, 1)
check(g.go('left', (4, 0x2c)), 'le volet mène au Soldat de Plomb (4:2c)')
g.stand(5, 11)
check(g.wait_text(240), 'le Soldat de Plomb parle')
g.w(40)
shoot('c10_soldat', 'Le Soldat de Plomb')
g.text_through()
g.w(60)
check(len(g.enemies(0x73)) > 0, "l'Armos Warrior est là")
check(g.tile(0x5e) == 0x79, 'le volet se ferme derrière Link (%02x)' % g.tile(0x5e))
g.clear_enemies()
g.w(240)
check(g.tile(0x57) == 0xf1, 'le coffre apparaît')
check(g.open_chest(5, 7), 'coffre ouvert : la clé du boss')
check(g.m[BOSS_KEYS] & 0x04, 'la clé du boss')
check(g.tile(0x5e) != 0x79, 'le volet se rouvre')

# Retour au hall, la porte du boss, l'antichambre
g.stand(5, 13)
check(g.go('right', (4, 0x2d)), 'retour au cristal')
g.stand(5, 7)
g.stand(9, 7)
check(g.go('down', (4, 0x32)), 'retour à 32')
g.stand(5, 12)
check(g.go('right', (4, 0x33)), 'le hall')
g.stand(5, 7, y_first=True)
g.stand(1, 7)
check(g.go('up', (4, 0x2e)), "la porte du boss mène à l'antichambre (4:2e)")
shoot('c11_antichambre', "L'antichambre")

# L'échelle (colonne 4, en haut) : Pantin-Sans-Fil
g.stand(5, 4, y_first=True)
g.stand(1, 4)
check(g.go('up', (4, 0x2b)), "l'échelle monte chez Pantin-Sans-Fil (4:2b)")
check(g.wait_text(200), 'Pantin-Sans-Fil menace, Marine répond')
g.w(40)
shoot('c12_pantin', 'Pantin-Sans-Fil')
g.text_through()

# Le combat : sous lui, une bombe, Select : Marine monte la lui faire avaler (sa bouche est en
# y $50, x $78) ; on recommence jusqu'à ce qu'il tombe
slot = button(0x03)
g.m[BOMBS] = 0x20
won = False
GREEN, PURPLE = 0, 4           # Enemy.direction : 0 vert, 2 bleu, 4 violet, 6 rouge (il encaisse)


def thwomp(offset):
    bases = g.enemies(ENEMY_HEAD_THWOMP)
    return g.m[bases[0] + offset] if bases else None


def thwomp_face():
    return thwomp(0x08)       # Enemy.direction


def thwomp_state():
    return thwomp(0x04)       # Enemy.state : 9 = il tourne normalement


for attempt in range(12):
    full_life()
    g.goto(None, 0x78)
    if not g.enemies(ENEMY_HEAD_THWOMP):
        won = True
        break
    g.wait_until(lambda: thwomp_state() in (9, None), 1200)
    # Comme Marine le dit : la bombe prête, la lancer dès qu'il devient violet (il sera rouge à
    # son arrivée)
    g.wait_until(lambda: thwomp_face() in (GREEN, None), 900)
    g.m[0xd02b] = 0x40
    g.tap(slot, 4)             # une bombe au-dessus de la tête
    g.wait_until(lambda: thwomp_face() in (PURPLE, None), 900)
    g.m[0xd02b] = 0x40
    g.w(8)                     # le temps de réagir (un joueur : 8 à 15 images)
    g.press('select', 6)
    if attempt == 0:
        g.w(14)
        shoot('c13_marine_monte', 'Marine monte la bombe')
    health = thwomp(0x29)
    protected(40)
    g.wait_until(lambda: thwomp_state() != 9, 80)
    g.wait_until(lambda: thwomp_state() in (9, None) or thwomp(0x29) != health, 1500)
    print('      bombe %d : vie %s -> %s' % (attempt + 1, health, thwomp(0x29)))
    g.w(60)
won = won or not g.enemies(ENEMY_HEAD_THWOMP)
print('      essais :', attempt + 1)
check(won, 'Pantin-Sans-Fil est vaincu (des bombes avalées, portées par Marine)')
g.w(240)
shoot('c14_victoire', 'Vaincu : le cœur, les échelles')
check(g.room_flags(4, 0x2b) & 0x80, 'le drapeau de la salle du boss')

# Le cœur, puis l'échelle de gauche : l'antichambre, l'essence
g.goto(None, 0x78)
g.w(120)
g.text_through()
check(g.m[MAX_HEALTH] >= 20, 'le réceptacle de cœur (%d quarts)' % g.m[MAX_HEALTH])
g.goto(None, 0x48)
check(g.go('down', (4, 0x2e)), "l'échelle redescend à l'antichambre")
g.w(60)
check(any(g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == INTERAC_ESSENCE
          for h in range(0xd2, 0xe0)), "l'essence est apparue dans l'antichambre")
shoot('c15_essence', "L'essence (le 2e couplet)")
g.stand(8, 7, y_first=True)
g.hold('up', 40)               # toucher l'essence, au-dessus du piédestal
for _ in range(20):
    g.w(60)
    g.text_through(10)
    if g.where() != (4, 0x2e):
        break
check(g.m[ESSENCES] & 0x02, "l'essence du Coffre à Jouets (le 2e couplet)")
g.settled()
g.w(60)
check(g.where() == (3, 0x21), 'réveil chez Lila (3:21)')
shoot('c16_reveil', 'Réveil chez Lila')

g.stop()
sheet(shots, os.path.join(OUT, 'planche.png'))
print('\n%d erreur(s)' % len(errors) if errors else '\nTout est bon.')
for e in errors:
    print('  -', e)
sys.exit(1 if errors else 0)
