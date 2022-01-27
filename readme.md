# AlphaGo
Ce projet s'inscrit dans le module Applications de l'Intelligence Artificielle. Il a pour objectif de réimplémenter AlphaGo, la célèbre IA qui a battu le champion du monde de Go en 2015. Nous avons repris les articles parus à l'époque, et d'autres qui voyaient l'évolution d'AlphaGo en AlphaGoZero.

## Installation
La liste des bibliothèques utilisées pour ce projets est dans le fichier requirements.txt. L'archive pour être extraite à la racine pour bien fonctionner.

Premièrement, ouvrir un terminal et créer un venv avec Python >3.8 et faire la commande `pip install -r requirements.txt`. (Modifier le chemin d'accès vers requirements.txt si nécessaire)
Installer jupyter lab localement avec `pip install jupyterlab`.

Une fois les différents bibliothèques installées, il est possible de lancer des parties avec la commande `py namedGame.py (X.py) gogolePlayer.py` avec `(X.py)` le nom d'un autre joueur (randomPlauer, gnugoPlayer...). 

## Organisation du projet
Ce projet est divisé en deux parties, une partie utilisant la logique et structure d'un MCTS (arbre de recherche) et une deuxième partie avec un réseau en Deep Learning permettant d'évaluer les coups pour l'exploration du graph.  
### MCTS
L'organisation du MCTS est dans le fichier `graph.py`, dans les class `Node` et `Graph`. La première classe `Node` représente un noeud du graph d'exploration des coups à jouer. Un noeud est associé à un coup possible, a un parent et des enfants et stock les différentes valeurs/évalutation du coup. La deuxième classe `Graph` représente le graph d'exploration des différents couts possible. Il possède un noeud racine (source de l'exploration) et est conservé ou reconstruit selon les coups joués.

### Réseau neuronal

Le réseau utilisé est le même que dans le papier AlphaGoZero. Il s'agit d'un réseau à convolutions, qui prend les 9 derniers tableaux, et renvoie:
--> une value: estimation de la probabilité du joueur courant de gagner la partie.
--> une policy: distribution de probabilités sur 82 valeurs, indiquant quel coup devrait jouer le joueur courant. Il y a 82 coups car il y a toutes les actions du plateau et il est possible de ne pas jouer.

Le réseau est créé dans le notebook value_and_policy_networks.ipynb. Attention à la première cellule qu'il est nécessaire de modifier si vous travaillez sur google colab, d'enlever sinon.


Dans les 8 premiers coups, les tableaux insérés pour compléter les 9 entrées sont des tableaux de 0.
Le modèle créé est ensuite sauvegaré à l'aide de callbacks keras si l'entraînement est interrompu.
Le modèle final est sauvegardé dans 'models/' afin d'être facilement chargé pendant que l'on déroule une partie.

## Fil d'exécution d'une partie

+ `GogolePlayer.__init__()` : Création du player 
+ `Graph.__init__()` : Création du graph
+ Tant que la partie n'est pas finie:
  + `MyPlayer.getPlayerMove()` : On demande au player le move qu'il veut jouer
    + `Graph.train()` : On veut explorer le graph avec un variable `depth` qui représente le nombre de branche explorées (sur un cran)
      + `Graph.canConserve()` -> Est ce qu'on peut conserver le graph ou repartir sur un nouveau noeud racine ?
      + On répète `depth` fois : 
        + `Graph.developBranch()` : On descend les noeuds en prennant le meilleur enfant (U + Q) 
        + `Node.exploreChildren()` : On regarde tous les coups possible à la suite du node, et on calcul U et Q avec `Node.defineU()` et `Node.defineQ()` grace au réseau de neurones chargé dans le fichier `neuronalModel.py`.
    + `Graph.probas()` : On récupère les probas de jouer chaque coup (à partir des N et pas U, Q).
    + On effectue le meilleur coup possible.
+ Fin de partie, on regarde qui a gagné.

## Résulats

Au début du premier tour du player, il y a un petit délai le temps que TensorFlow & le modèle neuronal load. Ensuite, on peut noter un temps non négligeable d'attente entre chaque coup (~20sec sur un mauvais CPU portable) pour 3 de depth (voir `graph.py`).

On arrive tout de même avec un coup très significatif à chaque étape.
[Un résultat du plateau à une étape](https://i.ibb.co/GtT0ZsX/AlphaGo.png)