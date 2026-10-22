# Idées de scènes (à placer dans l'aventure)

Notées au fil des discussions avec Denis. Pas de spoil du twist ici.

Le plan des sept autres îles (formes, habitants, donjons, objets, musiques) : `story/iles.md`,
dessiné dans `docs/iles_plans.png` par `tools/make_plans.py`.

## Une séquence à la Metal Gear Solid: Ghost Babel (demandée par Denis)
- De l'infiltration pure : des fantômes qui avancent sur leur ronde, chacun avec un rayon d'action
  (un cône de vision) ; s'ils voient Link, on recommence. Le moteur est déjà là : les Veilleurs de
  la Cathédrale des Échos (les gardes d'Ambi, ambiGuard.s) ; il faudrait les habiller en fantômes
  et rendre leur regard visible.
- Pendant cette séquence, le HUD de *Ghost Babel* : la mini-carte en haut à droite (le radar), la
  vie en bas (avec nos cœurs), les objets à droite (les cases B et A, « NO ITEM » quand vides). Gros
  chantier : la barre d'état d'Ages est en haut et fait toute la largeur.

## Les photos de Cocolint (une scène avec Marine, pour créer du lien)
- Une vraie scène où Link et Marine passent du temps ensemble, comme la balade sur la plage de
  *Link's Awakening DX*, mais **plus longue** (moment à choisir). C'est pour s'attacher à Marine.
- Clin d'œil à l'album de la souris photographe de *Link's Awakening DX*. Dans une veillée ou
  dans le Songe, Marine fouille la poche de Link :
  > « Hé, qu'est-ce que tu as dans la poche… Oh ! Nos photos ! »
  > « Mais comment tu fais pour transporter tous ces objets ? Tu n'as même pas de sac à dos ! »
  > « …Mais tu as gardé une petite place pour nos photos. »
- Photos à commenter (montrées par Denis) :
  - Marine qui trébuche et tombe sur Link (« On ne parle PAS de celle-là. ») ;
  - Link et Marine en haut de la falaise ;
  - la photo de la plage, assis de dos face à la mer, avec des mouettes dans le ciel :
    > « Mais attends… il n'y avait personne avec nous ce jour-là ! Qui a pris cette photo ?! »
    Et Marine remarque qu'il y avait déjà des mouettes sur la photo… (petit frisson).

## Les jeux du forain (demandés par Denis)
Un seul personnage, un forain un peu louche sur la plage est de Port-Veille, avec **deux modes** :
- **Creuse-Rubis** : un démineur comme le « Creuse-Frissons » de *Skyward Sword*. On creuse des
  trous avec la pelle ; chaque trou donne un rubis dont la **couleur dit combien de bombes il y a
  autour** ; tomber sur une bombe = perdu. But : gagner de l'argent.
- **Mamono** : un démineur à monstres, comme le mode Mamono de *Xplosive Adventures* (le jeu de
  Denis) : chaque case cache un ennemi d'un niveau (du petit ennemi nul jusqu'au **Lynel**, très
  résistant) ; les chiffres donnent la somme des niveaux autour ; on bat les plus faibles pour
  monter de niveau avant d'oser s'attaquer aux gros.
- **Plusieurs niveaux de difficulté** dans chaque mode ; **les deux plus durs de chaque mode
  donnent un quart de cœur** (la première fois qu'on les gagne), comme toujours dans Zelda.
- Marine commente (« Vert = rien autour. Rouge... cours ! »).

## La plongée (idée de Denis, plongeur)
- Un mini-jeu de **plongée en apnée** : descendre récupérer des trucs au fond, de plus en plus
  profond. **Chaque cœur augmente le temps d'apnée** (donc la profondeur qu'on peut atteindre).
  Un peu comme la Maison des Coquillages de *Link's Awakening*, mais animé.
