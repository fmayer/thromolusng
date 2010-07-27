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

import struct

import asynchia
import asynchia.ee

import thromolusng.packages

class MessageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self,
            [# Target channel.
             asynchia.ee.StructCollector('L', self.chancollected),
             # Origin
             asynchia.ee.StructCollector('L', self.set_size)],
            onclose)
        
        self.channel = None
        self.message = None
    
    def set_size(self, coll):
        self.add_collector(
            asynchia.ee.DelimitedCollector(
                asynchia.ee.StringCollector(),
                coll.value[0], self.msgcollected
            )
        )
    
    def chancollected(self, coll):
        self.channel = coll.value[0]
    
    def msgcollected(self, coll):
        self.message = coll.collector.string


class PositionCollector(asynchia.ee.StructCollector):
    def __init__(self, onclose=None):
        asynchia.ee.StructCollector.__init__(self, struct.Struct('BB'), onclose)


class HeaderCollector(asynchia.ee.StructCollector):
    def __init__(self, onclose=None):
        asynchia.ee.StructCollector.__init__(self, struct.Struct('B'), onclose)
    
    def get_value(self):
        return self.value[0]


class PackageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, header, dispatcher, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self, [header(self.header_finished)], onclose)
        self.collected = []
        
        self.dispatcher = dispatcher
    
    def header_finished(self, header):
        self.header = header
        self.type_ = header.get_value()
        self.add_collector(self.dispatcher[self.type_]())
    
    def finish_collector(self, coll):
        self.collected.append(coll)


class Connection(asynchia.ee.Handler):
    def __init__(self, server, socket_map, sock=None,
                 buffer_size=9046):
        self.server = server
        
        asynchia.ee.Handler.__init__(
            self,
            socket_map,
            sock,
            asynchia.ee.FactoryCollector(
                lambda: PackageCollector(HeaderCollector, TYPES,
                                         self.package_received)
            )
        )
    
    def package_received(self, pkg):
        print pkg


class Server(asynchia.AcceptHandler):
    def __init__(self, socket_map, sock=None):
        asynchia.AcceptHandler.__init__(self, socket_map, sock)
        
        self.game_idpool = asynchia.util.IDPool()
        self.player_idpool = asynchia.util.IDPool()
        
        self.channel_idpool = asynchia.util.IDPool()
        
        self.games = {}
    
    def handle_accept(self, sock, addr):
        Connection(self, self.socket_map, sock)


TYPES = {
    thromolusng.packages.TURN: (
        asynchia.ee.CollectorQueue(
            [
                # Game ID.
                asynchia.ee.StructCollector('B'),
                # Origin
                PositionCollector(),
                # Target
                PositionCollector()
            ]
        )
    ),
    thromolusng.packages.MSG: MessageCollector,
    
}


if __name__ == '__main__':
    def recv(pkg):
        print pkg.collected[1]
    
    m =  asynchia.ee.MockHandler(
        struct.pack('BB', thromolusng.packages.TEST, 251)
    )
    
    c = asynchia.ee.FactoryCollector(
        lambda: PackageCollector(HeaderCollector, TYPES, recv)
    )
    
    d = False
    while not d:
        d, s = c.add_data(m, 2)    

