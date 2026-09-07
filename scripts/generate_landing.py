#!/usr/bin/env python3
"""Generate a landing page from a brief, without inventing anything.

    python3 scripts/generate_landing.py --init brief.json [--shape lead]   # annotated brief to fill in
    python3 scripts/generate_landing.py brief.json -o page.html [--check]  # build, then gate it

The brief carries every word the page will show. This script lays those words
out in the order the brief gives, wires the mechanics the checker gates (one
action worded identically at the fold and at the close, labelled fields, Open
Graph, a privacy link beside the form, inline CSS, no render-blocking requests)
and refuses to paper over a gap: no proof in the brief means no proof section
on the page, marked with a comment, never a placeholder.

It writes no copy of its own. Every headline, sentence and button label comes
from the brief. That is the point.

Standard library only. Python 3.8+.
"""

import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_landing as cl  # noqa: E402

SHAPES = ("waitlist", "saas", "app", "lead", "sales", "event", "cause")
STYLES = ("editorial", "product", "bold")

# ------------------------------------------------------------------ styles
# Three sober presets. Every pair is at or above WCAG AA. Left-aligned hero with
# a two-column grid on wide screens; nothing is centred by default.

TOKENS = {
    "editorial": {
        "light": "--ink:#151a22;--ink-2:#4b5563;--ink-3:#6b7280;--bg:#fbfaf6;--surface:#ffffff;"
                 "--line:#e5e2da;--accent:#0f5132;--on-accent:#ffffff;--tint:#eef5f0;--focus:#c8a13a",
        "dark": "--ink:#eef0f3;--ink-2:#b3bac6;--ink-3:#8b94a3;--bg:#0f1319;--surface:#161c25;"
                "--line:#27303d;--accent:#7fd1a4;--on-accent:#0f1319;--tint:#152119;--focus:#e9c25a",
        "display": '"Iowan Old Style","Palatino Linotype","Noto Serif TC","Songti TC",Georgia,serif',
        "body": '"PingFang TC","Noto Sans TC",system-ui,-apple-system,"Segoe UI",sans-serif',
        "radius": "6px", "h1": "clamp(1.7rem,4.8vw,3.1rem)", "h1w": "600", "ls": "-.005em",
    },
    "product": {
        "light": "--ink:#0f172a;--ink-2:#475569;--ink-3:#64748b;--bg:#ffffff;--surface:#f8fafc;"
                 "--line:#e2e8f0;--accent:#1d4ed8;--on-accent:#ffffff;--tint:#eff4ff;--focus:#f59e0b",
        "dark": "--ink:#e5eaf2;--ink-2:#aab4c3;--ink-3:#7f8a9b;--bg:#0b1220;--surface:#111a2b;"
                "--line:#1f2a3d;--accent:#8fb3ff;--on-accent:#0b1220;--tint:#0f1a33;--focus:#fbbf24",
        "display": '"PingFang TC","Noto Sans TC",system-ui,-apple-system,"Segoe UI",sans-serif',
        "body": '"PingFang TC","Noto Sans TC",system-ui,-apple-system,"Segoe UI",sans-serif',
        "radius": "10px", "h1": "clamp(1.7rem,4.6vw,3rem)", "h1w": "700", "ls": "-.02em",
    },
    "bold": {
        "light": "--ink:#0d0f12;--ink-2:#3f434a;--ink-3:#5f646c;--bg:#f4f1ea;--surface:#ffffff;"
                 "--line:#d9d4c8;--accent:#0d0f12;--on-accent:#f4f1ea;--tint:#ebe6d9;--focus:#d97706",
        "dark": "--ink:#f2efe8;--ink-2:#c6c1b6;--ink-3:#948f84;--bg:#0d0f12;--surface:#15181d;"
                "--line:#2a2e35;--accent:#f0b429;--on-accent:#0d0f12;--tint:#1b1d22;--focus:#f0b429",
        "display": '"Avenir Next","Helvetica Neue","PingFang TC","Noto Sans TC",system-ui,sans-serif',
        "body": '"PingFang TC","Noto Sans TC",system-ui,-apple-system,"Segoe UI",sans-serif',
        "radius": "2px", "h1": "clamp(1.9rem,6vw,4rem)", "h1w": "800", "ls": "-.03em",
    },
}

