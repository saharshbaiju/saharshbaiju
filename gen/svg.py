"""Tiny SVG engine for frame-animated ASCII panels.

Every panel is a terminal window drawn in SVG.  A scene produces a list of
Grid frames (chars + colour per cell); the engine emits one <g> per frame and
cycles them with a CSS steps() keyframe.  No JavaScript is needed, so the
result animates inside GitHub's README <img> tags.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from html import escape

# ---------------------------------------------------------------- palette --
# 16-colour ANSI (Snazzy-ish) + a few UI tones.
P = {
    "bg": "#0b0d12", "panel": "#0f1219", "border": "#262b36", "fg": "#c9d1d9",
    "dim": "#4b5263", "dim2": "#6c7386",
    "black": "#1c1f26", "red": "#ff5c57", "green": "#5af78e", "yellow": "#f3f99d",
    "blue": "#57c7ff", "magenta": "#ff6ac1", "cyan": "#9aedfe", "white": "#f1f1f0",
    "bblack": "#686868", "bred": "#ff8785", "bgreen": "#8dffb4", "byellow": "#fbfdc8",
    "bblue": "#8fdbff", "bmagenta": "#ff9bd6", "bcyan": "#c7f5ff", "bwhite": "#ffffff",
    "orange": "#ffb86c", "dred": "#8c2f2b", "dgreen": "#2f6b45", "dblue": "#2b5c8c",
    "dyellow": "#8c8532", "dcyan": "#2f7a86", "dmagenta": "#8c3a6b",
}

FONT = "'JetBrains Mono','Fira Code','Cascadia Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
FS = 12.0          # font size px
CW = FS * 0.602    # char advance (most mono fonts are 0.6em)
LH = FS * 1.18     # line height


@dataclass
class Grid:
    w: int
    h: int
    ch: list = field(default_factory=list)
    co: list = field(default_factory=list)

    def __post_init__(self):
        self.ch = [[" "] * self.w for _ in range(self.h)]
        self.co = [[None] * self.w for _ in range(self.h)]

    def put(self, x, y, c, col=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.ch[y][x] = c
            self.co[y][x] = col

    def text(self, x, y, s, col=None):
        for i, c in enumerate(s):
            self.put(x + i, y, c, col)

    def line(self, x0, y0, x1, y1, c=None, col=None):
        """Bresenham; picks a slope glyph when c is None."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        if c is None:
            # cells are ~2:1 tall, so compare dy against dx/2
            if dx == 0: c = "|"
            elif dy == 0: c = "-"
            else:
                s = 2.0 * dy / dx
                if s < 0.6: c = "-"
                elif s > 3.5: c = "|"
                else: c = "/" if (x1 - x0) * (y1 - y0) < 0 else "\\"
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.put(x, y, c, col)
            if x == x1 and y == y1: break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x += sx
            if e2 < dx: err += dx; y += sy


def rows_svg(grid: Grid, x0: float, y0: float, default="fg", extra_attr="") -> str:
    """Emit one <text> per non-empty row, colour runs as <tspan>."""
    out = []
    for r in range(grid.h):
        chars, cols = grid.ch[r], grid.co[r]
        # trim trailing spaces
        last = len(chars)
        while last > 0 and chars[last - 1] == " ": last -= 1
        if last == 0: continue
        runs, cur, buf = [], cols[0], []
        for i in range(last):
            if cols[i] != cur and chars[i] != " ":
                runs.append((cur, "".join(buf))); buf, cur = [], cols[i]
            buf.append(chars[i])
        runs.append((cur, "".join(buf)))
        y = y0 + (r + 1) * LH - LH * 0.25
        parts = []
        for col, s in runs:
            key = col or default
            if key in P:
                parts.append(f'<tspan class="{key}">{escape(s)}</tspan>')
            else:
                parts.append(f'<tspan fill="{key}">{escape(s)}</tspan>')
        out.append(f'<text x="{x0:.1f}" y="{y:.1f}" xml:space="preserve"{extra_attr}>{"".join(parts)}</text>')
    return "\n".join(out)


