# The Legend of Zelda: Gulls of Life — notes de travail

Suite de Link's Awakening (Marine revenue en mouette) sur le moteur d'Oracle of Ages.
Ne pas dévoiler le twist de l'histoire à Denis : il veut le découvrir en jouant.

## Dépôts
- Ce dépôt : textes (`story/`), dessins (`art/`), outils (`tools/`), scripts de build.
- `oracles-disasm/` : fork soaresden/oracles-disasm, branche `hack/gulls-of-life`, partie de
  `upstream/hack-base` (Stewmath). Nos ajouts sont marqués `BALLADE` dans le code.
- `tools-build/wla-dx` : WLA-DX v10.6 (ici une jonction vers ZeldaOracleCombinedFR).

## Compiler et tester
- `./build.sh` (Git Bash) régénère textes + sprites puis compile -> `out/gulls_of_life.gbc`.
  La 1re compilation prend ~25 min (compression de toutes les salles), ensuite quelques secondes.
- `python tools/check_text.py` avant de compiler : 16 caractères par ligne au maximum.
- `python tools/play.py "SCENARIO" DOSSIER` : PyBoy avec `sound_emulated=True` (obligatoire).
  Nouvelle partie depuis le boot : `w900 start w120 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a`
  (titre, fichier 1, NEW GAME, nom « A », OK, vitesse du texte).
- Adresses RAM : `oracles-disasm/ages.sym` (ex. w1Link=$d000, wcc50=$cc50, wDisabledObjects=$cc8a).

