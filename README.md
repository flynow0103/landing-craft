# Landing Craft

An agent skill for designing, building, reviewing and optimising landing
pages, with a static checker that gates the page before it ships.

A landing page is one argument, made once, to one person, ending in one action.
This skill is opinionated about that and deliberately silent about visual style.
It puts the weight where conversion is decided — **the headline, the call to
action, social proof, and what sits above the fold** — and checks that the
mechanics do not undermine them.

## What it does

- **Constraints an agent applies without being asked.** MUST / NEVER / SHOULD
  rules for the fold, the headline, the subhead, the CTA, social proof, the
  form, speed, and honesty in the handoff. `/landing-craft <file>` reviews a
  page against them and reports violation → why → fix.
- **A workflow** from brief to launch: five questions, the fold thesis,
  sections ordered against objections, build, gate, optimise.
- **Starting points for people who have never made one.** Turn "the one thing I
  want a visitor to do" into a page shape, see what each shape is strong and
  weak at, and judge any template in ten minutes.
- **A CRO playbook.** The levers ranked by how much they move the number, a fold
  checklist, where each kind of social proof belongs, what to A/B test first,
  and the sample-size arithmetic that says whether you can test at all.
- **A checker** with no dependencies that finds what a parser can see and exits
  1 on anything that should block a launch.

## New to landing pages?

Start with [`references/starting-points.md`](references/starting-points.md).
It does not assume you know what the page is arguing; it helps you find out,
and it points at a free open-source template collection with a way to evaluate
any entry in it. Then run the workflow in `SKILL.md` from Step 1.

## What is in here

```
SKILL.md                       constraints + workflow: brief -> fold -> sequence -> build -> gate -> optimise
scripts/check_landing.py       static checker, no dependencies, exit 1 on P0
assets/skeleton.html           starting template; passes the checker on a clean checkout
tests/                         pages the checker must reject (used by CI)
references/
  starting-points.md           page shapes, what each is good and bad at, judging a template
  message-architecture.md      the fold, headline patterns, ordering sections against objections
  proof-and-honesty.md         evidence types, and the line this skill does not cross
  conversion-mechanics.md      CTA wording, form friction, mobile, what to delete
  cro-playbook.md              levers in order, fold checklist, social proof placement, A/B priorities
  performance-budget.md        LCP, CLS, INP, and a budget worth holding
```

## The checker

```bash
python3 scripts/check_landing.py page.html            # P0 blocks
python3 scripts/check_landing.py page.html --strict    # P1 blocks too
python3 scripts/check_landing.py *.html --json         # for CI
```

It finds what a parser can see:

- **headline** — missing, more than one, brand name instead of a promise, too
  long, an empty superlative in it, phrased as a question
- **fold** — no action between the `<h1>` and the first `<h2>`, two competing
  actions there, a headline with no subhead
- **CTA** — competing targets across the page, mechanism words (Submit, Learn
  more, Get started), fold and closing CTAs worded differently
- **proof** — placeholder text and placeholder images, unattributed quotes,
  ratings and headcounts with no source or link, logo walls whose logos have no
  name, numbers with no method anywhere
- **form** — field count, missing labels, missing `autocomplete`
- **speed** — render-blocking stylesheets and scripts, lazy-loaded hero image,
  images without dimensions
- **share, trust, measurement** — Open Graph tags, privacy and contact links,
  whether any analytics exists

It cannot tell you whether the promise is true, whether the offer is any good,
or whether the ad that sent the visitor said something else. A clean run means
the mechanics are sound, nothing more.

## Installing

**As a project skill** — copy the directory into a repository:

```bash
git clone https://github.com/flynow0103/landing-craft
mkdir -p your-project/.claude/skills
cp -r landing-craft your-project/.claude/skills/landing-craft
```

**For all your projects** — copy it to `~/.claude/skills/landing-craft` instead.

Then ask for a landing page in the normal way, or:

```
/landing-craft                 apply the constraints to the current work
/landing-craft page.html       review a page: violation, why, fix
/landing-craft brief           you do not know yet what the page should be
```

Requires Python 3.8+ for the checker. Nothing else.

## The one rule that is not about conversion rate

**Never invent proof.** No testimonial, customer name, logo, star rating, review
count, user total, or benchmark result that cannot be pointed at a source. Not
as a mockup, not as a placeholder "to be replaced later" — that is the one that
ships. If the brief has no proof in it, the page ships with an empty proof
section and a note saying so. `references/proof-and-honesty.md` covers what to
do when you genuinely have nothing yet.

## Provenance

Written from scratch. No third-party code, assets, or text. See
[PROVENANCE.md](PROVENANCE.md).

## Licence

MIT. See [LICENSE](LICENSE).