CSS = """
:root{%(light)s;--display:%(display)s;--body:%(body)s;--radius:%(radius)s;--max:66rem}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){%(dark)s}}
:root[data-theme="dark"]{%(dark)s}
*{box-sizing:border-box}
html{color-scheme:light dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:var(--max);margin:0 auto;padding:0 1.25rem}
header.hero{padding:3rem 0 3.5rem}
section{padding:3.5rem 0}
.band{background:var(--surface);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.mark{display:flex;align-items:center;gap:.6rem;color:var(--ink-3);font-size:.9375rem;margin-bottom:2rem}
.grid{display:grid;gap:2.5rem;align-items:start}\n.solo{max-width:44rem}
@media (min-width:56rem){.grid{grid-template-columns:minmax(0,1.3fr) minmax(0,.8fr)}}
h1{font-family:var(--display);font-size:%(h1)s;font-weight:%(h1w)s;letter-spacing:%(ls)s;line-height:1.15;margin:0 0 1rem;max-width:22ch;text-wrap:balance}
h2{font-family:var(--display);font-size:clamp(1.35rem,2.8vw,1.8rem);line-height:1.3;margin:0 0 .75rem;max-width:30ch;text-wrap:balance}
h3{font-size:1.0625rem;margin:0 0 .3rem}
p{margin:0 0 1rem;max-width:62ch;color:var(--ink-2);text-wrap:pretty}
.lede{font-size:1.125rem;max-width:50ch;color:var(--ink-2)}
.row{display:flex;flex-wrap:wrap;gap:.9rem;align-items:center;margin-top:1.75rem}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 1.5rem;border:0;border-radius:var(--radius);background:var(--accent);color:var(--on-accent);font:inherit;font-weight:700;text-decoration:none;cursor:pointer;transition:transform .12s ease}
.btn:hover{filter:brightness(1.06)}
.btn:active{transform:scale(.985)}
.aside{color:var(--ink-3);font-size:.9375rem;max-width:44ch;margin:0}
.signal{display:flex;gap:.6rem;align-items:flex-start;margin-top:1.5rem;padding:.9rem 1rem;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:0 var(--radius) var(--radius) 0;background:var(--surface);color:var(--ink-2);font-size:.9688rem;max-width:52ch}
.hero-side img{width:100%%;height:auto;border-radius:var(--radius);border:1px solid var(--line)}
.facts{display:grid;gap:.75rem;margin:1.5rem 0 0;padding:0;list-style:none}
@media (min-width:40rem){.facts{grid-template-columns:repeat(auto-fit,minmax(11rem,1fr))}}
.facts li{padding:1rem 1.1rem;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}
.facts b{display:block;font-family:var(--display);font-size:1.25rem}
.facts span{color:var(--ink-3);font-size:.9375rem}
.steps{counter-reset:s;display:grid;gap:.9rem;margin:1.75rem 0 0;padding:0;list-style:none}
.steps li{counter-increment:s;display:grid;grid-template-columns:2rem 1fr;column-gap:.9rem;padding-bottom:.9rem;border-bottom:1px solid var(--line)}
.steps li:last-child{border-bottom:0;padding-bottom:0}
.steps li::before{content:counter(s);font-size:.8125rem;color:var(--accent);border:1px solid var(--line);border-radius:50%%;width:2rem;height:2rem;display:grid;place-items:center;grid-row:span 2}
.steps b{display:block;font-size:1.0625rem}
.steps span{grid-column:2;color:var(--ink-2);font-size:.9688rem}
.quotes{display:grid;gap:1.25rem;margin-top:1.5rem}
@media (min-width:56rem){.quotes{grid-template-columns:repeat(auto-fit,minmax(18rem,1fr))}}
figure{margin:0;padding:1.25rem 1.35rem;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}
blockquote{margin:0 0 .75rem;font-size:1.0625rem;color:var(--ink)}
figcaption{color:var(--ink-3);font-size:.9375rem}
.numbers{display:grid;gap:1rem;margin:1.5rem 0 0;padding:0;list-style:none}
@media (min-width:40rem){.numbers{grid-template-columns:repeat(auto-fit,minmax(13rem,1fr))}}
.numbers li{padding:1rem 0;border-top:2px solid var(--accent)}
.numbers b{display:block;font-family:var(--display);font-size:1.75rem;line-height:1.1}
.numbers span{display:block;color:var(--ink-2);font-size:.9375rem}
.numbers cite{display:block;color:var(--ink-3);font-size:.875rem;font-style:normal;margin-top:.3rem}
.callout{padding:1.15rem 1.25rem;margin:1.5rem 0 0;border-left:3px solid var(--accent);background:var(--tint);border-radius:0 var(--radius) var(--radius) 0}
.callout b{display:block;margin-bottom:.3rem}
.callout p{margin:0;font-size:.9688rem}
.qa{display:grid;margin-top:1.5rem}
.qa div{padding:1.1rem 0;border-bottom:1px solid var(--line)}
.qa div:last-child{border-bottom:0}
.qa b{display:block;margin-bottom:.3rem}
.qa p{margin:0;font-size:.9688rem}
form{display:grid;gap:1.1rem;max-width:28rem;margin-top:1.5rem}
label{display:block;font-size:.9375rem;font-weight:700;margin-bottom:.35rem}
input,select,textarea{width:100%%;min-height:48px;padding:.65rem .85rem;font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius)}
input::placeholder{color:var(--ink-3)}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
footer{padding:2.25rem 0 3rem;border-top:1px solid var(--line);color:var(--ink-3);font-size:.9375rem}
footer a{color:inherit}
footer p{color:inherit}
@media (prefers-reduced-motion:reduce){*{transition-duration:.01ms!important}}
"""


