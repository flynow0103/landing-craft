# Conversion rate optimisation — what actually moves the number

CRO advice online is mostly a list of tactics with no ordering. Ordering is
the whole thing: a page with the wrong offer does not get fixed by a better
button colour. This file puts the levers in order of leverage, then covers
testing honestly — including the case, common on small sites, where you do not
have enough traffic to test at all.

---

## The levers, in order

Work top to bottom. Do not touch a lower lever while a higher one is broken.

### 1. Offer–audience match

*Is the thing on the page what the arriving visitor wanted?*

The biggest conversion losses happen before the page loads: an ad promises one
thing, the page delivers another; a search for a problem lands on a page about
a product. Nothing on the page can recover a visitor who was sent to the wrong
page.

- Check the top three traffic sources. For each, read the ad, post, or search
  query, then read your headline. Do they continue the same sentence?
- If not, you need a page per source, not a better page.

**Diagnostic**: bounce within five seconds, by source. A source that bounces
fast is a mismatch, not a design problem.

### 2. Fold clarity

*Can a stranger say what you offer and what to do about it within five
seconds?*

This is the headline, the subhead, and the visible action, covered in
`message-architecture.md`. The test is literal: show the fold to someone for
five seconds, take it away, ask them what the page was for. If they name the
product instead of the outcome, the headline is a label.

**Diagnostic**: scroll depth. If most visitors never reach the second section,
the fold is not earning the scroll.

### 3. Proof credibility

*Does the reader believe the claim?*

Not "is there proof" but "does the proof survive scrutiny". An unattributed
quote lowers credibility; a named one raises it. A round number with no source
lowers it; a precise number with a method raises it. `proof-and-honesty.md`
ranks the types.

**Placement rule**: proof goes next to the claim it supports and next to the
ask. A testimonial three screens away from the button is decoration.

**Diagnostic**: hesitation at the form. If visitors reach the form and leave
without starting it, they did not believe enough to type.

### 4. Friction at the action

*How much does it cost the visitor to say yes?*

Field count, unclear next step, a card required before value, a form that
looks like a commitment. Covered in `conversion-mechanics.md`.

**Diagnostic**: form starts versus form completions, and which field they
abandon on.

### 5. Speed

*Did they see the page before they left?*

Below the levers above only because a slow page loses visitors before any of
them apply — but a fast page with the wrong offer converts no one. Budget in
`performance-budget.md`.

**Diagnostic**: LCP at the 75th percentile on mobile, from field data.

### 6. Everything else

Button colour, hero image choice, font, spacing, animation. Real but small,
and only measurable once the levers above are stable. Most CRO articles are
about this level because it is the easiest to write about, not because it is
where the money is.

---

## The fold, as a checklist

Since it is the lever most often broken and most cheaply fixed:

- [ ] Headline states an outcome, not a product name or a category
- [ ] Subhead names the audience and the mechanism in one or two sentences
- [ ] One primary action, visible without scrolling at 375 px wide
- [ ] The action's label finishes the sentence "I want to…"
- [ ] One piece of evidence, or nothing — never an invented wall
- [ ] Nothing animates, autoplays, or pops over the fold on first paint
- [ ] The page has painted the headline within 2.5 s on a throttled phone

---

## Social proof: which kind, where

| Kind | Put it | Not there |
|---|---|---|
| Live demo / free tier | Above the fold, as the action itself | — |
| Number with method | Beside the claim it measures | In a stat strip with no context |
| Attributed quote | Beside the objection it answers | In a carousel nobody advances |
| Customer name or logo | Near the form, small | In a grey wall above the fold |
| Third-party audit, certification | In the objection section, linked | As a badge with no link |
| Volume ("4,000 teams") | Near the form, only if current | As the headline |

The rule from `proof-and-honesty.md` applies before any of this: if it is not
real, it does not go on the page.

---

## A/B testing, honestly

### Most pages cannot A/B test

To detect a 10 % relative lift on a page converting at 3 %, you need roughly
**twenty-five thousand visitors per variant**. At 5 % conversion, around
fourteen thousand. Below a few thousand visitors a month, an A/B test will
either run for the better part of a year or report noise as a result.

If that is your traffic, do not A/B test. Instead:

- **Make one big change at a time, and compare before/after over equal
  periods.** It is not rigorous, but a 40 % change is visible without
  statistics, and only big changes are worth making at low traffic.
- **Watch five people use the page.** Session recordings or a screen-share.
  Five is enough to find the top problems; that is well established.
- **Read the form abandonment field by field.** It tells you which question
  was one too many.
- **Ask the people who converted why.** One sentence each. Their words become
  your headline.

### If you do have the traffic

Test in this order — it is the lever order again, because a win on a lower
lever is wiped out by a change to a higher one:

1. **The offer** — what is being asked for (trial vs demo, free vs paid, email
   vs full signup)
2. **The headline** — outcome framing, specificity
3. **The primary action** — label, position, singularity
4. **Proof** — presence, kind, placement
5. **Form** — field count, layout, what is required
6. **Layout and visual** — last, and only with everything above frozen

### Rules that keep a test honest

- Decide the sample size and the stopping date before you start. Stopping when
  a variant "looks like it is winning" is the most common way to ship noise.
- One change per test. A redesign that moves everything tells you the number
  moved, not why.
- Run through at least one full weekly cycle. Weekday and weekend visitors
  differ.
- Expect the novelty effect: a variant often wins for a week because it is
  different, then regresses. Wait it out.
- Segment by source before believing an aggregate. A variant can win on
  search traffic and lose on social, and the average hides both.
- A test that changes a colour and "wins by 2 %" has almost certainly measured
  nothing. Small effects need enormous samples; be suspicious of them.

---

## Measurement plan

Set this up before the page goes live. After is too late for a baseline.

1. **Define the conversion event** precisely — form submitted and confirmed,
   not button clicked.
2. **Record the baseline** for at least two weeks before any change.
3. **Track scroll depth per section**, so you can see where the argument
   loses people.
4. **Track form starts and per-field abandonment**, not just completions.
5. **Tag every source**, so you can segment. A page converting at 4 % overall
   may be 9 % from search and 1 % from a mismatched ad.
6. **Re-check speed after every third-party script is added.** The analytics
   tag itself is a common cause of the regression it is meant to measure.

---

## Common false wins

- **The redesign that "doubled conversions"** — usually coincided with a
  traffic source change, a season, or the novelty effect.
- **The urgency timer** — converts on the first visit, kills the return visit,
  and is read as manipulative by exactly the buyers you want.
- **The popup** — often lifts email capture and drops the primary conversion,
  because it interrupts the argument to make a different ask.
- **The shorter page** — shorter is not better; *answering fewer objections* is
  worse. Cut padding, not argument.
- **The "trust badges"** — SSL padlocks, generic security icons, and award
  graphics with no link mostly signal that the page needed reassurance.
