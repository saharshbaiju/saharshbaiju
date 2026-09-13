"""The whole profile as one borderless black canvas."""
from html import escape
from ..svg import P, CW, LH, FS, Grid, rows_svg, frames_group, frames_once, screen
from . import scramble, globe, htop, ps, blackhole

def desc(st):
    cfg = st.get("config", {})
    return [("white", st["name"])] + [("dim2", t) for t in cfg.get("tagline", [])[:3]]


def render(st):
    cols, pad = 96, 10
    W = round(cols * CW + 2 * pad)
    css, body = [], []
    y = pad

    # 1. name, decoded from noise -------------------------------------------
    name_frames = scramble.render(st["headline"], n=56)
    c, b = frames_once(name_frames, pad, y, "n", 5.0)
    css.append(c); body.append(b)
    y += name_frames[0].h * LH + LH * 0.5

    # 2. left: description + htop ; right: globe --------------------------
    top = y
    DESC = desc(st)
    g = Grid(48, len(DESC) + 1)
    for i, (col, line) in enumerate(DESC):
        g.text(0, i, line[:48], col)
    body.append(rows_svg(g, pad, y))
    y += (len(DESC) + 1) * LH
    c, b, h = htop.body(st, pad, y)
    css.append(c); body.append(b)
    y += h
    loc = st.get("config", {}).get("location") or {}
    gl = globe.render(n=108, R=9, orb=1.3, pin=(loc.get("lat"), loc.get("lon")) if loc else None)
    gx = W - pad - gl[0].w * CW
    c, b = frames_group(gl, gx, top - LH * 0.5, "g", 9.0, glow=False)
    css.append(c); body.append(b)
    y = max(y, top + gl[0].h * LH) + LH

    # 3. ps aux + hexdump calendar ------------------------------------------
    prompt = f'<text x="{pad}" y="{y + LH*0.75:.1f}" xml:space="preserve"><tspan fill="{P["green"]}">{st["login"]}@github</tspan>:<tspan fill="{P["blue"]}">~</tspan>$ ps aux | head</text>'
    body.append(prompt); y += LH * 1.4
    c, b, h = ps.body(st, pad, y)
    css.append(c); body.append(b)
    y += h - LH

    # 4. gargantua ------------------------------------------------------------
    bh = blackhole.render(n=96)
    c, b = frames_group(bh, pad, y, "b", 8.0, glow=False)
    css.append(c); body.append(b)
    y += bh[0].h * LH
    foot = Grid(cols, 1)
    foot.text(0, 0, f"rendered {st['generated']} · refreshed daily · no javascript, just svg", "dim")
    body.append(rows_svg(foot, pad, y)); y += LH + pad
    return screen(W, round(y), "\n".join(body), "".join(css))
