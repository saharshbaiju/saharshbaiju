"""dmesg-style boot log typed out line by line with the real numbers, then a prompt."""
from html import escape
from ..svg import P, CW, LH, chrome, FS


def render(st):
    up = st["uptime_days"]
    L = [
        ("dim2", "", f"Booting saharsh-os 6.{st['year']%100}.{st['own_repos']}-generic (gcc 14.2) #1 SMP PREEMPT_DYNAMIC"),
        ("green", "0.000000", f"Linux version {st['year']}.{st['contribs']} ({st['login']}@github) ..."),
        ("green", "0.000420", f"Command line: root=/dev/{st['login']} ro quiet splash init=/sbin/build"),
        ("green", "0.001337", f"CPU0: {st['name']} @ {st.get('config',{}).get('boot_org','github')}  [{st.get('config',{}).get('boot_tags','builder')}]"),
        ("green", "0.002048", f"Memory: {st['repos']} repos ({st['own_repos']} own, {st['forks']} forks), {st['stars']} stars, {st['followers']} followers"),
        ("green", "0.004096", f"uptime: {up} days since {st['created']}  ({up//365}y {up%365}d)"),
        ("green", "0.008192", "Loading modules: " + " ".join(l.lower().replace("+", "p").replace("#", "sharp") for l, _, _ in st["langs"][:7]) + "  [ OK ]"),
        ("green", "0.016384", f"sched: {st['commits']} commits, {st['prs']} PRs, {st['reviews']} reviews this year  ({st['private']} private)"),
        ("yellow", "0.032768", f"streak: {st['streak']} days (best {st['best_streak']})  --  WARN: caffeine levels nominal"),
        ("green", "0.065536", "mount /dev/esp32  /mnt/rc-hardware    type telemetry   [ OK ]"),
        ("green", "0.131072", "mount /dev/icpc   /mnt/competitive     type cp         [ OK ]"),
        ("green", "0.262144", f"init: reached target profile.target  --  {st['generated']}"),
    ]
    cols = 96
    pad = 12
    width = round(cols * CW + pad * 2)
    rows = len(L) + 2
    height = round(26 + rows * LH + pad * 2)
    css = ["  .ln{opacity:0;animation:ln 22s steps(1,end) infinite backwards}",
           "  @keyframes ln{0%{opacity:0}2%{opacity:1}93%{opacity:1}93.5%{opacity:0}100%{opacity:0}}",
           "  .pr{opacity:0;animation:pr 22s steps(1,end) infinite backwards}",
           "  @keyframes pr{0%{opacity:0}1%{opacity:1}93%{opacity:1}93.5%{opacity:0}100%{opacity:0}}",
           "  .ok{fill:%s}.warn{fill:%s}.ts{fill:%s}.k{fill:%s}" % (P["green"], P["yellow"], P["dim2"], P["fg"])]
    body = [f"<style>{chr(10).join(css)}</style>"]
    y0 = 26 + pad
    t = 0.0
    for i, (kind, ts, msg) in enumerate(L):
        y = y0 + (i + 1) * LH - LH * 0.25
        t += 0.35 + (0.9 if i in (6, 9) else 0.0)
        msg_html = escape(msg).replace("[ OK ]", '<tspan class="ok">[ OK ]</tspan>').replace("WARN:", '<tspan class="warn">WARN:</tspan>')
        ts_html = f'<tspan class="ts">[{ts:>12}] </tspan>' if ts else ""
        body.append(f'<text class="ln k" style="animation-delay:{t:.2f}s" x="{pad}" y="{y:.1f}" xml:space="preserve">{ts_html}{msg_html}</text>')
    # prompt + blinking cursor
    y = y0 + (len(L) + 2) * LH - LH * 0.25
    t += 0.8
    prompt = (f'<tspan fill="{P["green"]}">{st["login"]}@github</tspan><tspan fill="{P["fg"]}">:</tspan>'
              f'<tspan fill="{P["blue"]}">~</tspan><tspan fill="{P["fg"]}">$ </tspan>'
              f'<tspan fill="{P["white"]}">cat README.md</tspan>')
    plen = len(f"{st['login']}@github:~$ cat README.md") + 1
    body.append(f'<g class="pr" style="animation-delay:{t:.2f}s"><text x="{pad}" y="{y:.1f}" xml:space="preserve">{prompt}</text>'
                f'<rect class="cur" x="{pad + plen*CW:.1f}" y="{y - FS + 1:.1f}" width="{CW:.1f}" height="{FS + 1}" fill="{P["green"]}"/></g>')
    return chrome(width, height, f"dmesg — {st['login']}", "tty1 · refreshed daily", "\n".join(body))
