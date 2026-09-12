"""donut.c, faithfully ported, coloured hot."""
import math
from ..svg import Grid, shade

CHARS = ".,-~:;=!*#$@"
HOT = ["dred", "dred", "red", "red", "orange", "orange", "yellow", "yellow", "byellow", "byellow", "white", "bwhite"]


def render(n=60, W=46, H=21):
    frames = []
    R1, R2, K2 = 1.0, 2.0, 5.0
    K1 = W * K2 * 3 / (8 * (R1 + R2)) * 0.85
    for f in range(n):
        A = f * 2 * math.pi / n * 2 + 1.0   # two full A turns per loop
        B = f * 2 * math.pi / n * 1 + 0.4   # one B turn -> seamless
        g = Grid(W, H)
        z = [[0.0] * W for _ in range(H)]
        cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
        th = 0.0
        while th < 2 * math.pi:
            ct, st = math.cos(th), math.sin(th)
            ph = 0.0
            while ph < 2 * math.pi:
                sp, cp = math.sin(ph), math.cos(ph)
                cx, cy = R2 + R1 * ct, R1 * st
                x = cx * (cB * cp + sA * sB * sp) - cy * cA * sB
                y = cx * (sB * cp - sA * cB * sp) + cy * cA * cB
                zz = K2 + cA * cx * sp + cy * sA
                ooz = 1 / zz
                xp = int(W / 2 + K1 * ooz * x)
                yp = int(H / 2 - K1 * ooz * y * 0.5)
                L = cp * ct * sB - cA * ct * sp - sA * st + cB * (cA * st - ct * sA * sp)
                if 0 <= xp < W and 0 <= yp < H and ooz > z[yp][xp]:
                    z[yp][xp] = ooz
                    li = max(0, int(L * 8))
                    li = min(li, 11)
                    g.put(xp, yp, CHARS[li], HOT[li])
                ph += 0.02
            th += 0.07
        frames.append(g)
    return frames