# ------------------------------------------------------------------ helpers

def esc(s):
    return html.escape(str(s), quote=True)


def text_of(brief):
    """Every visible string in the brief, for placeholder and superlative scans."""
    out = []

    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if not str(k).startswith("_"):
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            out.append(v)
    walk(brief)
    return "\n".join(out)


class Refuse(Exception):
    pass


def validate(b, warn):
    """Everything the generator will not do on the author's behalf."""
    problems = []
    hero, action = b.get("hero") or {}, b.get("action") or {}
    head = (hero.get("headline") or "").strip().replace("\n", " ")
    if not head:
        problems.append("hero.headline is empty. The page has no promise; write the outcome the visitor gets.")
    else:
        low = head.lower()
        hits = [w for w in cl.EMPTY_CLAIMS if w in low]
        if hits:
            problems.append("hero.headline contains an empty superlative (%s). Write the specific thing it stands for." % ", ".join(hits))
        if len(head) < 12:
            problems.append("hero.headline is %d characters; that is a name, not a promise." % len(head))
        if head.rstrip().endswith(("?", "？")):
            problems.append("hero.headline is a question. State the outcome instead.")
        if cl.word_count(head) > 14:
            problems.append("hero.headline is about %d words. Move the mechanism into the subhead." % cl.word_count(head))
    if not (hero.get("subhead") or "").strip():
        warn("hero.subhead is empty: who it is for and how it works go unanswered before the scroll.")
    if not (hero.get("signal") or "").strip():
        warn("hero.signal is empty: the fold has no credibility signal. Add one true line, or accept the gap.")

    label = (action.get("label") or "").strip()
    if not label:
        problems.append("action.label is empty. Name what the visitor gets.")
    elif label.lower().strip(" .!→>") in cl.WEAK_CTA:
        problems.append("action.label %r names the mechanism, not the outcome." % label)
    if not action.get("href") and not b.get("form"):
        problems.append("action needs either an href (a link to sign up, download, book) or a top-level form.")

    for i, s in enumerate(b.get("sections") or []):
        where = "sections[%d] (%s)" % (i, s.get("type", "?"))
        if not (s.get("title") or "").strip():
            problems.append(where + " has no title. Every section needs an <h2> the reader can scan.")
        if s.get("type") == "proof":
            for j, q in enumerate(s.get("quotes") or []):
                if not (q.get("quote") or "").strip():
                    continue
                if not (q.get("name") or "").strip() or not (q.get("role") or "").strip():
                    problems.append(where + ".quotes[%d] has no name and role. Attribute it or drop it." % j)
            for j, n in enumerate(s.get("numbers") or []):
                miss = [k for k in ("value", "what", "sample", "when") if not (n.get(k) or "").strip()]
                if miss:
                    problems.append(where + ".numbers[%d] is missing %s. A number without its method is a claim." % (j, ", ".join(miss)))
    if not any(s.get("type") == "proof" and (s.get("quotes") or s.get("numbers"))
               for s in b.get("sections") or []):
        warn("no proof section with content: the page ships with none, marked in a comment. That is honest; filler would not be.")

    form = b.get("form")
    if form:
        fields = form.get("fields") or []
        if not fields:
            problems.append("form.fields is empty.")
        for j, f in enumerate(fields):
            for k in ("name", "label", "autocomplete"):
                if not (f.get(k) or "").strip():
                    problems.append("form.fields[%d] is missing %s." % (j, k))
        if len(fields) > 5:
            problems.append("form has %d fields. Ask for what the next contact needs; the rest can come later." % len(fields))
        if not (form.get("privacy_href") or "").strip() or not (form.get("privacy_label") or "").strip():
            problems.append("form.privacy_href and form.privacy_label are required next to any form.")
        if not (form.get("action") or "").strip():
            problems.append("form.action (where the form posts) is empty.")

    meta = b.get("meta") or {}
    if not (meta.get("description") or "").strip():
        warn("meta.description is empty: the search snippet will be chosen for you.")
    if not (meta.get("og_image") or "").strip():
        warn("meta.og_image is empty: shared links show as a bare URL. The checker will flag it.")
    if not b.get("analytics"):
        warn("analytics is empty: the page cannot be measured, so it cannot be improved. The checker will flag it.")
    if not (b.get("footer") or {}).get("links"):
        warn("footer.links is empty: no contact or about route on the page.")

    low = text_of(b).lower()
    ph = [w for w in cl.PLACEHOLDER if w in low]
    if ph:
        problems.append("placeholder text in the brief (%s). Replace it with real content or delete the field." % ", ".join(ph))
    if problems:
        raise Refuse("\n".join("  - " + p for p in problems))


