"""ps aux: recently pushed repos as processes, plus a hexdump of the contribution calendar."""
from html import escape
from ..svg import P, CW, LH, chrome, Grid, rows_svg

HEAT = " .:-=+*#%@"
HEATC = ["dim", "dgreen", "dgreen", "green", "green", "green", "bgreen", "bgreen", "bgreen", "bwhite"]


def build(st, cols=96, nrepos=8):
    recent = st["recent"][:nrepos]
    g = Grid(cols, len(recent) + 12)
    g.text(0, 0, f"{'PID':>5} {'USER':<10}{'%CPU':>5} {'%MEM':>5} {'RSS':>7} {'STAT':<5}{'TIME':>6}  COMMAND", "black")
    for x in range(cols): g.co[0][x] = "bg"; 
    g.text(0, 0, f"{'PID':>5} {'USER':<10}{'%CPU':>5} {'%MEM':>5} {'RSS':>7} {'STAT':<5}{'TIME':>6}  COMMAND", "fg")
    maxkb = max((r["kb"] for r in recent), default=1) or 1
    for i, r in enumerate(recent):
        cpu = max(0.0, 100.0 * (1 - r["days"] / 180))
        mem = 100.0 * r["kb"] / maxkb
        stat = "R+" if r["days"] <= 14 else "S" if r["days"] <= 60 else "T"
        col = "green" if stat == "R+" else "fg" if stat == "S" else "dim2"
        line = f"{1000+i*7:>5} {st['login'][:9]:<10}{cpu:>5.1f} {mem:>5.1f} {r['kb']:>7} {stat:<5}{r['days']:>4}d   {r['name']}"
        g.text(0, i + 1, line, col)
        if r["lang"] != "-":
            g.text(len(line) + 2, i + 1, f"[{r['lang']}]", "cyan")
        if r["desc"]:
            start = len(line) + len(r["lang"]) + 5
            room = cols - start - 8
            if room > 10: g.text(start, i + 1, "# " + r["desc"][:room], "dim")
    # contribution graph: GitHub-style, month labels, weekday labels, 5 levels
    import datetime as _dt
    y = len(recent) + 3
    cal = st["calendar"]
    weeks = [cal[i:i + 7] for i in range(0, len(cal), 7)][:53]
    g.text(0, y - 1, f"$ contributions --year {st['year']}     "
           f"{st['contribs']} total · {st['commits']} commits · {st['prs']} PRs · streak {st['streak']}d (best {st['best_streak']}d)", "dim2")
    X0 = 5
    seen = set()
    for w, week in enumerate(weeks):
        d0 = _dt.date.fromisoformat(week[0][0])
        first = d0.month not in seen and (d0.day <= 7 or w == 0)
        if first:
            seen.add(d0.month)
            g.text(X0 + w, y, d0.strftime("%b"), "dim2")
    LV = [("dim", "·"), ("dgreen", "■"), ("green", "■"), ("bgreen", "■"), ("bwhite", "■")]
    top = max((c for _, c in cal), default=1) or 1
    today = _dt.date.today().isoformat()
    for d in range(7):
        if d in (1, 3, 5): g.text(0, y + 1 + d, ("Mon", "Wed", "Fri")[(d - 1) // 2], "dim2")
        for w, week in enumerate(weeks):
            if d < len(week):
                date, c = week[d]
                if date > today: continue
                k = 0 if c == 0 else 1 + min(3, int(3.999 * c / top))
                col, ch = LV[k]
                if date == today: ch, col = "▣", "yellow"
                g.put(X0 + w, y + 1 + d, ch, col)
    lg = X0 + len(weeks) + 3
    g.text(lg, y + 8, "less ", "dim2")
    for i, (col, ch) in enumerate(LV): g.put(lg + 5 + i, y + 8, ch, col)
    g.text(lg + 11, y + 8, " more   ▣ today", "dim2")
    return g


def body(st, x0, y0, cols=96):
    """Borderless variant: rows revealed progressively. Returns (css, svg, height)."""
    g = build(st, cols)
    out = []
    for r in range(g.h):
        sub = Grid(cols, 1); sub.ch[0] = g.ch[r]; sub.co[0] = g.co[r]
        out.append(f'<g class="row" style="animation-delay:{0.12*r:.2f}s">{rows_svg(sub, x0, y0 + r * LH)}</g>')
    css = ".row{opacity:0;animation:row 0.01s linear forwards}@keyframes row{to{opacity:1}}"
    return css, "\n".join(out), g.h * LH


def render(st):
    cols, pad = 96, 12
    g = build(st, cols)
    width = round(cols * CW + pad * 2)
    height = round(26 + g.h * LH + pad * 2)
    css = ("<style>.row{opacity:0;animation:row 0.01s linear forwards}@keyframes row{to{opacity:1}}</style>")
    # reveal rows progressively
    body = [css]
    for r in range(g.h):
        sub = Grid(cols, 1); sub.ch[0] = g.ch[r]; sub.co[0] = g.co[r]
        body.append(f'<g class="row" style="animation-delay:{0.12*r:.2f}s">{rows_svg(sub, pad, 26 + pad + r * LH)}</g>')
    return chrome(width, height, f"ps aux | head — {st['login']}", "sorted by pushed_at", "\n".join(body))
