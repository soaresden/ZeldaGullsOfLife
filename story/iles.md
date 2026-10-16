# Les îles de l'archipel : plans de fabrication

Le cahier des charges des sept îles qui restent, île par île : la forme, les écrans, les
habitants, le donjon (et sa forme), l'objet, les boss, les mini-jeux et la musique. Il part de
l'histoire écrite au début du projet (les rêves perdus, les couplets de Marine) et la traduit en
choses qu'on peut construire avec le moteur d'*Oracle of Ages*.

Pas de spoil ici au-delà de ce que Denis connaît déjà de l'histoire.

Les grilles (blocs `ile` et `donjon` ; `~` = la mer, `*` = le ciel) sont lues par `tools/make_plans.py`, qui dessine
`docs/iles_plans.png` : modifier une grille ici, relancer l'outil, et le plan suit.

## Les règles du jeu (pour toutes les îles)

- **Une île = un rêve perdu, un donjon, un objet, un boss, un couplet de Marine.** Le couplet est
  une phrase de sa chanson ; à la fin, les huit phrases forment la *Ballade de la Mouette*.
- **Le Réel et le Songe** partout : chaque île a son double bleuté (copie automatique, comme
  l'île de la Brume). Au moins une énigme par île ne se résout qu'en passant de l'un à l'autre
  avec la Lanterne, et le noctambule (le temps compté dans le Songe) reste la règle dehors.
- **Taille** : une île fait de 12 à 20 écrans (l'île de la Brume en fait 16). Les donjons
  grandissent doucement : 12 salles pour le premier (5 minutes), jusqu'à 22 pour le septième ; la
  Tour Sans-Nuit a 5 étages.
- **Chaque donjon a une forme** qu'on reconnaît sur la carte (Select), comme le Phare : un coffre
  à jouets, un cœur, une enclume, une cathédrale, une spirale, un flocon, une tour.
- **Chaque boss parle** en entrant, et Marine lui répond (comme Jack).
- **Voyager** : le Bateau-Rondin part du ponton de chaque île. On choisit sa destination sur la
  carte de l'archipel (pas de mer à traverser écran par écran : trop de salles). Une île n'apparaît
  sur la carte qu'une fois que Marine l'a repérée en lisant le vent.
- **Les cœurs** (12 au maximum, voir idees.md) : un réceptacle par boss, et 8 quarts répartis
  ci-dessous.

## L'ordre des objets

| Île | Objet du donjon | Objet trouvé dehors | Ce qu'il ouvre ensuite |
| --- | --- | --- | --- |
| 1. Brume | Lanterne des Songes (harpe) | Épée (le pêcheur) | Réel ↔ Songe, torches |
| 2. Hameau-Grelot | Boomerang-Toupie (boomerang) | Bombes (la boutique) | interrupteurs lointains, buissons |
| 3. Lagune des Serments | Écailles de Sirène (costume de sirène) | Palmes de Zora | plonger, nager sous l'eau |
| 4. Mont-Braise | Canne des Songes (canne de Somaria) | Bracelet de force (la forgeronne) | créer des blocs, soulever |
| 5. Île des Échos | Grappin-Écho (Switch Hook) | Pelle (le fossoyeur) | échanger sa place, creuser |
| 6. Nid des Vents | Cape de Roc (plume niveau 2) | Plume de Roc (au pied du nid) | sauter, planer |
| 7. Grand Sommeil | Clochette d'Aube (la flûte d'*Ages*, réécrite) | Lance-Graines | réveiller les dormeurs |
| 8. Œil de l'Insomnis | (tout) | — | la fin |

Tous ces objets marchent dans notre ROM (le boomerang et la cape viennent de *Seasons*, déjà
présents dans hack-base). La Clochette demande un peu de code : la flûte réveille un dormeur
devant Link au lieu d'appeler un animal.

---

## 2. Hameau-Grelot · le Jeu

*Un village de jouets en bois sur une île ronde comme un grelot. Les enfants sont assis en rang ;
ils ne courent plus, ils ne font plus semblant.*

**Forme** : ronde, avec une jetée qui fait la poignée du grelot. Décor : la ville de Symétrie du
passé (couleurs vives, toits ronds) ; le Songe y ajoute des confettis.

```ile 2
~ | Colline aux cerfs-volants | Manège arrêté | ~
Bois des cache-cache | La place du Grelot | Boutique de Pépin | Plage aux châteaux de sable
Terrain de jeu vide | Maison de Lila | École des Bonnets | Jardin des toupies
~ | Jetée (Bateau-Rondin) | Grotte de la Boîte | ~
```

**Habitants** (leur rêve perdu va dans le Carnet des Rêves) :
- **Lila**, la petite fille qui ne sait plus faire semblant. Le donjon est dans son rêve.
- **Pépin**, le marchand de jouets, qui vend des bombes « pour les feux d'artifice qu'on ne
  tire plus ». Il rêvait d'ouvrir un cirque.
- **Mme Bonnet**, la maîtresse d'école : elle fait réciter les tables, sans fin. Rêve perdu :
  raconter des histoires.
- **Les jumeaux Tic et Tac**, qui jouent à cache-cache sans se cacher. Dans le Songe, ils se
  cachent pour de vrai : les retrouver (5 cachettes) donne un **quart de cœur**.
- **Un vieux cerf-volant** accroché à un arbre, qui parle (seulement dans le Songe).

**Le Songe** : la place est un plateau de jeu de l'oie géant. Le pont-levis du château de sable
n'existe que dans le Songe.

**Donjon : le Coffre à Jouets** (dans le rêve de Lila ; on y entre en s'endormant près d'elle).
Forme : **une malle à jouets**, un rectangle large avec son couvercle. Décor : le donjon de la
Couronne d'*Ages* (sols de couleur, cubes à faire rouler). Énigmes : cubes de couleur, blocs qui
dansent, le boomerang qui frappe les interrupteurs derrière les grilles.

```donjon 2
. | # | # | B | # | # | .
# | # | # | M | # | # | #
# | C | # | # | # | K | #
# | # | # | E | # | # | #
```

- **Mini-boss : le Soldat de Plomb** (l'Armos Warrior : contourner son bouclier).
- **Boss : Pantin-Sans-Fil** (la Head Thwomp, recolorée en tête de marionnette) : le boomerang
  l'étourdit, puis on lui lance des bombes dans la tête. Il parle : « Qui tient mes fils ?
  Personne ! Alors je danse tout seul… et je t'écrase ! » Marine : « Tu danses mal. »
- Couplet 2. Les enfants rejouent ; Lila invente un chevalier qui ressemble à Link.

**Mini-jeux** : la course de Tic et Tac (le cache-cache), et le **stand de Pépin** (le tir aux
pipes de *Ages*, avec des toupies au lieu de cibles).

---

## 3. Lagune des Serments · l'Amour

*Un atoll : une couronne de sable autour d'une lagune turquoise. Un vieux couple vit dans la même
maison et se présente chaque matin comme deux inconnus.*

**Forme** : un anneau ; on fait le tour à pied, et on ne traverse la lagune qu'à la nage (Palmes).
Décor : la plage de l'île du Croissant et le village des Zoras ; dessous, la mer d'*Ages*.

```ile 3
Récif nord | Plage des serments | Maison d'Héloïse et Gaspard | Phare de corail
Rochers aux coquillages | Lagune (nage) | Lagune (nage) | Club de plongée
Ponton (Bateau-Rondin) | Lagune (nage) | Lagune (nage) | Grotte des amoureux
~ | Plage des bouteilles | Récif Murmurant (entrée) | ~
```

**Habitants** :
- **Héloïse et Gaspard**, le vieux couple. Gaspard donne les **Palmes de Zora** « à quelqu'un
  qui a encore quelqu'un à retrouver ».
- **Bulle**, la monitrice du club de plongée : le **mini-jeu de plongée** (voir idees.md),
  l'apnée dépend du nombre de cœurs. **Quart de cœur** au niveau le plus profond.
- **Le facteur des bouteilles**, qui ramasse les messages à la mer et ne sait plus à qui les
  rendre. Rêve perdu : recevoir une lettre.
- **Une sirène boudeuse** sous l'eau, qui a oublié la chanson de sa sœur.

**La carte au trésor** se trouve ici (dans une bouteille) : elle montre un point de la mer, au
large de l'île des Échos ; il faut y plonger plus de 10 secondes. **Quart de cœur.**

**Donjon : le Récif Murmurant** (sous l'eau). Forme : **un cœur**. Marine ne peut pas suivre :
c'est le seul donjon où Link est seul. Décor : la Grotte des Sirènes / Jabu-Jabu (salles sous
l'eau). Énigmes : coquillages-échos à faire chanter dans le bon ordre, courants.

```donjon 3
. | # | # | . | # | # | .
# | # | M | # | # | C | #
# | # | # | # | # | # | #
. | # | # | # | # | # | .
. | . | # | K | # | . | .
. | . | . | E | . | . | .
. | . | . | B | . | . | .
```

(Le boss est sous l'entrée : on redescend tout au fond, à la pointe du cœur.)

- **Objet : les Écailles de Sirène** (le costume de sirène d'*Ages*) : nager sous l'eau.
- **Mini-boss : la Baudroie** (Angler Fish).
- **Boss : la Murène du Silence** (Octogon) : elle avale les mots doux ; on la bat en faisant
  chanter les coquillages-échos autour d'elle, puis à l'épée. Elle ne parle pas : elle a tout
  avalé. Marine, en surface, ne dit rien non plus.
- Couplet 3. « Tu as été long. Ne refais jamais ça. »

**Pêche** : les Pierres de Pêche (le jeu de pêche) sont sur la plage des bouteilles. Le poisson
ultime est un minuscule Poisson-Rêve.

---

## 4. Mont-Braise · la Création

*Un volcan endormi ; des forgerons, des peintres et des musiciens qui recopient la même chose à
l'infini.*

**Forme** : un cône, avec un chemin qui monte en lacets jusqu'au cratère. Décor : la Crête
Roulante d'*Ages* (rochers, lave, grottes des Gorons).

```ile 4
~ | ~ | Cratère (la Forge) | ~ | ~
~ | Atelier des peintres | Lacets | Source chaude | ~
Mine abandonnée | Lacets | Village goron | Lacets | Belvédère
Ponton (Bateau-Rondin) | Plage noire | Marché des copies | Plage noire | ~
```

**Habitants** :
- **Forgeronne Brasia** (Goron), aux 412 épées identiques. Elle donne le **Bracelet de force**
  quand on lui apporte une idée (un objet de la chaîne de troc).
- **Pinceau**, un peintre qui peint toujours le même volcan. Le Songe lui montre la mer.
- **Les Cuivres**, une fanfare goron qui joue la même note : la **danse goron** d'*Ages* devient
  leur mini-jeu (suivre le rythme). **Quart de cœur.**
- **Le marchand de copies**, qui vend des objets en double (et un faux quart de cœur).

**Donjon : la Forge Endormie.** Forme : **une enclume**. Décor : les grottes des Gorons et la
Salle des Rites (lave). Énigmes : la Canne des Songes crée un bloc ; un bloc sur une plaque de
pression, un bloc dans la lave pour marcher dessus, deux blocs pour coincer un ennemi. L'idée
de l'histoire (combiner ce que Marine a vu le jour) devient : certains blocs n'apparaissent que
dans le Songe.

```donjon 4
# | # | # | # | # | # | #
# | M | # | B | # | C | #
. | . | # | # | # | . | .
. | . | # | K | # | . | .
. | # | # | E | # | # | .
```

- **Objet : la Canne des Songes** (la canne de Somaria).
- **Mini-boss : les Copies** (le Link Mimic) : de faux Link qui font tout comme lui.
- **Boss : Copiator** (Ramrock, le golem de pierre aux quatre phases) : chaque phase se bat avec
  un objet différent, et il copie la précédente. Il parle : « Montre-moi. Tout ce que tu fais,
  je le refais. En mieux. » Marine : « Et ça, tu sais le faire ? » (elle chante).
- Couplet 4.

---

## 5. Île des Échos · le Souvenir

*Une île de deuil, grise et silencieuse, avec un cimetière qui sonne quand le vent passe.*

**Forme** : **une cloche**, large en bas, la cathédrale au sommet. Décor : le cimetière d'*Ages*
(arbres morts, tombes) ; le Songe y est couleur sépia.

```ile 5
~ | ~ | Cathédrale des Échos | ~ | ~
~ | Allée des cloches | Parvis | Allée des cloches | ~
Cimetière ouest | Maison du fossoyeur | Place du silence | Chapelle | Cimetière est
Ponton (Bateau-Rondin) | Plage grise | Plage grise | Plage grise | Rocher de la veuve
```

**Habitants** :
- **Le fossoyeur Bêche**, qui prête la **Pelle** pour « déterrer ce qui doit l'être ».
- **La veuve Marée**, sur son rocher, qui ne rêve plus de son mari pêcheur.
- **Un enfant, Noé**, qui ne se souvient plus de la voix de sa grand-mère. Dans le Songe, on
  la retrouve (elle cache un **quart de cœur** dans sa boîte à couture).
- **Le sonneur**, qui sonne les cloches pour ne pas entendre le silence.

**Donjon : la Cathédrale des Échos.** Forme : **une croix de cathédrale** (la nef, le transept,
le chœur). Décor : le Tombeau Ancien d'*Ages*. C'est une **Nuit Blanche** : l'Insomnis rôde ;
s'il voit Link, Link se réveille à l'entrée de la salle. Le Grappin-Écho sert à échanger sa
place avec les statues pour se cacher derrière elles.

```donjon 5
. | . | . | C | . | . | .
. | . | # | # | # | . | .
# | # | # | M | # | # | #
. | . | # | # | # | . | .
. | . | # | K | # | . | .
. | . | # | E | # | . | .
```

- **Objet : le Grappin-Écho** (le Switch Hook).
- **Mini-boss : le Gardien des Cloches** (le Stalfos bleu).
- **Pas de boss.** Au fond du chœur, la maison de Marine à Mabe, et Tarkin (voir l'histoire).
  On peut y mettre la musique du village des Mouettes de *Link's Awakening DX* (son
  désassemblage est autorisé).
- Couplet 5, le plus beau.

---

## 6. Nid des Vents · la Liberté

*Une île qui flotte au-dessus des nuages. On ne l'atteint qu'en remontant un courant d'air que
Marine repère en lisant le vent.*

**Forme** : **une plume**, longue et fine, posée de travers dans le ciel. Décor : les Pics de
Talus d'*Ages* (rochers en hauteur) ; le bord de l'écran donne sur le vide (tomber = revenir au
dernier sol).

```ile 6
* | * | * | Le Nid (Spirale Céleste)
* | * | Pont de nuages | Corniche
* | Moulins à vent | Village des plumes | *
Courant ascendant (arrivée) | Prairie suspendue | * | *
```

**Habitants** :
- **Mère Plume**, la gardienne du nid, qui donne la **Plume de Roc**.
- **Zéphyr**, un garçon qui construit des ailes et n'ose plus sauter. Rêve perdu : voler.
- **Les meuniers**, dont les moulins ne tournent plus : la Sérénade du Vent les relance.
- **Un Rito égaré** (clin d'œil à *Wind Waker*), qui a oublié comment rentrer chez lui.

**Donjon : la Spirale Céleste.** Forme : **une spirale** qui s'enroule vers le centre. Décor : le
Donjon des Ailes d'*Ages*. Énigmes : sauts et vols planés au-dessus des trous, courants d'air.

```donjon 6
# | # | # | # | #
# | M | # | B | #
# | # | C | # | #
# | . | . | K | #
# | # | # | # | E
```

- **Objet : la Cape de Roc** (la plume niveau 2 : sauter plus loin, planer).
- **Mini-boss : Vire**, le démon-chauve-souris.
- **Boss : l'Ombre de Marine** (le Swoop, l'oiseau géant, en noir) : une mouette de cauchemar
  avec la voix de Marine. Elle parle : « Reste endormi, Link. Reste avec moi. » Marine (la
  vraie) : « …Non. »
- Couplet 6, et la Sérénade du Vent.

---

## 7. Île du Grand Sommeil · le Réveil

*Ici, tout le monde dort, et refuse de se réveiller. L'île gèle doucement.*

**Forme** : **un flocon**, avec ses branches de glace. Décor : *Ages* n'a pas de neige ; on la
fabrique comme le Songe, en recolorant des décors existants (le village et les falaises en blanc
et bleu glacé), avec la Salle des Rites version glace pour le palais.

```ile 7
~ | Branche nord | ~ | Branche nord-est | ~
Branche ouest | Village gelé | Palais Givré | Village gelé | Branche est
~ | Lac de glace | Maison du veilleur | Lac de glace | ~
~ | Ponton (Bateau-Rondin) | Branche sud | ~ | ~
```

**Habitants** (presque tous endormis : on les réveille avec la Clochette, un par un) :
- **Le roi d'une nuit**, furieux d'être réveillé : « Dans mon rêve, j'étais roi ! »
- **Une famille** qui dort depuis trois ans ; la petite sœur, seule réveillée, attend.
- **Le veilleur**, le seul qui ne dort pas : il garde la **Clochette d'Aube** et le **Lance-Graines**.
- **Une chanteuse** qui chante en dormant. Réveillée, elle apprend à Marine à tenir une note
  (le **mini-jeu de chant** : appuyer en rythme). **Quart de cœur.**

**Donjon : le Palais Givré.** Forme : **un flocon** à six branches (sur la grille : quatre
branches et le cœur). Décor : la Salle des Rites, palette glace. Énigmes : sols glissants, blocs
de glace à faire fondre (graines de feu du Lance-Graines), dormeurs qui bloquent les couloirs.

```donjon 7
. | . | # | # | # | . | .
# | . | # | C | # | . | #
# | # | # | # | # | # | #
. | M | # | B | # | K | .
# | # | # | # | # | # | #
# | . | # | # | # | . | #
. | . | # | E | # | . | .
```

- **Objet : la Clochette d'Aube** (la flûte réécrite).
- **Mini-boss : le Chevalier Gelé** (Stalfos bleu, palette glace).
- **Boss : Givrolin** (King Moblin recoloré en géant de glace) : il lance des boules de neige
  explosives qu'on lui renvoie avec le bracelet. « Laissez-les dormir ! Le froid, c'est doux. Le
  froid, ça ne fait pas mal. » Marine : « Si. Ça fait mal quand ça s'arrête. »
- Couplet 7. La fresque du Poisson-Rêve (la vérité sur l'Insomnis).

---

## 8. Œil de l'Insomnis · la Tour Sans-Nuit

*Une tour noire qui n'apparaît que quand le soleil et la lune sont dans le ciel en même temps.
On l'ouvre en jouant les sept duos.*

**Forme** : un rocher en forme d'œil, et la tour au milieu. Décor : la Tour Noire d'*Ages*
(dehors et dedans), son sommet pour le dernier étage.

```ile 8
~ | Paupière nord | ~
Paupière ouest | La Tour Sans-Nuit | Paupière est
~ | Ponton (Bateau-Rondin) | ~
```

**Le donjon final, inspiré du Château de Lorule** (*A Link Between Worlds*) : **5 étages**, et la
musique qui **gagne un instrument à chaque étage**. Au rez-de-chaussée, presque rien : un
métronome et une basse. Au sommet, tout l'orchestre, et la voix de Marine. Les cinq niveaux de
musique du boss en rythme (session « Prototype of the rhythm final boss », MUS $47, $49, $4b,
$37, $3a) servent aussi aux cinq étages : toute la tour est un long crescendo jusqu'au combat.

Chaque étage reprend un cauchemar de Link et une mécanique du jeu :

| Étage | Le cauchemar | Ce qu'on y refait | Ce que la musique gagne |
| --- | --- | --- | --- |
| 1 | **La Lune qui tombe** (un compte à rebours au plafond) | Réel ↔ Songe, torches | métronome + basse |
| 2 | **Dark Link** (Link Mimic, en duel) : Marine ne peut pas aider | Boomerang, bombes | + percussions |
| 3 | **Ganon** (celui d'*Ages*, version *A Link to the Past*) : éteindre et rallumer les torches | Canne des Songes, Grappin | + harmonie (cuivres) |
| 4 | **Le Cauchemar de Cocolint** : « TU ME RECONNAIS ? » | Cape de Roc, Clochette | + contre-chant |
| 5 | **L'Insomnis** : le boss en rythme, la berceuse | l'épée, en rythme | + la voix de Marine |

```donjon 8
. | # | 5 | # | .
. | # | 4 | # | .
. | # | 3 | # | .
. | # | 2 | # | .
# | # | 1 | # | #
. | . | E | . | .
```

(Un étage par ligne : chaque étage fait 5 à 8 salles autour de l'escalier, dessinées comme les
autres donjons quand on y sera.)

---

## Les habitants de l'île de la Brume (déjà dans le jeu, pour le Carnet)

L'aubergiste (dormir), le vieux pêcheur (l'épée), la dame insomniaque, le vieux qui compte les
moutons, l'ado qui rêve d'être marin, les deux enfants qui ne jouent plus ; plus tard, le forain
(Creuse-Rubis et Mamono, deux quarts de cœur).

**Les 8 quarts de cœur** : le forain ×2 (Brume), Tic et Tac (Grelot), la plongée et la carte au
trésor (Lagune), la fanfare goron (Mont-Braise), la grand-mère de Noé (Échos), la chanteuse
(Grand Sommeil).

---

## La musique

Tout est original (sauf les clins d'œil autorisés à *Link's Awakening DX*), écrit en partitions
texte dans `music/` et écouté par Denis avant d'être poussé. Les grands combats gardent l'esprit
des orchestres de *Hyrule Warriors* : cuivres, percussions, grandeur.

**Déjà fait** : l'écran titre (la Ballade chantée par Marine), l'île de la Brume, l'auberge, le
Phare Éteint, le thème du jeu (la *Ballade de la Mouette*), le boss (la Ballade en colère), le
mini-boss, le Veilleur Creux (en réserve), le boss en rythme (5 niveaux).

**À écrire** :

| Morceau | Où | L'idée |
| --- | --- | --- |
| La mer (Bateau-Rondin) | la carte de l'archipel, en voyage | large et marin, à la *Wind Waker* (le bateau) ; la Ballade cachée dans la basse |
| Hameau-Grelot | île 2 | boîte à musique et petite fanfare, en 6/8, un peu de travers |
| Le Coffre à Jouets | donjon 2 | xylophone et tambour de jouet, mystérieux mais gai |
| Lagune des Serments | île 3 | lent, tendre, guitare de plage ; le thème d'Héloïse et Gaspard |
| Le Récif Murmurant | donjon 3 | sous l'eau : nappes, échos, presque pas de mélodie (Link est seul) |
| La plongée | mini-jeu | une boucle calme qui s'accélère avec la profondeur |
| Mont-Braise | île 4 | enclumes en percussion (le bruit), cuivres goron |
| La Forge Endormie | donjon 4 | lourd, la même phrase répétée… qui finit par changer |
| Île des Échos | île 5 | une cloche, une mélodie qui revient en écho plus faible |
| La Cathédrale (Nuit Blanche) | donjon 5 | tension d'infiltration : un tic-tac, des silences |
| La maison de Tarkin | donjon 5 | le village des Mouettes de *Link's Awakening DX* (autorisé), ralenti |
| Nid des Vents | île 6 | aérien, arpèges rapides, flûte |
| La Spirale Céleste | donjon 6 | montée en spirale (gammes qui grimpent) |
| L'Ombre de Marine | boss 6 | la Ballade de la Mouette en mineur, déformée |
| Île du Grand Sommeil | île 7 | berceuse glacée, très lente, qui s'endort à la fin de la boucle |
| Le Palais Givré | donjon 7 | cristallin, aigu |
| L'Insomnis | partout où il parle | un motif court et doux (il fait peur parce qu'il est gentil) |
| Couplet obtenu | après chaque boss | un jingle : la phrase de la chanson de Marine qu'on vient de gagner |
| La Tour Sans-Nuit | donjon 8 | les 5 niveaux du boss en rythme (voir plus haut) |
| L'épilogue et le générique | la fin | la chanson complète de Marine, aux huit couplets |
| Le forain | mini-jeux de la Brume | orgue de foire, un peu louche |

Numéros : les musiques d'*Ages* qu'on n'utilise plus (leurs lieux n'existent pas chez nous) sont
libres de reprendre ; les numéros vides $24, $3b et $3d aussi. Le boss en rythme a pris $37,
$3a, $47, $48, $49 et $4b.

---

## Où ranger les écrans (groupe 1 = le Réel, groupe 0 = le Songe)

L'île de la Brume occupe 1:79-ac. Proposition pour les autres (une case = un écran, ligne puis
colonne de la grille 16 × 16 d'*Ages*) :

| Île | Écrans | Taille |
| --- | --- | --- |
| 2. Hameau-Grelot | 1:00-33 | 4 × 4 |
| 3. Lagune des Serments | 1:04-37 | 4 × 4 |
| 4. Mont-Braise | 1:08-3c | 4 × 5 |
| 5. Île des Échos | 1:40-74 | 4 × 5 |
| 6. Nid des Vents | 1:4c-7f | 4 × 4 |
| 7. Grand Sommeil | 1:b0-e4 | 4 × 5 |
| 8. Œil de l'Insomnis | 1:b8-da | 3 × 3 |

Les écrans entre les îles restent de la mer : on ne les visite pas (on voyage par la carte).
Les donjons vont dans le groupe 4 (le Phare y est déjà) puis le groupe 5.
