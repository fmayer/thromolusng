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
# in.
enum = itertools.count()

TURN = enum.next()
MSG = enum.next()
LIN_GCHALLENGE = enum.next()
LIN_RESPONSE = enum.next()
LOUT = enum.next()
INVALID = enum.next()
OPENG = enum.next()
GOPEN = enum.next()
LISTG = enum.next()
GDETAIL = enum.next()
GETCHAN = enum.next()
SUBSCHAN = enum.next()
UNSUBCHAN = enum.next()
CHANOFF = enum.next()
GETROOMS = enum.next()
