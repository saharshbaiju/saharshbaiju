"""Rotating tesseract: a cube inside a cube, projected 4D -> 3D -> 2D."""
import math, itertools
from ..svg import Grid


def rot(p, i, j, a):
    c, s = math.cos(a), math.sin(a)
    p = list(p)
    p[i], p[j] = p[i] * c - p[j] * s, p[i] * s + p[j] * c
    return p


def render(n=72, W=46, H=22):
    verts = list(itertools.product([-1, 1], repeat=4))
    edges = [(a, b) for a in range(16) for b in range(a + 1, 16)
             if sum(x != y for x, y in zip(verts[a], verts[b])) == 1]
    frames = []
    for f in range(n):
        t = 2 * math.pi * f / n
        g = Grid(W, H)
        pts = []
        for v in verts:
            p = rot(v, 0, 3, t)            # xw plane (4D spin)
            p = rot(p, 1, 2, t * 0.5)      # yz
            p = rot(p, 0, 2, 0.6)          # fixed tilt for depth
            p = rot(p, 0, 1, 0.35)
            d4 = 1.0 / (2.8 - p[3])        # 4D perspective
            x, y, z = p[0] * d4, p[1] * d4, p[2] * d4
            d3 = 1.0 / (2.3 - z)
            sx = int(W / 2 + x * d3 * W * 0.75)
            sy = int(H / 2 - y * d3 * H * 0.75)
            pts.append((sx, sy, z, p[3]))
        # draw far edges first so near ones win
        order = sorted(edges, key=lambda e: (pts[e[0]][2] + pts[e[1]][2]))
        for a, b in order:
            xa, ya, za, wa = pts[a]
            xb, yb, zb, wb = pts[b]
            if verts[a][3] != verts[b][3]:
                col = "dim2"                       # connectors between the two cubes
            elif verts[a][3] > 0:
                col = "cyan" if (za + zb) > 0 else "dcyan"
            else:
                col = "magenta" if (za + zb) > 0 else "dmagenta"
            g.line(xa, ya, xb, yb, None, col)
        for (x, y, z, w) in pts:
            g.put(x, y, "o" if z > 0 else "+", "bwhite" if z > 0 else "dim2")
        frames.append(g)
    return frames
