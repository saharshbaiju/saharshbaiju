"""A rectangle of random ASCII decodes into the name, then holds.

Font: ANSI-Shadow style block letters. Faces (█) are bright and tinted per
letter; the shadow strokes (╗╔╝╚═║) are dim, which gives the type depth.
"""
import random
from ..svg import Grid

SHADOW = {
 "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
 "B": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██████╔╝", "╚═════╝ "],
 "C": [" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"],
 "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
 "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
 "H": ["██╗  ██╗", "██║  ██║", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
 "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
 "J": ["     ██╗", "     ██║", "     ██║", "██   ██║", "╚█████╔╝", " ╚════╝ "],
 "K": ["██╗  ██╗", "██║ ██╔╝", "█████╔╝ ", "██╔═██╗ ", "██║  ██╗", "╚═╝  ╚═╝"],
 "L": ["██╗     ", "██║     ", "██║     ", "██║     ", "███████╗", "╚══════╝"],
 "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║", "╚═╝     ╚═╝"],
 "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"],
 "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
 "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
 "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
 "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
 "U": ["██╗   ██╗", "██║   ██║", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
 " ": ["   "] * 6,
}
NOISE = "!@#$%^&*()_+-=[]{};:,.<>?/\\|0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
TINT = ["#ffffff", "#e9f7ff", "#d3f0ff", "#bde9ff", "#a8e2ff", "#9aedfe", "#8fdbff", "#c7f5ff"]


def bitmap(text):
    """-> list of rows; each row is a list of (char, colour) cells."""
    text = text.upper()
    rows = [[] for _ in range(6)]
    for li, ch in enumerate(text):
        glyph = SHADOW.get(ch, SHADOW[" "])
        tint = TINT[li % len(TINT)]
        for r in range(6):
            for c in glyph[r]:
                if c == "█": rows[r].append((c, tint))
                elif c == " ": rows[r].append((" ", None))
                else: rows[r].append((c, "#3a4152"))
            rows[r].append((" ", None))
    return rows


def render(text="SAHARSH", n=56, pad=1):
    bm = bitmap(text)
    W = max(len(r) for r in bm) + 2 * pad
    H = 6 + 2 * pad
    rnd = random.Random(42)
    # decode front sweeps left->right with per-cell jitter, so it feels like
    # a wave of cells locking in rather than a hard curtain
    resolve_at = [[c * 36 / W + rnd.uniform(0, 2.5) + (r % 3) * 0.6 for c in range(W)] for r in range(H)]
    frames = []
    for f in range(n):
        g = Grid(W, H)
        for r in range(H):
            for c in range(W):
                cell = (" ", None)
                if 0 <= r - pad < 6 and 0 <= c - pad < len(bm[r - pad]):
                    cell = bm[r - pad][c - pad]
                d = f - resolve_at[r][c]
                if d < 0:
                    g.put(c, r, rnd.choice(NOISE), "dgreen" if rnd.random() < 0.65 else "dim")
                elif d < 1.5:
                    g.put(c, r, rnd.choice(NOISE) if rnd.random() < 0.6 else cell[0], "bgreen")
                else:
                    g.put(c, r, cell[0], cell[1])
        frames.append(g)
    return frames
