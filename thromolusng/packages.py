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


# Do not change order of symbols, less their values are changed,
# making them incompatible with prior versions. Append any new
# symbols on the bottom, stating the version they were introduced
# in. 256 is reserved in case package types run out.
enum = xrange(256)

# Do turn in a game. B[Game-Id]B[Origin-x]B[Origin-y]B[Target-x]B[Target-y]
TURN = enum.next() # dispatched
MSG = enum.next() # dispatched
LIN_GCHALLENGE = enum.next() # dispatched
LIN_RESPONSE = enum.next()
LOUT = enum.next() # dispatched
INVALID = enum.next()
OPENG = enum.next() # dispatched
GOPEN = enum.next() # only sent by server
LISTG = enum.next() # dispatched
GDETAIL = enum.next() # dispatched
GETCHAN = enum.next()
SUBSCHAN = enum.next() # dispatched
UNSUBCHAN = enum.next() # dispatched
CHANOFF = enum.next() # only sent by server
GETROOMS = enum.next() # dispatched
JOING = enum.next() # dispatched
INTERNALERROR = enum.next() # dispatched
# Do turn in a game. L[Game-Id]B[Player-id]B[Origin-x]B[Origin-y]B[Target-x]B[Target-y]
STURN = enum.next()
YTURN = enum.next()
GAMEL = enum.next()

STURN_STRUCT = struct.Struct('!LBBBBB')
YTURN_STRUCT = struct.Struct('!LB')

def make_STURN(player, origin, target):
    return STURN_STRUCT.pack(
        player.game.id_, player.id_, origin[0], origin[1],
        target[0], target[1]
    )


def make_YTURN(player, origin, target):
    return YTURN_STRUCT.pack(
        player.game.id_, player.id_
    )