# ------------------------------------------------------------------ render

def render_action(b, where):
    action, form = b["action"], b.get("form")
    label = esc(action["label"].strip())
    if action.get("href"):
        return '<a class="btn" href="%s">%s</a>' % (esc(action["href"]), label)
    if where == "hero":
        return '<a class="btn" href="#act">%s</a>' % label
    return '<button class="btn" type="submit">%s</button>' % label


def render_hero(b):
    h, out = b["hero"], []
    out.append('<header class="hero"><div class="wrap">')
    if b.get("site_name"):
        out.append('<div class="mark">%s</div>' % esc(b["site_name"]))
    img = h.get("image") or {}
    has_side = bool(img.get("src") or h.get("facts"))
    out.append('<div class="%s"><div>' % ("grid" if has_side else "solo"))
    # A newline in the headline is an authored line break; CJK has no spaces to break on.
    out.append("<h1>%s</h1>" % "<br>".join(esc(x.strip()) for x in h["headline"].strip().split("\n")))
    if h.get("subhead"):
        out.append('<p class="lede">%s</p>' % esc(h["subhead"].strip()))
    out.append('<div class="row">%s' % render_action(b, "hero"))
    if h.get("after_cta"):
        out.append('<p class="aside">%s</p>' % esc(h["after_cta"].strip()))
    out.append("</div>")
    if h.get("signal"):
        out.append('<p class="signal">%s</p>' % esc(h["signal"].strip()))
    out.append("</div>")
    if img.get("src"):
        out.append('<div class="hero-side"><img src="%s" alt="%s" width="%s" height="%s" '
                   'fetchpriority="high" decoding="async"></div>' % (
                       esc(img["src"]), esc(img.get("alt", "")),
                       esc(img.get("width", 1200)), esc(img.get("height", 800))))
    elif h.get("facts"):
        out.append('<div class="hero-side"><ul class="facts">')
        for f in h["facts"]:
            out.append("<li><b>%s</b><span>%s</span></li>" % (esc(f.get("value", "")), esc(f.get("label", ""))))
        out.append("</ul></div>")
    out.append("</div></div></header>")
    return "\n".join(out)


