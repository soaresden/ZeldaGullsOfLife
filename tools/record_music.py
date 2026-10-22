"""Enregistre le son du jeu (PyBoy) en .wav, pour écouter sans lancer d'émulateur.

Usage : python tools/record_music.py [NOM ...]   (sans nom : tout)
(N- : le numéro du niveau, l'île et son donjon, voir LEVEL ; 0 = partout)
  film      out/apercus/N-film_apercu.wav      le film d'ouverture (bruitages, cri de la mouette)
  titre     out/apercus/N-titre_apercu.wav     l'écran titre (42 s)
  phare     out/apercus/N-phare_apercu.wav     le Phare Éteint (salle 4:24)
  ile       out/apercus/N-ile_apercu.wav       l'île de la Brume (Port-Veille, 1:9a)
  auberge   out/apercus/N-auberge_apercu.wav   l'auberge (3:9e)
  boss      out/apercus/N-boss_apercu.wav      MUS_BOSS ($2e) = le thème du jeu
  veilleur  out/apercus/N-veilleur_apercu.wav  le Veilleur Creux ($45, pour un autre boss)
  miniboss  out/apercus/N-miniboss_apercu.wav  MUS_MINIBOSS ($2d)
  theme     out/apercus/N-theme_apercu.wav     le thème du jeu (MUS_BALLADE_THEME, $44)
  grelot    out/apercus/N-grelot_apercu.wav    Hameau-Grelot (la place, 1:11 ; $3d)
  coffre    out/apercus/N-coffre_apercu.wav    le Coffre à Jouets (4:37 ; $3b)
  lagune    out/apercus/N-lagune_apercu.wav    la Lagune des Serments (le ponton, 1:24 ; $25)
  recif     out/apercus/N-recif_apercu.wav     le Récif Murmurant (le hall, 5:3f ; $18)
  braise    out/apercus/N-braise_apercu.wav    Mont-Braise (le village goron, 1:2a ; $26)
  forge     out/apercus/N-forge_apercu.wav     la Forge Endormie (l'entrée, 4:bb ; $17)
  echos     out/apercus/N-echos_apercu.wav     l'île des Échos (1:62 ; $13)
  cathedrale out/apercus/N-cathedrale_apercu.wav la Cathédrale Engloutie (5:8b ; $1a)
  tarkin    out/apercus/N-tarkin_apercu.wav    la maison de Tarkin (3:26 ; $19)
  nid       out/apercus/N-nid_apercu.wav       le Nid des Vents (le village des plumes, 1:67 ; $15)
  spirale   out/apercus/N-spirale_apercu.wav   la Spirale Céleste (4:3d ; $14)
  sommeil   out/apercus/N-sommeil_apercu.wav   l'île du Grand Sommeil (le village gelé, 1:b1 ; $1c)
  palais    out/apercus/N-palais_apercu.wav    le Palais Givré (le cœur, 4:57 ; $16)
  tempetes  out/apercus/N-tempetes_apercu.wav  le Chant des Tempêtes ($2b, la fin du chapitre 6)
  gerudo    out/apercus/N-gerudo_apercu.wav    la Vallée Gerudo au violon (la plage du forain, 1:ac ; $0b)
  quiz      out/apercus/N-quiz_apercu.wav      le quiz de Marine (« Qui veut gagner des millions », $0a)
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
    'echos': (1, 0x62, 0x55, None, 52),
    'cathedrale': (5, 0x8b, 0x57, None, 50),
    'tarkin': (3, 0x26, 0x64, None, 40),
    'nid': (1, 0x67, 0x44, None, 48),
    'spirale': (4, 0x3d, 0x57, None, 48),
    'sommeil': (1, 0xb1, 0x44, None, 50),
    'palais': (4, 0x57, 0x97, None, 50),
    'tempetes': (4, 0x24, 0x51, 0x2b, 40),
    'gerudo': (1, 0xac, 0x55, None, 75),
    'quiz': (4, 0x24, 0x51, 0x0a, 40),
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


# Le niveau (l'île et son donjon) de chaque morceau : le fichier commence par ce numéro (« 7-palais_apercu.wav »),
# 0 pour ce qui sert partout (film, titre, thème, boss)
LEVEL = {'ile': 1, 'phare': 1, 'auberge': 1, 'grelot': 2, 'coffre': 2, 'lagune': 3, 'recif': 3, 'braise': 4,
         'forge': 4, 'echos': 5, 'cathedrale': 5, 'tarkin': 5, 'nid': 6, 'spirale': 6, 'tempetes': 6,
         'sommeil': 7, 'palais': 7, 'rythme': 8, 'gerudo': 1, 'quiz': 5}


def save(name):
    name = '%d-%s' % (LEVEL.get(name.replace('_apercu.wav', ''), 0), name)
    data = np.concatenate(rec).astype(np.float32)
    data -= data.mean(axis=0)
    peak = max(1.0, float(np.abs(data).max()))
    pcm = (data / peak * 28000).astype('<i2')
    os.makedirs(os.path.join(ROOT, 'out', 'apercus'), exist_ok=True)
    path = os.path.join(ROOT, 'out', 'apercus', name)     # les aperçus à écouter, rangés à part
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
