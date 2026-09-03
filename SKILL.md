---
name: landing-craft
description: >
  Design and build a landing page that has one job: turning a specific visitor
  into one specific action. Covers the brief, the above-the-fold thesis, section
  sequencing against objections, honest proof, CTA and form friction, and a
  performance budget. Ships a static checker that gates the page before launch.
  Use when asked for a landing page, a marketing page, a launch page, a waitlist
  or signup page, a product page that has to convert, or when asked to review or
  improve an existing one.
license: MIT
metadata:
  version: "1.0.0"
  homepage: https://github.com/flynow0103/landing-craft
---

# Landing Craft

A landing page is not a small website. It is one argument, made once, to one
person, ending in one action. Everything that does not serve that argument is
working against it.

This skill is opinionated about that and nothing else. It does not impose a
visual style; it makes you decide what the page is arguing and then checks that
the mechanics do not undermine the argument.

## Use this when

Building or reviewing a page whose success is measurable as a single action:
signup, waitlist, demo booking, download, purchase, donation, RSVP.

Do not use it for documentation, a blog, an app screen, or a homepage that has
to serve five audiences at once. Those pages have different jobs and this
skill's rules will make them worse.

---

## Step 1 — Get the brief before writing anything

Five questions. If you cannot answer them, the page cannot be written yet, and
the honest move is to ask rather than to invent.

1. **Who is landing here, and from where?** Someone arriving from a search for
   the problem needs a different opening from someone who clicked an ad that
   already made a claim. The page must continue the sentence the visitor was
   already reading.
2. **What is the one action?** Name it as the visitor would: "book a
   20-minute call", not "convert".
3. **What do they believe right now that stops them?** This is the objection
   the page exists to answer. Usually one of: I do not have this problem, this
   will not work for my case, I do not trust you, it costs too much, it is too
   much work to switch, not now.
4. **What proof do you actually have?** Not what would be persuasive. What
   exists, today, that you can show. See `references/proof-and-honesty.md`.
5. **How will you know it worked?** The conversion event, and the number it
   is at now. A page with no baseline cannot be improved, only replaced.

If the answers are not available, write the page under stated assumptions and
mark them at the top of your handoff. Do not quietly invent a persona.

---

## Step 2 — Write the above-the-fold thesis

Four things, in this order, before any scrolling:

| Slot | Question it answers | Failure mode |
|---|---|---|
| Headline | What do I get? | Naming the product instead of the outcome |
| Subhead | Who is it for, and how does it work? | Repeating the headline in longer words |
| Action | What do I do now? | Buried below the fold, or five competing buttons |
| Signal | Why should I believe any of this? | An invented logo wall |

Write the headline last, from the subhead. A headline you can write before you
know the mechanism is a headline about nothing.

Details and worked examples: `references/message-architecture.md`.

---

## Step 3 — Sequence the page against objections

Sections are not decoration; each one exists to remove one specific reason not
to act. The default order, which you should change when the brief demands it:

1. **Thesis** — the fold, above.
2. **Problem, in their words.** If they do not recognise themselves here,
   nothing below lands.
3. **Mechanism.** How it actually works, concretely enough to be doubted.
   Vagueness reads as evasion.
4. **Proof.** The evidence you listed in Step 1.
5. **Objection handling.** The specific ones from the brief, named plainly.
   Pricing and switching cost belong here.
6. **Action.** The same action as the fold, worded the same way.

Cut any section that does not remove an objection. A page of six honest sections
outperforms a page of twelve sections padded with feature cards.

---

## Step 4 — Build

- Static HTML unless the page genuinely needs interactivity. The promise must be
  in the HTML the server sends, not inserted by JavaScript: crawlers, social
  scrapers and readers on a failed script load all see the served markup.
- Start from `assets/skeleton.html`. It passes the checker on a clean checkout,
  so you begin on ground that is already sound.
- Inline the critical CSS. A stylesheet from another origin holds the first
  paint hostage on a page whose entire job happens in the first few seconds.
- Budget and technique: `references/performance-budget.md`.
- CTA wording, form friction, and what to remove: `references/conversion-mechanics.md`.

---

## Step 5 — Run the checker before you hand it over

```bash
python3 scripts/check_landing.py page.html
python3 scripts/check_landing.py page.html --strict   # P1 also blocks
python3 scripts/check_landing.py *.html --json        # for CI
```

It checks what a parser can see: how many actions compete, whether the promise
exists in the HTML, placeholder text and unattributed testimonials, form field
count and labelling, render-blocking requests and lazy-loaded hero images,
Open Graph completeness, privacy and contact links, and whether any analytics
exists at all. Exit code 1 on P0, so it can gate a build.

It cannot tell you whether the promise is true, whether the offer is any good,
or whether the ad that sent the visitor said something else. A clean run means
the mechanics are sound. Report it that way and do not let it stand in for
judgement.

---

## Hard rules

**Never fabricate proof.** No invented testimonials, customer names, logos,
review counts, user numbers, or benchmark results, not even as placeholders that
"will be replaced later". Ship the section empty with a comment, or delete it.
This is the one rule in this skill that is not about conversion rate.

**One primary action.** It appears above the fold and repeats at the end, worded
identically both times. Secondary paths are text links, not buttons.

**Name the outcome, not the mechanism.** "Submit" describes what the form does.
"Send me the skeleton" describes what the visitor gets.

**Ask for the minimum.** Every field is a reason to leave. Collect what you need
to make the next contact; the rest can come after.

**Numbers carry their source.** A statistic without what was measured, over what
sample, and when, invites the reader to discount every other number on the page.

**No empty superlatives.** Revolutionary, seamless, world-class, cutting-edge,
next-generation: interchangeable between products, therefore information-free.
Each one is standing in for something specific — write that instead.

**Accessibility is not a later pass.** Visible labels on every field, a visible
focus ring, contrast at WCAG 2.2 AA, and a touch target of at least 44x44 px.
A page that loses a reader at the form has not converted them either.

**State what you could not verify.** If the brief was incomplete and you filled
a gap with an assumption, say so in the handoff.

---

## References

- `references/message-architecture.md` — the fold, headline patterns, objection order
- `references/proof-and-honesty.md` — evidence types, and the line you do not cross
- `references/conversion-mechanics.md` — CTA, forms, friction, what to delete
- `references/performance-budget.md` — LCP, CLS, INP for a page that must load fast
- `assets/skeleton.html` — starting template, passes the checker
- `scripts/check_landing.py` — the gate