def paragraphs(items):
    return "\n".join("<p>%s</p>" % esc(p.strip()) for p in items or [] if p and p.strip())


def render_section(s, i):
    t = s.get("type", "text")
    cls = "band" if (s.get("band") if "band" in s else i % 2 == 1) else ""
    out = ['<section class="%s" id="s%d"><div class="wrap">' % (cls, i + 1),
           "<h2>%s</h2>" % esc(s["title"].strip())]
    if t == "problem" or t == "text":
        out.append(paragraphs(s.get("paragraphs")))
    elif t == "mechanism":
        if s.get("intro"):
            out.append("<p>%s</p>" % esc(s["intro"].strip()))
        if s.get("steps"):
            out.append('<ol class="steps">')
            for st in s["steps"]:
                out.append("<li><b>%s</b><span>%s</span></li>" % (esc(st.get("title", "")), esc(st.get("text", ""))))
            out.append("</ol>")
        if s.get("note"):
            out.append('<p class="aside" style="margin-top:1.25rem">%s</p>' % esc(s["note"].strip()))
    elif t == "facts":
        if s.get("intro"):
            out.append("<p>%s</p>" % esc(s["intro"].strip()))
        out.append('<ul class="facts">')
        for f in s.get("items") or []:
            out.append("<li><b>%s</b><span>%s</span></li>" % (esc(f.get("value", "")), esc(f.get("label", ""))))
        out.append("</ul>")
        if s.get("note"):
            out.append('<p class="aside" style="margin-top:1.25rem">%s</p>' % esc(s["note"].strip()))
    elif t == "proof":
        if s.get("intro"):
            out.append("<p>%s</p>" % esc(s["intro"].strip()))
        quotes = [q for q in s.get("quotes") or [] if (q.get("quote") or "").strip()]
        if quotes:
            out.append('<div class="quotes">')
            for q in quotes:
                who = ", ".join(x for x in (q.get("name"), q.get("role"), q.get("context")) if x)
                out.append("<figure><blockquote>%s</blockquote><figcaption>%s</figcaption></figure>"
                           % (esc(q["quote"].strip()), esc(who)))
            out.append("</div>")
        nums = [n for n in s.get("numbers") or [] if (n.get("value") or "").strip()]
        if nums:
            out.append('<ul class="numbers">')
            for n in nums:
                src = "; ".join(x for x in (n.get("sample"), n.get("when"), n.get("source")) if x)
                out.append("<li><b>%s</b><span>%s</span><cite>%s</cite></li>"
                           % (esc(n["value"]), esc(n.get("what", "")), esc(src)))
            out.append("</ul>")
        if not quotes and not nums:
            out.append("<!-- proof: nothing supplied in the brief. Left empty on purpose; do not fill with filler. -->")
    elif t == "objections":
        if s.get("intro"):
            out.append("<p>%s</p>" % esc(s["intro"].strip()))
        c = s.get("callout") or {}
        if c.get("title") or c.get("text"):
            out.append('<div class="callout"><b>%s</b><p>%s</p></div>' % (esc(c.get("title", "")), esc(c.get("text", ""))))
        if s.get("items"):
            out.append('<div class="qa">')
            for it in s["items"]:
                out.append("<div><b>%s</b><p>%s</p></div>" % (esc(it.get("q", "")), esc(it.get("a", ""))))
            out.append("</div>")
    else:
        out.append(paragraphs(s.get("paragraphs")))
    out.append("</div></section>")
    return "\n".join(out)


