# -*- coding: utf-8 -*-
''' This file is used to test the gogolePlayer aggainst a random player.
    Don't forget to change the number of game to the wanted value.
'''

import Goban 
import importlib
import time
from io import StringIO
import sys
import randomPlayer 
import gogolePlayer
import random

######################################
#        C o n s t a n t s           #
######################################

nb_games = 5

######################################
 
b = Goban.Board()
nb_win = 0
nb_deuce = 0
for U in range(nb_games):
    b.reset()
    players = [ randomPlayer.myPlayer(), gogolePlayer.myPlayer()]
    
    print('Game ', U+1, '/', nb_games)
    i = random.randint(0, 1)
    players[1-i].newGame(Goban.Board._BLACK)
    players[i].newGame(Goban.Board._WHITE)
    #
    totalTime = [0,0] # total real time for each player
    nextplayer = 0
    nextplayercolor = Goban.Board._BLACK
    nbmoves = 1
    #
    outputs = ["",""]
    wrongmovefrom = 0

    while not b.is_game_over():
        legals = b.legal_moves() # legal moves are given as internal (flat) coordinates, not A1, A2, ...
        
        nbmoves += 1
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        
        currentTime = time.time()
        move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)        
        totalTime[nextplayer] += time.time() - currentTime
        
        if not Goban.Board.name_to_flat(move) in legals:
            print(otherplayer, nextplayer, nextplayercolor)
            print("Problem: illegal move")
            wrongmovefrom = nextplayercolor
            break
        
        b.push(Goban.Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
        players[otherplayer].playOpponentMove(move)
    
        nextplayer = otherplayer
        nextplayercolor = othercolor
    
    result = b.result()
    color = players[1]._mycolor
    
    if wrongmovefrom > 0:
        if wrongmovefrom == b._WHITE and color == b._BLACK:
            nb_win += 1
        elif wrongmovefrom == b._BLACK  and color == b._WHITE:
            nb_win += 1
        else:
            print("ERROR")
    elif result == "1-0" and color == b._WHITE:
        nb_win += 1
        
    elif result == "0-1" and color == b._BLACK:
        nb_win += 1
    elif result == "1/2-1/2":
        nb_deuce += 1

print("Wins: ", nb_win, "/", nb_games, "(", 1.*nb_win/nb_games,")")
print("Loose: ", nb_games-nb_win, "/", nb_games, "(", 1.*(nb_games-nb_win)/nb_games,")")
print("Deuce: ", nb_deuce, "/", nb_games, "(", 1.*nb_deuce/nb_games,")")