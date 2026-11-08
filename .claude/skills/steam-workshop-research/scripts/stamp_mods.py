#!/usr/bin/env python
"""Stamp Steam Workshop items with authoritative metadata.

Usage:
    python stamp_mods.py <publishedfileid> [<publishedfileid> ...]

Prints one row per item, sorted newest-updated first:
    id | updated | days-ago | created | subs | vis | banned | title

Uses ISteamRemoteStorage/GetPublishedFileDetails, which needs no API key.
Stdlib only, so it runs anywhere without a curl quoting fight.

Read the result codes: 1 = normal, 9 = not in this endpoint, which is NOT proof
that the item is deleted -- open the Workshop page and check for the Subscribe
button and subscriber count before reporting anything as removed.
"""
import datetime
import json
import sys
import urllib.parse
import urllib.request

API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"


def fetch(ids):
    data = [("itemcount", str(len(ids)))]
    for i, pid in enumerate(ids):
        data.append(("publishedfileids[%d]" % i, pid))
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(API, data=body)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["response"]["publishedfiledetails"]


def main(argv):
    ids = [a.strip() for a in argv if a.strip().isdigit()]
    if not ids:
        print(__doc__)
        return 2

    now = datetime.datetime.utcnow()
    rows = []
    for f in fetch(ids):
        pid = f.get("publishedfileid")
        if f.get("result") != 1:
            rows.append((pid, f"NOT IN API (result={f.get('result')}) -- open the page to confirm"))
            continue
        created = datetime.datetime.utcfromtimestamp(f["time_created"])
        updated = datetime.datetime.utcfromtimestamp(f["time_updated"])
        rows.append((pid, None, updated, (now - updated).days, created,
                     f.get("subscriptions"), f.get("visibility"),
                     f.get("banned"), f.get("title")))

    rows.sort(key=lambda r: r[2] or datetime.datetime(1970, 1, 1), reverse=True)
    print("today (UTC): %s" % now.date())
    for r in rows:
        if len(r) == 2:
            print("%-12s %s" % (r[0], r[1]))
            continue
        pid, _, updated, days, created, subs, vis, banned, title = r
        print("%-12s updated=%s (%4dd ago) created=%s subs=%-8s vis=%s banned=%s  %s"
              % (pid, updated.date(), days, created.date(), subs, vis, banned, title))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
