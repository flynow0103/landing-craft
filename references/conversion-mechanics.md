# Conversion mechanics

## One action

A landing page has one primary action. It appears above the fold, repeats at the
end, and is worded identically both times — different wording reads as two
different offers.

Everything else is a text link. The moment a second button gets the same visual
weight, the reader has to make a choice you did not want them to make, and the
most common resolution of that choice is neither.

Legitimate secondary paths, styled as links rather than buttons: pricing, docs,
login, an existing-customer path. If a secondary action genuinely deserves equal
weight, the page is serving two audiences and should be two pages.

## Wording the action

Name the outcome in the reader's words.

| Instead of | Write |
|---|---|
| Submit | Send me the guide |
| Get started | Create my first project |
| Learn more | See how the sync works |
| Contact us | Book a 20-minute call |
| Sign up | Start the 14-day trial |

Two tests. **The completion test**: the label should finish the sentence "I
want to…". **The stranger test**: someone who has read only the button should be
able to say what happens next.

Set expectations next to the button, not after the click: what happens, how
long it takes, whether a card is needed. Surprise at the next step is where
funnels leak.

## Forms

Every field is a reason to leave. The question is not "what would be useful to
know" but "what is the minimum that lets me make the next contact".

- Two fields is a good target for a first contact; above five, completion falls
  off sharply.
- Every field gets a visible `<label>`. Placeholder text is not a label: it
  disappears exactly when the reader needs it, and it is not reliably announced.
- Set `autocomplete` and `inputmode`. On a phone, the wrong keyboard costs more
  than an extra field.
- Validate on blur, not on every keystroke. Error text goes next to the field
  and says how to fix it.
- Never disable the submit button until the form is valid — the reader is left
  with a dead control and no explanation. Let them submit and tell them what is
  wrong.
- Ask for the phone number only if a human will actually call. Optional fields
  still cost attention.
- Show what happens to the data, next to the button. A privacy link in the
  footer is not where the hesitation happens.

## Friction worth keeping

Not all friction is bad. Friction that filters is useful: a qualifying question
on a sales form saves both sides a meeting. Friction that only serves internal
reporting is not — move it to onboarding.

## Things to delete

- The three-feature-card row that appears on every page because it is easy to
  produce
- Logo walls without permission or recognition
- A newsletter signup competing with the primary action
- Cookie banners that block the fold on first paint
- Chat widgets that open by themselves
- Autoplaying video with sound
- A scroll-jacking hero that defeats the reader's own scrolling
- Countdown timers that reset on reload — the reader notices, and it costs the
  trust the whole page was built to earn

## Mobile

Most paid traffic lands on a phone. Check the fold at 375 px wide before you
check it at 1440.

- Body text at least 16 px. Below that, iOS zooms the page on input focus and
  does not zoom back.
- Touch targets at least 44x44 px, with at least 8 px between them.
- The primary action within thumb reach, not stranded at the top.
- Never `maximum-scale=1` or `user-scalable=no`: it breaks pinch-zoom and fails
  WCAG 2.2 §1.4.4.
- Respect `env(safe-area-inset-*)` on anything pinned to a screen edge.

## After launch

The page is a hypothesis. Instrument it before you ship it:

- Define the conversion event, and record the baseline before any change.
- Track scroll depth per section. A section nobody reaches is not persuading
  anyone; a section where everyone stops is where the argument breaks.
- Track form field abandonment, not just form abandonment. It tells you which
  question was the one too many.
- Change one argument at a time. A redesign that moves everything tells you
  nothing about why the number moved.
