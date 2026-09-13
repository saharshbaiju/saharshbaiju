"""python -m gen  ->  renders every panel into assets/."""
import json, os, sys, time
from .svg import frames_panel
from .stats import fetch
from .scenes import torus, cube, globe, name3d, rider, boot, htop, ps, screen

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    cache = os.environ.get("STATS_CACHE")
    if cache and os.path.exists(cache):
        st = json.load(open(cache))
    else:
        st = fetch()
        if cache: json.dump(st, open(cache, "w"))
    print(f"stats: {st['contribs']} contribs, {st['repos']} repos, uptime {st['uptime_days']}d")
    panels = {**{k: (lambda fn=fn: fn(st)) for k, fn in screen.SECTIONS.items()},
        "extra-boot.svg": lambda: boot.render(st),
        "extra-torus.svg": lambda: frames_panel(torus.render(), "donut.c", "spinning torus · 60 frames", secs=4.0),
        "extra-tesseract.svg": lambda: frames_panel(cube.render(), "tesseract.c", "4D hypercube · xw+yz rotation", secs=6.0),
        "extra-globe.svg": lambda: frames_panel(globe.render(), "globe.c", "@ = Amritapuri, Kerala", secs=8.0),
        "extra-name.svg": lambda: frames_panel(name3d.render(st["name"].split()[0]), "name3d.c", "5x7 bitmap · extruded · perspective", secs=6.0),
        "extra-ride.svg": lambda: rider.render(st),
        "extra-htop.svg": lambda: htop.render(st),
        "extra-ps.svg": lambda: ps.render(st),
    }
    args = sys.argv[1:]
    extras = "--extras" in args
    only = [a for a in args if not a.startswith("--")]
    for name, fn in panels.items():
        if only and name.split(".")[0] not in only: continue
        if not only and not extras and name not in screen.SECTIONS: continue
        t = time.time()
        svg = fn()
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)
        print(f"  {name:<16} {len(svg)/1024:7.1f} KB  {time.time()-t:5.1f}s")
    print(f"done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
