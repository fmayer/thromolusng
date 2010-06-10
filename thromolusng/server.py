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


class TestCollector(asynchia.ee.StructCollector):
    def __init__(self, onclose=None):
        asynchia.ee.StructCollector.__init__(self, struct.Struct('B'), onclose)


class HeaderCollector(asynchia.ee.StructCollector):
    def __init__(self, onclose=None):
        asynchia.ee.StructCollector.__init__(self, struct.Struct('B'), onclose)


class PackageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, onclose=None):
        asynchia.ee.CollectorQueue.__init__(
            self, [HeaderCollector(self.header_finished)], onclose)
        self.collected = []
    
    def header_finished(self, header):
        self.type_ = header.value[0]
        self.add_collector(TYPES[self.type_]())
    
    def finish_collector(self, coll):
        self.collected.append(coll)


class Connection(asynchia.ee.Handler):
    def __init__(self, socket_map, sock=None,
                 buffer_size=9046):
        asynchia.ee.Handler.__init__(
            self,
            socket_map,
            sock,
            asynchia.ee.FactoryCollector(
                lambda: PackageCollector(self.package_received)
            )
        )
    
    def package_received(self, pkg):
        print pkg

TYPES = {thromolusng.packages.TEST: TestCollector}

if __name__ == '__main__':
    def recv(pkg):
        print pkg
    
    m =  asynchia.ee.MockHandler(
        struct.pack('BB', thromolusng.packages.TEST, 251)
    )
    
    c = asynchia.ee.FactoryCollector(
        lambda: PackageCollector(recv)
    )
    
    d = False
    while not d:
        d, s = c.add_data(m, 2)    

