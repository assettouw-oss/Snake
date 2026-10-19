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
affiché en bas à droite ; `P` ou `Échap` met la partie en pause.
Choisis **DÉCOUVERTE**, **NORMAL** ou **EXPERT** au menu (bouton ou touche `D`) :
la vitesse et la fréquence des obstacles changent selon la difficulté.
Chaque course propose une mission avec une récompense de 250 points ; le décor
évolue entre le centre de Bamako, le Sahel et le grand marché. Une collision
avec un obstacle termine immédiatement la course. Ramasse les pièces pour
gagner 25 points et les bonus dorés pour gagner 100 points.
Le menu propose aussi 10 routes avec des chaussées et marquages distincts
(piste en terre, passage piéton, berges, autoroute, route de nuit, dunes, etc.)
et des ambiances différentes. La première est disponible au départ ; chaque
route suivante se débloque en battant un nouveau record par tranche de
1 000 points, jusqu'à 9 000 points pour la dixième. Le menu indique le nombre
de routes débloquées et le score restant avant la prochaine. Utilise les boutons
`<` et `>` ou les flèches gauche/droite pour choisir parmi les routes débloquées.
Après une défaite, `Espace` ou `R` permet de recommencer. Le record est enregistré dans
`moto_bamako_save.json` à côté du script. Le jeu, la musique et les effets
sonores originaux sont contenus dans `main.py` ; appuie sur `M` pour couper ou
rétablir le son. La musique s'arrête à la fin de la course et reprend au
lancement de la partie suivante.

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
