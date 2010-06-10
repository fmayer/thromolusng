import asynchia
import asynchia.ee

import itertools

enum = itertools.count()

TYPE_GAME = enum.next()
TYPE_TURN = enum.next()


class PackageCollector(asynchia.ee.CollectorQueue):
    def __init__(self, typemap, *args, **kwargs):
        asynchia.ee.CollectorQueue(self, 
            [asynchia.ee.StructCollector('B', self.pickedtype)]
            )
        self.args = args
        self.kwargs = kwargs
        self.typemap = typemap
    
    def pickedtype(self, coll):
        self.add_collector(self.typemap[coll.value](*args, **kwargs))


class GameCollector(asynchia.ee.CollectorQueue):
    def __init__(self, games):
        asynchia.ee.CollectorQueue(self,
            [asynchia.ee.StructCollector('B', self.pickedgame)]
        )
             
        self.game = None
        self.games = games
    
    def pickedgame(self, coll):
        self.game = self.games[coll.value]
        self.add_collector(PackageCollector(GAME_TYPEMAP, self.game))


class MainCollector(asynchia.ee.FactoryCollector):    
    def __init__(self, games):
        asynchia.ee.FactoryCollector.__init__(
            self,
            factory=lambda: PackageCollector(TOP_TYPEMAP, games)
        )
        self.games = games


class TurnCollector(asynchia.ee.StructCollector):
    def __init__(self, game):
        asynchia.ee.StructCollector('B' * 4)
        self.game = game
    
    def close(self):
        asynchia.ee.StructCollector.close()
        origin_x, origin_y, target_x, target_y = self.value
        self.game.turn((origin_x, origin_y), (target_x, target_y))
    
    
GAME_TYPEMAP = {
    TYPE_TURN: TurnCollector
}

TOP_TYPEMAP = {
    TYPE_GAME: GameCollector,
}
