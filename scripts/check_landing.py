#!/usr/bin/env python3
"""Static checks for a landing page.

A landing page has one job: turn a specific visitor into one specific action.
This script checks the parts of that job a parser can see -- how many actions
compete for the click, whether the promise is stated in the HTML itself,
whether the proof is real or placeholder, how much friction the form adds,
and what will hurt the largest contentful paint.

No third-party dependencies. Python 3.8+.

    python check_landing.py page.html [more.html ...] [--json] [--strict]

Exit code 1 when a P0 finding is present, so it can gate a build.

What it cannot see: whether the promise is true, whether the offer is any
good, whether the visitor came from an ad that said something different, and
anything the browser computes at runtime. A clean run means the mechanics are
sound, not that the page converts.
"""

import argparse
import json
import os
import re
import sys

# ------------------------------------------------------------------ patterns

# Words that promise nothing. A landing page built on these is describing
# itself instead of the visitor's problem.
EMPTY_CLAIMS = [
    "revolutionary", "cutting-edge", "cutting edge", "world-class", "world class",
    "best-in-class", "best in class", "seamless", "seamlessly", "game-changing",
    "game changing", "next-generation", "next generation", "state-of-the-art",
    "state of the art", "unparalleled", "unleash", "supercharge", "empower",
    "transform your", "take it to the next level", "one-stop shop", "synergy",
    "leverage the power", "innovative solution", "disruptive",
    "顛覆", "賦能", "無縫", "一站式", "革命性", "業界領先", "極致體驗",
]

# CTA labels that describe the mechanism instead of the outcome.
WEAK_CTA = [
    "submit", "click here", "learn more", "read more", "get started", "continue",
    "next", "go", "send", "ok", "確定", "送出", "更多", "了解更多", "點這裡",
]

# Text that betrays an unfinished page shipped as if it were finished.
# Multi-word only. A bare "placeholder" or "lorem" also matches prose that is
# merely talking about placeholders, which made this fire on its own template.
PLACEHOLDER = [
    "lorem ipsum", "dolor sit amet", "your company name", "company name here",
    "your logo here", "john doe", "jane doe", "customer name here",
    "testimonial here", "placeholder text", "yourdomain.com",
    "在此輸入", "範例文字", "這裡放",
]

PLACEHOLDER_IMG = ["placehold.co", "placeholder.com", "via.placeholder",
                   "picsum.photos", "dummyimage.com", "unsplash.it", "placekitten"]

# A claim shaped like evidence: a number with a unit, e.g. "40% faster", "10x".
STAT_RE = re.compile(r"\b\d[\d,.]*\s?(%|x\b|倍|％)", re.I)
CITE_NEAR_RE = re.compile(r"(source|據|資料來源|based on|n\s*=|sample|methodology|<cite)", re.I)

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


class Finding:
    __slots__ = ("sev", "check", "where", "msg", "fix")

    def __init__(self, sev, check, where, msg, fix=""):
        self.sev, self.check, self.where, self.msg, self.fix = sev, check, where, msg, fix

    def as_dict(self):
        return {"severity": self.sev, "check": self.check, "where": self.where,
                "message": self.msg, "fix": self.fix}


# ------------------------------------------------------------------- helpers

def visible_text(html):
    """Body text with script/style stripped. Good enough for word-level checks."""
    body = re.search(r"<body\b[^>]*>(.*)</body>", html, re.S | re.I)
    s = body.group(1) if body else html
    s = SCRIPT_STYLE_RE.sub(" ", s)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = TAG_RE.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def head_of(html):
    m = re.search(r"<head\b[^>]*>(.*?)</head>", html, re.S | re.I)
    return m.group(1) if m else ""


def inner_text(fragment):
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", fragment)).strip()


def meta(html, key, attr="name"):
    m = re.search(r'<meta[^>]+' + attr + r'=["\']' + re.escape(key) +
                  r'["\'][^>]*content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*' + attr +
                      r'=["\']' + re.escape(key) + r'["\']', html, re.I)
    return m.group(1) if m else None


