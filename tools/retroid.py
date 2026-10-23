"""La Retroid de Denis (Batocera), par son partage réseau \\\\BATOCERA\\share (sans mot de passe) :

1. sauvegarde ce qu'il joue : la sauvegarde (.srm), les save states (.stateN) et leurs images
   (.stateN.png), et ses captures d'écran du jeu ;
2. avec --zip : envoie le zip du jeu (à la racine du dépôt, fait par tools/make_zip.py) dans
   roms/gbc/, s'il a changé.

Rien n'est copié si rien n'a changé depuis la dernière fois.
- retroid/AAAA-MM-JJ_HHMM/ : une copie par changement (jamais effacée)
- retroid/dernier/ : la dernière copie (la sauvegarde pour les tests : dernier/*.srm)
- retroid/planche.png : les images des save states et les captures, les plus récentes
  d'abord, avec leur nom et leur date (pour voir où en est Denis)

Usage : python tools/retroid.py [--zip] [--quiet]   (retroid/ : pas dans git)
Autre chemin du partage : RETROID_SHARE=\\\\192.168.1.21\\share
"""
import hashlib
import os
import shutil
import sys
import time

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'retroid')
SHARE = os.environ.get('RETROID_SHARE', r'\\BATOCERA\share')
GAME = 'Legend of Zelda, The - Gulls of Life'
ZIP = os.path.join(ROOT, GAME + '.zip')
QUIET = '--quiet' in sys.argv


def say(*a):
    if not QUIET:
        print(*a, flush=True)


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def remote_files():
    """Les fichiers du jeu sur la Retroid : {nom: chemin}."""
    found = {}
    for sub, test in (('saves/gbc', lambda n: n.startswith(GAME)),
                      ('screenshots', lambda n: 'gulls' in n.lower())):
        folder = os.path.join(SHARE, *sub.split('/'))
        if os.path.isdir(folder):
            for n in os.listdir(folder):
                if test(n) and os.path.isfile(os.path.join(folder, n)):
                    found[n] = os.path.join(folder, n)
    return found


def backup():
    files = remote_files()
    if not files:
        say('Rien de Gulls of Life sur la Retroid.')
        return
    h = hashlib.sha1()
    for n in sorted(files):
        h.update(n.encode('utf-8'))
        h.update(sha1(files[n]).encode())
    new = h.hexdigest()
    os.makedirs(OUT, exist_ok=True)
    stamp = os.path.join(OUT, 'dernier.sha1')
    latest = os.path.join(OUT, 'dernier')
    if os.path.exists(stamp) and open(stamp).read().strip() == new:
        say('Sauvegardes : rien de nouveau (%d fichiers).' % len(files))
    else:
        folder = os.path.join(OUT, time.strftime('%Y-%m-%d_%H%M'))
        if os.path.isdir(latest):
            shutil.rmtree(latest)
        for dst in (folder, latest):
            os.makedirs(dst, exist_ok=True)
            for n, src in files.items():
                shutil.copy2(src, os.path.join(dst, n))
        open(stamp, 'w').write(new)
        say('Sauvegardes copiées : %s (%d fichiers)' % (os.path.relpath(folder, ROOT), len(files)))
    for n in sorted(files):
        say('  %-52s %7d octets  %s' % (n, os.path.getsize(files[n]),
                                         time.strftime('%d/%m %H:%M', time.localtime(os.path.getmtime(files[n])))))
    dst = sheet(latest)
    if dst:
        say('Planche :', os.path.relpath(dst, ROOT))


def sheet(folder):
    shots = [n for n in os.listdir(folder) if n.lower().endswith('.png')]
    shots.sort(key=lambda n: -os.path.getmtime(os.path.join(folder, n)))
    if not shots:
        return None
    w, h, cols = 320, 288 + 18, 4
    im = Image.new('RGB', (w * cols, h * ((len(shots) + cols - 1) // cols)), 'white')
    d = ImageDraw.Draw(im)
    for i, n in enumerate(shots):
        path = os.path.join(folder, n)
        pic = Image.open(path).convert('RGB')
        pic = pic.resize((320, 288), Image.NEAREST) if pic.size == (160, 144) else pic
        pic.thumbnail((320, 288))
        x, y = (i % cols) * w, (i // cols) * h
        im.paste(pic, (x, y))
        label = n.replace(GAME, '').strip(' .') or n
        stamp = time.strftime('%d/%m %H:%M', time.localtime(os.path.getmtime(path)))
        d.text((x + 4, y + 291), '%s  %s' % (label, stamp), fill='black')
    dst = os.path.join(OUT, 'planche.png')
    im.save(dst)
    return dst


def send_zip():
    """Le zip du jeu dans roms/gbc/ de la Retroid, s'il a changé."""
    if not os.path.exists(ZIP):
        say('Pas de zip à envoyer (%s).' % os.path.basename(ZIP))
        return
    dst = os.path.join(SHARE, 'roms', 'gbc', GAME + '.zip')
    if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(ZIP) and sha1(dst) == sha1(ZIP):
        say('Zip : déjà à jour sur la Retroid.')
        return
    # (l'ancien zip de la Retroid est gardé : retroid/zips/)
    if os.path.exists(dst):
        keep = os.path.join(OUT, 'zips', time.strftime('%Y-%m-%d_%H%M', time.localtime(os.path.getmtime(dst)))
                            + '_' + os.path.basename(dst))
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        if not os.path.exists(keep):
            shutil.copy2(dst, keep)
    tmp = dst + '.envoi'
    shutil.copyfile(ZIP, tmp)
    os.replace(tmp, dst)
    say('Zip envoyé sur la Retroid : roms/gbc/%s (%d octets, du %s)'
        % (os.path.basename(dst), os.path.getsize(dst),
           time.strftime('%d/%m %H:%M', time.localtime(os.path.getmtime(ZIP)))))


def main():
    if not os.path.isdir(SHARE):
        sys.exit('Retroid injoignable (%s) : éteinte, ou pas sur le wifi ?' % SHARE)
    backup()
    if '--zip' in sys.argv:
        send_zip()


main()