def render_closing(b, i):
    c, form = b.get("closing") or {}, b.get("form")
    cls = "band" if i % 2 == 1 else ""
    out = ['<section class="%s" id="act"><div class="wrap">' % cls]
    if c.get("title"):
        out.append("<h2>%s</h2>" % esc(c["title"].strip()))
    if c.get("text"):
        out.append("<p>%s</p>" % esc(c["text"].strip()))
    if form:
        out.append('<form method="%s" action="%s">' % (esc(form.get("method", "post")), esc(form["action"])))
        for j, f in enumerate(form["fields"]):
            fid = "f-" + re.sub(r"[^a-z0-9]+", "-", f["name"].lower())
            ftype = f.get("type", "text")
            attrs = ['id="%s"' % fid, 'name="%s"' % esc(f["name"]), 'autocomplete="%s"' % esc(f["autocomplete"])]
            if f.get("required", True):
                attrs.append("required")
            if f.get("placeholder"):
                attrs.append('placeholder="%s"' % esc(f["placeholder"]))
            if ftype == "textarea":
                out.append('<div><label for="%s">%s</label><textarea %s rows="4"></textarea></div>'
                           % (fid, esc(f["label"]), " ".join(attrs)))
            else:
                attrs.insert(2, 'type="%s"' % esc(ftype))
                if ftype in ("text", "email", "tel", "url"):
                    attrs.append('spellcheck="false"')
                out.append('<div><label for="%s">%s</label><input %s></div>' % (fid, esc(f["label"]), " ".join(attrs)))
        out.append(render_action(b, "closing"))
        note = esc(form.get("note", "").strip())
        out.append('<p class="aside">%s%s<a href="%s">%s</a></p>' % (
            note, " " if note else "", esc(form["privacy_href"]), esc(form["privacy_label"])))
        out.append("</form>")
    else:
        out.append('<div class="row">%s' % render_action(b, "closing"))
        if (b.get("hero") or {}).get("after_cta"):
            out.append('<p class="aside">%s</p>' % esc(b["hero"]["after_cta"].strip()))
        out.append("</div>")
    out.append("</div></section>")
    return "\n".join(out)


def render_footer(b):
    f = b.get("footer") or {}
    out = ["<footer><div class=\"wrap\">"]
    bits = [esc(b.get("site_name", ""))] if b.get("site_name") else []
    for l in f.get("links") or []:
        bits.append('<a href="%s">%s</a>' % (esc(l["href"]), esc(l["label"])))
    if bits:
        out.append("<p>%s</p>" % " · ".join(bits))
    if f.get("legal"):
        out.append('<p style="margin-top:.5rem">%s</p>' % esc(f["legal"].strip()))
    out.append("</div></footer>")
    return "\n".join(out)


def render_analytics(b):
    a = b.get("analytics")
    if not a or not a.get("src"):
        return "<!-- analytics: none configured. Fill brief.analytics before launch, or the page cannot be measured. -->"
    attrs = " ".join('%s="%s"' % (esc(k), esc(v)) for k, v in (a.get("attrs") or {}).items())
    return '<script defer src="%s" %s></script>' % (esc(a["src"]), attrs)


