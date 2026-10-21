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

## Menu de test caché (pour tester les niveaux sans tout rejouer)
- Dans le jeu : à l'écran titre, **TENIR HAUT 5 secondes** (petit son de secret), puis Start et un
  fichier (ou NEW GAME). La partie commence dans une pièce vide (3:9f, copie de l'auberge :
  story/salles/debug.txt) : la langue, l'île (1-8), puis Plage / Ville / Donjon / Fin, et pour
  Donjon : Entrée / M-boss / Boss. Link part avec les objets et les drapeaux de l'histoire, comme
  s'il avait tout joué avant. Une étape pas encore construite : son d'erreur, retour à l'île.
- Invisible pour un joueur : le code est en SRAM $bff2 (BALLADE_DEBUG_CODE), effacé à chaque écran
  titre et à chaque début de partie ; HAUT tenu moins de 5 s ne fait rien.
- Code : code/ages/balladeDebug.s (INTERAC_BALLADE_DEBUG $ec ; textes TX_5af0-f3, les mêmes dans
  les deux langues). Les boîtes d'Ages n'affichent que 2 lignes : 8 choix au plus, et le premier
  choix d'une ligne doit avoir un espace devant. **Pour chaque nouvelle île** : remplir sa ligne de
  `debugEntries` (6 moments : nombre d'étapes, groupe, salle, case, liste en plus) et ajouter ses
  étapes à `debugMilestones` (objets, essence, réceptacle, drapeaux), dans l'ordre du jeu.
- Une boîte de texte demandée pendant l'arrivée dans une salle est refusée : attendre que
  wScrollMode ait le bit 0 (textThreadStart).
- PyBoy : `tools/debug_menu.py` (classe Game : `g.level(île, 'Boss', 'fr')`, `g.choose`,
  `g.where()`...) ; `python tools/test_niveaux.py DOSSIER [ÎLE...]` teste chaque niveau construit
  (arrivée, objets, drapeaux, un petit bout de jeu) + que le menu reste caché, et fait une planche
  DOSSIER/planche.png. Un choix ne se valide qu'une fois le curseur prêt (w7SelectedTextPosition,
  banque 7 de la WRAM, non nul).
- Dernière planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/niveaux.png

