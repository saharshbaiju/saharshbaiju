"""Spinning ASCII Earth from a baked 2-degree land mask, lit from the upper left."""
import math, os, random
from ..svg import Grid

HERE = os.path.dirname(os.path.dirname(__file__))
MASK = open(os.path.join(HERE, "data", "landmask.txt")).read().split("\n")
MH, MW = len(MASK), len(MASK[0])

LAND = [("dgreen", ":"), ("dgreen", "%"), ("green", "#"), ("green", "@"), ("bgreen", "@")]
SEA = [("dim", "."), ("dblue", "."), ("dblue", "~"), ("blue", "~"), ("blue", ":")]
PIN = (9.09, 76.49)   # Amritapuri, Kerala


def is_land(lat, lon):
    j = int((90 - lat) / 180 * MH) % MH
    i = int((lon + 180) / 360 * MW) % MW
    return MASK[j][i] == "#"


def render(n=72, R=11, orb=1.3, pin=PIN):
    H, W = 2 * R + 3, int(2 * (orb * 2 * R + 3))
    rnd = random.Random(7)
    stars = [(rnd.randrange(7, W), rnd.randrange(H), rnd.choice(".'*+")) for _ in range(28)]
    frames = []
    lx, ly, lz = -0.5, 0.6, 0.65
    ln = math.sqrt(lx * lx + ly * ly + lz * lz); lx, ly, lz = lx / ln, ly / ln, lz / ln
    tilt = math.radians(-23.4)
    for f in range(n):
        spin = 2 * math.pi * f / n
        g = Grid(W, H)
        for sx, sy, c in stars:
            g.put(sx, sy, c, "dim")
        cx, cy = W / 2, H / 2
        for r in range(H):
            for c in range(W):
                x = (c + 0.5 - cx) / (2 * R)
                y = (cy - r - 0.5) / R
                d2 = x * x + y * y
                if d2 > 1:
                    # the cell centre is off the sphere, but part of the cell
                    # may still be: pull the sample to the cell's inner edge
                    x = math.copysign(max(0.0, abs(x) - 0.5 / (2 * R)), x)
                    y = math.copysign(max(0.0, abs(y) - 0.5 / R), y)
                    d2 = x * x + y * y
                    if d2 > 1: continue
                z = math.sqrt(1 - d2)
                # tilt axis, then un-spin to find surface lat/lon
                y1 = y * math.cos(tilt) - z * math.sin(tilt)
                z1 = y * math.sin(tilt) + z * math.cos(tilt)
                x1 = x
                lat = math.degrees(math.asin(max(-1, min(1, y1))))
                lon = math.degrees(math.atan2(x1, z1)) - math.degrees(spin)
                lon = (lon + 540) % 360 - 180
                light = max(0.0, x * lx + y * ly + z * lz)
                idx = min(4, int(light * 5.5))
                col, ch = (LAND if is_land(lat, lon) else SEA)[idx]
                g.put(c, r, ch, col)
        # "you are here" pin
        plat, plon = pin if pin and pin[0] is not None else (None, None)
        if plat is None:
            pz = -1.0
        else:
            lonr = math.radians(plon + math.degrees(spin))
            latr = math.radians(plat)
            px, py1, pz1 = math.cos(latr) * math.sin(lonr), math.sin(latr), math.cos(latr) * math.cos(lonr)
            py = py1 * math.cos(tilt) + pz1 * math.sin(tilt)
            pz = -py1 * math.sin(tilt) + pz1 * math.cos(tilt)
        if pz > 0.05:
            g.put(int(cx + px * 2 * R), int(cy - py * R), "@", "red")
        # satellite: inclined circular orbit, two revolutions per loop,
        # occluded when it passes behind the disc
        a = (2 * math.pi * f / n) + 0.8          # one revolution per loop
        inc = math.radians(38)
        ox, oy0, oz0 = orb * math.cos(a), 0.0, orb * math.sin(a)
        oy = oy0 * math.cos(inc) - oz0 * math.sin(inc)
        oz = oy0 * math.sin(inc) + oz0 * math.cos(inc)
        oy, ox = oy * math.cos(0.5) + ox * math.sin(0.5) * 0.35, ox
        sx, sy = int(round(cx + ox * 2 * R)), int(round(cy - oy * R))
        sprite = [("=", "blue"), ("[", "dim2"), ("o", "bwhite"), ("]", "dim2"), ("=", "blue")]
        for i, (ch, col) in enumerate(sprite):
            xx, yy = sx - 2 + i, sy
            dx, dy = (xx + 0.5 - cx) / (2 * R), (cy - yy - 0.5) / R
            if oz < 0 and dx * dx + dy * dy < 1.0:
                continue        # behind the planet
            g.put(xx, yy, ch, col if oz >= 0 else "dim")
        frames.append(g)
    return frames
