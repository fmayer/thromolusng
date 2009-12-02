from PyQt4 import QtCore

import time

class Container(object):
    def __init__(self, value):
        self.value = value


class Range(object):
    def __init__(self, start, stop):
        if stop < start:
            raise ValueError
        self.start = start
        self.stop = stop
    
    def __eq__(self, other):
        return self.start == other.start and self.stop == other.stop
    
    def fullycontains(self, other):
        return (other.start > self.start and other.stop < self.stop)
    
    def contains(self, other):
        return (other.start >= self.start and other.stop <= self.stop)
    
    def intersect(self, other):
        if self == other:
            return self
        
        begin = max(self.start, other.start)
        end = min(self.stop, other.stop)
        
        if end > begin:
            return Range(begin, end)
        return None
    
    def magnitude(self):
        return self.stop - self.start
    
    def __repr__(self):
        return "<Range(%r, %r)>" % (self.start, self.stop)


class Transistion(object):
    def __init__(self, vchange=None):
        self.vchange = vchange
    
    def tick(self, delta, pos):
        raise NotImplementedError
    
    def value_changed(self, value):
        if self.vchange is not None:
            self.vchange(self, value)


class LinearTransistion(Transistion):
    def __init__(self, value, vdelta, vchange=None):
        Transistion.__init__(self, vchange)
        
        self.value = self.start = value
        self.vdelta = vdelta
    
    def tick(self, delta, pos):
        self.value += self.vdelta * delta
        self.value_changed(self.value)
    
    def reset(self):
        self.value = self.start


class QuadraticTransistion(Transistion):
    def __init__(self, length, height, start=0, vchange=None):
        Transistion.__init__(self, vchange)
        
        self.k = height / float(length) ** 2
        self.x = 0
        self.value = self.start = start
    
    def tick(self, delta, pos):
        self.x += delta
        self.value = self.k * (self.x ** 2) + self.start
        self.value_changed(self.value)
    
    def reset(self):
        self.value = self.start
        self.x = 0


class Timeline(object):
    def __init__(self, transitions=None, loop=False):
        if transitions is None:
            transitions = []
        self.transistions = transitions
        self.loop = loop
        
        self.starttime = None
        self.lasttick = None
        self.enabled = False
    
    def reset(self):
        self.starttime = None
        self.lasttick = None
        self.enabled = False
        
        for ran, trans in self.transistions:
            trans.reset()
    
    def add_transistion(self, ran, trans):
        self.transistions.append((ran, trans))
    
    def start(self):
        self.last = max(ran.stop for (ran, trans) in self.transistions)
        self.starttime = self.lasttick = time.time()
        self.enabled = True
    
    def stop(self):
        self.enabled = False
    
    def tick(self):
        t = time.time()
        pos = t - self.starttime
        lastpos = self.lasttick - self.starttime
        
        delta = Range(lastpos, pos)
        
        for ran, trans in self.transistions:
            intersect = ran.intersect(delta)
            if intersect is None:
                continue
            trans.tick(intersect.magnitude(), delta.stop)
        
        self.lasttick = t
        if self.loop and pos > self.last:
            for ran, trans in self.transistions:
                trans.reset()
                self.starttime = self.lasttick = t


class Engine(object):
    def __init__(self, timelines=None):
        if timelines is None:
            timelines = []
        self.timelines = timelines
        
        self.enabled = False
        self.timer = QtCore.QTimer()
        self.timer.connect(self.timer, 
                           QtCore.SIGNAL('timeout()'),
                           self.tick
                           )
    
    def add_timeline(self, timeline):
        self.timelines.append(timeline)
    
    def del_timeline(self, timeline):
        self.timelines.remove(timeline)
    
    def tick(self):
        for timeline in self.timelines:
            if timeline.enabled:
                timeline.tick()
    
    def start(self, interval):
        self.timer.start(interval)
        self.enabled = True
    
    def stop(self):
        self.timer.stop()
        self.enabled = False


if __name__ == '__main__':
    lt = LinearTransistion(0, 1)
    tl = Timeline()
    tl.add_transistion(Range(10, 20), lt)
    tl.start()
    st = time.time()
    
    while time.time() - 30 < st:
        tl.tick(True)
        print lt.value
        time.sleep(1.2)
