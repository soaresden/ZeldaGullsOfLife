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

## Chapitre 3 : la Lagune des Serments (île 3)
- story/salles/ile_lagune.txt (1:04-37, décor 18 ; Songe 7e) : un fer à cheval de sable autour
  d'une lagune ; lagune = $fa (TILETYPE_WATER : on y nage avec les Palmes), mer = $fc (SEAWATER :
  on s'y noie sans le costume de sirène, et on ne peut pas y changer d'écran) ; un récif de rochers
  $f4 (solides) sépare les deux ; l'îlot du sud (1:35-36) ne s'atteint qu'à la nage. Briques de
  rivage du décor 18 : convexes 20 21 22 26 27 28 24 2a, coins rentrants 29 (eau en bas à droite)
  et 2b (en bas à gauche) ; il n'en existe PAS pour l'eau en haut à gauche / à droite : éviter ces
  formes. Le plan a été tracé d'une grande carte 40 x 32 avec rivages automatiques (script jetable).
- Portes (tuiles $dc-$df, $ed-$ef dehors) : maison 1:06 -> 3:23, club 1:17 -> 3:24, grotte des
  amoureux 1:27 -> 5:b1 (coffre de 50 rubis). Les warps / roomGfxChanges / roomTileChanger d'Ages
  sur 0:/1:04-37 sont commentés (« la Lagune des Serments »). Dans le Songe, portes fermées.
- L'énigme du Songe : Gaspard (INTERAC_BALLADE_OBJECT $11) a jeté une bouteille, restée sur l'îlot
  de 1:15 ; dans le Songe (0:14-0:15, story/salles/songe.txt) la lagune s'ouvre en deux (fe/ff,
  fond 1a/1b) jusqu'à elle ($12 : l'objet d'échange 1, le papier à lettres d'Ages renommé
  « Bouteille », TX_005b / TX_090a). Gaspard la reprend et donne les Palmes de Zora (TX_0031,
  TX_0918). Héloïse $0e, Bulle $0f (une Zora), le facteur $10 : habitants à deux répliques
  (masque d'essence $04). Le Récif Murmurant (1:36) : un totem dont la bouche (dd) sera l'entrée
  du donjon 3 ; Marine ne suit pas sous l'eau (TX_5a7b).
- Le noctambule (7 s dans le Songe) : Link ne se réveille pas sur le fond de la mer ouverte, ni
  pendant un défilement d'écran (sinon : réveil dans l'eau profonde du Réel, noyades jusqu'au
  game over) ; la Lanterne refuse de marcher sur ce fond (harpFluteParent.s).
- Musique : $25 (music/lagune.txt) ; le Récif : $18 (music/recif.txt).
- Test : python tools/test_lagune.py DOSSIER (tout le chapitre jusqu'aux Palmes, la nage, les
  habitants ; un saut g.warp depuis un intérieur rend la Lanterne muette : sortir par la porte).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/lagune.png

## Le Récif Murmurant (donjon 3)
- story/salles/recif.txt (plans tirés d'un script jetable) : groupe 5, les salles de la Grotte des
  Sirènes d'Ages côté passé ; décors 3c (sec) et 3d (sous l'eau) passés à l'index de donjon 3
  (tilesets.s, b0 $2c -> $23). dungeon03LayoutRecif, deux étages : B1 2d / 30 2e 35 ; 1F 37 36 39 /
  3a 3b 38 3c 3d / 3e 3f 40 / 44. Entrée : la bouche du visage de corail (1:36, dd) -> 5:44 $97 ;
  sortie -> 1:36 $44. Link est seul : Select ne fait rien (marineTalk, checkBombPower : donjon 3).
- Plonger : B en nageant sur fc (il faut les Écailles de Sirène = TREASURE_MERMAID_SUIT) ->
  l'étage du dessous, même case ; remonter : B sur une case autorisée par underwaterSurfaceData.s
  (salles 5:30 lignes 8-9 colonnes 1-6, 5:35 lignes 1-4 colonnes 12-13, 5:2d : bitmaps d'Ages
  gardés, nos plans les respectent). Ailleurs dans un donjon, on ne remonte pas. Sous l'eau, les
  passages ouest / est font trois cases (Link glisse).
