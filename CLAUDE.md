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
- Film : `tools/play.py "w560 ..."` arrive vers l'arrivée de la mouette (le film dure ~1100 images).

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
