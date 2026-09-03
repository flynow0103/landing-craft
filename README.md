# Landing Craft

An agent skill for designing and building landing pages, with a static checker
that gates the page before it ships.

A landing page is one argument, made once, to one person, ending in one action.
This skill is opinionated about that and deliberately silent about visual style.
It makes you decide what the page is arguing, then checks that the mechanics do
not undermine the argument.

## What is in here

```
SKILL.md                       the workflow: brief -> thesis -> sequence -> build -> gate
scripts/check_landing.py       static checker, no dependencies, exit 1 on P0
assets/skeleton.html           starting template; passes the checker on a clean checkout
references/
  message-architecture.md      the fold, headline patterns, ordering sections against objections
  proof-and-honesty.md         evidence types, and the line this skill does not cross
  conversion-mechanics.md      CTA wording, form friction, mobile, what to delete
  performance-budget.md        LCP, CLS, INP, and a budget worth holding
```

## The checker

```bash
python3 scripts/check_landing.py page.html            # P0 blocks
python3 scripts/check_landing.py page.html --strict    # P1 blocks too
python3 scripts/check_landing.py *.html --json         # for CI
```

It finds what a parser can see:

- competing calls to action, and CTA text that names the mechanism instead of the outcome
- a promise that exists only after JavaScript runs
- placeholder text and unattributed testimonials still on the page
- numeric claims with no method or source anywhere
- form field count, missing labels, missing `autocomplete`
- render-blocking stylesheets and scripts, lazy-loaded hero images, images without dimensions
- missing Open Graph tags, missing privacy or contact links, missing analytics

It cannot tell you whether the promise is true or the offer is any good. A clean
run means the mechanics are sound, nothing more.

## Installing

**As a project skill** — copy the directory into a repository:

```bash
git clone https://github.com/flynow0103/landing-craft
mkdir -p your-project/.claude/skills
cp -r landing-craft your-project/.claude/skills/landing-craft
```

**For all your projects** — copy it to `~/.claude/skills/landing-craft` instead.

Then ask for a landing page in the normal way, or invoke `/landing-craft`.

Requires Python 3.8+ for the checker. Nothing else.

## The one rule that is not about conversion rate

**Never invent proof.** No testimonial, customer name, logo, review count, user
total, or benchmark result that cannot be pointed at a source. Not as a mockup,
not as a placeholder "to be replaced later" — that is the one that ships. If the
brief has no proof in it, the page ships with an empty proof section and a note
saying so. `references/proof-and-honesty.md` covers what to do when you genuinely
have nothing yet.

## Provenance

Written from scratch. No third-party code, assets, or text. See
[PROVENANCE.md](PROVENANCE.md).

## Licence

MIT. See [LICENSE](LICENSE).
