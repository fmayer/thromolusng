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
import traceback

import asynchia
import asynchia.ee
import asynchia.maps

import thromolusng.packages

class FixedSizeStringCollector(asynchia.ee.CollectorQueue):
    def __init__(self, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self,
            [asynchia.ee.StructCollector(struct.Struct('!L'), self.set_size)],
            onclose)
        self.message = None
    
    def set_size(self):
        self.add_collector(
            asynchia.ee.DelimitedCollector(
                asynchia.ee.StringCollector(),
                coll.value[0], self.msgcollected
            )
        )
    
    def msgcollected(self, coll):
        self.message = coll.collector.string


class MessageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self,
            [# Target channel.
             asynchia.ee.StructCollector(
                 struct.Struct('!L'), self.chancollected),
             # Origin
             asynchia.ee.StructCollector(
                 struct.Struct('!L'), self.set_size)
             ],
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
        asynchia.ee.StructCollector.__init__(
            self, struct.Struct('!BB'), onclose
        )


class HeaderCollector(asynchia.ee.StructCollector):
    def __init__(self, onclose=None):
        asynchia.ee.StructCollector.__init__(self, struct.Struct('!B'), onclose)
    
    def get_value(self):
        return self.value[0]


class PackageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, header, dispatcher, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self, [header(self.header_finished)], onclose)
        
        self.collected = []
        self.dispatcher = dispatcher
        self.invalid = False
    
    def header_finished(self, header):
        self.header = header
        self.type_ = header.get_value()
        try:
            coll = self.dispatcher[self.type_]
        except KeyError:
            self.invalid = True
        else:
            if coll is not None:
                self.add_collector(coll())
    
    def finish_collector(self, coll):
        self.collected.append(coll)


class Connection(asynchia.ee.Handler):
    def __init__(self, server, socket_map, sock=None,
                 buffer_size=9046):
        self.server = server
        
        self.loggedin = False
        self.expected_response = None
        
        self.package_dispatcher = {
            thromolusng.packages.LIN_GCHALLENGE: self.lin_challenge
        }
            
        
        asynchia.ee.Handler.__init__(
            self,
            socket_map,
            sock,
            asynchia.ee.FactoryCollector(
                lambda: PackageCollector(HeaderCollector, TYPES,
                                         self.packet_received)
            )
        )
    
    def lin_challenge(self, pkg):
        pass
    
    def invalid_packet(self, pkg):
        pass
    
    def internal_error(self, pkg):
        self.send_str(
            struct.pack(
                '!BL', thromolusng.packages.INTERNALERROR,
                self.server.log_error(traceback.format_exc())
            )
        )
    
    def packet_received(self, pkg):
        try:
            fun = self.package_dispatcher[pkg.type_]
        except KeyError:
            self._handle_return(self.invalid_packet(pkg))
        else:
            try:
                self._handle_return(self.invalid_packet(pkg))
            except Exception:
                self._handle_return(self.internal_error(pkg))
    
    def _handle_return(self, ret):
        if ret is not None:
            self.send_input(ret)
        


class Server(asynchia.AcceptHandler):
    def __init__(self, socket_map, sock=None):
        asynchia.AcceptHandler.__init__(self, socket_map, sock)
        
        self.game_idpool = asynchia.util.IDPool()
        self.player_idpool = asynchia.util.IDPool()
        self.channel_idpool = asynchia.util.IDPool()
        
        self.games = {}
    
    def handle_accept(self, sock, addr):
        Connection(self, self.socket_map, sock)
    
    def log_error(self, msg):
        """ Log error with msg and return a unique identifier for it. """
        pass


TYPES = {
    thromolusng.packages.TURN: lambda: (
        asynchia.ee.KeepingCollectorQueue(
            [
                # Game ID.
                asynchia.ee.StructCollector(struct.Struct('!L')),
                # Origin
                PositionCollector(),
                # Target
                PositionCollector()
            ]
        )
    ),
    thromolusng.packages.MSG: MessageCollector,
    thromolusng.packages.LOUT: None,
    thromolusng.packages.LIN_GCHALLENGE: None,
    thromolusng.packages.LISTG: None,
    thromolusng.packages.GETROOMS: None,
    thromolusng.packages.GOPEN: None,
    thromolusng.packages.SUBSCHAN: (
        lambda: asynchia.ee.StructCollector(struct.Struct('!L'))
    ),
    thromolusng.packages.UNSUBCHAN: (
        lambda: asynchia.ee.StructCollector(struct.Struct('!L'))
    ),
    thromolusng.packages.JOING: (
        lambda: asynchia.ee.StructCollector(struct.Struct('!L'))
    ),
    thromolusng.packages.JOING: (
        lambda: asynchia.ee.StructCollector(struct.Struct('!L'))
    ),
    thromolusng.packages.GDETAIL: (
        lambda: asynchia.ee.StructCollector(struct.Struct('!L'))
    ),
    thromolusng.packages.GETCHAN: FixedSizeStringCollector
}


def _simpletest():
    def recv(pkg):
        print pkg.collected[1].value
    
    m =  asynchia.ee.MockHandler(
        struct.pack('!BL', thromolusng.packages.SUBSCHAN, 251)
    )
    
    c = asynchia.ee.FactoryCollector(
        lambda: PackageCollector(HeaderCollector, TYPES, recv)
    )
    
    d = False
    while not d:
        d, s = c.add_data(m, 2)    


def _test():
    m = asynchia.maps.DefaultSocketMap()
    s = Server(m)
    s.reuse_addr()
    s.bind(('', 12345))
    s.listen(0)
    
    try:
        m.run()
    finally:
        m.close()


if __name__ == '__main__':
    _test()
