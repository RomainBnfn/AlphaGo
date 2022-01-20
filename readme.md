# AlphaGo
[Description brève du projet]
## Installation
La liste des bibliothèques utilisées pour ce projets est dans le fichier requirements.txt. L'archive pour être extraite à la racine pour bien fonctionner.

Premièrement, ouvrir un terminal et créer un venv avec Python >3.8 et faire la commande `pip install -r requirements.txt`. (Modifier le chemin d'accès vers requirements.txt si nécessaire)

Une fois les différents bibliothèques installées, il est possible de lancer des parties avec la commande `py namedGame.py (X.py) gogolePlayer.py` avec `(X.py)` le nom d'un autre joueur (randomPlauer, gnugoPlayer...). 

## Organisation du projet
Ce projet est divisé en deux parties, une partie utilisant la logique et structure d'un MCTS (arbre de recherche) et une deuxième partie avec un réseau en Deep Learning permettant d'évaluer les coups pour l'exploration du graph.  
### MCTS
L'organisation du MCTS est dans le fichier `graph.py`, dans les class `Node` et `Graph`. La première classe `Node` représente un noeud du graph d'exploration des coups à jouer. Un noeud est associé à un coup possible, a un parent et des enfants et stock les différentes valeurs/évalutation du coup. La deuxième classe `Graph` représente le graph d'exploration des différents couts possible. Il possède un noeud racine (source de l'exploration) et est conservé ou reconstruit selon les coups joués.

### Réseau neuronal
[Description]

## Fil d'éxécution du player
**Exécution**

+ Création du player: 
+ Création du graph (unique)
+ getPlayerMove()
  + train _graph() (parler de depth)
  + Conservation ?
  + Choisir une branche à développer
    + Développer 
    + Coups possibles
    + Couts des coups
+ graph.probas()
    + Selon N et pas les couts
+  move