# -------------------------------------------------------------------- checks

def check_promise(html, findings):
    """The promise has to exist in the HTML, not only after JS runs."""
    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not h1s:
        findings.append(Finding(
            "P0", "promise", "<h1>",
            "No <h1> in the served HTML. Whatever the page promises, a crawler, "
            "a social scraper and a reader on a failed JS load all see nothing.",
            "Put the headline in the HTML the server sends, even for an SPA."))
    elif len(h1s) > 1:
        findings.append(Finding(
            "P1", "promise", "<h1>",
            str(len(h1s)) + " <h1> elements. More than one top-level claim means "
            "the page has not decided what it is about.",
            "Keep one <h1>: the single promise. Demote the rest to <h2>."))
    else:
        t = inner_text(h1s[0])
        if len(t) < 12:
            findings.append(Finding(
                "P1", "promise", "<h1>",
                "The <h1> is " + str(len(t)) + " characters (" + repr(t) + "). "
                "That is usually a brand name, not a promise.",
                "State what the visitor gets, not what the product is called."))

    order = [int(m.group(1)) for m in re.finditer(r"<h([1-6])\b", html, re.I)]
    for prev, cur in zip(order, order[1:]):
        if cur > prev + 1:
            findings.append(Finding(
                "P2", "promise", "heading order",
                "Heading level jumps h" + str(prev) + " to h" + str(cur) +
                ". Screen-reader users navigate by this outline.",
                "Do not skip levels; style with CSS instead."))
            break


def _cta_candidates(html):
    out = []
    for m in re.finditer(r"<(a|button)\b([^>]*)>(.*?)</\1>", html, re.S | re.I):
        attrs, inner = m.group(2), m.group(3)
        text = inner_text(inner)
        href = re.search(r'href=["\']([^"\']*)["\']', attrs, re.I)
        out.append({"tag": m.group(1).lower(), "text": text,
                    "href": href.group(1) if href else None, "attrs": attrs})
    return out


def check_cta(html, findings):
    ctas = _cta_candidates(html)
    if not ctas:
        findings.append(Finding(
            "P0", "cta", "page",
            "No <a> or <button> found. A landing page with no action is a poster.",
            "Add the one action you want the visitor to take."))
        return

    # Which targets look like the conversion action rather than navigation?
    # "#start" jumps to the form and is a real call to action; a bare "#" is not.
    nav_like = re.compile(r"^(#$|/?$|/(about|blog|docs|pricing|login|privacy|terms|contact)"
                          r"|mailto:|tel:|https?://(www\.)?(twitter|x|facebook|linkedin|"
                          r"instagram|github|youtube)\.com)", re.I)
    action = [c for c in ctas if c["text"] and
              not (c["href"] and nav_like.match(c["href"] or ""))]

    targets = {}
    for c in action:
        key = (c["href"] or "form:" + c["text"].lower())
        targets.setdefault(key, []).append(c["text"])

    if len(targets) > 3:
        sample = ", ".join(list(targets)[:4])
        findings.append(Finding(
            "P1", "cta", "page",
            str(len(targets)) + " competing action targets (" + sample + " ...). "
            "Every extra choice splits attention and lowers the odds any one is taken.",
            "Pick one primary action. Everything else becomes a text link or goes away."))

    weak = [c["text"] for c in action
            if c["text"].strip().lower().strip(" .!→>") in WEAK_CTA]
    if weak:
        findings.append(Finding(
            "P1", "cta", ", ".join(sorted(set(weak))[:5]),
            "CTA text names the mechanism, not the outcome. "
            '"Submit" tells the visitor what the form does, not what they get.',
            'Use the outcome in the visitor\'s words: "Start my free trial", '
            '"Book the 20-minute demo".'))

    # Is any action reachable before the reader scrolls? Approximate: within the
    # first 40% of body markup.
    body = re.search(r"<body\b[^>]*>(.*)</body>", html, re.S | re.I)
    if body and action:
        b = body.group(1)
        cutoff = len(b) * 0.4
        first = min((b.find(c["text"]) for c in action if c["text"] and c["text"] in b),
                    default=-1)
        if first < 0 or first > cutoff:
            findings.append(Finding(
                "P2", "cta", "above the fold",
                "No action appears in the first 40% of the markup. Readers who are "
                "already convinced have nothing to click.",
                "Repeat the primary CTA near the headline."))


