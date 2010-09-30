# Copyright 2010 Erik Gilling

__version__ = """v0.1 (2010-09-30)"""
__author__  = "Erik Gilling"
__license__ = "GPL"
__url__     = "http://www.konkers.net/boxmaker"
__doc__     = \
"""boxmaker
Creates vector art of finger jointed boxes suitible for 
laser cutting

Copyright %s
Version %s
License %s
Homepage %s

""" % \
(__author__,__version__,__license__,__url__)

def xfrange(start, stop=None, step=None):
    """Like range(), but returns list of floats instead

    All numbers are generated on-demand using generators
    """

    if stop is None:
        stop = float(start)
        start = 0.0

    if step is None:
        step = 1.0

    cur = float(start)

    if stop > start:
        while cur < stop:
            yield cur
            cur += step
    else:
        while cur > stop:
            yield cur
            cur -= step

class Box:

    def __init__(self, height, width, depth, spacing, thick):
        self.height = height
        self.width = width
        self.depth = depth
        self.spacing = spacing
        self.thick = thick

        self.gen()

    def new_edge(self, start, end, state):
        fingers = []

        for i in list(xfrange(start, end, self.spacing)):
            fingers.append((i, state));
            if state == 1:
                state = 0
            else:
                state = 1
        fingers.append((end, state));

        return fingers

    def invert_edge(self, e):
        fingers = []
    
        for f in e:
            if f[1] == 1:
                fingers.append((f[0], 0))
            else:
                fingers.append((f[0], 1))

        return fingers

    def invert_mirror_edge(self, e):
        fingers = []
    
        for f in reversed(e):
            if f[1] == 1:
                fingers.append((f[0], 1))
            else:
                fingers.append((f[0], 0))

        return fingers

    def cast_edge(self, e):
        fingers = []
        if e[0][0] < e[-1][0]:
            adjust = self.thick
        else:
            adjust = -self.thick

        f = e[0]
        if f[1] == 1:
            fingers.append((f[0], 1))
            fingers.append((f[0] + adjust, 0))
        else:
            fingers.append((f[0], 1))

        for f in e[1:-1]:
            if f[1] == 1:
                fingers.append((f[0], 0))
            else:
                fingers.append((f[0], 1))

        f = e[-1]
        if f[1] == 0:
            fingers.append((f[0] - adjust, 1))
            fingers.append((f[0], 0))
        else:
            fingers.append((f[0], 0))

        return fingers

    def cast_mirror_edge(self, e):
        fingers = []
    
        if e[0][0] < e[-1][0]:
            adjust = self.thick
        else:
            adjust = -self.thick

        f = e[-1]
        if f[1] == 0:
            fingers.append((f[0], 1))
            fingers.append((f[0] - adjust, 0))
        else:
            fingers.append((f[0], 0))

        for f in list(reversed(e))[1:-1]:
            if f[1] == 1:
                fingers.append((f[0], 1))
            else:
                fingers.append((f[0], 0))

        f = e[0]
        if f[1] == 1:
            fingers.append((f[0] + adjust, 1))
            fingers.append((f[0], 0))
        else:
            fingers.append((f[0], 0))


        return fingers

    def box_points(self, edges):
        h = edges[1][-1][0];
        w = edges[0][-1][0];
        points = [];

        p = edges[0][0]
        points.append((p[0] + p[1] * self.thick, p[1] * self.thick, 0));

        for p in edges[0][1:-1]:
            points.append((p[0], self.thick - p[1] * self.thick,0))
            points.append((p[0], p[1] * self.thick,0))

        p = edges[0][-1]
        points.append((p[0] - self.thick + p[1] * self.thick, self.thick - p[1] * self.thick,0))
    

        for p in edges[1][1:-1]:
            points.append((w - self.thick + p[1] * self.thick, p[0], 0))
            points.append((w - p[1] * self.thick, p[0],0))

        p = edges[1][-1]
        points.append((w - self.thick + p[1] * self.thick, p[0] - self.thick + p[1] * self.thick, 0))

        for p in edges[2][1:-1]:
            points.append((p[0], h - self.thick + p[1] * self.thick,0))
            points.append((p[0], h - p[1] * self.thick,0))

        p = edges[2][-1]
        points.append((p[0] + self.thick - p[1] * self.thick, h - self.thick + p[1] * self.thick,0))

        for p in edges[3][1:-1]:
            points.append((self.thick - p[1] * self.thick, p[0], 0))
            points.append((p[1] * self.thick, p[0],0))

        p = edges[3][-1]
        points.append((self.thick - p[1] * self.thick, p[0] + self.thick - p[1] * self.thick, 0))

        return points;

    def gen(self):
        e1 = self.new_edge(0, self.width, 0)
        e2 = self.new_edge(0, self.height, e1[-2][1])
        e3 = self.new_edge(self.width, 0, e2[-2][1])
        e4 = self.new_edge(self.height, 0, e3[-2][1])
        front = [e1, e2, e3, e4]

        e1 = self.invert_edge(front[0])
        e2 = self.new_edge(0, self.depth, e1[-2][1])
        e3 = self.new_edge(self.width, 0, e2[-2][1])
        e4 = self.new_edge(self.depth, 0, e3[-2][1])
        bottom = [e1, e2, e3, e4]

        e1 = self.invert_mirror_edge(front[2])
        e2 = self.new_edge(0, self.depth, e1[-2][1])
        e3 = self.new_edge(self.width, 0, e2[-2][1])
        e4 = self.new_edge(self.depth, 0, e3[-2][1])
        top = [e1, e2, e3, e4]

        e1 = self.invert_mirror_edge(bottom[2])
        e2 = self.new_edge(0, self.height, e1[-2][1])
        e3 = self.new_edge(self.width, 0, e2[-2][1])
        e4 = self.new_edge(self.height, 0, e3[-2][1])
        back = [e1, e2, e3, e4]

        e1 = self.cast_edge(bottom[1])
        e2 = self.cast_edge(back[1])
        e3 = self.cast_mirror_edge(top[1])
        e4 = self.cast_mirror_edge(front[1])
        right = [e1, e2, e3, e4]

        e1 = self.cast_mirror_edge(bottom[3])
        e2 = self.cast_mirror_edge(back[3])
        e3 = self.cast_edge(top[3])
        e4 = self.cast_edge(front[3])
        left = [e1, e2, e3, e4]

        self.front_points = self.box_points(front)
        self.bottom_points = self.box_points(bottom)
        self.top_points = self.box_points(top)
        self.back_points = self.box_points(back)
        self.right_points = self.box_points(right)
        self.left_points = self.box_points(left)
