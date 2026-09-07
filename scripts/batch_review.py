#!/usr/bin/env python3
"""Review many landing pages at once and rank them.

Feeds each page through check_landing.py and writes a scoreboard, so a gallery,
a competitor set, or a whole folder of drafts can be compared on the same rules.

Sources (combine freely):
  --urls URL [URL ...]         pages to fetch
  --urls-file FILE             one URL per line, '#' starts a comment
  --files FILE [FILE ...]      local HTML files, no network needed
  --gallery URL --limit N      best effort: the first N external sites linked from a
                               gallery or listing page (lapa.ninja, land-book, ...),
                               in the order the gallery shows them. Pass the listing
                               already sorted the way you want ranked.

Output:
  a Markdown scoreboard on stdout or --out report.md, and --json report.json.
  Every fetched page is saved under --save-dir (default: batch-pages/) so the
  judgement half of the review, the part no parser can do, has the HTML to read.

Score = P0 x 10 + P1 x 3 + P2 x 1. Lower is better. The four columns that decide
conversion (headline, fold, cta, proof) are broken out beside the total.

Standard library only. Python 3.8+.
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_landing as cl  # noqa: E402

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36 landing-craft/1.2")
WEIGHT = {"P0": 10, "P1": 3, "P2": 1}
FOCUS = ("headline", "fold", "cta", "proof")

# Hosts that a gallery links to but that are never the showcased landing page.
NOT_A_SITE = re.compile(
    r"(^|\.)(twitter|x|facebook|instagram|linkedin|github|youtube|producthunt|"
    r"dribbble|behance|pinterest|medium|threads|tiktok|reddit|discord|t)\.(com|net|me)$|"
    r"(^|\.)(google|apple|apps\.apple|play\.google|gstatic|googleapis|cloudflare|"
    r"cloudfront|gravatar|unsplash|figma|notion|typeform|mailchimp|substack)\.(com|net|so)$",
    re.I)


# ------------------------------------------------------------------ fetching

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,zh-TW;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        final = resp.geturl()
        ctype = resp.headers.get("Content-Type", "")
    m = re.search(r"charset=([\w-]+)", ctype, re.I)
    enc = m.group(1) if m else "utf-8"
    try:
        return raw.decode(enc, errors="replace"), final
    except LookupError:
        return raw.decode("utf-8", errors="replace"), final


def host_of(url):
    h = urllib.parse.urlsplit(url).hostname or ""
    return h[4:] if h.startswith("www.") else h


def slug(url):
    h = host_of(url) or "page"
    p = urllib.parse.urlsplit(url).path.strip("/")
    p = re.sub(r"\.html?$", "", p).replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", h + ("_" + p if p else ""))
    return s[:80]


# ------------------------------------------------------------------ gallery

def links_in(html, base):
    out = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\']', html, re.I):
        href = urllib.parse.urljoin(base, m.group(1).strip())
        if href.startswith(("http://", "https://")):
            out.append(href)
    return out


def gallery_sites(url, limit, log):
    """External sites linked from a listing page, in page order. If the listing
    links to its own detail pages instead, follow each one level down and take the
    first external site there."""
    html, final = fetch(url)
    gal = host_of(final)
    seen, sites = set(), []

    def take(links):
        for l in links:
            h = host_of(l)
            if not h or h == gal or h.endswith("." + gal) or NOT_A_SITE.search(h):
                continue
            if h in seen:
                continue
            seen.add(h)
            sites.append(l)
            if len(sites) >= limit:
                return True
        return False

    if take(links_in(html, final)):
        return sites

    internal, iseen = [], set()
    for l in links_in(html, final):
        h = host_of(l)
        path = urllib.parse.urlsplit(l).path
        if (h == gal or h.endswith("." + gal)) and path.count("/") >= 2 and l not in iseen:
            iseen.add(l)
            internal.append(l)
    log("gallery: %d external sites on the listing, following %d detail pages"
        % (len(sites), len(internal)))
    for l in internal:
        if len(sites) >= limit:
            break
        try:
            sub, subfinal = fetch(l)
        except Exception as e:  # noqa: BLE001
            log("  skip %s (%s)" % (l, e))
            continue
        ext = [x for x in links_in(sub, subfinal)
               if host_of(x) and host_of(x) != gal and not host_of(x).endswith("." + gal)
               and not NOT_A_SITE.search(host_of(x))]
        if ext:
            take(ext[:1])
        time.sleep(0.3)
    return sites


# ------------------------------------------------------------------ review

def review_one(src, is_url, save_dir):
    row = {"source": src, "fetched_from": None, "ok": False, "error": None,
           "score": 0, "P0": 0, "P1": 0, "P2": 0, "by_check": {}, "findings": [],
           "saved": None}
    try:
        if is_url:
            html, final = fetch(src)
            row["fetched_from"] = final
            path = os.path.join(save_dir, slug(final) + ".html")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            row["saved"] = path
        else:
            path = src
        fs = cl.audit(path)
    except Exception as e:  # noqa: BLE001
        row["error"] = "%s: %s" % (type(e).__name__, e)
        return row
    row["ok"] = True
    for f in sorted(fs, key=lambda f: (cl.ORDER[f.sev], f.check)):
        row[f.sev] += 1
        row["score"] += WEIGHT[f.sev]
        row["by_check"][f.check] = row["by_check"].get(f.check, 0) + 1
        row["findings"].append(f.as_dict())
    return row


def label(row):
    src = row["fetched_from"] or row["source"]
    if not src.startswith(("http://", "https://")):
        return os.path.basename(src)
    path = urllib.parse.urlsplit(src).path.rstrip("/")
    return host_of(src) + (path if path else "")


def markdown(rows, show_all):
    ok = [r for r in rows if r["ok"]]
    bad = [r for r in rows if not r["ok"]]
    out = ["# Landing page scoreboard", "",
           "%d pages reviewed, %d could not be fetched. Score = P0×10 + P1×3 + P2×1, "
           "lower is better. Mechanics only: a low score means the page does not "
           "undermine its own argument, not that the argument is good." % (len(ok), len(bad)),
           "",
           "| # | Page | Score | P0 | P1 | P2 | headline | fold | cta | proof | other |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ok, 1):
        bc = r["by_check"]
        other = sum(v for k, v in bc.items() if k not in FOCUS)
        out.append("| %d | %s | %d | %d | %d | %d | %s | %s | %s | %s | %s |" % (
            i, label(r), r["score"], r["P0"], r["P1"], r["P2"],
            bc.get("headline", 0) or "·", bc.get("fold", 0) or "·",
            bc.get("cta", 0) or "·", bc.get("proof", 0) or "·", other or "·"))
    if bad:
        out += ["", "## Could not be fetched", ""]
        for r in bad:
            out.append("- %s — %s" % (r["source"], r["error"]))
    out += ["", "## Findings per page", ""]
    for i, r in enumerate(ok, 1):
        out.append("### %d. %s" % (i, label(r)))
        out.append("")
        out.append("Source: %s" % (r["fetched_from"] or r["source"]))
        if r["saved"]:
            out.append("Saved HTML: `%s`" % r["saved"])
        out.append("")
        shown = [f for f in r["findings"] if show_all or f["severity"] != "P2"]
        if not shown:
            out.append("_no %s findings_" % ("" if show_all else "P0/P1 "))
        for f in shown:
            out.append("- **[%s] %s** — %s" % (f["severity"], f["check"], f["message"]))
            if f["fix"]:
                out.append("  - fix: %s" % f["fix"])
        hidden = len(r["findings"]) - len(shown)
        if hidden:
            out.append("- _%d P2 finding(s) hidden; pass --all to show_" % hidden)
        out.append("")
    return "\n".join(out)


HTML_CSS = """
:root{--ink:#161a20;--ink-2:#4b5563;--bg:#fbfaf7;--surface:#fff;--line:#e3e0d8;--p0:#b42318;--p1:#b54708;--p2:#475467;--ok:#067647}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#eef0f3;--ink-2:#aab2bf;--bg:#0f1319;--surface:#161c25;--line:#27303d;--p0:#f97066;--p1:#f79009;--p2:#98a2b3;--ok:#47cd89}}
:root[data-theme="dark"]{--ink:#eef0f3;--ink-2:#aab2bf;--bg:#0f1319;--surface:#161c25;--line:#27303d;--p0:#f97066;--p1:#f79009;--p2:#98a2b3;--ok:#47cd89}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI","PingFang TC","Noto Sans TC",sans-serif}
.wrap{max-width:72rem;margin:0 auto;padding:2rem 1.25rem}
h1{font-size:1.6rem;margin:0 0 .25rem}h2{font-size:1.15rem;margin:2rem 0 .5rem}h3{font-size:1rem;margin:1.5rem 0 .25rem}
p{color:var(--ink-2);max-width:70ch}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--line);white-space:nowrap}th{font-weight:600;color:var(--ink-2)}
td.n{text-align:right}.P0{color:var(--p0);font-weight:700}.P1{color:var(--p1);font-weight:600}.P2{color:var(--p2)}.ok{color:var(--ok)}
.bar{display:inline-block;height:.6rem;background:var(--p1);border-radius:2px;vertical-align:middle;margin-right:.4rem}
details{border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:.6rem .9rem;margin:.5rem 0}
summary{cursor:pointer;font-weight:600}li{margin:.35rem 0}.fix{color:var(--ink-2)}code{font-size:.9em}
"""


def html_report(rows, show_all):
    e = lambda s: (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    ok = [r for r in rows if r["ok"]]
    bad = [r for r in rows if not r["ok"]]
    top = max([r["score"] for r in ok] + [1])
    out = ["<title>Landing page scoreboard</title>", "<style>" + HTML_CSS + "</style>",
           '<div class="wrap">', "<h1>Landing page scoreboard</h1>",
           "<p>%d pages reviewed, %d could not be fetched. Score = P0×10 + P1×3 + P2×1, lower is better. "
           "Mechanics only: a low score means the page does not undermine its own argument, not that the "
           "argument is good.</p>" % (len(ok), len(bad)),
           '<div class="scroll"><table><thead><tr><th>#</th><th>Page</th><th>Score</th><th>P0</th><th>P1</th>'
           '<th>P2</th><th>headline</th><th>fold</th><th>cta</th><th>proof</th><th>other</th></tr></thead><tbody>']
    for i, r in enumerate(ok, 1):
        bc = r["by_check"]
        other = sum(v for k, v in bc.items() if k not in FOCUS)
        w = int(120 * r["score"] / top) if top else 0
        out.append('<tr><td>%d</td><td><a href="%s">%s</a></td><td class="n"><span class="bar" style="width:%dpx"></span>%d</td>'
                   '<td class="n %s">%d</td><td class="n %s">%d</td><td class="n P2">%d</td>'
                   '<td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
                       i, e(r["fetched_from"] or r["source"]), e(label(r)), w, r["score"],
                       "P0" if r["P0"] else "", r["P0"], "P1" if r["P1"] else "", r["P1"], r["P2"],
                       bc.get("headline", 0) or "·", bc.get("fold", 0) or "·", bc.get("cta", 0) or "·",
                       bc.get("proof", 0) or "·", other or "·"))
    out.append("</tbody></table></div>")
    if bad:
        out.append("<h2>Could not be fetched</h2><ul>")
        for r in bad:
            out.append("<li>%s — %s</li>" % (e(r["source"]), e(r["error"])))
        out.append("</ul>")
    out.append("<h2>Findings per page</h2>")
    for i, r in enumerate(ok, 1):
        shown = [f for f in r["findings"] if show_all or f["severity"] != "P2"]
        hidden = len(r["findings"]) - len(shown)
        out.append("<details%s><summary>%d. %s — score %d</summary>" % (" open" if i <= 3 else "", i, e(label(r)), r["score"]))
        if r["saved"]:
            out.append("<p>Saved HTML: <code>%s</code></p>" % e(r["saved"]))
        if not shown:
            out.append('<p class="ok">no %sfindings</p>' % ("" if show_all else "P0/P1 "))
        else:
            out.append("<ul>")
            for f in shown:
                out.append('<li><span class="%s">[%s] %s</span> — %s%s</li>' % (
                    f["severity"], f["severity"], e(f["check"]), e(f["message"]),
                    ('<div class="fix">fix: %s</div>' % e(f["fix"])) if f["fix"] else ""))
            out.append("</ul>")
        if hidden:
            out.append("<p>%d P2 finding(s) hidden; pass --all to include them.</p>" % hidden)
        out.append("</details>")
    out.append("</div>")
    return "\n".join(out)


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--urls", nargs="*", default=[])
    ap.add_argument("--urls-file")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--gallery")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--save-dir", default="batch-pages")
    ap.add_argument("--out", help="write the Markdown scoreboard here instead of stdout")
    ap.add_argument("--json", help="also write the full report as JSON")
    ap.add_argument("--html", help="also write a standalone HTML report")
    ap.add_argument("--all", action="store_true", help="show P2 findings per page too")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--keep-order", action="store_true",
                    help="keep source order (e.g. the gallery's ranking) instead of sorting by score")
    args = ap.parse_args()

    def log(msg):
        print(msg, file=sys.stderr)

    urls = list(args.urls)
    if args.urls_file:
        with open(args.urls_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    urls.append(line)
    if args.gallery:
        try:
            found = gallery_sites(args.gallery, args.limit, log)
        except Exception as e:  # noqa: BLE001
            log("gallery fetch failed: %s" % e)
            found = []
        log("gallery: %d site(s) collected" % len(found))
        for u in found:
            log("  " + u)
        urls += found

    jobs = [(u, True) for u in urls] + [(f, False) for f in args.files]
    if not jobs:
        ap.error("nothing to review: pass --urls, --urls-file, --files or --gallery")
    if urls:
        os.makedirs(args.save_dir, exist_ok=True)

    rows = [None] * len(jobs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {ex.submit(review_one, src, is_url, args.save_dir): i
                for i, (src, is_url) in enumerate(jobs)}
        for fut in concurrent.futures.as_completed(futs):
            i = futs[fut]
            rows[i] = fut.result()
            r = rows[i]
            log("%s %s  score=%s" % ("ok  " if r["ok"] else "FAIL", label(r),
                                     r["score"] if r["ok"] else r["error"]))

    if not args.keep_order:
        rows.sort(key=lambda r: (not r["ok"], r["score"], r["P0"], r["P1"]))

    md = markdown(rows, args.all)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        log("wrote " + args.out)
    else:
        print(md)
    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(html_report(rows, args.all))
        log("wrote " + args.html)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"weights": WEIGHT, "ranked": rows}, fh, indent=2, ensure_ascii=False)
        log("wrote " + args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