def check_language(html, findings):
    text = visible_text(html)
    low = text.lower()
    hits = sorted({w for w in EMPTY_CLAIMS if w in low})
    if len(hits) >= 3:
        findings.append(Finding(
            "P1", "copy", ", ".join(hits[:6]),
            str(len(hits)) + " empty superlatives. They are interchangeable between "
            "products, so they carry no information and read as generated.",
            "Replace each with the specific thing it is standing in for: a number, "
            "a named integration, a before/after."))
    elif hits:
        findings.append(Finding(
            "P2", "copy", ", ".join(hits),
            "Empty superlative(s) in the copy.",
            "Say the specific thing instead."))

    if not text:
        findings.append(Finding(
            "P0", "copy", "<body>",
            "No visible text in the served HTML.",
            "Render the copy server-side or prerender the page."))
        return
    words = len(re.findall(r"[A-Za-z']+", text)) + len(re.findall(r"[一-鿿]", text))
    if words < 120:
        findings.append(Finding(
            "P2", "copy", "<body>",
            "About " + str(words) + " words of copy. A landing page that answers "
            "objections is usually longer; this may be a shell.",
            "Check the page is not relying on JS to insert its own content."))


def check_proof(html, findings):
    text = visible_text(html)
    low = text.lower()

    ph = sorted({w for w in PLACEHOLDER if w in low})
    if ph:
        findings.append(Finding(
            "P0", "proof", ", ".join(ph[:5]),
            "Placeholder text is still on the page. Shipping filler as if it were "
            "proof is the fastest way to lose the visitor's trust.",
            "Replace with real content, or delete the section until you have it."))

    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    ph_img = [i for i in imgs if any(h in i.lower() for h in PLACEHOLDER_IMG)]
    if ph_img:
        findings.append(Finding(
            "P1", "proof", str(len(ph_img)) + " <img>",
            "Images still point at a placeholder service. On a real deployment they "
            "are also a third-party dependency and a privacy leak.",
            "Ship real assets from your own origin."))

    # A quoted testimonial with nobody attached to it.
    quotes = re.findall(r"<(blockquote|figure)\b[^>]*>(.*?)</\1>", html, re.S | re.I)
    unattributed = 0
    for _tag, inner in quotes:
        if not re.search(r"<(cite|figcaption)\b", inner, re.I) and len(inner_text(inner)) > 40:
            unattributed += 1
    if unattributed:
        findings.append(Finding(
            "P1", "proof", str(unattributed) + " quote block(s)",
            "Testimonial-shaped content with no attribution. An unattributed quote "
            "is treated as invented, so it costs trust rather than adding it.",
            "Add a real name, role and company in <cite>/<figcaption>, or drop it."))

    stats = STAT_RE.findall(text)
    if stats and not CITE_NEAR_RE.search(text):
        findings.append(Finding(
            "P2", "proof", str(len(stats)) + " numeric claim(s)",
            "The page states measured-sounding numbers with no source or method "
            "anywhere. Unsourced numbers invite the reader to discount all of them.",
            "Add what was measured, over what sample, when."))


