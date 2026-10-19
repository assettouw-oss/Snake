# Snake

Jeu Snake créé avec Python et Pygame. La version web est construite avec
[Pygbag](https://pygame-web.github.io/) et publiée sur GitHub Pages.

## Application de gestion immobilière

Le dossier contient également une application web autonome pour gérer un
portefeuille immobilier et suivre les loyers.

1. Ouvre `index.html` dans un navigateur.
2. Ajoute tes biens, puis indique chaque loyer comme encaissé depuis le tableau.
3. Les biens et les paiements sont enregistrés dans le stockage local du navigateur.

Cette première version fonctionne sans serveur ni compte utilisateur. Les données
restent dans le navigateur utilisé et ne sont pas synchronisées entre appareils.

## Jouer en local

Installe Pygame avec `python -m pip install pygame`, puis lance `python main.py`
depuis ce dossier.

Le menu permet de choisir entre trois niveaux de difficulté. Pendant une partie,
utilise les flèches ou ZQSD pour diriger le serpent ; `P` ou la barre d’espace
met la partie en pause, et `Échap` met en pause ou revient au menu depuis la
pause. Chaque fruit rapporte 10 points et la vitesse augmente progressivement.
Sur téléphone, ouvre le jeu dans le navigateur, touche **JOUER**, puis glisse sur
le plateau pour diriger le serpent. Tu peux aussi utiliser les grosses flèches
tactiles et le bouton **PAUSE**. Le record est sauvegardé dans `snake_save.json`
à côté du jeu (dans la version web, la sauvegarde dépend du navigateur utilisé).

## Publier le jeu en ligne

1. Crée un dépôt GitHub nommé `Snake` et ajoute les fichiers de ce dossier.
2. Dans **Settings > Actions > General**, choisis **Read and write permissions**
   pour les permissions du workflow.
3. Envoie les fichiers sur la branche `main`. Le workflow construit le jeu pour
   le navigateur et crée la branche `gh-pages`. Tu peux suivre l’avancement dans
   l’onglet **Actions**.
4. Une fois le premier workflow terminé, dans **Settings > Pages**, sélectionne
   la branche `gh-pages` comme source du site.

L’adresse du jeu sera de la forme
`https://TON-NOM-GITHUB.github.io/Snake/`.
Ouvre cette adresse depuis le navigateur du téléphone pour jouer sans installer
Python ni Pygame. Après chaque mise à jour envoyée sur `main`, attends la fin du
workflow **Build and publish Snake**, puis recharge la page sur ton téléphone.

## Moto Bamako (jeu Pygame)

Le projet inclut aussi un jeu de course autonome dans `main.py`. Il nécessite
Pygame et se lance avec `py -3.13 main.py` sous Windows (ou avec l'interpréteur
Python de VS Code si Pygame y est installé). Depuis le menu, clique sur **JOUER**
ou appuie sur `Espace` / `Entrée`. Au premier lancement, un tutoriel interactif
présente les commandes clavier et téléphone ; appuie sur **C'EST PARTI !** ou
`Entrée` pour commencer. Le tutoriel n'est affiché qu'une fois et son état est
conservé dans `moto_bamako_save.json`. Pendant la course, `Espace`, `Flèche haut`
ou un clic fait sauter la moto. Sur téléphone, touche le bouton **SAUTER**
affiché en bas à droite ; touche-le deux fois rapidement pour faire un double
saut et prolonger l'ascension. Le double appui fonctionne aussi au clavier.
Le deuxième saut déclenche un salto visuel de la moto, sans ajouter de troisième saut.
`P` ou `Échap` met la partie en pause.
Choisis **DÉCOUVERTE**, **NORMAL** ou **EXPERT** dans **RÉGLAGES** (ou avec `D`) :
la vitesse et la fréquence des obstacles changent selon la difficulté.
Chaque course propose une mission avec une récompense de 250 points ; le décor
évolue entre le centre de Bamako, le Sahel et le grand marché. Une collision
avec un obstacle termine immédiatement la course. Ramasse les pièces pour
gagner 25 points et les bonus dorés pour gagner 100 points.
Les pièges comprennent maintenant les trous, dos-d'âne, Sotrama, grosses pierres,
barrières de chantier et bidons ; il faut les sauter ou les éviter en dirigeant
la moto, car tout contact met fin à la course.
Le menu propose 33 routes avec des chaussées, marquages, paysages et ambiances
visuelles différents (piste en terre, berges, autoroute, route de nuit, dunes,
forêt, lac, falaises, etc.). La première est disponible au départ ; chaque
route suivante se débloque en battant un nouveau record par tranche de
1 000 points, jusqu'à 32 000 points pour la route 33. Le menu indique le nombre
de routes débloquées et le score restant avant la prochaine. Utilise les boutons
`<` et `>` ou les flèches gauche/droite pour choisir parmi les routes débloquées.
Chaque route a maintenant des couleurs de terrain et de chaussée harmonisées,
avec un léger reflet sur la route pour mieux la distinguer.
Après une défaite, `Espace` ou `R` permet de recommencer. Le record est enregistré dans
`moto_bamako_save.json` à côté du script. Le jeu, la musique et les effets
sonores originaux sont générés directement dans `main.py`, sans fichier audio
externe. Chaque route possède sa mélodie et son tempo. La sonorité alterne entre
plusieurs instruments synthétisés (piano, cloche, marimba, orgue, corde pincée
et synthétiseur) ; les effets sonores reprennent l'instrument et la tonalité de
la route sélectionnée. Le bouton
**RÉGLAGES** du menu permet de modifier
le volume de la musique et des effets, la difficulté et l'affichage des boutons
tactiles de direction. Les boutons tactiles de saut et de pause restent
disponibles ; si les commandes de direction sont désactivées, le saut tactile
fonctionne toujours. Les préférences sont sauvegardées avec le record. Appuie
sur `M` pour couper ou rétablir le son. La musique s'arrête à la fin de la course
et reprend au lancement de la partie suivante.

### Jouer sur téléphone

Le workflow GitHub Actions ci-dessus construit `main.py` avec Pygbag et publie
le jeu sur GitHub Pages. Une fois la publication terminée, ouvre le site publié
dans le navigateur du téléphone et touche l'écran pour démarrer. Pendant la
course, le bouton **SAUTER** est en bas à droite ; le bouton **pause** est juste
au-dessus. Maintiens **RECULER** ou **AVANCER** en bas à gauche pour déplacer
la moto. Au clavier, utilise aussi les flèches `←` et `→` ou `A` et `D`.
Mets le téléphone à l'horizontale pour profiter de tout l'écran.
La boucle du jeu cède régulièrement le contrôle au navigateur pour permettre
au rendu Web et aux événements tactiles de fonctionner.