## Pièges déjà rencontrés
- Les heredocs Bash de l'outil réduisent `\\` en `\` : écrire les fichiers avec des `\` via Write/Edit.
- `parseText.py` lisait le texte avec l'encodage Windows : corrigé (UTF-8) dans le fork.
- Textes : style YAML `|-` avec retours à la ligne choisis à la main ; `\stop` en fin de ligne.
- Coucher Link (LINK_ANIM_MODE_COLLAPSED) : `writememory wDisabledObjects, $04` (pas $91, qui gèle
  Link et l'empêche de changer d'état), `asm15 setLinkForceStateToState08`, attendre
  `checkmemoryeq w1Link.state, LINK_STATE_08`, puis écrire wcc50 (son 1er passage l'efface).
  Pour le relever : `enableallobjects`, `wait 1`, puis `setdisabledobjectsto91`.
- Sprites `spr_*` : couleurs inversées (noir = transparent, gris foncé = couleur 1, gris clair = 2,
  blanc = 3). Marine = palette 2 (noir / rouge / crème), animations du perroquet (INTERAC_KNOW_IT_ALL_BIRD).

- Banque 3 (cinématiques) pleine : le film est dans sa propre section superfree (`balladeFilm`),
  appelée par `jpab` depuis `introCinematic_filmCaller` ; n'y utiliser que des fonctions de la banque 0.
- `jr` limité à ±127 octets : utiliser `jp` vers les fonctions communes d'un fichier long.
- Sprites OAM : le premier écrit passe devant (dessiner du premier plan vers le fond).
- WLA-DX : `.db $aa <TX_xxxx` est lu comme une comparaison (`$aa < TX`) : séparer par des virgules.
- Select : appui court = Marine parle (`code/ages/balladeMarine.s`, table groupe/salle/texte, sinon
  TX_5a10-13 au hasard), maintenu BALLADE_SELECT_HOLD_FRAMES images = carte (bank2.s, b2_updateMenus ;
  compteur wBalladeSelectTimer en $cde5).
- Film : `tools/play.py "w560 ..."` arrive vers l'arrivée de la mouette (le film dure ~1100 images).

## Salles
- Plans : `story/salles/*.txt` (salle XX decor YY + 8 lignes de 10 briques), objets dans
  `story/salles/objets.txt` ; `tools/make_rooms.py` (appelé par build.sh) écrit roomGGSS.bin et
  group1Tilesets.bin, et redéfinit les objets de nos salles à la fin de objects/ages/mainData.s
  (régénéré depuis upstream/hack-base : ne pas éditer ce fichier à la main pour nos salles).
- Fichier de disposition = selon le GROUPE de la salle (hack-base, @getLayoutGroup) : groupe 0 ->
  room00SS, 1 -> room02SS, 2 -> room01SS, 3 -> room03SS (l'octet 6 du décor est ignoré).
- hack-base : chaque décor a ses propres images (gfx/ages/gfx_tilesetXX.png), briques
  (tileset_layouts_expanded/ages/tilesetMappingsXX.bin) et collisions : un nouveau décor doit les
  avoir (tools/make_songe.py les copie pour $7d-$7f).
- `python tools/catalog.py 10 18` : planche numérotée des briques ; `--salles 9a 9b` : photos de
  salles avec les numéros. Décor 10 = village du passé (maisons 8a 81 82 / 90 91 92 / f6 de f6,
  toit long 8f + f6 a3 de, arbres 08 09 / 2c 3c, buisson cd, sol 3b, pavés 0c, eau fa/fc, pont 1d/1e,
  colonnes 99) ; décor 18 = plage (sable bf, rivages 21/24/26/27, coins 22/28/2a, buisson c5,
  planches 0e, palmier 80 81 / 90 91).
- Téléporter Link dans PyBoy : écrire $81, salle, $00, position, $03 en wWarpDestVariables ($cc47).

## Le Songe
- Réel = groupes 1 (dehors) et 3 (dedans) ; Songe = groupes 0 et 2, mêmes numéros de salles.
  Décors du Songe $7d (village), $7e (plage), $7f (auberge), palettes bleutées (tools/make_songe.py).
  Les salles du Songe sont des copies automatiques (tools/make_rooms.py) sauf story/salles/songe.txt.
- Passage : balladeMarine.switchDream (groupe xor 1, même salle, case de Link). Le lit de l'auberge
  (3:9e, case $17 vers la droite, LINK_STATE_SLEEPING) envoie dans le Songe (2:9e) ; Select dans le
  Songe crée INTERAC_MARINE $01 qui propose le réveil.
- Ondulation : INTERAC_BALLADE_DREAM_FX ($e9), ajoutée d'office à chaque salle du Songe. Elle écrit
  wBigBuffer à chaque image : PAS de « loadscript » dans le Songe (ces scripts tournent depuis
  wBigBuffer) ; et elle se met en pause pendant les textes (le mode « vague » cache les boîtes).
- Tests : BALLADE_SANS_ONDULATION=1 ./build.sh compile sans l'ondulation.
- Marine humaine : art/marine_humaine.txt (4 poses de villageoise d'après la branche sprites/marin, robe
  redessinée : orange, ceinture et ourlet clairs ; palette 3 = cheveux orange), gfx $e2.

## Choix de conception (Denis)
- Marine ne suit PAS Link à l'écran (trop de sprites, ça bloquerait des choses) : elle voyage au chaud
  dans sa tunique. Elle parle depuis la tunique ; pour ses pouvoirs (planer, repérer, porter une bombe)
  elle en sort le temps de l'action, puis y retourne.

## Repères dans Ages
- Groupes : 0 présent, 1 passé (extérieurs), 2/3 intérieurs. Plage du réveil = salle 1:aa.
- Lit qui fait dormir Link : `checkLinkPushingAgainstBed` (link.s), LINK_STATE_SLEEPING -> futur passage au Songe.
- Intro : runIntroCinematic (bank3Cutscenes.s) : 0 = notre film (à la place de la chevauchée), 1 = temple
  (sauté), 2 = montée de l'arbre puis écran titre.
- Film : visage de Marine dans les nuages (art/film_sprites.txt @face, palette 5, scintillement
  pour l'effet de vision ; minuteur en $cbc0). Références de Denis : portrait pixel de Hyrule
  Warriors, fin du remake Switch.
