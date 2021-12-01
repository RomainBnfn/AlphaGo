import numpy as np
import random
import Goban

rd = random.Random()

class Graph: 
    
    def __init__(self, board, color):
        # Initilialise le graph à une certaine position pour une certaine couleur.
        self.racineNode = Node(None, board, None, color)
        self.board = board
        self.c = 0
        
    def tau(self):
        if self.c < 10:
            return 1
        return 1 / self.c
        
    def setRacine(self, node):
        self.racineNode = node
        node.makeRacine()
    
    def train(self, depth, nbRollOut):
        """Entraine le graph avec [depth] nouvelles profondeurs avec [nbRollOut] nombre de 
        roll out à chaque noeud 

        Args:
            depth (number): le nb de profondeur
            nbRollOut (number): le pn de roll out à chaque noeud
        """
        # Conservation du graph
        moves = self.getTwoLastMoves()
        if len(moves) > 2:
            # Le jeu a déjà au moins 2 coups joués
            canConserve, node = self.canConserve()
            if not canConserve:
                node = Node(Node, None, Goban.Board.flip(self.color) )
                depth += 1 # On rajoute de la depth car l'arbre a été reconstruit
            self.setRacine(node)
        # Exploration 
        for _ in range(depth):
            self.developBranch(nbRollOut)
        self.c += 2 # Deux tours entre chaque train
    
    def developBranch(self, nbRollOut):
        node = self.racineNode
        while node.hasBeenExplored:
            # On descend jusqu'à trouver une branche non explorée
            index = np.argmax(node.childrenScore)
            node = node.children[index]
        self.developNode(node, nbRollOut)
    
    def getMoveProbas(self):
        tauInv = 1 / self.tau
        #
        childrenN = np.array(self.racineNode.ChildrenN)
        sumNTau = 0
        for N in ChildrenN:
            sumNTau += N ^ tauInv
        #
        probas = np.zeros(82)
        for i in range(len(childrenN)):
            node = self._actualNode.children[i]
            x, y = Goban.Board.unflatten(node.move)
            index = fromXYToIndex(x, y)
            probas[index] = node.N ^ tauInv / sumNTau
        probas = probas / np.sum(probas) # normalize
        return probas
        
    def developNode(self, node, nbRollOut):
        node.exploreChildren(self.board, nbRollOut)
    
    def canConserve(self):
        twoLastMoves = self.getTwoLastMoves()
        node = self.findNode(twoLastMoves)
        return node is not None, node

    def getTwoLastMoves(self):
        # Entre deux étapes il y a 2 coups joués (le notre et celui de l'adversaire)
        moves = self.board._historyMoveNames
        if(len(moves) < 2):
            return moves
        return moves[-2:]
        
    def findNode(self, moves):
        """Retourne le Node si on effectue une suite de coups à partir du noeud racine actuel. 
         (Peut renvoyer None si la suite de coup correspond à un chemin non exploré)

        Args:
            moves ([string[]]): La liste des coups à effectuer

        Returns:
            [Node | None]: Le noeud correspondant
        """
        lastNode = self.racineNode
        for move in moves:
            if move is None: 
                return None
            isSet = False 
            for child in lastNode.children:
                if child.move == move:
                    lastNode = child
                    isSet = True
                    break
            if not isSet:
                # Le noeud joué n'est pas dans les enfants déjà étudiés. (par exemple enfants non développés)
                return None
        return lastNode   

    

class Node:
    C = 1

    def __init__(self, move, parent, color):
        """Noeud

        Args:
            move (string): Le coup qui doit être joué pour arrivé du plus proche parent à ce noeud
            parent (Node): Le Noeud du parent précédent 
            color (int): La couleur du joueur du noeud
        """
        self._move = move  # Le coup qui doit être joué pour arrivé du plus proche parent à ce noeud
        self._parent = parent
        self._children = []
        if parent is not None:
            parent.addChildren(self)
        self._Q = 0
        self._U = 0
        self._N = 0
        self._color = color
    
    def addChildren(self, children):
        self._children.append(children)          

    def visitParents(self):
        parent = self.parent
        while parent is not None:
            parent.N += 1
            parent = parent.parent 
            
    def exploreChildren(self, board, nbRollOut):
        if self.hasBeenExplored:
            return
        #
        compteur = self.goToOurMove()
        colorNextMove = Goban.Board.flip(self.color)
        for move in board.legal_moves():
            node = Node(move, board, self, colorNextMove)
            node.evaluateQ(board, nbRollOut)
            node.N += 1
            # Explore older nodes
            self.N += 1
            self.visitParents()
        self.undoMoves(compteur)
        return self.children

    def evaluateQ(self, board, nbRollOut):
        """Evaluation de Q -> EN ÉTANT AU NOEUD PARENT PRECEDENT (sur le Board)

        Args:
            board ([Goban.Board]): Le plateau
            nbRollOut ([int]): Le nb de roll out

        Returns:
            [double]: Q
        """
        board.push(self.move)
        wins = 0
        for _ in range(nbRollOut):
            compteur = 0
            while not board.is_game_over():
                moves = board.legal_moves()
                move = rd.choice(moves)
                board.push(move)
                compteur += 1
            res = board.result()
            if (res == '1-0' and self.color == 1) or (res == '0-1' and self.color == 2):
                wins += 1
            self.undoMoves(compteur)
        board.pop()
        self._Q = wins / nbRollOut
        return self._Q
    
    # --
    #

    def makeRacine(self) :
        self.parent = None
        self.move = None
    
    def undoMoves(self, board, k):
        for i in range(k):
            board.pop()

    def goToOurMove(self, board):
        k = 0
        moves = [self.move]
        parent = self.parent
        while parent is not None:
            moves.insert(0, parent.move)
            parent = parent.parent
        for move in moves:
            if move is None:
                break
            board.push(move)
            k += 1
        return k
            
    # - - - - - - - - - - - - - - - - - -
    #           Properties 
    #

    @property
    def U(self):
        if not self.hasParent:
            return 0
        SNb = 0  # Somme des Nb
        for child in self.parent.children:
            SNb += child.N
        return SNb / (1 + self.N) 
    
    @property
    def childrenScore(self):
        _childrenScore = []
        for child in self.children:
            _childrenScore.append(child.U + child.Q)
        return _childrenScore

    @property
    def childrenN(self):
        _childrenN = []
        for child in self.children:
            _childrenN.append(child.N)
        return _childrenN
    
    @property
    def hasBeenExplored(self):
        return len(self.children) > 0

    @property
    def children(self):
        return self._children

    @property
    def move(self):
        return self._move

    @property
    def parent(self):
        return self._parent

    @property
    def hasParent(self):
        return self._parent is None

    @property
    def parents(self):
        if not self.hasParent:
            return []
        parents = []
        parent = self.parent
        while parent.hasParent:
            parents.insert(0, parent)
            parent = parent.parent
        return parents

    @property
    def Q(self):
        return self._Q

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, value):
        self._N = value

    @property
    def color(self):
        return self._color
