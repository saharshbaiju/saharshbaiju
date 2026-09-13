"""The profile as a stack of borderless black sections (each its own SVG so the
README can wrap them in links)."""
from html import escape
from ..svg import P, CW, LH, FS, Grid, rows_svg, frames_group, frames_once, screen
from . import scramble, globe, htop, ps, blackhole, session

DESC = [
    ("white", "Saharsh Baiju"),
    ("dim2", "systems · backend architecture · RC hardware"),
    ("dim2", "amFOSS @ Amrita · ICPC prep · low-level curious"),
]
COLS, PAD = 96, 10
W = round(COLS * CW + 2 * PAD)


def sec_name(st):
    fr = scramble.render(st["name"].split()[0], n=56)
    c, b = frames_once(fr, PAD, 4, "n", 5.0)
    return screen(W, round(fr[0].h * LH + 8), b, c)


def sec_main(st):
    css, body, y = [], [], 4
    g = Grid(48, len(DESC) + 1)
    for i, (col, line) in enumerate(DESC):
        g.text(0, i, line[:48], col)
    body.append(rows_svg(g, PAD, y))
    y += (len(DESC) + 1) * LH
    c, b, h = htop.body(st, PAD, y)
    css.append(c); body.append(b); y += h
    gl = globe.render(n=108, R=9, orb=1.3)
    gx = W - PAD - gl[0].w * CW
    c, b = frames_group(gl, gx, 0, "g", 9.0, glow=False)
    css.append(c); body.append(b)
    y = max(y, gl[0].h * LH) + 4
    return screen(W, round(y), "\n".join(body), "".join(css))


def sec_ps(st):
    y = 4
    body = [f'<text x="{PAD}" y="{y + LH*0.75:.1f}" xml:space="preserve"><tspan class="green">{st["login"]}@github</tspan>:<tspan class="blue">~</tspan>$ ps aux | head</text>']
    y += LH * 1.4
    c, b, h = ps.body(st, PAD, y)
    body.append(b); y += h
    return screen(W, round(y), "\n".join(body), c)


def sec_session(st):
    y = 4
    body = [f'<text x="{PAD}" y="{y + LH*0.75:.1f}" xml:space="preserve"><tspan class="dim2"># visitors\' session — run your own command via the links below</tspan></text>']
    y += LH * 1.4
    c, b, h = session.body(st, PAD, y)
    body.append(b); y += h + 4
    return screen(W, round(y), "\n".join(body), c)


def sec_blackhole(st):
    bh = blackhole.render(n=96)
    c, b = frames_group(bh, PAD, 0, "b", 8.0, glow=False)
    y = bh[0].h * LH
    foot = Grid(COLS, 1)
    foot.text(0, 0, f"rendered {st['generated']} · refreshed daily · no javascript, just svg", "dim")
    b += rows_svg(foot, PAD, y)
    return screen(W, round(y + LH + 6), b, c)


SECTIONS = {"name.svg": sec_name, "main.svg": sec_main, "ps.svg": sec_ps,
            "session.svg": sec_session, "blackhole.svg": sec_blackhole}