def chrome(width, height, title, right="", body="", extra_defs="", cycle=None):
    """Wrap body in a terminal window. cycle=(n_frames, seconds) adds frame CSS."""
    css = "".join(f".{k}{{fill:{v}}}" for k, v in P.items()) + f"""
  text{{font-family:{FONT};font-size:{FS}px;fill:{P['fg']};white-space:pre}}
  .t{{font-size:11px;fill:{P['dim2']}}}
  .glow{{filter:url(#glow)}}
  .cur{{animation:blink 1s steps(1,end) infinite}}
  @keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}"""
    if cycle:
        n, secs = cycle
        step = 100.0 / n
        css += f"""
  .fr{{opacity:0;animation:cyc {secs}s steps(1,end) infinite}}
  @keyframes cyc{{0%{{opacity:1}}{step:.4f}%{{opacity:0}}100%{{opacity:0}}}}"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>{escape(title)}</title>
<defs>
  <pattern id="scan" width="1" height="3" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill="#000" opacity="0.18"/></pattern>
  <radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.45"/></radialGradient>
  <filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  {extra_defs}
</defs>
<style>{css}
</style>
<rect width="{width}" height="{height}" rx="8" fill="{P['bg']}"/>
<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="8" fill="none" stroke="{P['border']}"/>
<rect x="1" y="1" width="{width-2}" height="24" rx="8" fill="{P['panel']}"/>
<rect x="1" y="16" width="{width-2}" height="9" fill="{P['panel']}"/>
<line x1="1" y1="25.5" x2="{width-1}" y2="25.5" stroke="{P['border']}"/>
<circle cx="14" cy="13" r="4.5" fill="{P['red']}"/><circle cx="28" cy="13" r="4.5" fill="{P['yellow']}"/><circle cx="42" cy="13" r="4.5" fill="{P['green']}"/>
<text class="t" x="56" y="17">{escape(title)}</text>
<text class="t" x="{width-12}" y="17" text-anchor="end">{escape(right)}</text>
{body}
<rect x="1" y="26" width="{width-2}" height="{height-27}" fill="url(#scan)" pointer-events="none"/>
<rect x="1" y="26" width="{width-2}" height="{height-27}" fill="url(#vig)" pointer-events="none"/>
</svg>'''


def frames_panel(frames: list[Grid], title, right="", secs=4.0, pad=12, static_top: str = "", glow=True):
    g0 = frames[0]
    width = round(g0.w * CW + pad * 2)
    height = round(26 + g0.h * LH + pad * 2)
    body = [static_top]
    n = len(frames)
    dt = secs / n
    cls = "fr glow" if glow else "fr"
    for i, g in enumerate(frames):
        body.append(f'<g class="{cls}" style="animation-delay:{-i*dt:.4f}s">')
        body.append(rows_svg(g, pad, 26 + pad))
        body.append("</g>")
    return chrome(width, height, title, right, "\n".join(body), cycle=(n, secs))


def shade(lum, keys):
    """Map lum in [0,1] to one of the palette keys."""
    i = int(max(0.0, min(0.999, lum)) * len(keys))
    return keys[i]


# ------------------------------------------------------------ borderless --
def frames_group(frames, x, y, tag, secs, glow=True, default="fg"):
    """Frame cycle for a sub-region of a bigger canvas. Returns (css, body)."""
    n = len(frames)
    step = 100.0 / n
    css = (f".fr-{tag}{{visibility:hidden;animation:c{tag} {secs}s steps(1,end) infinite}}"
           f"@keyframes c{tag}{{0%{{visibility:visible}}{step:.4f}%{{visibility:hidden}}100%{{visibility:hidden}}}}")
    body = []
    dt = secs / n
    cls = f"fr-{tag}"
    for i, g in enumerate(frames):
        body.append(f'<g class="{cls}" style="animation-delay:{-i*dt:.4f}s">{rows_svg(g, x, y, default)}</g>')
    return css, "\n".join(body)


def screen(width, height, body, css=""):
    """Pure-black OLED canvas, no chrome."""
    pal = "".join(f".{k}{{fill:{v}}}" for k, v in P.items())
    base = f"text{{font-family:{FONT};font-size:{FS}px;fill:{P['fg']};white-space:pre}}{pal}.glow{{filter:url(#glow)}}.cur{{animation:blink 1s steps(1,end) infinite}}@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.1" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>{base}{css}</style>
<rect width="{width}" height="{height}" fill="#000"/>
{body}
</svg>'''


def frames_once(frames, x, y, tag, secs, glow=True, default="fg"):
    """Play frames once, then hold the last one forever. Returns (css, body).

    Opacity-based: each frame starts at opacity 0 (base style), is switched on
    for exactly its slot by a `forwards` animation and switched off at the end.
    The last frame's animation ends at opacity 1 and is held forever.
    """
    n = len(frames)
    dt = secs / n
    css = (f".on-{tag}{{opacity:0;animation:o{tag} {dt:.4f}s steps(1,end) forwards}}"
           f"@keyframes o{tag}{{0%{{opacity:1}}100%{{opacity:0}}}}"
           f".hd-{tag}{{opacity:0;animation:h{tag} {dt:.4f}s steps(1,end) forwards}}"
           f"@keyframes h{tag}{{0%{{opacity:1}}100%{{opacity:1}}}}")
    body = []
    for i, g in enumerate(frames):
        cls = (f"hd-{tag} glow" if i == n - 1 and glow else f"hd-{tag}" if i == n - 1 else f"on-{tag}")
        body.append(f'<g class="{cls}" style="animation-delay:{i*dt:.4f}s">{rows_svg(g, x, y, default)}</g>')
    return css, "\n".join(body)
