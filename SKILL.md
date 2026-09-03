---
name: landing-craft
description: >
  Design, build, review and optimise landing pages, weighted toward the four
  things that decide whether a page converts: the headline, the call to action,
  social proof, and what sits above the fold. Opinionated MUST / NEVER / SHOULD
  constraints an agent applies directly, a workflow from brief to launch, page
  shapes and template guidance for people who have never made a landing page,
  a CRO playbook with A/B-test priorities, and a static checker that gates the
  page. Use when asked for a landing page, marketing page, launch page,
  waitlist or signup page, or a product page that has to convert; when asked to
  review, critique or improve one; or when asked about headlines, CTAs, social
  proof, above-the-fold content, conversion rate, or what to A/B test first.
license: MIT
metadata:
  version: "1.1.0"
  homepage: https://github.com/flynow0103/landing-craft
---

# Landing Craft

A landing page is one argument, made once, to one person, ending in one action.
This skill is opinionated about that and silent about visual style. It puts the
weight where conversion is actually decided — the headline, the call to action,
the proof, and the fold — and checks that the mechanics do not undermine them.

## How to use

- `/landing-craft`
  Apply the constraints below to any landing page work in this conversation.

- `/landing-craft <file.html>`
  Review the file against the constraints and output, per finding:
  - the violation, quoting the exact line or snippet
  - why it matters, in one sentence
  - the concrete fix, at copy or code level
  Run `python3 scripts/check_landing.py <file>` first and merge its findings
  into the review so nothing a parser can catch is left to eyesight.

- `/landing-craft brief`
  The user does not yet know what the page should be. Go to Step 0 before
  proposing anything.

## Use when, and not when

Building, reviewing or optimising a page whose success is one measurable
action: signup, waitlist, demo booking, download, purchase, donation, RSVP.

Not for documentation, a blog, an app screen, or a homepage that has to serve
five audiences at once. Those pages have different jobs and these rules will
make them worse.

---

## Constraints

MUST and NEVER are gates: do not hand over a page that breaks one. SHOULD is
the default unless the brief gives a reason.

### Above the fold

- MUST show, before any scrolling: one headline, one subhead, one primary
  action, one credibility signal. Nothing else is required; most other things
  are in the way.
- MUST put the headline and the primary action in the HTML the server sends,
  not inserted by JavaScript.
- MUST continue the sentence the visitor was already reading: the ad, the post
  or the search result that sent them. A mismatch here is the largest single
  cause of bounce and no amount of design below fixes it.
- MUST keep the primary action visible on a 360×640 viewport without scrolling.
- NEVER place a carousel, an autoplaying video, a cookie wall or a popup
  between the visitor and the headline.
- NEVER set the fold's copy over a photograph. It fails contrast and it ties
  the first paint to the largest asset on the page.
- SHOULD keep the header to a logo and at most one exit link. Every link in the
  header is a way to leave before the argument starts.
- SHOULD make the signal in the fold the strongest proof you have, in one line:
  a named customer, a sourced number, a rating with a link.

### Headline

- MUST state the outcome the visitor gets, not the name of the product or the
  category it belongs to.
- MUST be the only `<h1>` on the page.
- MUST stand alone: if the subhead vanished, the headline would still say
  something specific to this product.
- SHOULD be under 12 words. A headline you cannot say in one breath is two
  headlines, and the visitor reads neither.
- SHOULD carry one specific: a number, a time, a named integration, a
  before/after. Specificity is what separates a claim from a slogan.
- SHOULD be written last, from the subhead. The subhead holds the mechanism;
  the headline holds the result of that mechanism.
- NEVER use an empty superlative in it: revolutionary, seamless, world-class,
  cutting-edge, next-generation, best-in-class. Each is standing in for a
  specific thing — write that thing.
- NEVER lead with a question the visitor can answer "no" to.
- NEVER use a pun or a brand slogan where a plain claim would do. The visitor
  is not here to admire the copy.

### Subhead

- MUST answer "who is this for" and "how does it work" in one or two
  sentences.
- NEVER restate the headline in longer words.

### Call to action

- MUST be one primary action: above the fold, and again at the end, worded
  identically both times so the reader knows it is the same promise.
- MUST name what the visitor gets, in their words: "Send me the skeleton",
  "Book the 20-minute call", "Start my free trial".
- MUST be a real `<a href>` or `<button>`, at least 44×44 px, with a visible
  focus ring.
- NEVER use a mechanism label: Submit, Click here, Learn more, Get started,
  Continue, Next, Go.
- NEVER show two button styles competing in the same view. Secondary paths are
  text links.
- NEVER manufacture urgency: a countdown that resets, "only 3 left" that never
  changes, "ends today" every day. It works once and costs the brand after.
- SHOULD say what happens next beside the button: no card required, takes two
  minutes, unsubscribe in one click.
- SHOULD open with a verb the visitor would use: get, start, book, send,
  download, reserve, join.

### Social proof

- NEVER invent a testimonial, name, role, logo, star rating, review count,
  user number or benchmark — not even as a placeholder "to be replaced". The
  placeholder is the one that ships.
- MUST attribute every quote: a real name and a role or context, in `<cite>`
  or `<figcaption>`. An unattributed quote is read as invented and costs trust
  instead of adding it.