- Vire = le mini-boss (la Baudroie d'iles.md, l'Angler Fish, demande les graines odorantes et une
  salle à défilement latéral à sec : abandonnée). Il apparaît quand Link s'avance au milieu.
  Textes TX_2f12-2f18 réécrits (plus de Veran). Son coffre : les Écailles ($12 $02).
- La Murène du Silence = Octogon d'Ages, dans ses salles d'origine (5:36 surface, 5:2d dessous ;
  porte de droite de 5:36 murée), préparé par $90 $0f dans l'antichambre 5:38 ; script de mort
  $20 $01 (dungeonScript_bossDeath du donjon 3) ; l'essence apparaît dans sa salle (objet $08,
  drapeau $80 de 5:36) ; elle ramène sur la plage des bouteilles (1:35) : fin du chapitre 3
  (@endings : 1:35 puis 3:23), Mont-Braise repéré (GLOBALFLAG_BALLADE_ISLAND4).
- Les coquillages-échos (5:39, INTERAC_BALLADE_OBJECT $13) : briques $11 ; A (ou B) face au grand
  (ligne 2, colonne 7) : il chante l'ordre (flûtes de Ricky, Dimitri, Moosh) ; toucher les petits
  dans cet ordre -> setTile du coffre de la clé du boss ($8b), drapeau $40 de la salle.
- Pièges : objets.txt ne doit avoir qu'UNE liste par salle (la 2e remplaçait la 1re : make_rooms
  refuse maintenant) ; arrivalTalk et la fin de chapitre (étape 0) utilisent tous deux le drapeau
  $40 de la salle : ne pas les mettre dans la même salle.
- Test : python tools/test_recif.py DOSSIER (tout le donjon, ennemis et boss retirés ; sous l'eau,
  swim_to : petits coups de bouton, Link glisse).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/recif.png

## Chapitre 4 : Mont-Braise (île 4)
- story/salles/ile_braise.txt (1:08-3c, 5 x 4 ; tracé par un script jetable) : décor 1e (la Crête
  Roulante d'Ages, passé) ; son Songe = le décor 06 (à la place de la ville de Symétrie en ruine :
  make_songe.py, l'entrée 0x06 de tilesets.s est sur une ligne avec « ; Tileset 0x06 »).
  Passages : nord / sud colonnes 4-5, est / ouest lignes 3-4. Rochers c0 : Bracelet de force
  (garder le bouton face au rocher et tirer) -> sol 3a. La mine (1:28, dd) -> 5:b2 (un coffre).
- La quête : Pinceau (1:19, $15) ne peint que le volcan ; dans le Songe (0:19, $16) il voit la mer,
  peint le tableau (l'objet d'échange 2 : le sac puant d'Ages redessiné, art/tableau.txt, palette
  5) ; Brasia (1:2a, $14) a une idée : le Bracelet de force (TX_0026, TX_092b) ; les rochers du nord
  du village s'ouvrent sur les lacets (1:1a) et le cratère (1:0a, la bouche du grand visage : la
  Forge Endormie, donjon 4). Les Cuivres ($17), le marchand de copies ($18) : villager (la table
  @texts est maintenant cherchée par sous-type).
- Piège : $1a / $1b sont du sol à Mont-Braise : la Lanterne et le noctambule ne regardent le « fond
  de la mer ouverte » que dans les décors $7d et $7e (wTilesetIndex).
- Test : python tools/test_braise.py DOSSIER (arrivée, radeau, Pinceau dans les deux mondes, le
  tableau, Brasia, les rochers, le cratère, la mine, le marché). Dans le Songe, attendre la fin du
  rayon de lumière (~160 images) avant d'agir.
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/braise.png

