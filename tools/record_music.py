"""Enregistre le son du jeu (PyBoy) en .wav, pour écouter sans lancer d'émulateur.

Usage : python tools/record_music.py [NOM ...]   (sans nom : tout)
  film      out/film_apercu.wav      le film d'ouverture (bruitages, cri de la mouette)
  titre     out/titre_apercu.wav     l'écran titre (42 s)
  phare     out/phare_apercu.wav     le Phare Éteint (salle 4:24)
  ile       out/ile_apercu.wav       l'île de la Brume (Port-Veille, 1:9a)
  auberge   out/auberge_apercu.wav   l'auberge (3:9e)
  boss      out/boss_apercu.wav      MUS_BOSS ($2e) = le thème du jeu
  veilleur  out/veilleur_apercu.wav  le Veilleur Creux ($45, pour un autre boss)
  miniboss  out/miniboss_apercu.wav  MUS_MINIBOSS ($2d)
  theme     out/theme_apercu.wav     le thème du jeu (MUS_BALLADE_THEME, $44)
  grelot    out/grelot_apercu.wav    Hameau-Grelot (la place, 1:11 ; $3d)
  coffre    out/coffre_apercu.wav    le Coffre à Jouets (4:37 ; $3b)
  lagune    out/lagune_apercu.wav    la Lagune des Serments (le ponton, 1:24 ; $25)
  recif     out/recif_apercu.wav     le Récif Murmurant (le hall, 5:3f ; $18)
  braise    out/braise_apercu.wav    Mont-Braise (le village goron, 1:2a ; $26)
  forge     out/forge_apercu.wav     la Forge Endormie (l'entrée, 4:bb ; $17)
Pour le boss et le miniboss (pas de salle où ils jouent d'office), l'appel à playSound qui lance
la musique du Phare est détourné vers la leur (crochet PyBoy sur playSound, ROM intacte).
"""
import os
import sys
import wave

import numpy as np
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAY_SOUND = 0x0c09   # playSound (banque 0, voir oracles-disasm/ages.sym)
MUS_PHARE = 0x41
# nom : (groupe, salle, position, musique à la place de celle du Phare, secondes)
TRACKS = {
    'phare': (4, 0x24, 0x51, None, 45),
    'ile': (1, 0x9a, 0x55, None, 50),
    'auberge': (3, 0x9e, 0x57, None, 46),
    'boss': (4, 0x24, 0x51, 0x2e, 46),
    'veilleur': (4, 0x24, 0x51, 0x45, 31),
    'miniboss': (4, 0x24, 0x51, 0x2d, 24),
    'theme': (4, 0x24, 0x51, 0x44, 46),
    'grelot': (1, 0x11, 0x44, None, 48),
    'coffre': (4, 0x37, 0x57, None, 50),
    'lagune': (1, 0x24, 0x33, None, 52),
    'recif': (5, 0x3f, 0x57, None, 56),
    'braise': (1, 0x2a, 0x55, None, 50),
    'forge': (4, 0xbb, 0x57, None, 56),
}
wanted = sys.argv[1:] or ['film', 'titre'] + list(TRACKS)

ROM = os.environ.get('ROM', os.path.join(ROOT, 'out', 'gulls_of_life.gbc'))   # ROM=... pour une autre ROM
pb = PyBoy(ROM, window='null', sound_emulated=True)
pb.set_emulation_speed(0)
rec = None
swap = [None]


def on_play_sound(_):
    if swap[0] is not None and pb.register_file.A == MUS_PHARE:
        pb.register_file.A = swap[0]


pb.hook_register(0, PLAY_SOUND, on_play_sound, None)


def w(n):
    for _ in range(n):
        pb.tick(1, False)
        if rec is not None:
            rec.append(pb.sound.ndarray.copy())


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def warp(g, r, pos):
    for i, v in enumerate((0x80 | g, r, 0x00, pos, 0x03)):
        pb.memory[0xcc47 + i] = v


def save(name):
    data = np.concatenate(rec).astype(np.float32)
    data -= data.mean(axis=0)
    peak = max(1.0, float(np.abs(data).max()))
    pcm = (data / peak * 28000).astype('<i2')
    path = os.path.join(ROOT, 'out', name)
    with wave.open(path, 'wb') as f:
        f.setnchannels(pcm.shape[1])
        f.setsampwidth(2)
        f.setframerate(pb.sound.sample_rate)
        f.writeframes(pcm.tobytes())
    print('->', path, '%.1f s' % (len(pcm) / pb.sound.sample_rate))


# Le film d'ouverture (du logo à l'écran titre)
if 'film' in wanted:
    rec = []
w(1500)
if 'film' in wanted:
    save('film_apercu.wav')
rec = None
# L'écran titre (sa musique), si demandé
if 'titre' in wanted:
    rec = []
    w(42 * 60)
    save('titre_apercu.wav')
    rec = None

# Nouvelle partie, scène de la plage
for c in 'start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if pb.memory[0xcc8a] == 0 and i > 60:
        break
w(60)

for name, (g, r, pos, music, seconds) in TRACKS.items():
    if name not in wanted:
        continue
    # Passer d'abord par une autre musique, pour que la salle relance la sienne
    warp(3, 0x9e, 0x57) if g != 3 else warp(1, 0x9a, 0x55)
    w(120)
    swap[0] = music
    warp(g, r, pos)
    w(30)
    rec = []
    w(int(seconds * 60))
    print(name, ': salle', pb.memory[0xcc2d], hex(pb.memory[0xcc30]), 'musique', hex(pb.memory[0xcc35]))
    save(name + '_apercu.wav')
    rec = None
    swap[0] = None
pb.stop(save=False)
