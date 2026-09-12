"""A mounted warrior charging along the year's contribution track.

The horse's resting position on the track is the *real* contribution count
versus the goal; it gallops in place once it arrives.
"""
from html import escape
from ..svg import P, CW, LH, chrome, rows_svg, Grid, FS

# 4-frame gallop cycle. Rider = helmet 'o', lance '/' with pennant.
RIDER = [
r"""
                          |\
                          | \
                   o      |__\
                  /|\    /|
        ,-.      ( _ )  / |    ,--.
       (   `-.__.'   `-'  `--''  /\|
        `-.      \                 `
           \      \  ,-.          /
            `.     `'   `-.______'
              \    |        \    \
               \   |         \    \
               ~'  ~'        ~'   ~'
""",
r"""
                          |\
                          | \
                   o      |__\
                  /|\    /|
        ,-.      ( _ )  / |    ,--.
       (   `-.__.'   `-'  `--''  /\|
        `-.      \                 `
           \      \  ,-.          /
            `.     `'   `-.______'
              /    /          \    \
              /   /            \    \
             ~'  ~'             ~'   ~'
""",
r"""
                          |\
                          | \
                   o      |__\
                  /|\    /|
        ,-.      ( _ )  / |    ,--.
       (   `-.__.'   `-'  `--''  /\|
        `-.      \                 `
           \      \  ,-.          /
            `.     `'   `-.______'
               \   \          /    /
                \   \        /    /
                ~'   ~'     ~'   ~'
""",
r"""
                          |\
                          | \
                   o      |__\
                  /|\    /|
        ,-.      ( _ )  / |    ,--.
       (   `-.__.'   `-'  `--''  /\|
        `-.      \                 `
           \      \  ,-.          /
            `.     `'   `-.______'
              /    /          \    \
              /   /            \    \
             ~'  ~'             ~'   ~'
""",
]

CASTLE = [
"  |>",
" _|_",
"|_|_|",
]


def colour_rider(g: Grid, x0, y0, art):
    lines = art.strip("\n").split("\n")
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == " ": continue
            col = "orange"
            if r <= 2 and c >= 26: col = "red"                    # pennant
            elif r == 3 and c >= 25: col = "bwhite"               # pole
            elif r == 4 and 24 <= c <= 26: col = "bwhite"
            elif r in (2, 3) and 18 <= c <= 21: col = "byellow"   # rider
            elif r == 4 and 17 <= c <= 21: col = "byellow"        # saddle
            elif r >= 9: col = "dyellow"                           # legs
            elif r >= 5 and c >= 30: col = "bred" if r == 5 and c >= 33 else "orange"
            g.put(x0 + c, y0 + r, ch, col)


def render(st):
    cols, rows = 96, 17
    pad = 12
    width = round(cols * CW + pad * 2)
    height = round(26 + rows * LH + pad * 2)
    pct = min(1.0, st["contribs"] / st["goal"])
    x0 = pad
    ytop = 26 + pad
    track_w = (cols - 22) * CW
    tx = x0 + 2 * CW
    ty = ytop + 12 * LH
    body = []
    # static: header, castles, ground
    head = Grid(cols, rows)
    head.text(0, 15, f"THE CAMPAIGN OF {st['year']}", "byellow")
    head.text(0, 16, f"{st['contribs']} contributions ridden of {st['goal']}  [{int(pct*100):>3}%]   streak {st['streak']}d  best {st['best_streak']}d", "dim2")
    # milestones
    for i, q in enumerate((0.25, 0.5, 0.75, 1.0)):
        cx = 2 + int((cols - 22) * q)
        for r, line in enumerate(CASTLE):
            head.text(cx - 2, 9 + r, line, "bwhite" if pct >= q else "dim")
        head.text(cx - 2, 13, f"{int(st['goal']*q)}", "green" if pct >= q else "dim")
    head.text(0, 12, "_" * (cols - 18) + "_", "dim2")
    head.text(cols - 13, 15, f"{int(st['year_progress']*100)}% of year", "dim")
    ticks = "".join("." if i % 5 else "|" for i in range(cols - 18))
    head.text(0, 14, ticks, "dim")
    head.text(cols - 32, 16, "castles = 25/50/75/100% of goal", "dim")
    body.append(rows_svg(head, x0, ytop))
    # gallop frames, positioned by real progress via a one-shot charge animation
    n = len(RIDER)
    end_x = tx + track_w * pct
    art_w = 38 * CW
    charge = f"""
  .charge{{animation:charge 3.6s cubic-bezier(.2,.8,.2,1) 1 forwards}}
  @keyframes charge{{from{{transform:translate({x0:.1f}px,0)}}to{{transform:translate({end_x-art_w+8:.1f}px,0)}}}}
  .gl{{opacity:0;animation:gal 0.5s steps(1,end) infinite}}
  @keyframes gal{{0%{{opacity:1}}25%{{opacity:0}}100%{{opacity:0}}}}
  .dust{{animation:dust 0.9s linear infinite}}
  @keyframes dust{{0%{{opacity:.9;transform:translate(0,0)}}100%{{opacity:0;transform:translate(-26px,-5px)}}}}"""
    body.append(f'<style>{charge}</style>')
    body.append('<g class="charge">')
    for i, art in enumerate(RIDER):
        g = Grid(40, 12)
        colour_rider(g, 1, 0, art)
        body.append(f'<g class="gl glow" style="animation-delay:{-i*0.125:.3f}s">{rows_svg(g, 0, ytop + 0.5 * LH)}</g>')
    # dust puffs
    for i, (dx, dy) in enumerate(((6, 0), (0, -3), (-6, 1))):
        body.append(f'<text class="dust" style="animation-delay:{-i*0.3:.2f}s" x="{dx}" y="{ty - 2:.1f}" fill="{P["dim2"]}">{escape("°º")}</text>')
    body.append("</g>")
    right = f"{st['login']}@campaign · {st['generated']}"
    return chrome(width, height, "ride.sh — warrior progress on the yearly track", right, "\n".join(body))
