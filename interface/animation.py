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
    def tick(self, delta, pos):
        raise NotImplementedError


class LinearTransistion(object):
    def __init__(self, value, vdelta):
        self.value = value
        self.vdelta = vdelta
    
    def tick(self, delta, pos):
        self.value += self.vdelta * delta


class QuadraticTransistion(object):
    def __init__(self, length, height, start=0):
        self.k = height / float(length) ** 2
        self.x = 0
        self.value = self.start = start
    
    def tick(self, delta, pos):
        self.x += delta
        self.value = self.k * (self.x ** 2) + self.start


class Timeline(object):
    def __init__(self):
        self.transistions = []
        self.starttime = None
        self.lasttick = None
    
    def add_transistion(self, ran, trans):
        self.transistions.append((ran, trans))
    
    def start(self):
        self.starttime = self.lasttick = time.time()
    
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


if __name__ == '__main__':
    lt = LinearTransistion(0, 1)
    tl = Timeline()
    tl.add_transistion(Range(10, 20), lt)
    tl.start()
    st = time.time()
    
    while time.time() - 30 < st:
        tl.tick()
        print lt.value
        time.sleep(1.2)