def check_form(html, findings):
    for fm in re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, re.S | re.I):
        inner = fm.group(2)
        fields = re.findall(r"<(input|select|textarea)\b([^>]*)>", inner, re.I)
        real = [(t, a) for t, a in fields
                if not re.search(r'type=["\'](hidden|submit|button|image)["\']', a, re.I)]
        if len(real) > 5:
            findings.append(Finding(
                "P1", "form", "<form> with " + str(len(real)) + " fields",
                "Every field is a reason to abandon. Above about five, completion "
                "falls off sharply for a first contact.",
                "Ask only for what you need to make the next contact. The rest can "
                "come later."))
        no_label = 0
        for t, a in real:
            has_id = re.search(r'id=["\']([^"\']+)["\']', a, re.I)
            labelled = has_id and re.search(
                r'<label[^>]+for=["\']' + re.escape(has_id.group(1)) + r'["\']', inner, re.I)
            if not labelled and "aria-label" not in a.lower():
                no_label += 1
        if no_label:
            findings.append(Finding(
                "P0", "form", str(no_label) + " field(s)",
                "Form fields with no <label> and no aria-label. Placeholder text "
                "disappears on focus and is not announced as a name.",
                "Give every field a visible <label for=...>."))
        no_ac = [1 for t, a in real
                 if t.lower() == "input" and "autocomplete" not in a.lower()]
        if no_ac:
            findings.append(Finding(
                "P2", "form", str(len(no_ac)) + " input(s)",
                "No autocomplete attribute, so the browser cannot fill known values.",
                'Add autocomplete="email" / "name" / "tel" as appropriate.'))


def check_lcp(html, findings):
    head = head_of(html)

    blocking = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', head, re.I)
    remote_blocking = [l for l in blocking if re.search(r'href=["\']https?://', l, re.I)]
    if remote_blocking:
        findings.append(Finding(
            "P1", "lcp", str(len(remote_blocking)) + " stylesheet(s)",
            "Render-blocking stylesheet from another origin in <head>. The page "
            "cannot paint until a third party responds.",
            "Inline the critical CSS and self-host the rest."))

    sync_js = [t for t in re.findall(r"<script\b[^>]*>", head, re.I)
               if "src=" in t.lower() and not re.search(r"\b(async|defer|type=[\"']module)", t, re.I)]
    if sync_js:
        findings.append(Finding(
            "P1", "lcp", str(len(sync_js)) + " script(s)",
            "Synchronous external script in <head>. It blocks parsing before "
            "anything is on screen.",
            "Add defer, or move it to the end of <body>."))

    fonts = re.findall(r'<link[^>]+href=["\'][^"\']*fonts?[^"\']*["\'][^>]*>', head, re.I)
    no_swap = [f for f in fonts if "display=swap" not in f.lower()]
    if no_swap:
        findings.append(Finding(
            "P2", "lcp", "webfont link",
            "Webfont loaded without display=swap, so the headline can stay invisible "
            "while the font downloads.",
            "Append &display=swap, or set font-display: swap in @font-face."))

    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    if imgs:
        first = imgs[0]
        if "fetchpriority" not in first.lower():
            findings.append(Finding(
                "P2", "lcp", "first <img>",
                "The first image is most often the LCP element but is not "
                "prioritised, so it queues behind other requests.",
                'Add fetchpriority="high" to the hero image (and never lazy-load it).'))
        if re.search(r'loading=["\']lazy["\']', first, re.I):
            findings.append(Finding(
                "P1", "lcp", "first <img>",
                "The hero image is lazy-loaded, which delays the largest paint by "
                "design.",
                'Remove loading="lazy" from the above-the-fold image.'))
    missing_dims = [i for i in imgs
                    if not (re.search(r"\bwidth=", i, re.I) and re.search(r"\bheight=", i, re.I))
                    and "aspect-ratio" not in i.lower()]
    if missing_dims:
        findings.append(Finding(
            "P1", "lcp", str(len(missing_dims)) + " of " + str(len(imgs)) + " <img>",
            "Images without width/height reserve no space, so the text reflows as "
            "they arrive. That is the main source of layout shift.",
            "Set width and height attributes (CSS can still resize them)."))


