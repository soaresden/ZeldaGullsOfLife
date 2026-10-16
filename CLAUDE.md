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

## Le Phare Éteint (donjon 1)
- Emplacement du 1er donjon d'Ages (index 1, groupe 4, décor 36), plan sur 2 étages
  (dungeon01LayoutPhare). Salles : story/salles/phare.txt (grandes salles 15 x 11) ; on garde la
  salle du boss (4:13, Pumpkin Head = le Veilleur Creux) et celle de l'essence (4:11).
- Briques du décor 36 : tools/render_room.py SORTIE --decor 36 (portes à clé 70-73, du boss 74-77,
  coffre f1, escaliers 44/45 ; f4-f7 sont des trous). Coffres : data/ages/chestData.s (groupe 4).
- Objet de coffre : mode d'apparition $38 (TREASURE_OBJECT_HARP_02 = la Lanterne ; les harpes
  d'origine, mode $0a, ne sortent pas d'un coffre).
- Entrée : porte 1:7b -> destination 4:$02 ; sortie 4:24 -> 1:$4a.
- Après l'essence : essence.s (@essenceWarps, ligne du donjon 1) ramène sur le cap 1:7b, où
  INTERAC_MARINE $02 (objets.txt) joue la fin si l'essence 1 est là, une seule fois (ROOMFLAG $40).
- Lanterne des Songes = la harpe d'Ages : harpFluteParent.s saute directement au voyage dans le
  temps (groupe xor 1, même salle), dehors seulement ; le coffre donne l'air des Âges (paramètre $03).
  L'eau de nos îles ($fa) est dans timewarpInvalidTiles.s (sinon Link se noie à l'arrivée).
  La table « renvoyé par une force étrange » (miscCutscenes.s) est vidée.
- Tests : tools/test_phare.py, tools/test_lanterne.py, tools/test_fin.py (DOSSIER_CAPTURES).
- Patch : python tools/make_patch.py "chemin/ROM Ages (USA).gbc" -> out/gulls_of_life.bps.
- tools/render_room.py dessine n'importe quelle salle sans lancer le jeu (adresse des tuiles = idx ^ $80).

## Pièges (suite)
- wTextboxFlags (ex. TEXTBOXFLAG_ALTPALETTE1 sur fond noir) est remis à zéro après chaque texte :
  le réécrire avant chaque showtext.
- Un PNJ posé sur les planches du ponton (0e) ne réagit pas au bouton A : le mettre sur le sable.
- Banque des scripts (mainScripts, banque $0c) presque pleine : les longs scripts vont dans
  scripts/ages/balladeLong.s (loadscript), sauf dans les salles du Songe avec ondulation.
- Ne plus réécrire l'historique (amend / force) : une autre session travaille dans ce dépôt
  (index.html, page du jeu).

- Songe : la vague (INTERAC_BALLADE_DREAM_FX) remplace le défilement horizontal ligne par ligne ;
  elle y ajoute wGfxRegs2.SCX en une seule passe (sinon écran figé ou déchiré entre deux salles).
  L'objet est invisible (sinon une image au hasard en haut à gauche).
- Ages modifie des cases de certaines salles au chargement (code/ages/roomSpecificTileChanges.s,
  data/ages/singleTileChanges.s) : désactivé pour les salles qu'on réutilise. À vérifier pour
  toute nouvelle salle.
- tools/check_edges.py [--fix] : bords entre salles (pas de buisson coupable face à un mur).
- Un script chargé par loadscript ne peut pas afficher de texte avant la fin de l'arrivée dans la
  salle (la boîte est effacée aussitôt) : attendre (ex. que Link soit allongé).
- Case B/A : la harpe (Lanterne) prend la « petite version » de l'icône (demi-tuiles $ad-$ae de
  spr_item_icons_3.png, x = 104), 8 pixels de large ; l'inventaire et le coffre prennent $ab-$ac.

## Deux langues (une seule ROM)
- Langue 0 = anglais (story/textes.en.yaml), 1 = français (story/textes.yaml), choisie au réveil sur
  la plage (TX_5a17), gardée dans la sauvegarde (wActiveLanguage, $c62a).
- tools/make_text.py écrit text/ages/text.yaml et text_fr.yaml ; le français est compilé à part
  (tools/build/parseTextLang.py, banques $71+) ; code/textbox.s choisit la table.
- Les textes d'Ages non remplacés restent en anglais ; on traduit nous-mêmes ceux que la démo
  montre (pas de copie de la VF de Nintendo dans le patch). Menus graphiques : encore en anglais.
- tools/check_text.py vérifie les deux fichiers (16 caractères, mêmes noms, police).
- Police : seulement les accents de la version US (pas de « ô » : écrire « coté »), vérifié par
  tools/check_text.py.

## Écran titre
- Après le film, plus de montée de l'arbre : introCinematic_gotoTitle -> écran titre.
- tools/make_title.py : image en bandes (ciel, logo, aube, mer), 6 palettes, GFXH_TITLE /
  PALH_TITLE ; lettres du logo dans art/titre_logo.txt (tools/draw_title_logo.py, une fois).
- Logo rose corail en Palatino gras italique (Denis : pas de jaune, féminin, c'est Marine).
- Marine en mouette est un sprite animé (code/ages/cutscenes/titleGull.s, spr_title_gull) : elle
  arrive, se pose sur le « s », sautille, clin d'œil + cœur, repart. Point de pose : LAND_X/Y
  (make_title.py) = TITLE_GULL_LAND_X/Y (titleGull.s).

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
