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

class InvalidTurn(Exception):
    pass


class InvalidPlayer(Exception):
    pass


class Board(object):
    def __init__(self, rows, cols, curplayer=1):
        self.board = [[0 for _ in xrange(cols)] for _ in xrange(rows)]
        self.board[0][0] = self.board[rows - 1][cols - 1] = 1
        self.board[0][cols - 1] = self.board[rows - 1][0] = 2
        
        self.curplayer = curplayer
        self.rows = rows
        self.cols = cols
    
    @staticmethod
    def other_player(player):
        return 3 - player
    
    def turn(self, origin, target):
        if self.board[target]:
            raise InvalidTurn
        dr = origin[0] - target[0]
        dc = origin[1] - target[1]
        if abs(dr) < 2 and abs(dc) < 2:
            self.set(origin, target)
        else:
            self.jump(origin, target)
    
    def set(self, origin, target):
        if self[origin] != self.curplayer:
            raise InvalidTurn
        dr = origin[0] - target[0]
        dc = origin[1] - target[1]
        if abs(dr) > 1 or abs(dc) > 1 or self[target]:
            raise InvalidTurn
        self[target] = self[origin]
        self.curplayer = self.other_player(self.curplayer)
    
    def jump(self, origin, target):
        if self[origin] != self.curplayer:
            raise InvalidTurn
        dr = abs(origin[0] - target[0])
        dc = abs(origin[1] - target[1])
        
        if not ((dr == 2 and dc == 2) or (dr == 2 and dc == 0)
            or (dr == 0 and dc == 2)):
            raise InvalidTurn
        
        self[target] = self[origin]
        self[origin] = 0
        self.curplayer = self.other_player(self.curplayer)
    
    def __setitem__(self, i, v):
        if len(i) != 2:
            raise IndexError
        self.board[i[0]][i[1]] = v
    
    def __getitem__(self, i):
        if len(i) != 2:
            raise IndexError
        return self.board[i[0]][i[1]]