- **Au plus profond, la Master Sword**, enterrée (la Pelle). Il faut assez de cœurs pour y
  descendre : on les a **après le donjon 7** (3 au départ + un réceptacle par boss : 1, 2, 3, 4,
  6, 7 ; la Cathédrale n'a pas de boss = 9, plus les quarts trouvés). Régler la profondeur pour
  qu'avant le donjon 7 on voie le fond sans pouvoir l'atteindre.
- Quart de cœur à gagner, comme les deux autres mini-jeux.
- **Fait** (la Fosse de Bulle, story/salles/fosse.txt, tools/test_fosse.py) : Bulle, au club de
  plongée, propose la plongée après le Récif. Cinq profondeurs sous l'eau ; **les cœurs sont le
  souffle** (ils se vident d'un quart toutes les 1,5 s ; plus on en a, plus on descend) ; à bout de
  souffle, Bulle tire sur la corde. Des rubis, un **quart de cœur** à la profondeur 3, et au fond
  l'**Épée de Légende** plantée dans le sable : avec 8 cœurs on la voit, mais il faut le souffle de
  **9 cœurs** (après le donjon 7) pour la dégager. **Ganon ne craint qu'elle** (Tour Sans-Nuit,
  3F : sans elle, Marine pense à la Fosse). Pas de Pelle sous l'eau : l'épée se tire du sable.

## La planche de surf (demandée par Denis)
- Link a une **planche de surf** pour aller plus vite sur l'eau, comme Pikachu qui surfe dans
  *Pokémon*. À placer (un objet trouvé sur une île de mer : la Lagune ? un PNJ surfeur ?) ; dans
  le moteur : une vitesse de nage plus grande tant qu'on a l'objet (ou qu'on le tient sur B), et
  un sprite de Link debout sur la planche.
- **Fait (la vitesse)** : Bulle, la monitrice du club de plongée de la Lagune (3:24), donne sa
  planche de surf une fois le Récif Murmurant sauvé (GLOBALFLAG_BALLADE_SURF) ; avec elle, la nage
  aux Écailles de Sirène monte à SPEED_200 (contre $120, $160 avec l'anneau du nageur) : environ
  1,5 fois plus loin (tools/test_surf.py). **Reste** : le sprite de Link debout sur la planche.

## Gerudo Valley et le Chant des Tempêtes (demandés par Denis, scénario à trouver)
- **Le Chant des Tempêtes** (*Ocarina of Time*) : c'est la chanson de l'homme du moulin ; le Nid des
  Vents a des moulins qui repartent à la fin du chapitre 6 : ce pourrait être la « Sérénade du
  Vent » que Marine chante pour les relancer (ou un air de la Lanterne qui fait tourner le vent).
- **Gerudo Valley** : un endroit vivant et rapide : le forain et ses jeux, un marché, une île de
  pirates ou de désert dans la deuxième moitié, ou une course (le radeau ?).
- À écrire en partitions (music/*.txt) comme le village des Mouettes de LADX ; pas de
  désassemblage d'*Ocarina* sur la machine : transcrire.
- **Fait** : le Chant des Tempêtes (music/tempetes.txt, $2b, transcrit de mémoire, à vérifier à
  l'oreille : out/apercus/tempetes_apercu.wav) joue à la fin du chapitre 6, quand les moulins
  repartent.
- **Fait** : **Gerudo Valley** (music/gerudo.txt, $0b), la version violon de Taylor Davis que Denis
  adore, relevée dans son mp3 : la musique du forain (la plage du forain, 1:ac). 2e version validée
  (« excellent, on reconnaît ») : le violon sur l'onde (forme d'onde de corde frottée), pas de
  grosse basse, deux mesures de guitare puis le thème.

## Le temps ralenti (le tokitobashi de Hit, *Dragon Ball Super*) (demandé par Denis)
- Ses mots : « un objet pour ralentir le temps, un peu comme le tokitobashi de Hit dans Dragon
  Ball Super, ça ralentit le temps et du coup on peut s'exciter sur l'ennemi. Et à la reprise du
  cours normal, il se reçoit plein de dégâts et visuellement et au niveau du son on sent
  l'impact. »
- Pistes : ~3 s de temps figé (ennemis et projectiles arrêtés, Link bouge, couleurs grisées ou
  bleutées, musique coupée et un tic-tac) ; les coups sont comptés sans dégâts, puis tout d'un
  coup à la reprise : tremblement d'écran, flash blanc, gros son ; une recharge ou un coût.
- **Fait** : le **Sablier** (TREASURE_14 ; code/ages/balladeObjects.s, tools/test_sablier.py). La
  Lune qui tombe (Tour Sans-Nuit, 1F) le laisse tomber en remontant (clin d'œil à *Majora's Mask*).
  On le retourne (bouton B ou A) : 3 secondes de temps arrêté (ennemis et tirs figés, le décor
  assombri, un tic-tac), Link frappe à volonté sans être blessé ; puis les coups éclatent **en
  crescendo** (« les dégâts en crescendo », Denis) : autant de coups de tonnerre que de coups
  donnés, l'écran tremble de plus en plus, une grande explosion sur chaque ennemi touché, et le
  k-ième coup reçu par un ennemi compte k-1 de plus (3 coups = 3 de plus, 6 coups = 15 de plus).
  Recharge : 8 secondes (le sable retombe). À régler en jouant : la durée, la recharge, le bonus ;
  Ganon (seulement l'Épée de Légende) ne devra pas y céder.

## Le contre parfait (*Onimusha*) (demandé par Denis)
- Ses mots : « si on sort son épée au bon moment, un son puissant, et ça permet de se téléporter à
  côté de l'ennemi et de le one shot, comme dans Onimusha. »
- Pistes : une fenêtre de quelques images avant qu'un ennemi touche Link ; l'épée sortie dedans
  = son fort, flash, Link téléporté à côté, l'ennemi tué d'un coup.
- **Fait** (code/ages/balladeParry.s, tools/test_contre.py) : l'épée sortie moins de 12 images
  avant qu'un ennemi touche Link (BALLADE_PARRY_WINDOW) : pas de dégâts, une explosion sonore,
  l'écran tremble, Link passe de l'autre côté de l'ennemi, qui meurt d'un coup ; un boss perd 8
  points (sans mourir de ce coup). À régler en jouant : la fenêtre, le son, un vrai flash blanc.

## Le gantelet des âmes (*Onimusha*) : un donjon (demandé par Denis)
- Ses mots : « un donjon où on nous donne le gantelet pour absorber les âmes des ennemis (comme
  Onimusha justement) ; et à la fin le boss, c'est justement qu'il apparaît uniquement si on en a
  récupéré assez. Pendant ce temps les ennemis apparaissent toujours ; une fois qu'on en a assez,
  il apparaît et on va pouvoir le tuer. L'idée c'est de lui faire mal et d'aspirer ses âmes, et
  il maigrit au fur et à mesure, alors oui il disparaît au fur et à mesure, mais comme il maigrit
  il devient plus rapide. Ensuite le gantelet absorbe son âme et ça devient une relique ; mais on
  garde le bracelet pour pouvoir causer des dommages à distance aux ennemis et absorber leur
  vie. »

## Les cœurs : 12 au maximum
- 3 au départ + 7 réceptacles (un par boss) = 10 ; + 2 cœurs en quarts (8 quarts).
- Les quarts : le mini-jeu de plongée, le démineur (Creuse-Rubis / Mamono), un dans un coffre
  (endroit à choisir), et un **trésor à déterrer** : on trouve une **carte au trésor** qui
  indique un endroit en mer ; il faut y rester **plus de 10 secondes** (en plongée) pour l'avoir.

## Musique
- Fait : la Ballade chantée par Marine en mouette (écran titre), la Ballade énervée (boss),
  le miniboss façon *Hyrule Warriors*, l'île de la Brume, l'auberge jazzy, le Phare (music/).
- À venir : les autres îles, la carte de l'archipel ; garder les **thèmes orchestraux de
  *Hyrule Warriors*** en tête (grandeur, cuivres, percussions).
- **Le boss de fin en rythme** (idée de Denis) : la musique se tait, il ne reste qu'un tic-tac
  de métronome ; on frappe l'épée dans le vent (A) sur le rythme de la Ballade (« A A A... A A
  A... A A A A A... »). Chaque coup juste fait entendre une note de plus de la chanson, et plus
  on est dans le rythme, plus la chanson revient ; à la fin, Marine la chante par-dessus et le
  boss en meurt. Faisable : métronome sur le bruit, appuis comparés au compteur d'images, la
  mélodie jouée note à note (ou son volume monté) à chaque coup réussi.

## Le Songe
- Écran bleuté et qui ondule doucement, comme sous l'eau dans *Ages* (demandé par Denis).

## Graphismes de Marine humaine (Songe)
- Base possible : la branche `sprites/marin` d'oracles-disasm (Marine au format Oracle).
- Denis a trouvé des sprites étendus de Marine par **gekiganger3** sur DeviantArt
  (« Marin - Extended Sprites ») : à créditer, et demander son accord avant de les mettre
  dans le jeu (le dépôt est public).

## Déjà écrit dans la conversation de départ
- La veillée autour du feu : Link raconte sa vie en mimant (le lapin rose, les cocottes, la
  chanteuse Nayru, le rendez-vous avec Rosa, l'arbre amoureux, le kangourou boxeur, Zelda) ;
  Marine jalouse mais tendre ; Tingle qui s'incruste dans le rêve.
- Les Songes des Héros : rêves des autres Links (masques, fée qui crie, Zelda qui pousse Link
  d'une falaise à Célesbourg) et Marine qui commente ; le Sifflet de Marine (elle rattrape
  Link quand il tombe).
