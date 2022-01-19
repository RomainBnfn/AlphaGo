import numpy as np
import random
import Goban
import math
from neuronalModel import getEvaluation

rd = random.Random()

class Graph: 
    
    def __init__(self, board, color):
        # Initilialise le graph à une certaine position pour une certaine couleur.
        self.racineNode = Node(None, None, color)
        self.board = board
        self.c = 0
    
    def getPlates(self):
        plates = []
        moves = []
        
        for i in range( min(9, 
                            len(self.board._historyMoveNames) ) ):
            board = np.array( self.board._board )
            board = np.reshape(board, (9, 9))
            plates.insert(0, board) #from older to newer
            #
            move = self.board._historyMoveNames[-1]
            moves.insert(0, move)
            self.board.pop()
        # restore
        for move in moves:
            self.board.push( Goban.Board.name_to_flat(move) )
            
        if len(plates) < 9:
            # 0 padding
            numberOfPlateMissing = 9 - len(plates)
            [plates.insert(0, np.zeros((9, 9))) for _ in range(numberOfPlateMissing)]
        else:
            plates = plates[-9:]
        return np.array(plates)

    def tau(self):
        if self.c < 10:
            return 1
        return 1 / self.c
        
    def setRacine(self, node):
        self.racineNode = node
        node.makeRacine()
    
    def train(self, depth):
        """Entraine le graph avec [depth] nouvelles profondeurs 

        Args:
            depth (number): le nb de profondeur
        """
        self.getPlates()

        # Conservation du graph
        moves = self.getTwoLastMoves()
        if len(moves) > 2:
            # Le jeu a déjà au moins 2 coups joués
            canConserve, node = self.canConserve()
            if not canConserve:
                node = Node(Node, None, Goban.Board.flip(self.color) )
                depth += 1 # On rajoute de la depth car l'arbre vient juste d'être reconstruit
            self.setRacine(node)
        # Exploration 
        for _ in range(depth):
            self.developBranch()
        self.c += 2 # Deux tours entre chaque train
    
    def developBranch(self):
        node = self.racineNode
        while node.hasBeenExplored:
            # On descend jusqu'à trouver une branche non explorée
            index = np.argmax(node.childrenScore)
            node = node.children[index]
        self.developNode(node)
    
    def getMoveProbas(self, fromXYToIndex):
        tauInv = 1.0 / self.tau()
        sumNTau = 0
        #
        probas = np.zeros(82)
        for node in self.racineNode.children:
            move = node.move
            sumNTau += pow(node.N, tauInv)
            probas[move] = pow(node.N, tauInv)
        probas = probas / sumNTau
        probas = probas / np.sum(probas) # normalize
        return probas
        
    def developNode(self, node):
        node.exploreChildren(self.board, self)
    
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
            
    def exploreChildren(self, board, graph):
        if self.hasBeenExplored:
            return
        #
        compteur = self.goToOurMove(board)
        colorNextMove = Goban.Board.flip(self.color)
        # The get Evaluation fct return the evaluation of any move, even if they are unlegal
        childrenScores = getEvaluation( graph.getPlates() )
        for move in board.legal_moves():
            score = childrenScores[0][move]
            node = Node(move, self, colorNextMove)
            node.defineQ(score)
            node.N += 1
            # Explore older nodes
            self.N += 1
            self.visitParents()
        self.undoMoves(board, compteur)
        return self.children

    def defineQ(self, score):
        self._Q = score
        
    # OLD : with roll out
    def evaluateQ(self, board, nbRollOut):
        """Evaluation de Q -> EN ÉTANT AU NOEUD PARENT PRECEDENT (sur le Board)

        Args:
            board ([Goban.Board]): Le plateau
            nbRollOut ([number]) : Le nombre de roll out

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
            self.undoMoves(board, compteur)
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
        return self.N / (1.0 + SNb)
    
    @property
    def childrenScore(self):
        _childrenScore = []
        for child in self.children:
            _childrenScore.append(child.U + child.Q)
        return _childrenScore
    
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
