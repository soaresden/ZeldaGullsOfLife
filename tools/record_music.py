"""Enregistre le son du jeu (PyBoy) en .wav, pour écouter sans lancer d'émulateur.

Usage : python tools/record_music.py [SECONDES]
  out/film_apercu.wav  : le film d'ouverture (bruitages, cri de la mouette)
  out/phare_apercu.wav : le Phare Éteint (salle d'entrée 4:24), SECONDES secondes (45 par défaut)
"""
import os
import sys
import wave

import numpy as np
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 45

pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
pb.set_emulation_speed(0)
rec = None


def w(n):
    for _ in range(n):
        pb.tick(1, False)
        if rec is not None:
            rec.append(pb.sound.ndarray.copy())


def press(b, n=4):
    pb.button(b, 3)
    w(n)


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
rec = []
w(1500)
save('film_apercu.wav')
rec = None

# Nouvelle partie, scène de la plage, puis le Phare
for c in 'start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if pb.memory[0xcc8a] == 0 and i > 60:
        break
w(60)
for i, v in enumerate((0x80 | 4, 0x24, 0x00, 0x51, 0x03)):
    pb.memory[0xcc47 + i] = v
w(30)
rec = []
w(int(SECONDS * 60))
print('salle', pb.memory[0xcc2d], hex(pb.memory[0xcc30]), 'musique', hex(pb.memory[0xcc35]))
pb.screen.image.save(os.path.join(ROOT, 'out', 'phare_apercu.png'))
save('phare_apercu.wav')
pb.stop(save=False)
