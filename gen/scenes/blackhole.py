"""Gargantua: an edge-on accretion disk seen from just above its plane.

Front half of the disk: a thin band crossing *in front of* the shadow.
Back half: lensed up and over the shadow into a thick halo (and a thin
secondary image below).  Doppler beaming brightens the approaching side and
hot spots flow around the ring frame by frame.
"""
import math
from ..svg import Grid

CH = " .,:-~=+*#%@"
COL = ["dim", "dred", "dred", "red", "red", "orange", "orange", "yellow", "yellow", "byellow", "white", "bwhite"]


def render(n=48, W=96, H=26, Rs=5.0):
    frames = []
    cx, cy = W / 2, H / 2
    incl = 0.20
    r_in, r_out = 1.5 * Rs, 3.3 * Rs
    for f in range(n):
        t = 2 * math.pi * f / n
        front = [[0.0] * W for _ in range(H)]
        back = [[0.0] * W for _ in range(H)]

        def splat(buf, x, y, b):
            X, Y = cx + 2 * x, cy - y
            xi, yi = int(X), int(Y)
            if 0 <= xi < W and 0 <= yi < H and b > buf[yi][xi]:
                buf[yi][xi] = b

        r = r_in
        while r < r_out:
            rad = ((r_in / r) ** 2.0) * (1 - ((r - r_in) / (r_out - r_in)) ** 3)
            for k in range(0, 1440):
                th = math.radians(k / 4)
                dop = 1.0 + 0.6 * math.cos(th + math.pi)          # left side approaches -> brighter
                flow = 0.72 + 0.18 * math.sin(5 * th + 2 * t) + 0.10 * math.sin(11 * th - 3 * t + r)
                b = min(1.0, 1.35 * rad * dop * flow)
                x, s = r * math.cos(th), math.sin(th)
                if s >= 0:                                           # near half
                    y = -r * s * incl
                    splat(front, x, y, b)
                    splat(front, x, y - 0.5, b * 0.8)
                    # faint secondary image just under the shadow
                    if abs(x) < 1.6 * Rs:
                        y2 = -math.sqrt(max(0.0, (1.15 * Rs) ** 2 - x * x)) - (r - r_in) * 0.12
                        splat(back, x, y2, b * 0.35)
                else:                                                # far half, lensed over the top
                    u = -s
                    y = (1.15 * Rs + (r - r_in) * 0.42 * u) * math.sqrt(max(0.0, 1 - (x / (r * 1.05)) ** 2)) * (0.35 + 0.65 * u) + r * u * incl * 0.35
                    splat(back, x, y, b * 0.95)
            r += 0.05 * Rs
        # photon ring hugging the shadow
        for k in range(1440):
            th = math.radians(k / 4)
            splat(back, 1.03 * Rs * math.cos(th), 1.03 * Rs * math.sin(th), 0.6 + 0.3 * math.cos(th + math.pi))
        g = Grid(W, H)
        for yi in range(H):
            for xi in range(W):
                dx, dy = (xi + 0.5 - cx) / 2, cy - yi - 0.5
                inside = dx * dx + dy * dy < (0.98 * Rs) ** 2
                b = front[yi][xi] if inside else max(front[yi][xi], back[yi][xi])
                if b <= 0.10: continue
                i = min(len(CH) - 1, int(b * (len(CH) - 1) + 0.5))
                g.put(xi, yi, CH[i], COL[i])
        frames.append(g)
    return frames
