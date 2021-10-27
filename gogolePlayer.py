# -*- coding: utf-8 -*-
''' This is the famous random player which (almost) always looses.
'''

import Goban
from playerInterface import *

import numpy as np
import matplotlib.pyplot as plt
import randomPlayer

import random

rd = random.Random()


#  On calcule au plus loin possible des U & Q des enfants, pour ensuite les explorer
#  Puis au moment de la décision, on choisi une branche selon les proba : Na ^(1/t) / Somme ( Nb ^(1/t) )
#                                                       avec t = 0.5 (ou 1; 2) pour les 4 premiers coups puis -> 0

class Node:
    C = 1

    def __init__(self, move, board, parent, color):
        """Noeud

        Args:
            move (string): Le coup qui doit être joué pour arrivé du plus proche parent à ce noeud
            board (Goban.Board): Le plateau 
            parent (Node): Le Noeud du parent précédent 
            color (int): La couleur du joueur du noeud
        """
        self._move = move  # Le coup qui doit être joué pour arrivé du plus proche parent à ce noeud
        self._parent = parent

        self._children = []

        self._board = board

        self._Q = 0
        self._U = 0
        self._N = 0

        self._color = color

    def chooseBranchToDevelope(self):
        return self.children[np.argmax(self.childrenScore)]
        
    def developeBranch(self):
        #
        self.N += 1
        parent = self.parent
        while parent.hasParent:
            parent.N += 1
            parent = parent.parent
        #
        self.exploreChild()
        """
        # Evaluate Children
        for node in self.children:
            Q = node.evaluateQ()
            U = node.evaluateU()
            self._childrenScore.append(Q + U)
        """

    def exploreChild(self):
        if self.hasBeenExplored:
            return
        compteur = 1
        for parent in self.parents:
            self.board.push(parent.move)
            compteur += 1
        self.board.push(self.move)
        #
        childrenMoves = self.board.legal_moves()
        #
        color = Goban.Board.flip(self.color)
        for move in childrenMoves:
            node = Node(move, self.board, self, color)
            self.children.append(node)
        #
        for i in range(compteur):
            self._board.pop()
        return self.children

    def evaluateQ(self, k):
        # k : le nombre de rollout
        self.board.push(self.move)
        w = 0
        for i in range(k):
            compteur = 0
            while not self._board.is_game_over():
                moves = self._board.legal_moves()
                move = rd.choice(moves)
                self._board.push(move)
                compteur += 1
            res = self._board.result()
            if (res == '1-0' and self.color == 1) or (res == '0-1' and self.color == 2):
                w += 1
            for u in range(compteur):
                self._board.pop()
        self._board.pop()
        self._Q = w / k
        return self._Q

    @property
    def U(self):
        if not self.hasParent:
            return 0
        p = 1
        SNb = 0  # Somme des Nb
        for child in self.parent.children:
            SNb += child.N
        return p * SNb / (1 + self.N) * self.C

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
    def board(self):
        return self._board

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


def fromXYToIndex(x, y):
    return y * Goban.Board._BOARDSIZE + x


class myPlayer(PlayerInterface):
    ''' A random roll player
    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

        self._actualNode = Node()

    def getPlayerName(self):
        return "Best Player Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        # Get the list of all possible moves
        moves = self._board.legal_moves()  # Dont use weak_legal_moves() here!

        # Let's plot some board probabilities
        import go_plot

        evals = np.zeros(82)
        for move in moves:
            x, y = Goban.Board.unflatten(move)
            index = fromXYToIndex(x, y)
            for i in range(2):
                evals[index] += self.evalMove(move)
        # Normalize them
        evals /= np.sum(evals)

        # We plot them
        go_plot.plot_play_probabilities(self._board, evals)
        plt.show()

        move = moves[np.argmax(evals)]
        # Correct number for PASS
        if move == 81:
            move = -1
        self._board.push(move)

        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        # print("Opponent played ", move, "i.e. ", move) # New here
        #  the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    def evalMove(self, move):
        eval = -1
        compteur = 1
        self._board.push(move)
        while not self._board.is_game_over():
            moves = self._board.legal_moves()
            move = rd.choice(moves)
            self._board.push(move)
            compteur += 1
        res = self._board.result()
        if (res == '1-0' and self._mycolor == 1) or (res == '0-1' and self._mycolor == 2):
            eval = 1
        elif res == "1/2-1/2":
            eval = 0
        for i in range(compteur):
            self._board.pop()
        return eval