## La Forge Endormie (donjon 4)
- story/salles/forge.txt (tracé par un script jetable) : groupe 4, les salles du Donjon de la
  Couronne d'Ages (décor 3a passé à l'index de donjon 4 : tilesets.s $25 -> $24), un étage en
  enclume (dungeon04LayoutForge) : ae af b0 b1 b2 / be bf b6 / b9 ba bb bc bd. Entrée : la bouche
  du grand visage du cratère (1:0a, dd) -> 4:bb $97 ; sortie -> 1:0a $24.
- Les Copies (mini-boss) = 4 Arm Mimics (la liste d'Ages group4Mapc8EnemyObjectData, en
  obj_BeforeEvent : ils ne reviennent pas) ; volets $1e $08-$0b ; puis la Canne des Songes (la
  canne de Somaria, TX_0073 / TX_093c). Copiator = Smog d'Ages dans sa salle (4:bf, volet du haut
  muré), TX_2f26 réécrit (Marine lui répond en chantant) ; l'essence apparaît en (7, 3) (à l'écart
  des blocs du combat ; elle ne tombe que si Link arrive juste en dessous, centré).
- Boutons : PART_BUTTON avec le bit 7 du sous-type ($80, $81) ne reste pressé que sous un poids
  (Link, bloc poussé, bloc de la Canne) ; sans le bit 7, un seul pas le bloque pour de bon. Le
  coffre qui apparaît selon wActiveTriggers : INTERAC_DUNGEON_EVENTS $21 $17 Y=position X=valeur.
  Un bloc de la Canne se pose une case devant Link (appui bref pour se tourner, sinon Link avance
  sur le bouton).
- Fin du chapitre 4 (@endings : 1:2a) : le village fête la Forge, Marine lit le vent (l'île des
  Échos, GLOBALFLAG_BALLADE_ISLAND5).
- Musiques : $26 (music/braise.txt, Mont-Braise, au lieu de la maison des Tokays), $17
  (music/forge.txt, au lieu du Donjon de la Couronne).
- Musiques de l'île 5 et du donjon 5 : $13 (music/echos.txt, l'île des Échos et la cabane, au
  lieu du Tombeau des Esprits), $1a (music/cathedrale.txt, la Nuit Blanche, au lieu du Tombeau
  Ancien), $19 (music/tarkin.txt, la maison de Tarkin : le village des Mouettes de LADX recopié de
  MusicMabeVillage, ralenti ; les notes de LADX sont une octave plus bas que les nôtres : C_1 = c2).
- Test : python tools/test_forge.py DOSSIER (tout le donjon, ennemis et boss retirés).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/forge.png

## Chapitre 5 : l'île des Échos (île 5)
- story/salles/ile_echos.txt (1:40-74, 5 x 4 ; tracé par un script jetable) : décor 13 (le cimetière
  de Yoll d'Ages, passé) ; son Songe = le décor 07 (copie sépia, make_songe.py). Passages : nord /
  sud colonnes 4-5, est / ouest lignes 3-4. La cabane du fossoyeur (1:61, dd) -> 3:25 (copie du
  décor 2b de 3:9e, story/salles/echos_interieurs.txt).
- La quête : Bêche ($19) prête la Pelle ; Noé ($1a, place du silence 1:62) ne se souvient plus de
  la voix de sa grand-mère ; dans le Songe (0:62), Mamie Rose ($1b) dit où est enterrée la clé
  (devant la tombe fleurie du cimetière de l'est, 1:64, case 5:5 : $1e, invisible) ; la Pelle la
  déterre (la clé du cimetière d'Ages, donnée tout de suite par giveTreasure : sinon Ages la pose
  par terre) ; Mamie Rose donne alors le quart de cœur (ROOMFLAG_ITEM de 0:62) ; la grille de la
  cathédrale (1:42, $1f) s'ouvre avec la clé (A face à elle) -> dd. Le sonneur ($1d), la veuve
  Marée ($1c) : villager.
- Menu de test : île 5 Plage (1:70) / Ville (1:62) ; jalon 19 = Pelle + clé + drapeaux de 1:64 et 1:42.
- Test : python tools/test_echos.py DOSSIER (arrivée, Bêche, Noé, Mamie Rose dans le Songe, la clé,
  le quart de cœur, la grille, la veuve Marée).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/echos.png

## La Cathédrale des Échos (donjon 5)
- story/salles/cathedrale.txt (tracé par un script jetable) : groupe 5, les salles du Tombeau Ancien
  d'Ages (décor 40 passé à l'index de donjon 5 : tilesets.s $28 -> $25), un étage en croix
  (dungeon05LayoutCathedrale) : 7b / 7c 7d 7f / 80 81 82 83 85 86 89 / 8b 8d 8e / 8f 90 91 /
  92 aa 93. Entrée : la grille de 1:42 (dd) -> 5:aa $97 ; sortie -> 1:42 $54.
- Nuit Blanche : les Veilleurs de l'Insomnis = ENEMY_AMBI_GUARD (les gardes du palais d'Ambi),
  sous-types $0d-$14, leurs rondes à la fin de ambiGuard.s (ms_* : une ronde part de la position
  de l'objet ; « ms_down $58 » sur place = se tourner). Ils voient en ligne droite devant eux (un
  rayon arrêté par les murs et les statues, pas par les trous) et à une case autour, devant. S'ils
  voient Link : dans le donjon 5, pas de CUTSCENE_BOOTED_FROM_PALACE mais un warp vers la même
  salle, à wLinkLocalRespawnY/X (là où Link est entré) : il se réveille à l'entrée de la salle.
  Toujours une statue devant les portes des salles gardées (sinon on se réveille sous leurs yeux).
