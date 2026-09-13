"""Fetch real profile data from the GitHub GraphQL API (token from env or gh)."""
from __future__ import annotations
import json, os, subprocess, urllib.request, datetime as dt
from collections import Counter

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CONFIG = json.load(open(CONFIG_PATH)) if os.path.exists(CONFIG_PATH) else {}
LOGIN = os.environ.get("PROFILE_LOGIN") or CONFIG.get("login", "octocat")
GOAL = int(os.environ.get("CONTRIB_GOAL") or CONFIG.get("contrib_goal", 1000))

Q = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login){
    name login createdAt followers{totalCount} following{totalCount}
    contributionsCollection(from:$from, to:$to){
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions restrictedContributionsCount
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
    repositories(first:100, ownerAffiliations:OWNER, orderBy:{field:PUSHED_AT,direction:DESC}){
      totalCount
      nodes{ name isFork stargazerCount forkCount pushedAt diskUsage primaryLanguage{name color} description
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{name color} } } }
    }
  }
}"""


def _token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t: return t
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        return None


def fetch(login=LOGIN):
    year = dt.datetime.now(dt.timezone.utc).year
    body = json.dumps({"query": Q, "variables": {
        "login": login, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {_token()}", "Content-Type": "application/json",
        "User-Agent": "profile-renderer"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return shape(data["data"]["user"], year)


def shape(u, year):
    now = dt.datetime.now(dt.timezone.utc)
    created = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    # streaks
    counts = {d["date"]: d["contributionCount"] for d in days}
    streak, best, run = 0, 0, 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    for d in reversed(days):
        if dt.date.fromisoformat(d["date"]) > now.date(): continue
        if d["contributionCount"] > 0: streak += 1
        elif streak == 0 and d["date"] == now.date().isoformat(): continue
        else: break
    repos = [r for r in u["repositories"]["nodes"]]
    own = [r for r in repos if not r["isFork"]]
    # language share: each repo contributes 1.0 split by its language bytes,
    # so a single vendored monster repo can't dominate.
    langs, lang_color = Counter(), {}
    for r in own:
        tot = sum(e["size"] for e in r["languages"]["edges"]) or 1
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"] / tot
            lang_color[e["node"]["name"]] = e["node"]["color"]
    total = sum(langs.values()) or 1
    lang_share = [(k, v / total, lang_color.get(k)) for k, v in langs.most_common(10)]
    stars = sum(r["stargazerCount"] for r in own)
    year_start = dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc)
    year_len = (dt.datetime(year + 1, 1, 1, tzinfo=dt.timezone.utc) - year_start).days
    return {
        "config": CONFIG,
        "login": u["login"], "name": CONFIG.get("display_name") or u["name"] or u["login"], "year": year,
        "headline": CONFIG.get("headline") or (u["name"] or u["login"]).split()[0],
        "created": created.date().isoformat(),
        "uptime_days": (now - created).days,
        "followers": u["followers"]["totalCount"], "following": u["following"]["totalCount"],
        "repos": u["repositories"]["totalCount"], "own_repos": len(own), "forks": len(repos) - len(own),
        "stars": stars,
        "commits": cc["totalCommitContributions"], "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"], "reviews": cc["totalPullRequestReviewContributions"],
        "private": cc["restrictedContributionsCount"],
        "contribs": cal["totalContributions"], "goal": GOAL,
        "streak": streak, "best_streak": best,
        "calendar": [(d["date"], d["contributionCount"]) for d in days],
        "year_progress": min(1.0, (now - year_start).days / year_len),
        "langs": lang_share,
        "recent": [{"name": r["name"], "lang": (r["primaryLanguage"] or {}).get("name") or "-",
                    "stars": r["stargazerCount"], "kb": r["diskUsage"],
                    "days": (now - dt.datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00"))).days,
                    "desc": (r["description"] or "").strip()} for r in repos[:12]],
        "generated": now.strftime("%Y-%m-%d %H:%M UTC"),
    }
