# -*- coding: utf-8 -*-
''' This is the famous random player which (almost) always looses.
'''

import Goban
from playerInterface import *

import numpy as np
import matplotlib.pyplot as plt
import randomPlayer
from graph import *
 
import random

rd = random.Random()


#  On calcule au plus loin possible des U & Q des enfants, pour ensuite les explorer
#  Puis au moment de la décision, on choisi une branche selon les proba : Na ^(1/t) / Somme ( Nb ^(1/t) )
#                                                       avec t = 0.5 (ou 1; 2) pour les 4 premiers coups puis -> 0



def fromXYToIndex(x, y):
    return y * Goban.Board._BOARDSIZE + x


class myPlayer(PlayerInterface):
    ''' A random roll player
    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.graph = None
        
    def getGraph(self):
        # Lazy loading car mycolor non définit au début
        if self.graph is None:
            self.graph = Graph(Goban.Board, self._mycolor)
        return self.graph

    def getPlayerName(self):
        return "Best Player Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        graph = self.getGraph()
        probas = graph.getMoveProbas()
        
        # Let's plot some board probabilities
        import go_plot
        go_plot.plot_play_probabilities(self._board, probas)
        plt.show()

        move = moves[np.argmax(probas)]
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
