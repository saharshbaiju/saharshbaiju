"""The issue-driven shell.

Visitors open an issue titled `$ <command>`; the workflow runs this module,
which appends the command and its output to gen/data/session.json (rendered
into the profile) and writes reply.md for the issue comment.

Titles are untrusted input: they are parsed here, never passed to a shell.
"""
from __future__ import annotations
import json, os, random, re, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SESSION = os.path.join(HERE, "data", "session.json")
MAX_ENTRIES = 4          # entries shown on the profile
MAX_MSG = 60
SAFE = re.compile(r"[^A-Za-z0-9 .,!?'\"()\-:;#@+*/_<>=~^&%|]")

FORTUNES = [
    "There are only two hard things in CS: cache invalidation, naming things, and off-by-one errors.",
    "It works on my machine.  -- every engineer, moments before disaster",
    "A SQL query walks into a bar, sees two tables and asks: may I join you?",
    "rm -rf / is not a cleanup strategy.",
    "The best code is no code. The second best is code someone else maintains.",
    "Premature optimisation is the root of all evil. Late optimisation is the root of all overtime.",
    "In theory, theory and practice are the same. In practice, they are not.",
    "sudo make me a sandwich.",
    "Real programmers count from 0.",
    "The cloud is just someone else's computer, running your bugs at scale.",
    "Segfaults are the universe's way of saying you should have used bounds checks.",
    "99 little bugs in the code, take one down, patch it around, 127 little bugs in the code.",
]

COW = r"""
 {msg}
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||"""


def clean(s: str, n=MAX_MSG) -> str:
    s = SAFE.sub("", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:n]


def parse(title: str):
    t = title.strip()
    if t.startswith("$"): t = t[1:]
    t = t.strip()
    if not t: return "help", ""
    parts = t.split(None, 1)
    return parts[0].lower(), (parts[1] if len(parts) > 1 else "")


def run(cmd: str, arg: str, user: str, issue: int, st: dict | None) -> list[tuple[str, str]]:
    """-> list of (colour, line)."""
    st = st or {}
    if cmd == "say":
        msg = clean(arg)
        if not msg: return [("red", "say: nothing to say. usage: $ say <message>")]
        return [("byellow", f"[{user}] {msg}")]
    if cmd == "cowsay":
        msg = clean(arg) or "moo"
        top = " " + "_" * (len(msg) + 2)
        bot = " " + "-" * (len(msg) + 2)
        lines = [top, f"< {msg} >", bot] + COW.strip("\n").split("\n")[1:]
        return [("white", l) for l in lines]
    if cmd == "fortune":
        return [("cyan", FORTUNES[(issue or random.randrange(999)) % len(FORTUNES)])]
    if cmd == "ping":
        return [("fg", f"PING saharsh ({user}) 56(84) bytes of data."),
                ("green", f"64 bytes from saharsh: icmp_seq={issue} ttl=64 time=0.0{issue % 90 + 10} ms"),
                ("dim2", "--- saharsh ping statistics ---  1 packets transmitted, 1 received, 0% packet loss")]
    if cmd == "neofetch":
        rows = [
            ("green", f"{st.get('login','saharshbaiju')}@github"),
            ("dim2", "-------------------"),
            ("cyan", "OS: "), ("cyan", "Uptime: "), ("cyan", "Repos: "), ("cyan", "Contribs: "),
            ("cyan", "Streak: "), ("cyan", "Shell: "), ("cyan", "Location: "),
        ]
        vals = ["", "", "saharsh-os (github-actions) x86_64",
                f"{st.get('uptime_days','?')} days",
                f"{st.get('repos','?')} ({st.get('stars','?')} stars)",
                f"{st.get('contribs','?')} this year",
                f"{st.get('streak','?')} days (best {st.get('best_streak','?')})",
                "issue-sh 1.0", "Amritapuri, Kerala"]
        return [(c, k + v) for (c, k), v in zip(rows, vals)]
    if cmd in ("help", "?"):
        return [("fg", "available: say <msg> · cowsay <msg> · fortune · neofetch · ping · help"),
                ("dim2", "open an issue titled `$ <command>` and it runs on this profile")]
    if cmd in ("rm", "sudo", "curl", "wget"):
        return [("red", f"{cmd}: permission denied (nice try)")]
    return [("red", f"{clean(cmd, 20)}: command not found. try `$ help`")]


def main():
    title = os.environ.get("CMD_TITLE", " ".join(sys.argv[1:]) or "$ help")
    user = clean(os.environ.get("CMD_USER", "visitor"), 30) or "visitor"
    issue = int(os.environ.get("CMD_ISSUE", "0") or 0)
    cmd, arg = parse(title)
    st = None
    try:
        from .stats import fetch
        st = fetch()
    except Exception as e:  # stats are optional for the shell
        print("stats unavailable:", e, file=sys.stderr)
    out = run(cmd, arg, user, issue, st)
    entry = {"user": user, "cmd": clean(f"{cmd} {arg}".strip(), 70), "out": out,
             "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"), "issue": issue}
    log = []
    if os.path.exists(SESSION):
        log = json.load(open(SESSION))
    log = (log + [entry])[-MAX_ENTRIES:]
    json.dump(log, open(SESSION, "w"), indent=1)
    text = "\n".join(l for _, l in out)
    with open("reply.md", "w") as f:
        f.write(f"```\n{user}@saharsh:~$ {entry['cmd']}\n{text}\n```\n\n"
                f"Rendered into the profile: https://github.com/{st['login'] if st else 'saharshbaiju'}\n")
    print(text)


if __name__ == "__main__":
    main()
