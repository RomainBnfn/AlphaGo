import numpy as np
import random
import Goban

rd = random.Random()

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
        if parent is not None:
            parent.addChildren(self)
            
        self._board = board

        self._Q = 0
        self._U = 0
        self._N = 0

        self._color = color

    def addChildren(self, children):
        self._children.append(children)
        
    def chooseBranchToDevelope(self):
        return self.children[np.argmax(self.childrenScore)]       
    
    def developeBranch(self, k):
        #
        self.N += 1
        parent = self.parent
        while (parent is not None and parent.hasParent):
            parent.N += 1
            parent = parent.parent
        #
        self.exploreChild()
        
        # Evaluate Children
        for node in self.children:
            Q = node.evaluateQ(k)

    def exploreChild(self):
        if self.hasBeenExplored:
            return
        moves = [self.move]
        parent = self.parent
        while parent is not None:
            moves.insert(0, parent.move)
            parent = parent.parent
            
        compteur = 0
        for move in moves:
            if move is None:
                break
            self.board.push(move)
            compteur += 1
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