def render(b):
    style = b.get("style") or "editorial"
    if style not in STYLES:
        raise Refuse("  - style must be one of %s" % ", ".join(STYLES))
    meta, hero = b.get("meta") or {}, b["hero"]
    title = (meta.get("title") or hero["headline"]).strip()
    desc = (meta.get("description") or hero.get("subhead") or "").strip()
    og_img = (meta.get("og_image") or "").strip()
    head = ['<!doctype html>', '<html lang="%s">' % esc(b.get("lang", "en")), "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
            "<title>%s</title>" % esc(title)]
    if desc:
        head.append('<meta name="description" content="%s">' % esc(desc))
    if meta.get("canonical"):
        head.append('<link rel="canonical" href="%s">' % esc(meta["canonical"]))
    head += ['<meta property="og:type" content="website">',
             '<meta property="og:title" content="%s">' % esc(title)]
    if desc:
        head.append('<meta property="og:description" content="%s">' % esc(desc))
    if og_img:
        head.append('<meta property="og:image" content="%s">' % esc(og_img))
        head.append('<meta name="twitter:card" content="summary_large_image">')
    if b.get("site_name"):
        head.append('<meta property="og:site_name" content="%s">' % esc(b["site_name"]))
    head.append("<style>%s</style>" % (CSS % TOKENS[style]).strip())
    head.append("</head>")

    body = ["<body>", render_hero(b)]
    sections = b.get("sections") or []
    for i, s in enumerate(sections):
        body.append(render_section(s, i))
    body.append(render_closing(b, len(sections)))
    body.append(render_footer(b))
    body.append(render_analytics(b))
    body.append("</body></html>")
    return "\n".join(head + body) + "\n"


# ------------------------------------------------------------------ --init