## Chapitre 2 : Hameau-Grelot (île 2)
- Fin du chapitre 1 (au port, après « À l'abordaaaage ! ») : Marine lit le vent (TX_5a54) ;
  GLOBALFLAG_BALLADE_RAFT ($50) et GLOBALFLAG_BALLADE_ISLAND2 ($51). Drapeaux globaux à nous :
  $50-$7f (Ages s'arrête à $4f), constants/common/globalFlags.s. Parties de la v1.0/1.1 déjà
  finies : INTERAC_BALLADE_OBJECT $02 (1:ab, 9b, 99) rattrape la scène.
- INTERAC_BALLADE_OBJECT ($ed, code/ages/balladeObjects.s, une section à part) : tous nos objets
  ASM, un sous-type par objet ; images dans art/objets.txt -> spr_ballade_objects (gfx $e3, image n
  = tuiles 4n à 4n+3, tools/make_sprites.py) ; animations des villageois (image fixe).
  $00 le Bateau-Rondin, $01 Marine parle en entrant (@arrivalTexts : groupe, salle, texte,
  drapeau global appris), $02 rattrapage, $03 le grelot de la grotte.
  Piège : objectAddToAButtonSensitiveObjectList prend `de` = Interaction.pressedAButton.
- Le Bateau-Rondin (1:99 la Brume, 1:31 Grelot) : A -> Marine propose les îles repérées
  (TX_5a50-52 selon leur nombre), fondu vers la jetée (table `jetties`). Boîte de collision large
  (il flotte à coté du ponton).
- L'île : story/salles/ile_grelot.txt, écrans 1:00-33, décor 7b = copie du décor 00 (Lynna du
  présent) marquée « passé » (TILESETFLAG_PAST : symbole de l'époque, carte), son Songe 7c
  (tools/make_songe.py, REEL et SONGE ; en-tête de palette $d0, PALH_TITLE reste $cf).
  Les groupes 0 et 2, 1 et 3 partagent leurs drapeaux de salle (wPresentRoomFlags / wPastRoomFlags).
- Intérieurs (story/salles/grelot_interieurs.txt) : boutique de Pépin 3:20 (copie de 3:5e ;
  roomGfxChanges.s `$20 $04` pour les prix), maison de Lila 3:21, école 3:22, Lila du Songe 2:21,
  la grotte de la Boîte 5:b0 (décor 58). Portes : warpSources.s / warpDestinations.s (BALLADE).
- Bombes : la boutique de Pépin vend les premières (shopItem.s : plus besoin d'en avoir déjà).
  Dans Oracles, le bouton des bombes en fait tenir une au-dessus de la tête ; un 2e appui la lance.
- Pouvoir de Marine (GLOBALFLAG_BALLADE_MARINE_BOMB $58, appris dans la grotte) : Link tient une
  bombe, Select -> balladeMarine.checkBombPower (appelé par bank2.s à la 1re image de l'appui) ->
  INTERAC_MARINE $06 (bombCarrier) emporte la bombe BALLADE_CARRY_FRAMES images droit devant, la
  lâche, revient. Le grelot ($03) sonne si une bombe explose à moins de 24 pixels : drapeau $40
  de la salle, cases du pont (@bridges) avec setTile.
- Test : python tools/test_grelot.py DOSSIER (radeau aller-retour, bombes, falaise, grotte,
  Marine, grelot, pont). Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/grelot.png
- tools/check_edges.py [--fix] PLAN vérifie les bords de n'importe quel plan (piquets f7 pour 7b).
- Lila (INTERAC_BALLADE_OBJECT $04, 3:21) : Sire Bouchon = l'objet d'échange 0 d'Ages (la pendule ;
  icône art/sire_bouchon.txt dans spr_quest_items_1, TX_005a / TX_0909), dans le coffre de la grotte
  (TREASURE_OBJECT_TRADEITEM_0c, apparition $38). Rendu -> GLOBALFLAG_BALLADE_LILA_ASLEEP ($59) ; le
  lit de sa maison (link.s, comme l'auberge) mène à son rêve 2:21 : Lila ($05) et le Coffre à Jouets
  ($06, « Entrer ? » -> l'entrée du donjon 2, @dungeonEntrance). Habitants en ASM : npcInit,
  npcCheckTalk, npcSay, npcWaitText (balladeObjects.s).
- Le Carnet des Rêves = l'objet $12 d'Ages (inutilisé) : itemUsageTables.s, parentItemUsage.s ->
  parentItemCode_carnet (harpFluteParent.s) -> balladeObjects.readCarnet (une page par nombre d'îles
  sauvées : TX_5a60, 5a61...) ; icône art/carnet.txt (à la place de l'air des Échos, $a3-$a4),
  nom TX_0942, reçu TX_0072. Donné par l'aubergiste pendant le tour du village ; parties anciennes :
  INTERAC_BALLADE_OBJECT $07 dans l'auberge. La banque des scripts ($0c) est pleine : les nouveaux
  habitants sont en ASM.

## Le Coffre à Jouets (donjon 2)
- story/salles/coffre.txt : les salles du 2e donjon d'Ages (groupe 4, $2b-$3b), décor 37 (le Donjon
  des Ailes), dungeon02LayoutCoffre (dungeonData02, un étage). Entrée 4:39 depuis le Coffre à
  Jouets du rêve de Lila (INTERAC_BALLADE_OBJECT $06, warp direct) ; sortie -> 2:21.
  INTERAC_DUNGEON_STUFF $00 (nom du donjon, remise à zéro des cristaux) ne marche qu'au chargement
  d'une partie : nos entrées utilisent INTERAC_BALLADE_OBJECT $09 (même rôle, TX_0200 + donjon).
- Chemin : Zols (clé 1 qui tombe, $12 $01) ; porte à clé -> hall ; soldats (volet $1e $09) ->
  coffre du Boomerang-Toupie ($12 $02, TREASURE_OBJECT_BOOMERANG_04) ; grelot de 4:34 (Marine,
  pont @bridges, clé 2) ; cristal 4:2d (PART_SWITCH $01 -> $24 $01 -> volet $1e $07), le boomerang
  L1 porte à ~4 cases (65 pixels) ; Soldat de Plomb = l'Armos Warrior (objets de la salle 4:80,
  TX_2f01-02 traduits) -> clé du boss ; porte du boss -> antichambre 4:2e ; l'échelle (colonne 4)
  monte dans 4:2b (défilement latéral) : Pantin-Sans-Fil = la Head Thwomp d'Ages (ses objets
  d'origine gardés dans objets.txt) + Marine ($01, TX_5a63).
- Pantin-Sans-Fil : une bombe entrée dans sa bouche (y $50, x $78, à 12 pixels près) quand son
  visage est rouge (ou passe au rouge) lui coûte un cœur (4 cœurs) ; il tourne plus vite à chaque
  coup (visage 26/23/20/17 images, transition 11/10/8/7). En défilement latéral, Marine monte
  (3 pixels par image) : la lancer 1 à 16 images après le passage au violet marche à tous les
  niveaux (« la bombe prête, lance-moi dès qu'il devient violet »). Après sa mort : cœur, échelles ;
  l'essence apparaît dans l'antichambre (INTERAC_BALLADE_OBJECT $08) -> réveil chez Lila (3:21).
- Test : python tools/test_coffre.py DOSSIER (tout le donjon, ennemis retirés sauf le boss).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/coffre.png

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
- Select : appui court = la carte ; maintenu BALLADE_SELECT_HOLD_FRAMES images = Marine parle
  (`code/ages/balladeMarine.s`, table groupe/salle/texte, sinon TX_5a10-13 au hasard) (bank2.s,
  b2_updateMenus ; compteur wBalladeSelectTimer en $cde5).
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
- Emplacement du 1er donjon d'Ages (index 1, groupe 4, décor 36), un seul étage tout en hauteur
  comme un phare (dungeon01LayoutPhare : pied 1b-14-15, tour 16-18-17, galerie 19-12-1a, Jack 13,
  la lumière/essence 11). Dans un donjon, la salle voisine vient du plan (wDungeonMapPosition ±1/±8),
  pas du numéro de salle. Salles : story/salles/phare.txt (« sombre », « boss » après le décor) ;
  make_rooms.py écrit aussi group4DungeonProperties.bin (mini-carte, bit $80 = salle sombre).
- Le temple : la Lanterne, dans un donjon, crée une graine de feu (ITEM_EMBER_SEED sous-type 0,
  comme la sacoche) : elle allume les torches (tuile 08 -> 09 ; PART_LIGHTABLE_TORCH). Salle sombre
  = bit $80 + obj_Part $08 $00 $00 (s'éclaire torche après torche, rend les torches allumables).
  Volet ouvert par N torches : INTERAC_DOOR_CONTROLLER $1e $14 (2 torches, haut) ; coffre :
  INTERAC_TRIGGER_TRANSLATOR $24 $02 N $01 + INTERAC_DUNGEON_SCRIPT $20 $00 Y X.
- Jack (Pumpkin Head, boss 4:13) : la citrouille tombe (épée sur le corps) ; la flamme de la
  Lanterne la brûle (pumpkinHead_head_checkBurned : var2a = $9b, état $17 pendant 240 images) et le
  fantôme sort, touchable. Plus besoin du bracelet. Banque 15 (Enemy_Code_Bank0f) pleine à
  quelques octets près. En entrant, INTERAC_MARINE $04 : Jack menace (TX_5a34), Marine réplique
  (TX_5a35), une fois (ROOMFLAG $40). Le boss attend que les volets se ferment derrière Link
  (wcc93) : un test doit entrer en marchant, pas par téléportation.
- Mini-boss : le Ghini géant d'Ages (salle 4:18, ses objets d'origine).
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
- Tests : tools/test_temple.py (torches, Jack, essence), tools/test_lanterne.py, tools/test_fin.py
  (DOSSIER_CAPTURES).
- Patch : python tools/make_patch.py "chemin/ROM Ages (USA).gbc" -> out/gulls_of_life.bps.
- tools/render_room.py dessine n'importe quelle salle sans lancer le jeu (adresse des tuiles = idx ^ $80).

## Pièges (suite)
- wTextboxFlags (ex. TEXTBOXFLAG_ALTPALETTE1 sur fond noir) est remis à zéro après chaque texte :
  le réécrire avant chaque showtext.
- Un PNJ posé sur les planches du ponton (0e) ne réagit pas au bouton A : le mettre sur le sable.
- Superposer un PNJ et Link (câlin) : `writememory wLinkCanPassNpcs, $01` sinon le PNJ solide
  pousse Link ; le jeu dessine Link DEVANT tout objet moins de 11 pixels plus bas que lui
  (objectSetPriorityRelativeToLink) : pour un vrai câlin, Marine passe derrière (au-dessus de
  Link, son visage par-dessus son épaule). Remettre $00 après.
- Le Songe ouvre la mer en deux là où était le pont du sentier (0:8a : murs de vagues fe/ff, fond
  de la mer 1a/1b) ; dans le Réel (1:8a) l'île est coupée en deux, sans ouvriers pour réparer.
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
  montre (pas de copie de la VF de Nintendo dans le patch).
- Menus graphiques en français : tools/make_menus_fr.py (lancé par build.sh) écrit les gfx_*_fr.png
  (gfx_compressible/common) en recomposant les mots avec les lettres des menus anglais (lettres
  manquantes et accents dessinés dans le script, fond rayé recousu avec les vraies rayures) ;
  aperçu out/menus_fr.png. Headers $bd-$c8 (data/ages/gfxHeaders.s) + table
  balladeLangGfxHeaders : loadGfxHeader (bank0.s, balladeLangGfxHeader) prend la variante
  française si wActiveLanguage = 1. Ne JAMAIS importer les images de la ROM européenne.
- Choix du fichier (langue pas encore connue) : saveFile écrit wActiveLanguage en SRAM $bff0
  (libre, après les 6 copies de fichiers) ; fileSelectMode0 (bank2.s, balladeMenuLanguage) la
  relit. Premier démarrage = anglais. « Sauver et quitter » relance le jeu (logo, film, titre).
- Test : python tools/test_menus.py DOSSIER [fr|en] [ROM] (nom, sauvegarde, retour au choix du
  fichier, inventaire, Game Over).
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

## Musique et bruitages
- Partitions lisibles dans `music/*.txt` (notation en tête de music/phare.txt : `d5:2` = note + durée
  en croches, `-:3` silence, `4f` = images, `2/3` = triolet, `[v6] [duty 1] [onde 0e] [vib e1]
  [gate .8] [detune 1]`, `( ... )x8`, `<melodie+3>` = écho d'une autre voix, `mouette:3` = cri de
  mouette, `[chant mouette]` = notes chantées comme un cri). `tools/make_music.py` (build.sh) vérifie
  mesures et durées des 4 voix, écrit `audio/ages/mus/ballade.s` (une section superfree par morceau),
  `audio/ages/balladeChannelPointers.s` (tables des canaux, incluses par soundChannelPointers.s) et
  la musique des salles (`audio/ages/groupNIDs.bin`, un octet par salle ; liste ROOM_MUSIC).
- Moteur d'Ages : canaux 0/1 = carrés (accordéon / mélodie), 4 = onde (basse ; `duty` = n° de forme
  d'onde, le volume y est ignoré), 6 = bruit (`note $2a` charleston, `$2e` caisse claire ; types dans
  audio/common/noise.s). Un silence NE coupe PAS le bruit : prendre un bruit qui s'éteint seul
  (pas $22/$28/$30). Durées en images (60/s) ; les carrés jouent à partir de c2 ; `cmdfd` décale la
  hauteur (en unités du registre de fréquence). Bruitages : canaux 2/3/5/7 ; `cmdf0 $X0` passe en
  fréquences brutes (`.db poids_fort poids_faible durée`).
- La table des canaux est dans la banque du code audio, les données dans n'importe quelle banque
  (m_soundPointer stocke un écart de banque).
- Les morceaux (tous validés par Denis à l'écoute) :
  - $01 MUS_TITLESCREEN : music/titre.txt, la Ballade du Poisson-Rêve chantée par Marine en mouette
    (notes de LADX, MusicMarinSing), rythme 3+3+2, vrais cris de mouette dans les silences.
  - $2e MUS_BOSS : music/theme.txt (= MUS_BALLADE_THEME $44), la Ballade en version énervée façon
    Ninja Gaiden, puis « Marine est déterminée ». Tous les boss la jouent (commonBossCode).
  - $2d MUS_MINIBOSS : music/miniboss.txt, façon Hyrule Warriors. Tout miniboss d'Ages la joue
    (le Ghini géant du temple compris) ; sinon `setmusic MUS_MINIBOSS`.
  - $41 MUS_BALLADE_PHARE : music/phare.txt, chant de marins en 6/8 avec « HEY ! » (forme d'onde
    « voix » $2e de audio/common/waveforms.s, d'après l'enregistrement de Denis).
  - $42 MUS_BALLADE_ILE : music/ile.txt, l'île de la Brume (1:79-ac et 0:79-ac), brume et écho.
  - $43 MUS_BALLADE_AUBERGE : music/auberge.txt, swing jazzy et chaleureux (3:9e et 2:9e).
  - $45 MUS_BALLADE_VEILLEUR : music/boss.txt, combat façon Zelda, en réserve pour un autre boss.
- SND_BALLADE_GULL = $d6 : cri de mouette de LADX (JINGLE_SEAGULL) porté image par image ; joué au
  clin d'œil de Marine dans le film. Le même cri existe dans la musique (`mouette:3`).
- Denis accepte qu'on reprenne sons, musiques et objets de Link's Awakening DX
  (https://github.com/zladx/LADX-Disassembly) ; pas la VF de Nintendo pour les textes.
- Le désassemblage de LADX est sur la machine : D:\DOCS\Documents\GitHub\ZeldaOracleCombinedFR\LADX-Disassembly-main
  (sons : src/code/audio/, musiques, sprites : src/gfx/...). Le lire là plutôt que sur GitHub.
- Aperçus à écouter : `python tools/record_music.py [film titre phare ile auberge boss veilleur
  miniboss theme]` -> out/NOM_apercu.wav ; `ROM=chemin` pour une autre ROM ; les morceaux sans
  salle sont lancés en détournant playSound (crochet PyBoy). Denis veut ÉCOUTER une musique avant
  qu'on la pousse ; ses références : Wind Waker / Linebeck (marin), Resident Evil (salle de
  sauvegarde), Hyrule Warriors, Ninja Gaiden NES.

## Boss de fin en rythme (boss du donjon 8, prototype)
- Idée de Denis (story/idees.md) : la musique se tait, il reste un métronome ; A en rythme de la
  Ballade fait revenir la chanson note à note ; Marine chante la suite et donne le coup de grâce.
- INTERAC_BALLADE_RHYTHM ($ea) : code/ages/balladeRhythm.s (section à part ; banque $10 = 6 octets).
  Salle de test 4:4a (arène de l'ancien donjon 3), silencieuse en entrant (musique de salle $f0 =
  SNDCTRL_STOPMUSIC) : Marine parle (« Allez, donne-moi le 'La' ! »), puis le morceau commence.
- 5 niveaux, comme les 5 étapes de Lorule Castle (A Link Between Worlds, la référence de Denis ;
  analyse : étape 1 sans basse, 2 + basse, 3 + percussions, 4 + aigus/cuivres, 5 tout) : un bon tour
  de la phrase = un niveau de plus = un autre morceau (même phrase, un instrument de plus), lancé au
  début du tour suivant. MUS $47 (music/rythme.txt, avec 2 mesures de décompte), $49 (rythme2),
  $4b (rythme3), $37 (rythme4), $3a (rythme5) ; puis $48 (rythme_fin.txt : Marine chante la 2e
  moitié de la Ballade). make_music.py vérifie que les 5 niveaux ont exactement les mêmes notes à
  frapper. Numéros pris parmi les musiques vides d'Ages (restent libres : $24, $3b, $3d).
- Technique : le morceau joue en entier, le jeu coupe les voix avec NR51 ($ff25 ; le moteur d'Ages
  ne l'écrit qu'au démarrage, et code/audio.s le remet à $ff à chaque nouvelle musique : sortir de
  la salle rend le son). Bruit (métronome / batterie) toujours ; mélodie ouverte jusqu'à la fin de
  la note après un coup juste ; harpe puis basse à 6 / 12 coups justes d'affilée.
- Réglé tolérant (Denis : « c'est pas un jeu de rythme ») : fenêtre ±12 images ; un coup en retard
  mais plus près de la note suivante compte pour la suivante ; note ratée = enchaînement / 2 ; coup
  dans le vide = -2. Bon tour = notes justes - coups dans le vide >= 14 sur 18 (taper sans arrêt ne
  marche pas). Constantes BALLADE_RHYTHM_* (constants/common/version.s).
- Marine (TX_5a36-3d, 2 lignes seulement : une 3e attendrait A ; \wait(120) = bulle de ~3 s qui se
  ferme seule, demandé par Denis) : en arrivant ; après chaque bon tour (« Ouais... Je
  reconnais !... », « C'est ça ! Plus fort ! », « Je reprends mon souffle... », « Ma voix... Elle
  revient ! », « Tu as retenu ♥ ! ») ; « Je vais me le faire ! » quand elle chante ; à la fin de son
  chant, le coup de grâce « RETOURNE D'OÙ TU VIENS ! », puis le boss meurt. Pendant une bulle Link
  ne bouge pas : pas de jugement (les bulles tombent dans les mesures sans note). \heart = cœur
  (tools/check_text.py le compte pour 1 caractère).
- Le temps : wBalladeRhythmClock ($cde9), compté dans updateSound (le son tourne sur
  l'interruption du minuteur, pas sur les images) et remis à zéro quand le boss lance un morceau.
  make_music.py écrit la table des notes à frapper (data/ages/balladeRhythmNotes.s, depuis la
  mélodie de la boucle de music/rythme.txt) : changer la partition change le jeu.
- Rien n'y mène dans le jeu normal. Accès secret pour le tester : à l'écran titre, TENIR SELECT et
  appuyer sur START (petit son de secret), puis choisir un fichier : la partie commence dans 4:4a.
  Après le boss, le jeu revient au début (logos, titre). Le code est en SRAM $bff1 (effacé à chaque
  écran titre et à chaque début de partie) ; balladeRhythm.checkTestStart (appelé par
  initializeGame, bank1.s) remplace le point de départ, et le vrai est rendu en arrivant dans la
  salle (wBalladeRhythmSpawn) : sauvegarder pendant le test ne change pas le départ du fichier.
- Test + aperçu : python tools/test_rythme.py [DOSSIER] (ROM=...) -> out/rythme_apercu.wav (un
  joueur qui rate le 1er tour puis réussit les 5 niveaux, Marine, le coup de grâce) ; il rejoue
  aussi les vrais coups de Denis et le code secret. Étape en $cdec, coups en $cdeb.
- tools/rythme.html (navigateur) : la partition de la phrase avec un curseur ; Denis tape à la
  barre d'espace (tenue = épée maintenue), mêmes règles que le jeu ; le texte du résultat (écart de
  chaque note en images) se colle à Claude.
- À faire pour le vrai boss : le boss lui-même (ici : tremblement + SND_BOSS_DEAD), un repère visuel
  du rythme, qui donne l'épée (ici la salle de test la met sur A). Idée de Denis : le donjon final
  en 5 étages aussi, comme Lorule Castle.
