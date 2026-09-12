"""htop: language meters as CPU cores, contributions as memory."""
from html import escape
from ..svg import P, CW, LH, chrome, FS


def meter(x, y, label, frac, txt, delay, cells=24):
    """[|||||      ] with htop's green/yellow/red thirds, filled by a scaleX sweep."""
    out = [f'<text x="{x:.1f}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["cyan"]}">{escape(label):>4}</tspan><tspan fill="{P["fg"]}">[</tspan></text>']
    bx = x + 5 * CW
    n = int(round(frac * cells))
    out.append(f'<g style="transform-origin:{bx:.1f}px 0;animation:fill 1.6s cubic-bezier(.2,.8,.2,1) {delay:.2f}s 1 backwards">')
    for i in range(n):
        f = i / cells
        col = P["green"] if f < 0.5 else P["yellow"] if f < 0.8 else P["red"]
        out.append(f'<text x="{bx + i*CW:.1f}" y="{y:.1f}"><tspan fill="{col}">|</tspan></text>')
    out.append("</g>")
    out.append(f'<text x="{bx + cells*CW:.1f}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["fg"]}">]</tspan><tspan fill="{P["dim2"]}"> {escape(txt)}</tspan></text>')
    return "\n".join(out)


def render(st):
    cols, pad = 60, 12
    langs = st["langs"][:8]
    rows = len(langs) + 7
    width = round(cols * CW + pad * 2)
    height = round(26 + rows * LH + pad * 2)
    y0 = 26 + pad
    body = [f"<style>@keyframes fill{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}</style>"]
    top = max(f for _, f, _ in langs) or 1
    for i, (name, frac, _) in enumerate(langs):
        y = y0 + (i + 1) * LH - LH * 0.25
        body.append(meter(pad, y, f"{i}", frac / top, f"{frac*100:5.1f}%  {name}", 0.15 * i))
    y = y0 + (len(langs) + 1) * LH - LH * 0.25
    body.append(meter(pad, y, "Mem", min(1, st["contribs"] / st["goal"]), f"{st['contribs']}/{st['goal']} contributions", 1.3))
    y += LH
    body.append(meter(pad, y, "Swp", min(1, st["prs"] / 50), f"{st['prs']} pull requests", 1.5))
    y += 3 * LH
    info = (f"Tasks: {st['repos']} repos, {sum(1 for r in st['recent'] if r['days'] <= 30)} running")
    info2 = f"Load average: {st['streak']} {st['best_streak']} {st['contribs']}   Uptime: {st['uptime_days']} days"
    body.append(f'<text x="{pad}" y="{y - LH:.1f}" xml:space="preserve">{escape(info)}</text>')
    body.append(f'<text x="{pad}" y="{y:.1f}" xml:space="preserve">{escape(info2)}</text>')
    y += LH
    keys = "".join(f'<tspan fill="{P["fg"]}">F{i+1}</tspan><tspan fill="{P["black"]}" style="fill:{P["bg"]}"></tspan><tspan fill="{P["bg"]}" ></tspan>' for i in range(0))
    foot = [("F1", "Help"), ("F3", "Search"), ("F6", "SortBy"), ("F9", "Kill"), ("F10", "Quit")]
    fx = pad
    for k, v in foot:
        body.append(f'<text x="{fx:.1f}" y="{y:.1f}" fill="{P["fg"]}" xml:space="preserve">{k}</text>')
        fx += len(k) * CW
        body.append(f'<rect x="{fx:.1f}" y="{y - FS + 1:.1f}" width="{7*CW:.1f}" height="{FS + 2}" fill="{P["cyan"]}"/>')
        body.append(f'<text x="{fx + CW*0.5:.1f}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["bg"]}">{v}</tspan></text>')
        fx += 7 * CW + CW
    return chrome(width, height, f"htop — {st['login']}", "lang share by repo · daily", "\n".join(body))


def body(st, x0, y0, cols=46, cells=18, nlangs=6):
    """Borderless variant for the OLED screen. Returns (css, svg)."""
    langs = st["langs"][:nlangs]
    out = []
    top = max(f for _, f, _ in langs) or 1
    y = y0 + LH - LH * 0.25
    for i, (name, frac, _) in enumerate(langs):
        out.append(meter(x0, y, f"{i}", frac / top, f"{frac*100:4.1f}% {name}", 0.15 * i, cells))
        y += LH
    out.append(meter(x0, y, "Mem", min(1, st["contribs"] / st["goal"]), f"{st['contribs']}/{st['goal']} contribs", 1.0, cells)); y += LH
    out.append(meter(x0, y, "Swp", min(1, st["prs"] / 50), f"{st['prs']} pull requests", 1.2, cells)); y += LH * 1.6
    out.append(f'<text x="{x0}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["dim2"]}">Tasks: </tspan>{st["repos"]} repos, {sum(1 for r in st["recent"] if r["days"] <= 30)} running</text>'); y += LH
    out.append(f'<text x="{x0}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["dim2"]}">Load average: </tspan>{st["streak"]} {st["best_streak"]} {st["contribs"]}</text>'); y += LH
    out.append(f'<text x="{x0}" y="{y:.1f}" xml:space="preserve"><tspan fill="{P["dim2"]}">Uptime: </tspan>{st["uptime_days"]} days since {st["created"]}</text>'); y += LH
    css = "@keyframes fill{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    return css, "\n".join(out), y - y0