- MUST give every number its source: what was measured, over what sample, when.
  A rating links to where it lives.
- MUST place each piece of proof where the objection it answers arises, and
  put the single strongest signal in the fold.
- SHOULD prefer specific over impressive: "onboarding went from three days to
  forty minutes" outperforms "loved by thousands".
- SHOULD match the proof to the visitor. A wall of enterprise logos does not
  reassure a solo developer; one named peer does.
- SHOULD ship the proof section empty, with an HTML comment, when there is no
  proof yet, and say so in the handoff. Empty is honest; filler is not.
- NEVER show a logo without permission, and NEVER show one the reader cannot
  name. Unnamed logos are unverifiable and silent to a screen reader.

### Form

- MUST ask only for what the next contact needs. Every field is an exit.
- MUST have a visible `<label>` per field, the right `type`, and `autocomplete`.
- NEVER use placeholder text as the only label.
- SHOULD show an error next to the field, in words that say how to fix it.

### Speed

- MUST inline the critical CSS. NEVER block first paint on a cross-origin
  stylesheet or a synchronous script.
- NEVER lazy-load the hero image. MUST set `width` and `height` on every image.
- SHOULD keep the fold's HTML and CSS inside the first round trip.

### Honesty and handoff

- MUST state what the brief did not give you and what you assumed instead.
- NEVER claim a result the page has not measured.
- MUST put a privacy link next to every form and a contact route on the page.
- MUST report the checker's result as what it is: mechanics, not judgement.

---

## Workflow

### Step 0 — If you do not know what the page should be

Read `references/starting-points.md`. It turns "what is the one thing I want a
visitor to do" into a page shape (waitlist, SaaS trial, app download, lead
capture, long-form sales, event, cause), says what each shape is strong and
weak at, and gives a ten-minute way to judge any template — including the free
open-source ones it points to. Come back here once you can finish the sentence
"the one thing I want a visitor to do is …".

### Step 1 — Get the brief

Five questions. If they cannot be answered, ask rather than invent.

1. **Who is landing here, and from where?** The page continues the sentence
   the visitor was already reading.
2. **What is the one action?** Named as the visitor would say it.
3. **What do they believe right now that stops them?** Usually one of: I do
   not have this problem, it will not work for my case, I do not trust you, it
   costs too much, switching is too much work, not now.
4. **What proof exists today?** Not what would be persuasive; what you can
   show. See `references/proof-and-honesty.md`.
5. **How will you know it worked?** The conversion event and its current
   number. A page with no baseline cannot be improved, only replaced.

When answers are missing, write the page under stated assumptions and put
them at the top of the handoff.

### Step 2 — Write the above-the-fold thesis

| Slot | Question it answers | Failure mode |
|---|---|---|
| Headline | What do I get? | Naming the product instead of the outcome |
| Subhead | Who is it for, and how does it work? | The headline again, longer |
| Action | What do I do now? | Below the fold, or five competing buttons |
| Signal | Why should I believe this? | An invented logo wall |

Patterns and worked examples: `references/message-architecture.md`.

### Step 3 — Sequence the page against objections

Each section removes one reason not to act. Default order, changed when the
brief demands it: thesis → problem in their words → mechanism → proof →
objection handling (pricing and switching cost live here) → the same action,
worded the same way. Cut any section that removes no objection.

### Step 4 — Build

Static HTML unless the page genuinely needs interactivity. Start from
`assets/skeleton.html`, which passes the checker on a clean checkout. Inline
the critical CSS. Budget: `references/performance-budget.md`. CTA wording,
form friction and what to delete: `references/conversion-mechanics.md`.

### Step 5 — Run the checker before you hand over

```bash
python3 scripts/check_landing.py page.html
python3 scripts/check_landing.py page.html --strict   # P1 also blocks
python3 scripts/check_landing.py *.html --json        # for CI
```

It checks what a parser can see: headline length and content, whether the
fold has one action and a subhead, whether the fold and closing CTAs match,
competing targets, mechanism-word buttons, placeholder text, unattributed
quotes, ratings and headcounts with no source, unnamed logo walls, form
fields and labels, render-blocking requests, lazy-loaded hero images, Open
Graph tags, privacy and contact links, and whether any analytics exists.

It cannot tell you whether the promise is true, whether the offer is any good,
or whether the ad that sent the visitor said something else. Report a clean
run as "mechanics are sound" and nothing more.

### Step 6 — Optimise, in order

`references/cro-playbook.md`. The levers ranked by how much they move the
number (offer–audience match, fold clarity, proof credibility, friction,
speed, then everything else), a fold checklist, where each kind of social
proof belongs, and what to A/B test first — with the sample-size arithmetic
that tells you whether you can test at all. Do not test the button colour
while the offer is unclear.

---

## References

- `references/starting-points.md` — page shapes, what each is good and bad at, judging a template
- `references/message-architecture.md` — the fold, headline patterns, objection order
- `references/proof-and-honesty.md` — evidence types, and the line you do not cross
- `references/conversion-mechanics.md` — CTA, forms, friction, what to delete
- `references/cro-playbook.md` — levers in order, fold checklist, social proof placement, A/B priorities
- `references/performance-budget.md` — LCP, CLS, INP for a page that must load fast
- `assets/skeleton.html` — starting template, passes the checker
- `scripts/check_landing.py` — the gate
