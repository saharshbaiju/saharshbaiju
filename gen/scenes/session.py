"""The visitors' session log: commands run through issues, rendered as a tty."""
import json, os
from ..svg import Grid, rows_svg, LH

SESSION = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "session.json")


def body(st, x0, y0, cols=96):
    log = json.load(open(SESSION)) if os.path.exists(SESSION) else []
    lines = []
    for e in log:
        lines.append([("green", f"{e['user']}@saharsh"), ("fg", ":"), ("blue", "~"), ("fg", f"$ {e['cmd']}"), ("dim", f"   # {e['ts']}")])
        for col, text in e["out"]:
            lines.append([(col, text)])
        lines.append([])
    lines.append([("green", "visitor@saharsh"), ("fg", ":"), ("blue", "~"), ("fg", "$ ")])
    g = Grid(cols, len(lines))
    for r, parts in enumerate(lines):
        x = 0
        for col, text in parts:
            g.text(x, r, text[: cols - x], col)
            x += len(text)
    out = [rows_svg(g, x0, y0)]
    # blinking cursor after the empty prompt
    from ..svg import CW, FS, P
    cx = x0 + len("visitor@saharsh:~$ ") * CW
    cy = y0 + (len(lines) - 1) * LH + LH * 0.75 - FS + 1
    out.append(f'<rect class="cur" x="{cx:.1f}" y="{cy:.1f}" width="{CW:.1f}" height="{FS + 1}" fill="{P["green"]}"/>')
    return "", "\n".join(out), len(lines) * LH
