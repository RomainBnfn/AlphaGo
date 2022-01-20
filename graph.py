# -*- coding: utf-8 -*-
''' This file contains two class to represent the graph of possible move in Go.
    A graph is composed of one racine node and many child nodes.
'''
import numpy as np
import random
import Goban
import math
from neuronalModel import getEvaluation

rd = random.Random()

class Graph: 
    
    def __init__(self, board, color):
        self.racineNode = Node(None, None, color)
        self.board = board
        self.c = 0
    
    def getPlates(self):
        """Get the 9 last boards as np array (for the NN)
            If the board is recent (<9 moves), we apply a 0 padding instead
            (we add plates with 0) 

        Returns:
            [np.array]: The 9 last plates
        """
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
    
    def train(self, depth):
        """Explore the graph by [depth] times. This parms doesn't represent the 
            depth of exploration but the amount of time that we develop a branch.

        Args:
            depth [int]: Number of explorations
        """
        # Conservation du graph
        moves = self.getTwoLastMoves()
        if len(moves) == 2:
            # Le jeu a déjà au moins 2 coups joués
            canConserve, node = self.canConserve()
            if not canConserve:
                node = Node(Node, None, Goban.Board.flip(self.racineNode.color) )
                depth += 1 # On rajoute de la depth car l'arbre vient juste d'être reconstruit
            self.setRacine(node)
        # Exploration 
        for _ in range(depth):
            self.developBranch()
        self.c += 2 # Deux tours entre chaque train
    
    def developBranch(self):
        """Explore a branch by exploring the best of its child
        """
        node = self.racineNode
        while node.hasBeenExplored:
            # On descend jusqu'à trouver une branche non explorée
            index = np.argmax(node.childrenScore)
            node = node.children[index]
        self.developNode(node)
    
    def getMoveProbas(self):
        """Transform all the scores of branches to probabilities

        Returns:
            [np.array]: The probability of each move, 0 for unlegal
        """
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
        """Return if the actual graph has already explore the real move (of opponent) 

        Returns:
            [bool, Node]: If the graph can be conserved, The new racine node | None 
        """
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
        """ Return the node by making the moves in [moves] (can be None if it's an unexplored path)

        Args:
            moves ([string[]]): Moves to make

        Returns:
            [Node | None]: The node
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
    
    def setRacine(self, node):
        self.racineNode = node
        node.makeRacine()
    
    def tau(self):
        if self.c < 10:
            return 1
        return 1 / self.c   

    

class Node:
    C = 1 # Constant on U calculation

    def __init__(self, move, parent, color):
        """Node

        Args:
            move (string): The move need to from the parend node to this node
            parent (Node): The previous node
            color (int): The color of the player 
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

    def visitParents(self):
        """Add 1 to all parent N
        """
        parent = self.parent
        while parent is not None:
            parent.N += 1
            parent = parent.parent 
            
    def exploreChildren(self, board, graph):
        """Explore the next nodes

        Args:
            board ([Goban.Board]): The board object
            graph ([Graph]): The graph object

        Returns:
            [list]: The children
        """
        if self.hasBeenExplored:
            return
        #
        compteur = self.goToOurMove(board)
        colorNextMove = Goban.Board.flip(self.color)
        
        # The get Evaluation fct return the evaluation of any move, even if they are unlegal
        _, childrenScores = getEvaluation( graph.getPlates() )
        
        previous_plates = graph.getPlates()[1:] #only 8 previous plates 
        # previous plates here to avoid to call getPlates for each child while
        # the last plate changes
        
        for move in board.legal_moves():
            score = childrenScores[0][move]
            #
            node = Node(move, self, colorNextMove)
            node.defineQ(board, previous_plates) # val from NN
            node.defineU(score)
            node.N += 1
            # Explore older nodes
            self.N += 1
            self.visitParents()
        self.undoMoves(board, compteur)
        return self.children

    def defineQ(self, board, previous_plates):
        """Define the Q value by asking the neural network

        Args:
            board ([Goban.Board]): The board object
            previous_plates ([np.array]): The 8-last plates
        """
        # From parent
        board.push(self.move)
        
        plate = np.array( board._board )
        plate = np.reshape(plate, (9, 9))
        previous_plates = np.append(previous_plates, [plate])
            
        val, _ = getEvaluation( previous_plates )
        self._Q = val
        board.pop()
        
    # def defineQ(self, board, nbRollOut):
    #     """Define G by making [nbRollOut] games

    #     Args:
    #         board ([Goban.Board]): The board object
    #         nbRollOut ([number]) : Amount of roll out

    #     Returns:
    #         [double]: Q
    #     """
    #     board.push(self.move)
    #     wins = 0
    #     for _ in range(nbRollOut):
    #         compteur = 0
    #         while not board.is_game_over():
    #             moves = board.legal_moves()
    #             move = rd.choice(moves)
    #             board.push(move)
    #             compteur += 1
    #         res = board.result()
    #         if (res == '1-0' and self.color == 1) or (res == '0-1' and self.color == 2):
    #             wins += 1
    #         self.undoMoves(board, compteur)
    #     board.pop()
    #     self._Q = wins / nbRollOut
    #     return self._Q
    

    def goToOurMove(self, board):
        """A fct which make all needed move to go the node board

        Args:
            board (Goban.Board): The board object

        Returns:
            [int]: The number of moves made
        """
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
          
    def defineU(self, score):
        """Define the U score with the formula: 
              U = C * P(s,a) * sqrt(Sum(Nb)) / N with  b the other childs of the parent
        

        Args:
            score (float): P(s,a), calculated by the neural network

        Returns:
            [type]: [description]
        """
        if not self.hasParent:
            self._U = 0
        else:
            SNb = 0  # Somme des Nb
            for child in self.parent.children:
                SNb += child.N
            SNb = math.sqrt(SNb)
            # score ~ P(s, a) : prediction of NN
            self._U = score * self.C * SNb/(1.0 + self.N)
            
    ##################################
    
    def addChildren(self, children):
        self._children.append(children)          

    def makeRacine(self) :
        self._parent = None
        self._move = None
    
    def undoMoves(self, board, k):
        for i in range(k):
            board.pop()
            
    #####################################
    #           Properties              #
    #####################################

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
    def U(self):
        return self._U
    
    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, value):
        self._N = value

    @property
    def color(self):
        return self._color
