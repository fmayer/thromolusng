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
import hashlib

import asynchia
import asynchia.ee
import asynchia.maps

import thromolusng.packages
import thromolusng.crypto


class ServerPlayer(thromolusng.Player):
    def __init__(self, session, gid):
        thromolusng.Player.__init__(self)
        
        self.session = session
        self.gid = gid
    
    def show_turn(self, player, origin, target):
        self.session.show_turn(player, origin, target)
    
    def your_turn(self):
        self.session.your_turn(self)


class Session(object):
    def __init__(self, server_data, connection):
        self.server_data = server_data
        self.connection = connection
        
        self.players = {}
    
    def turn(self, pkg):
        id_, origin, target = pkg.value
        self.players[id_].turn(origin, target)
    
    def join_game(self, id_):
        self.players[id_] = self.server_data.games[id_].add_player(
            ServerPlayer(self, id_)
        )
        
        self.connection.send_input(
            thromolusng.packages.s_pack(
                thromolusng.packages.JOINEDG,
                id_
            )
        )
    
    def your_turn(self, splayer):
        self.connection.send_input(
            thromolusng.packages.s_pack(
                thromolusng.packages.YTURN,
                id_
            )
        )
    
    def show_turn(self, splayer, origin, target):
        self.connection.send_input(
            thromolusng.packages.s_pack(
                thromolusng.packages.STURN,
                splayer.gid,
                origin,
                target
            )
        )


class Connection(asynchia.ee.Handler):
    def __init__(self, server, socket_map, sock=None,
                 buffer_size=9046):
        self.server = server
        
        self.session = Session(server)
        self.loggedin = False
        self.expected_response = None
        
        self.package_dispatcher = {
            thromolusng.packages.JOING: self.session.join_game,
            thromolusng.packages.DOTURN: self.session.turn,
        }
            
        
        asynchia.ee.Handler.__init__(
            self,
            socket_map,
            sock,
            asynchia.ee.FactoryCollector(
                lambda: thromolusng.packages.Dispatcher(
                    s.B(),
                    thromolusng.packages.TSERVER,
                    self.packet_received
                )
            )
        )
    
    def list_games(self, pkg):     
        # Not used for now.
        room = pkg.value[0]
        
        self.send_input(
            s_pack(
                (
                    len(self.server.games),
                    (key, len(value), value in self.server.games.iteritems())
                )
            )
        )
    
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
                self._handle_return(fun(pkg))
            except Exception:
                self._handle_return(self.internal_error(pkg))
    
    def _handle_return(self, ret):
        if ret is not None:
            self.send_input(ret)


class ServerData(object):
    def __init__(self):
        self.game_idpool = asynchia.util.IDPool()
        self.player_idpool = asynchia.util.IDPool()
        self.channel_idpool = asynchia.util.IDPool()
        
        self.games = {}
    
    def get_pwd(self, user):
        pass
    
    def log_error(self, msg):
        """ Log error with msg and return a unique identifier for it. """
        pass


class Server(asynchia.AcceptHandler):
    def __init__(self, socket_map, sock=None):
        asynchia.AcceptHandler.__init__(self, socket_map, sock)
        
        self.server_data = ServerData()
    
    def handle_accept(self, sock, addr):
        Connection(self.server_data, self.socket_map, sock)
