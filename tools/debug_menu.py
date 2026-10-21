"""Le menu de test caché, piloté depuis PyBoy (à importer dans les tests).

Dans le jeu : à l'écran titre, TENIR HAUT 5 secondes (petit son de secret), puis Start et un
fichier ; la partie commence dans une salle vide (3:9f) avec trois boîtes de choix : la langue,
l'île (1-8), le moment (Plage, Ville, Donjon, Fin ; pour le donjon : Entrée, M-boss, Boss). Code : oracles-disasm,
code/ages/balladeDebug.s.

    from debug_menu import Game
    g = Game()                    # ROM=chemin pour une autre ROM
    g.level(1, 'Boss', 'fr')      # depuis le démarrage jusqu'à l'endroit choisi
    g.shot('DOSSIER/boss.png')

Le son est toujours émulé (sinon le jeu boucle après le logo Capcom).
"""
import os

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = ('Plage', 'Ville', 'Donjon', 'M-boss', 'Boss', 'Fin')
ISLANDS = ('Brume', 'Grelot', 'Lagune', 'Braise', 'Échos', 'Nid', 'Sommeil', 'Œil')

# Adresses (oracles-disasm/ages.sym)
GROUP, ROOM = 0xcc2d, 0xcc30
TEXT_ACTIVE = 0xcba0
SCROLL_MODE = 0xcd00
LINK_Y, LINK_X = 0xd00b, 0xd00d
HEALTH, MAX_HEALTH = 0xc6aa, 0xc6ab
INV_B, INV_A = 0xc688, 0xc689
TREASURES = 0xc69a        # wObtainedTreasureFlags (un bit par trésor)
ESSENCES = 0xc6bf
SMALL_KEYS = 0xc672       # + numéro du donjon
BOSS_KEYS = 0xc682
LANGUAGE = 0xc62a
DEBUG_HOLD = 0xcdfe
OPTION_POSITIONS = (7, 0xd0e0)   # w7TextboxOptionPositions (banque 7 de la WRAM)
SELECTED_POSITION = (7, 0xd0e9)  # w7SelectedTextPosition : non nul quand le curseur est prêt


class Game:
    def __init__(self, rom=None):
        rom = rom or os.environ.get('ROM') or os.path.join(ROOT, 'out', 'gulls_of_life.gbc')
        self.pb = PyBoy(rom, window='null', sound_emulated=True)
        self.pb.set_emulation_speed(0)
        self.m = self.pb.memory

    # --- les bases ---
    def w(self, n=1):
        self.pb.tick(n, True)

    def press(self, b, n=6):
        self.pb.button(b, 3)
        self.w(n)

    def hold(self, b, n):
        self.pb.button_press(b)
        self.w(n)
        self.pb.button_release(b)
        self.w(4)

    def shot(self, path):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        self.pb.screen.image.save(path)

    def where(self):
        return self.m[GROUP], self.m[ROOM]

    def has(self, treasure):
        return bool(self.m[TREASURES + treasure // 8] & (1 << (treasure % 8)))

    def stop(self):
        self.pb.stop(save=False)

    def wait_until(self, cond, limit=600):
        for _ in range(limit):
            if cond():
                return True
            self.w()
        return False

    def wait_text(self, limit=600):
        """Attendre qu'une boîte de texte s'ouvre."""
        return self.wait_until(lambda: self.m[TEXT_ACTIVE], limit)

    def wait_no_text(self, limit=600):
        return self.wait_until(lambda: not self.m[TEXT_ACTIVE], limit)

    def settled(self, limit=600):
        """Attendre la fin d'une arrivée dans une salle (wScrollMode bit 0)."""
        self.w(10)
        return self.wait_until(lambda: self.m[SCROLL_MODE] & 1, limit)

    # --- du démarrage au menu ---
    def title(self):
        """Du démarrage à l'écran titre (le film est passé avec Start)."""
        self.w(900)
        self.press('start', 120)

    def secret(self, frames=320):
        """Tenir HAUT à l'écran titre (5 s = 300 images)."""
        self.hold('up', frames)

    def new_game(self):
        """De l'écran titre à la partie : fichier 1, NEW GAME, nom « A », vitesse du texte."""
        for b, n in (('start', 60), ('a', 60), ('a', 80), ('a', 10), ('start', 20), ('a', 60),
                     ('a', 60), ('a', 60)):
            self.press(b, n)
        self.settled()

    def options_shown(self):
        bank, addr = OPTION_POSITIONS
        return sum(1 for i in range(8) if self.m[bank, addr + i])

    def choose(self, option, count=2):
        """Dans une boîte à choix (count choix) : attendre que tous les choix soient écrits, aller
        sur le n-ième, valider."""
        self.wait_text()
        self.wait_until(lambda: self.options_shown() >= count and self.m[SELECTED_POSITION], 900)
        self.w(10)
        for _ in range(option):
            self.press('right', 8)
        self.press('a', 10)
        self.wait_no_text()

    def menu(self, island, step, lang='fr'):
        """Les trois choix du menu (le jeu est dans la salle 3:9f)."""
        assert self.where() == (3, 0x9f), 'pas dans la salle du menu : %d:%02x' % self.where()
        self.choose(0 if lang == 'fr' else 1, 2)
        self.choose(island - 1, 8)
        self.island_step(step)
        self.arrive()

    def island_step(self, step):
        """Le choix du moment, une fois l'île choisie."""
        step = STEPS.index(step) if isinstance(step, str) else step
        # Plage, Ville, Donjon, Fin ; pour le donjon : Entrée, M-boss, Boss
        if step in (2, 3, 4):
            self.choose(2, 4)
            self.choose(step - 2, 3)
        else:
            self.choose({0: 0, 1: 1, 5: 3}[step], 4)

    def arrive(self, limit=600):
        """Attendre d'avoir quitté la salle du menu et d'être arrivé."""
        ok = self.wait_until(lambda: self.where() != (3, 0x9f), limit)
        self.settled()
        self.w(30)
        return ok

    def level(self, island, step, lang='fr'):
        """Du démarrage jusqu'au niveau choisi."""
        self.title()
        self.secret()
        self.new_game()
        self.menu(island, step, lang)