- Banque 0e (code des ennemis) pleine : la résurrection de Ganon (enemyCode60, fin du jeu lié)
  n'est plus qu'un `jp enemyDelete` dans Ages.
- Le Grappin-Écho (le Switch Hook, TREASURE_OBJECT_SWITCH_HOOK_00, TX_0030 / TX_093d) : portée 5
  cases ; les diamants db (tile des donjons). Les diamants reviennent à leur place en rentrant
  dans la salle : jamais devant une porte, et un diamant de chaque coté de chaque gouffre. Viser
  avec une case libre devant soi : au bord d'un trou, Link glisse dedans et le grappin ne part pas.
  Les coffres ne s'ouvrent que par en dessous.
- Le Gardien des Cloches = le Stalfos bleu d'Ages (obj_BeforeEvent group5Map82BeforeEventObjectData),
  volets $1e $09-$0b, INTERAC_DUNGEON_SCRIPT $00 (sa mort : le portail). Pas de boss : la clé du
  chœur (la clé du boss, 5:89) ouvre le chœur (5:7b) ; l'escalier -> le souvenir (3:26, la maison
  de Marine à Mabe, décor 2b) : Tarkin ($20, le moustachu d'Ages) ; Marine lui chante le couplet
  (drapeau $80 de 3:26 = wPastRoomFlags+$26) ; au retour, l'essence tombe dans le chœur.
- Fin du chapitre 5 (@endings : 1:62) : les cloches chantent la chanson de Mamie Rose, Marine lit
  le vent (le Nid des Vents, GLOBALFLAG_BALLADE_ISLAND6 ; l'île 6 n'existe pas encore : le radeau
  y mène à la Brume).
- arrivalTalk attend 8 images et qu'aucun texte ne soit ouvert (le nom du donjon d'abord).
- Menu de test : île 5 Donjon (5:aa) / M-boss (5:83, le Grappin) / Boss (5:7d, la clé du chœur) /
  Fin (1:62, l'essence) ; jalons 20-22.
- Test : python tools/test_cathedrale.py DOSSIER (tout le donjon ; les Veilleurs lus dans la
  mémoire : on passe quand ils regardent ailleurs ; une fois exprès sous leurs yeux).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/cathedrale.png

## Chapitre 6 : le Nid des Vents (île 6)
- story/salles/ile_nid.txt (1:45-78, 4 x 4 ; tracé par un script jetable ; 1:4c-7f prévus dans
  iles.md touchaient la Brume en 7c) : décor 1a (les Pics de Talus d'Ages, passé) ; son Songe = le
  décor 08 (copie bleutée, make_songe.py ; l'entrée 0x08 de tilesets.s est sur une ligne). Une
  plume dans le ciel : 75 l'arrivée -> 76 prairie -> 66 moulins -> 67 village -> 57 pont de nuages
  -> 58 corniche -> 48 le Nid ; le reste = le ciel.
- Le ciel = la brique f3 (le seul trou des extérieurs, hazards.s) redessinée en bleu clair dans le
  décor 1a (tilesetMappings1a.bin : tuile unie $80, palette 7 ; paletteData4d00, palette 5 :
  couleur 0 = le bleu du ciel). On y tombe : retour au dernier sol.
- Ponts : 0e = pont vertical (on n'en sort pas sur le coté), 1f = pont horizontal (1d / 1e : les
  bouts) ; on ne descend pas d'un pont horizontal : une case de sol au bout.
- La quête : le Rito égaré ($21), les meuniers ($24), Zéphyr ($22 ; dans le Songe $23 : « les nuages
  tiennent ») : villager. Le pont de nuages (1:57) a deux trous ; dans le Songe (0:57, songe.txt)
  le pont est entier : on traverse avant le noctambule. Mère Plume ($25, 1:48) donne la Plume de
  Roc (TX_0027, TX_092c) ; avec elle on saute les trous ; l'entrée du Nid (dd, 1:48) est derrière
  un trou.
- Bug corrigé : la Lanterne et le réveil du noctambule remettent wcddf à zéro (sinon, après un
  « renvoyé par une force étrange », la salle suivante reprenait la disposition de la salle de
  départ : le Réel dans le Songe). Lanterne collé à un habitant qui est au même endroit dans
  l'autre monde : Link est renvoyé (comme dans Ages).
- Menu de test : île 6 Plage (1:75) / Ville (1:67) ; jalon 23 = la fin du chapitre 5 vue.
- Test : python tools/test_nid.py DOSSIER (arrivée, radeau à 6 îles, chute dans le ciel, Rito,
  meunier, Zéphyr dans les deux mondes, le pont par le Songe, Mère Plume, les sauts).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/nid.png

## La Spirale Céleste (donjon 6)
- story/salles/spirale.txt (tracé par un script jetable, avec un solveur pour le carrelage) :
  groupe 4, salles 4:3c-48 et 4:4b-54, décor 3b = le Donjon des Ailes (déjà pris par le Coffre à
  Jouets, index 2) recopié par make_songe.py à l'index de donjon 6, en bleuté ; l'entrée 0x3b de
  tilesets.s est sur une ligne (render_room.py ne sait pas la lire). Un étage en spirale
  (dungeon06LayoutSpirale). Entrée : le dd du Nid (1:48, derrière un trou : la Plume) -> 4:3c $97.
- Portées mesurées : la Plume saute ~2 cases (un gouffre de 2 avec de l'élan), la Cape ~4 (un
  gouffre de 3 ; le second appui ~20 images après le premier) ; le Grappin 5 cases. Donc : 1-2
  cases = Plume, 3 = Cape ou Grappin. Vers le bas, partir une case avant le trou (les pieds de Link
  y arrivent plus tôt : il glisse et ne saute pas). Deux lignes de sol entre deux tranchées.
- Les énigmes : 3e le bouton sur l'îlot (PART_BUTTON $80) : un bloc de la Canne dessus ouvre le
  volet (door controller $07, bit 0) ; 3f trois cases de gouffre : le Grappin et deux diamants ;
  42 le carrelage (INTERAC_TILE_FILLER $25 + INTERAC_DUNGEON_EVENTS $11 : tout peindre d'un seul
  trait, 16 solutions) ; 43 le cristal (PART_SWITCH $08) au Boomerang -> INTERAC_TRIGGER_TRANSLATOR
  $31 -> volet du nord ($1e $04, X = bit 3) ; 46 le Grappin puis un saut ; 4c -> 4d le cristal
  (bit 2 de wSwitchState) jette un pont dans la salle suivante (commonTileSubstitutions.s, appliqué
  au chargement) ; 3d le raccourci du cœur (4e -> 3d) n'est franchissable qu'à la Cape.
- Après un échange au Grappin, le diamant reprend sa place ~70 images plus tard (là où était Link).
- Les changements de cases d'Ages des salles reprises sont commentés (roomSpecificTileChanges.s :
  4c, 4e, 52 ; commonTileSubstitutions.s : 4c, 4e, 53).
- Le Fouisseur = le Subterror d'Ages (ses objets de 4:4d) ; l'Ombre de Marine = le Swoop (4:34,
  recoloré violet-noir : PALH_OMBRE $d5, palette 6 des sprites, enemyData $71 -> $60),
  INTERAC_DUNGEON_SCRIPT $01 ajouté au donjon 6 (dungeonScript_bossDeath : le cœur) ; l'essence
  (wGroup4RoomFlags+$54) ramène au village des plumes (1:67) : les moulins, Zéphyr, le Rito ;
  Marine lit le vent (l'île du Grand Sommeil, GLOBALFLAG_BALLADE_ISLAND7).
- Musiques : $15 le Nid des Vents (music/nid.txt), $14 la Spirale Céleste (music/spirale.txt).
- Menu de test : île 6 Donjon / M-boss (la Cape) / Boss (4:53, la clé du boss) / Fin ; jalons 24-27.
- Test : python tools/test_spirale.py DOSSIER (chaque énigme jouée comme un joueur).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/spirale.png

## Chapitre 7 : l'île du Grand Sommeil (île 7)
- story/salles/ile_sommeil.txt (1:a0-d4, 5 x 4 ; tracé par un script jetable). La carte d'Ages
  s'arrête à la ligne d (14 x 14 écrans) : on ne défile pas vers la ligne e (1:e? seulement par
  téléportation). Un flocon : ponton d1, branche sud d2, maison du veilleur c2, lacs de glace c1 /
  c3, village gelé b1 / b3, le Palais Givré b2, branches b0 / b4 / a1 / a3.
- Décor 0d = le village du passé (10) sous la neige (make_songe.py : ice(), à la place des Hautes
  Terres de Nuun) ; son Songe = le 0e (dream(ice())). La glace (TILETYPE_ICE, brique ea dehors, 8a
  dans les donjons) n'est dessinée par aucun décor : make_songe.py (PATCHES) lui donne des tuiles.
- Intérieurs 3:27 (le veilleur), 3:28 (la famille), 3:29 (la chanteuse) : copies de l'auberge. Les
  salles 3:XX partagent leurs drapeaux avec 1:XX : la chanteuse garde les siens dans 1:b3.
- La quête : le veilleur ($27) donne le Lance-Graines (TREASURE_SHOOTER, avec la sacoche et 20
  graines de feu ; il en remet si moins de 10). La porte du palais (1:b2, $2d) est un mur f6 tant
  que le drapeau $80 de 1:b2 n'est pas mis. Dans le Songe (0:b2, songe.txt), l'étang n'est pas
  gelé : le cristal (PART_SWITCH $40 = la brique 9e dehors, dessinée en losange par make_songe.py)
  sur l'îlot, des buissons en face : seulement en biais (le Lance-Graines tourne en tenant B, une
  pression vers la droite = un huitième de tour). $2e voit le bit 6 de wSwitchState et met le
  drapeau de 1:b2. Le roi d'une nuit dort (1:d2, $26) ; dans le Songe (0:d2, $2c) il est roi et
  dit de frapper en biais. Dormeurs ($26, $2a, $2b) : immobiles tant que l'essence 7 manque.
  La chanteuse ($29) : la Clochette d'Aube (la flûte, wLinkPlayingInstrument non nul) à moins de
  2 cases la réveille ; quart de cœur.
- Menu de test : île 7 Plage (1:d1) / Ville (1:b1) ; jalon 28 = la fin du chapitre 6 vue.
- Test : python tools/test_sommeil.py DOSSIER (arrivée, le roi, le veilleur, la porte gelée, le
  cristal du Songe, la porte dégelée, le roi du Songe, la famille, l'entrée du palais).
  Planche : https://raw.githubusercontent.com/soaresden/ZeldaGullsOfLife/main/docs/tests/sommeil.png
- Compiler quand le Python du Store refuse (« Permission denied ») : PYTHON=/c/msys64/clang64/bin/python.exe
  et /c/msys64/clang64/bin en tête du PATH (Pillow y est installé : pacman,
  mingw-w64-clang-x86_64-python-pillow).

## Pièges déjà rencontrés
- La brique 64 (bord de roche) est une FALAISE dans tous les décors d'extérieur (cliffTiles.s,
  ANGLE_DOWN) : Link saute par-dessus en marchant vers le bas et tombe dans l'écran du dessous.
  Pour un mur de roche, prendre 60 (Mont-Braise, île des Échos).
- Salle de boss / mini-boss d'Ages : les portes doivent être OUVERTES dans le plan (a0) et fermées par
  INTERAC_DOOR_CONTROLLER $08-0b. Un volet déjà fermé dans le plan ne compte pas dans wcc93 : le
  boss (Fouisseur, Swoop…) attend indéfiniment que wcc93 retombe et Link reste gelé.
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
  La ROM Ages (USA) est dans D:\DOCS\Documents\GitHub\ZeldaOracleCombinedFR\. Versions : v1.0/N
  (tag v1.0-N) = N donjons jouables ; v1.0-2 = chapitres 1-2 (ROM obtenue CRC32 6f5d4e60).
- Nom des donjons sur la carte : tools/make_blurbs.py (NAMES ; lettres manquantes dessinées dans
  DRAWN) ; la version française a son gfx header (GFXH_DUNGEON_N_BLURB_FR) et une ligne dans
  balladeLangGfxHeaders (data/ages/gfxHeaders.s).
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
  - $3d MUS_BALLADE_GRELOT : music/grelot.txt, Hameau-Grelot (1:00-33, 0:00-33, 3:21-22, 2:21),
    boîte à musique + fanfare de jouets en 6/8, un peu de travers (hémiole dans le pont).
  - $3b MUS_BALLADE_COFFRE : music/coffre.txt, le Coffre à Jouets (4:2b-3b), xylophone, tambour,
    contrebasse ; refrain en sol, marche des soldats de bois.
  - $25 MUS_BALLADE_LAGUNE : music/lagune.txt, la Lagune (valse lente, guitare de plage) ; au
    lieu de MUS_SYMMETRY_PAST. $18 MUS_BALLADE_RECIF : music/recif.txt, le Récif Murmurant
    (nappes, écho, gouttes) ; au lieu de MUS_MERMAIDS_CAVE.
  - Plus AUCUN numéro vide : $24 n'est PAS libre (MUS_SYMMETRY_PRESENT, avec un cas spécial dans
    bank1.s). Pour une nouvelle île, réutiliser un morceau d'Ages qu'on n'entend plus (comme $25
    et $18 : vérifier qu'aucun code ne le teste, grep MUS_xxx).
- SND_BALLADE_GULL = $d6 : cri de mouette de LADX (JINGLE_SEAGULL) porté image par image ; joué au
  clin d'œil de Marine dans le film. Le même cri existe dans la musique (`mouette:3`).
- Denis accepte qu'on reprenne sons, musiques et objets de Link's Awakening DX
  (https://github.com/zladx/LADX-Disassembly) ; pas la VF de Nintendo pour les textes.
- Le désassemblage de LADX est sur la machine : D:\DOCS\Documents\GitHub\ZeldaOracleCombinedFR\LADX-Disassembly-main
  (sons : src/code/audio/, musiques, sprites : src/gfx/...). Le lire là plutôt que sur GitHub.
- Aperçus à écouter : `python tools/record_music.py [film titre phare ile auberge boss veilleur
  miniboss theme grelot coffre lagune recif braise forge echos cathedrale tarkin]` -> out/NOM_apercu.wav ; `ROM=chemin` pour une autre ROM ; les morceaux sans
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
  frapper. Numéros pris parmi les musiques vides d'Ages ($3b et $3d sont depuis pris par l'île 2).
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