def init_brief(shape):
    """An annotated brief. Keys starting with _ are notes and are ignored."""
    lead_form = {
        "_hint": "Ask only for what the next contact needs. Every field is an exit.",
        "action": "/intake", "method": "post",
        "fields": [
            {"name": "email", "label": "", "type": "email", "autocomplete": "email", "required": True, "placeholder": ""}
        ],
        "note": "", "privacy_label": "", "privacy_href": "/privacy",
    }
    b = {
        "_read_me": [
            "Every visible word on the page comes from this file. The generator writes no copy.",
            "Leave a field empty and the element is omitted. Required fields are checked; the run refuses with a list.",
            "Never type a testimonial, name, logo, rating or number you cannot point at a source for.",
            "Keys starting with _ are notes for you and are ignored.",
        ],
        "lang": "en", "site_name": "", "shape": shape, "style": "editorial",
        "_style": "editorial | product | bold",
        "meta": {"title": "", "description": "", "og_image": "/og.png", "canonical": ""},
        "hero": {
            "_hint": "Headline = the outcome the visitor gets, under 12 words. Subhead = who it is for and how it works. Signal = one TRUE credibility line.",
            "headline": "", "subhead": "", "signal": "", "after_cta": "",
            "image": {"src": "", "alt": "", "width": 1200, "height": 800},
        },
        "action": {"_hint": "Name what the visitor gets: 'Send me the guide', 'Book the 20-minute call'. Give href for a link, or leave href empty and fill form below.",
                   "label": "", "href": ""},
        "sections": [],
        "closing": {"title": "", "text": ""},
        "form": None,
        "footer": {"links": [{"label": "", "href": "/about"}, {"label": "", "href": "/contact"}, {"label": "", "href": "/privacy"}], "legal": ""},
        "analytics": {"_hint": "e.g. {\"src\": \"/umami.js\", \"attrs\": {\"data-website-id\": \"...\"}}. Empty = page cannot be measured.",
                      "src": "", "attrs": {}},
    }
    problem = {"type": "problem", "title": "", "paragraphs": ["", ""], "_hint": "The problem in the visitor's words. If they do not recognise themselves here, nothing below lands."}
    mechanism = {"type": "mechanism", "title": "", "intro": "", "steps": [{"title": "", "text": ""}, {"title": "", "text": ""}, {"title": "", "text": ""}], "note": ""}
    proof = {"type": "proof", "title": "", "intro": "",
             "quotes": [{"quote": "", "name": "", "role": "", "context": ""}],
             "numbers": [{"value": "", "what": "", "sample": "", "when": "", "source": ""}],
             "_hint": "Real people, real numbers with method. Leave empty and the section is omitted with a comment."}
    objections = {"type": "objections", "title": "", "intro": "", "callout": {"title": "", "text": ""},
                  "items": [{"q": "", "a": ""}, {"q": "", "a": ""}],
                  "_hint": "The specific reasons not to act, answered plainly. Price and switching cost live here."}
    facts = {"type": "facts", "title": "", "intro": "", "items": [{"value": "", "label": ""}], "note": ""}

    if shape == "waitlist":
        b["sections"] = [problem, mechanism, proof]
        b["form"] = lead_form
        b["_shape"] = "Waitlist: one field, honest scarcity, say when they will hear from you."
    elif shape == "saas":
        b["sections"] = [problem, mechanism, proof, objections]
        b["action"]["href"] = "/signup"
        b["_shape"] = "SaaS: link to the trial; pricing objection answered on the page, not hidden."
    elif shape == "app":
        b["sections"] = [mechanism, proof, objections]
        b["action"]["href"] = "https://apps.apple.com/app/..."
        b["_shape"] = "App: one store link as the primary action; the other store as a text link."
    elif shape == "lead":
        b["sections"] = [problem, mechanism, proof, objections]
        b["form"] = lead_form
        b["form"]["fields"].append({"name": "detail", "label": "", "type": "text", "autocomplete": "off", "required": True, "placeholder": ""})
        b["_shape"] = "Lead capture: two or three fields, and say what happens after they submit."
    elif shape == "sales":
        b["sections"] = [problem, mechanism, proof, objections, facts]
        b["action"]["href"] = "/checkout"
        b["_shape"] = "Long-form sales: every section removes one objection; the facts block carries the offer and price."
    elif shape == "event":
        b["hero"]["facts"] = [{"value": "", "label": "date"}, {"value": "", "label": "place"}]
        b["sections"] = [problem, facts, proof, objections]
        b["form"] = lead_form
        b["_shape"] = "Event: date and place in the fold; the facts block is the agenda."
    elif shape == "cause":
        b["sections"] = [problem, mechanism, proof, objections]
        b["action"]["href"] = "/donate"
        b["_shape"] = "Cause: the mechanism section says where the money goes, concretely."
    return b


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brief", nargs="?", help="brief JSON to build from")
    ap.add_argument("-o", "--out", help="output HTML (default: stdout)")
    ap.add_argument("--init", metavar="FILE", help="write an annotated brief to FILE and exit")
    ap.add_argument("--shape", default="lead", choices=SHAPES, help="shape for --init")
    ap.add_argument("--check", action="store_true", help="run check_landing on the output")
    ap.add_argument("--strict", action="store_true", help="with --check: P1 also fails")
    args = ap.parse_args()

    if args.init:
        if os.path.exists(args.init):
            print("refusing to overwrite " + args.init, file=sys.stderr)
            return 2
        with open(args.init, "w", encoding="utf-8") as fh:
            json.dump(init_brief(args.shape), fh, indent=2, ensure_ascii=False)
        print("wrote %s (shape: %s). Fill it in, then: generate_landing.py %s -o page.html --check"
              % (args.init, args.shape, args.init), file=sys.stderr)
        return 0
    if not args.brief:
        ap.error("give a brief JSON, or --init FILE")

    with open(args.brief, encoding="utf-8") as fh:
        brief = json.load(fh)
    warnings = []
    try:
        validate(brief, warnings.append)
        page = render(brief)
    except Refuse as r:
        print("refused: the brief needs work before a page can be built from it\n" + str(r), file=sys.stderr)
        return 2
    for w in warnings:
        print("warning: " + w, file=sys.stderr)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(page)
        print("wrote " + args.out, file=sys.stderr)
    else:
        sys.stdout.write(page)

    if args.check and args.out:
        fs = sorted(cl.audit(args.out), key=lambda f: (cl.ORDER[f.sev], f.check))
        tot = {"P0": 0, "P1": 0, "P2": 0}
        for f in fs:
            tot[f.sev] += 1
            print("  [%s] %s: %s\n        %s" % (f.sev, f.check, f.where, f.msg), file=sys.stderr)
        print("check: P0=%d P1=%d P2=%d" % (tot["P0"], tot["P1"], tot["P2"]), file=sys.stderr)
        if tot["P0"] or (args.strict and tot["P1"]):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
