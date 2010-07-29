# thromolusng - a game
# Copyright (C) 2009 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import random

class InvalidTurn(Exception):
    pass


class InvalidPlayer(Exception):
    pass


class GameFull(Exception):
    pass


class GameNotFull(Exception):
    pass


class Observer(object):
    def __init__(self):
        pass
    
    def observe(self):
        pass

class Player(object):
    def __init__(self):
        self.game = None
        self.id_ = None
        
        self.hascontrol = False
    
    def setid(self, id_):
        self.id_ = id_
    
    def setgame(self, game):
        self.game = game
    
    def your_turn(self):
        pass
    
    def show_turn(self, player, origin, target):
        pass
    
    def turn(self, origin, target):
        self.game.turn(self, origin, target)


class Game(object):
    def __init__(self, board=None):
        if board is None:
            board = Board()
        self.board = board
        
        self.players = []
        self.curplayer = None
    
    def add_player(self, player):
        player.setid(self.new_id())
        player.setgame(self)
        
        self.players.append(player)
        # Might be helpsome so that the player can be constructed
        # in the parameter list, such as game.add_player(Player()).
        return player
    
    def get_player_by_id(self ,id_):
        return self.players[id_ - 1]

    def new_id(self):
        """ Get the next free uid for a player. """
        players = len(self.players)
        if players == 2:
            raise GameFull
        return players + 1
    
    def random_beginner(self):
        if len(self.players) != 2:
            raise GameNotFull
        self.curplayer = random.choice(self.players)
        return self.curplayer
    
    def start(self):
        self.curplayer.your_turn()
        self.curplayer.hascontrol = True
    
    def turn(self, player, origin, target):
        if player is self.curplayer:
            self.board.turn(player.id_, origin, target)
            for playr in self.players:
                playr.show_turn(player, origin, target)
                playr.hascontrol = False
            self.curplayer = self.other_player(player)
            self.curplayer.hascontrol = True
            self.curplayer.your_turn()
        else:
            raise InvalidPlayer
    
    def other_player(self, player):
        return self.players[2 - player.id_]


class Board(object):
    def __init__(self, rows, cols):
        self.board = [[0 for _ in xrange(cols)] for _ in xrange(rows)]
        self.board[0][0] = self.board[rows - 1][cols - 1] = 1
        self.board[0][cols - 1] = self.board[rows - 1][0] = 2
        
        self.rows = rows
        self.cols = cols
    
    @staticmethod
    def other_player(player):
        return 3 - player
    
    def turn(self, player, origin, target):
        if self[target]:
            raise InvalidTurn(player, origin, target)
        dr = origin[0] - target[0]
        dc = origin[1] - target[1]
        if abs(dr) < 2 and abs(dc) < 2:
            self.walk(player, origin, target)
        else:
            self.jump(player, origin, target)
    
    def walk(self, player, origin, target):
        if self[origin] != player:
            raise InvalidTurn
        dr = origin[0] - target[0]
        dc = origin[1] - target[1]
        if abs(dr) > 1 or abs(dc) > 1 or self[target]:
            raise InvalidTurn
        self[target] = self[origin]
    
    def jump(self, player, origin, target):
        if self[origin] != player:
            raise InvalidTurn
        dr = abs(origin[0] - target[0])
        dc = abs(origin[1] - target[1])
        
        if not ((dr == 2 and dc == 2) or (dr == 2 and dc == 0)
            or (dr == 0 and dc == 2)):
            raise InvalidTurn
        
        self[target] = self[origin]
        self[origin] = 0
    
    def __setitem__(self, i, v):
        if len(i) != 2:
            raise IndexError
        row, col = i
        if v != 0:
            for ar, ac in itertools.product([0, 1, -1], repeat=2):
                nr = row + ar
                nc = col + ac
                if nr < 0 or nr >= self.rows or nc >= self.cols or nc < 0:
                    continue
                if self.board[nr][nc]:
                    self.board[nr][nc] = v
        self.board[row][col] = v
    
    def __getitem__(self, i):
        if len(i) != 2:
            raise IndexError
        return self.board[i[0]][i[1]]