def check_share(html, findings):
    missing = [k for k in ("og:title", "og:description", "og:image")
               if not meta(html, k, "property")]
    if missing:
        findings.append(Finding(
            "P1", "share", "<head>",
            "Missing " + ", ".join(missing) + ". A landing page is pasted into chat "
            "and social far more than it is browsed to; without these it appears as "
            "a bare URL.",
            "Add the Open Graph trio, with an image of at least 1200x630."))
    if not meta(html, "description"):
        findings.append(Finding(
            "P2", "share", "<head>",
            "No meta description, so the search snippet is chosen for you.",
            "Write one that states the promise in about 155 characters."))


def check_trust(html, findings):
    low = html.lower()
    has_form = "<form" in low
    links = " ".join(re.findall(r"<a\b[^>]*>.*?</a>", html, re.S | re.I)).lower()
    if has_form and not re.search(r"(privacy|隱私|policy|gdpr)", links):
        findings.append(Finding(
            "P1", "trust", "<form>",
            "The page collects personal data but links to no privacy policy. That "
            "is a trust problem before it is a compliance problem.",
            "Link the policy next to the submit button, not only in the footer."))
    if not re.search(r"(contact|about|聯絡|關於|company|imprint)", links):
        findings.append(Finding(
            "P2", "trust", "page",
            "No contact or about link. Visitors check who is behind an offer before "
            "handing over an email.",
            "Add a real identity: company, location, a way to reach a human."))


def check_measurement(html, findings):
    known = ("gtag(", "googletagmanager", "plausible", "umami", "fathom", "posthog",
             "matomo", "mixpanel", "segment.", "amplitude", "clarity.ms", "hotjar",
             "data-website-id", "va.vercel-scripts", "cloudflareinsights")
    if not any(k in html.lower() for k in known):
        findings.append(Finding(
            "P2", "measurement", "page",
            "No analytics detected. A landing page you cannot measure cannot be "
            "improved -- you will be guessing at every future change.",
            "Add a privacy-respecting analytics script and define the conversion "
            "event before launch."))


# --------------------------------------------------------------------- audit

def audit(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    findings = []
    for fn in (check_promise, check_cta, check_language, check_proof, check_form,
               check_lcp, check_share, check_trust, check_measurement):
        fn(html, findings)
    return findings


ORDER = {"P0": 0, "P1": 1, "P2": 2}


def main():
    ap = argparse.ArgumentParser(description="Static checks for a landing page.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on P1 findings too")
    args = ap.parse_args()

    report, total = {}, {"P0": 0, "P1": 0, "P2": 0}
    for path in args.files:
        if not os.path.isfile(path):
            print("skip: " + path + " is not a file", file=sys.stderr)
            continue
        fs = sorted(audit(path), key=lambda f: (ORDER[f.sev], f.check))
        report[path] = [f.as_dict() for f in fs]
        for f in fs:
            total[f.sev] += 1

    if args.json:
        print(json.dumps({"summary": total, "files": report},
                         indent=2, ensure_ascii=False))
    else:
        for path, fs in report.items():
            print("\n=== " + path + " ===")
            if not fs:
                print("  no findings")
            for f in fs:
                print("  [" + f["severity"] + "] " + f["check"] + ": " + f["where"])
                print("        " + f["message"])
                if f["fix"]:
                    print("        fix: " + f["fix"])
        print("\nTOTAL  P0=%d  P1=%d  P2=%d" % (total["P0"], total["P1"], total["P2"]))
        if total["P0"]:
            print("GATE: FAILED - P0 findings block launch.")
        elif args.strict and total["P1"]:
            print("GATE: FAILED (--strict) - P1 findings present.")
        else:
            print("GATE: passed (mechanics only - it cannot tell you if the offer is good).")

    if total["P0"] or (args.strict and total["P1"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
