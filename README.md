🇬🇧 [English version](README.en.md)

# The Legend of Zelda: Gulls of Life

*La Ballade de la Mouette* : la suite de **Link's Awakening**, en ROM hack
Game Boy Color.

Le Poisson-Rêve s'est réveillé et l'île Cocolint a disparu… mais pas tout à
fait. Marine a fait un vœu : avoir des ailes pour partir au-delà de la mer. Elle
revient en **mouette**, et elle accompagne Link dans un archipel où plus
personne ne rêve.

*Gulls of Life* : *gulls* (les mouettes) sonne comme *goals* (les buts). C'est
la morale du jeu : on réalise ses rêves, on n'y reste pas, et on avance malgré
les obstacles.

![Film d'ouverture : la mouette se pose sur le rondin de Link](docs/film_ouverture.png)

![Chapitre 1 : Marine réveille Link sur la plage](docs/chapitre1_plage.png)

## Où on en est

| Partie | État |
| --- | --- |
| Nouvelle partie : plus d'intro d'*Ages*, Link se réveille sur une plage | ✅ |
| Marine en mouette (sprite dessiné pour le jeu, avec sa fleur d'hibiscus) | ✅ |
| Chapitre 1 : Link évanoui, Marine arrive en volant, se pose et lui parle (choix de réponse), puis se glisse au chaud dans la tunique de Link | ✅ |
| Textes en français, avec les accents | ✅ |
| Film d'ouverture avant l'écran titre : à l'aube, Link dérive sur son rondin et lève les yeux ; le visage de Marine apparaît dans les nuages (comme à la fin secrète de *Link's Awakening*) et s'efface ; une mouette s'en envole et se pose, « ? », clin d'œil, « ! », ils sautent de joie tous les deux et leurs cœurs s'envolent | ✅ |
| Écran titre *Gulls of Life* (aujourd'hui : celui d'*Ages*) | à faire |
| Marine voyage dans la tunique de Link : elle parle aux moments clés, on peut lui demander un indice | à faire |
| Dormir pour passer dans le Songe (Marine y redevient humaine) | à faire |
| Port-Veille, le Phare Éteint et son boss, le premier couplet de la chanson de Marine | à faire |
| Musiques : la chanson de Marine | à faire |

## Comment c'est fait

Le jeu repose sur le **moteur d'Oracle of Ages**, grâce au désassemblage
complet [oracles-disasm](https://github.com/Stewmath/oracles-disasm) de
Stewmath (branche `hack-base`, prévue pour les hacks). Le passage
présent/passé d'*Ages* servira au Réel et au Songe.

| Quoi | Où |
| --- | --- |
| Code, scripts, données | Branche [`hack/gulls-of-life`](https://github.com/soaresden/oracles-disasm/tree/hack/gulls-of-life) du fork (ajouts marqués `BALLADE`) : `scripts/ages/ballade.s`, `object_code/ages/interactions/marine.s` |
| Dialogues | `story/textes.yaml`, en français normal ; `tools/make_text.py` les ajoute au jeu, `tools/check_text.py` vérifie la largeur des lignes (16 caractères) |
| Sprites | Dessins en texte dans `art/` ; `tools/make_sprites.py` les convertit |
| Film d'ouverture | `code/ages/cutscenes/film.s` (fork) ; décor et sprites fabriqués par `tools/make_film.py` (ciel et nuages, soleil, mer, rondin, poses de Link prises dans le jeu, visage de Marine) ; `tools/preview_film.py` en donne un aperçu sans compiler |
| Tests | `tools/play.py` joue la ROM dans PyBoy et prend des captures |

Aucune ROM n'est distribuée ici : il faudra un patch à appliquer sur sa propre
ROM *Oracle of Ages* (USA).

## Compiler (Windows)

Prérequis : [MSYS2](https://www.msys2.org/) dans `C:\msys64` (avec `cmake`,
`make`, `mingw-w64-x86_64-gcc`) et Python 3 avec
`pip install pyyaml pillow pyboy`. Depuis Git Bash :

```bash
./setup.sh
```

```bash
./build.sh
```

La ROM sort dans `out/gulls_of_life.gbc`.
