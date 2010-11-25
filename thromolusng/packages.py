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

from asynchia.dsl import s, LFLSE, lb
from asynchia.ee import KeepingCollectorQueue, FactoryCollector

class Dispatcher(KeepingCollectorQueue):
    def __init__(self, header, dispatch_table, onclose=None):
        KeepingCollectorQueue.__init__(self,
                                       [header(onclose=self.header_complete)],
                                        onclose
                                        )
        self.dispatch_table = dispatch_table
        
        self.invalid = False
    
    def header_complete(self, header):
        try:
            self.add_collector(self.dispatch_table[header.value])
        except IndexError:
            self.invalid = True


_POS = lambda: s.B() + s.B()
_GAME = lambda: s.L()
_CHANNEL = lambda: s.L()

enum = iter(xrange(256))

INTERNALERROR = enum.next()

MKGAME = enum.next()
DOTURN = enum.next()
LISTGAMES = enum.next()
JOING = enum.next()

TSERVER = {
    MKGAME: s.B() + LFLSE(0),
    DOTURN: _GAME() + _POS() + _POS(),
    LISTGAMES: s.L(),
    JOING: _GAME(),
}

START = enum.next()
YTURN = enum.next()
GAMES = enum.next()
JOINEDG = enum.next()
STURN = enum.next()

TCLIENT = {
    START: _GAME(),
    YTURN: _GAME(),
    GAMES: _GAME() + lb(-1) * (_GAME() + s.B() + LFLSE(-1)),
    JOINEDG: _GAME(),
    STURN: _GAME() + _POS() + _POS(),
}


def c_pack(enum, *args):
    return s.B().produce(enum) + TSERVER[enum].produce(*args)


def s_pack(enum, *args):
    return s.B().produce(enum) + TCLIENT[enum].produce(*args)


print s_pack(GAMES,
    [1, [[1, 2, 'ab']]]
)
    