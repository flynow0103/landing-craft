# Starting points — for when you do not know what a landing page should look like

Most people who need a landing page have never made one. This file gives you a
shape to start from, tells you what each shape is good and bad at, and shows
how to evaluate a template before you commit to it.

Read this before `message-architecture.md`. That file assumes you already know
what the page is arguing; this one helps you find out.

---

## First, the one question

**What is the single thing you want a visitor to do?**

Everything else follows from the answer. If you have two answers, you have two
pages. If you have no answer, you do not need a landing page yet — you need a
decision.

| Your answer | The shape to start from |
|---|---|
| Leave their email so I can tell them when it is ready | **Waitlist** |
| Sign up or start a trial of software | **SaaS product** |
| Install a mobile app | **App download** |
| Call, book, or request a quote for a service | **Lead capture** |
| Buy a course, a book, a high-ticket programme | **Long-form sales** |
| Register for a date-bound thing | **Event / launch** |
| Donate or volunteer | **Cause** |
| Hire me / look at my work | Probably **not a landing page** — see below |

---

## The shapes, with what each is good and bad at

### Waitlist / coming soon

*Fits when* the product does not exist yet, or exists for a few people only.

- **Strong at**: lowest possible friction; one field; scarcity is honest because
  supply is genuinely limited.
- **Weak at**: proof — you have none, and a logo wall here is always invented.
  Also weak at explaining the mechanism, because there often is not one yet.
- **Keep**: the headline, one field, one sentence on what happens after
  signing up.
- **Cut**: feature grids, pricing, testimonials. Anything that pretends the
  product is further along than it is.
- **Objection it must answer**: *why should I care before it exists?* Answer
  with the problem, stated sharply, and who is building it.

### SaaS product

*Fits when* the visitor can start using the thing today, alone, from the
browser.

- **Strong at**: showing the mechanism — screenshots, a short recording, a
  live demo. The product can be its own proof.
- **Weak at**: the fold, because SaaS pages default to a category label
  ("The platform for modern teams") instead of an outcome. Also the most prone
  to the three-feature-card row that answers no objection.
- **Keep**: one outcome headline, a real screenshot of the real product, the
  first step made visible, pricing on the page.
- **Cut**: integration logo walls unless they are decision-relevant, "trusted
  by" rows you do not have permission for.
- **Objection it must answer**: *will this work for my case?* Answer with the
  mechanism, concretely enough to be doubted.

### App download

*Fits when* the action is an install on a phone.

- **Strong at**: the device is the frame — three screenshots inside a phone
  outline tell the story faster than copy. Store badges carry trust you did not
  have to earn.
- **Weak at**: the desktop visitor, who cannot install and has no action.
  Also weak when screenshots are of an empty app.
- **Keep**: store badges above the fold, screenshots with real content, one
  line per screenshot saying what is happening.
- **Cut**: long feature lists; the store listing already has them.
- **Objection it must answer**: *is it worth the install?* Answer by showing the
  moment of value in the first screenshot, not the onboarding screen.

### Lead capture (services: agency, clinic, law firm, contractor, restaurant)

*Fits when* the conversion is a human contact — a call, a booking, a quote.

- **Strong at**: local and personal trust — a real name, a real address, a
  face, opening hours. These pages win on identity.
- **Weak at**: over-asking. The form wants everything the CRM wants; the
  visitor wants to ask one question.
- **Keep**: phone number as a tap target, a short form, the specific area or
  specialty served, a photo of the actual place or people.
- **Cut**: stock photography of other people's offices; "we are passionate
  about"; any award you cannot link.
- **Objection it must answer**: *are you real, and are you near me?* Answer
  with address, hours, and who exactly will answer the phone.

### Long-form sales

*Fits when* the price is high enough, or the belief change big enough, that the
reader needs the full argument before acting.

- **Strong at**: clearing every objection in order. Length is a feature here;
  the reader who scrolls to the bottom is the buyer.
- **Weak at**: the reader who is already convinced and cannot find the button.
  Also the shape most likely to drift into pressure tactics — countdowns that
  reset, invented scarcity, unsourced numbers.
- **Keep**: a sticky or repeated CTA, section headings that name the objection
  they answer, a plain statement of what is included and what is not.
- **Cut**: fake urgency. It converts once and costs every future visit.
- **Objection it must answer**: all of them, in the order the reader raises
  them. See the table in `message-architecture.md`.

### Event / launch

*Fits when* there is a date.

- **Strong at**: the date does the urgency for you, honestly.
- **Weak at**: the day after. Plan the page's afterlife — recording, next
  event, waitlist — before it goes live.
- **Keep**: date, time with timezone, place or platform, who is speaking, one
  registration action.
- **Cut**: a speaker grid for speakers nobody knows; sponsor logos above the
  registration button.
- **Objection it must answer**: *is this worth my time slot?* Answer with what
  the attendee leaves knowing.

### Cause (nonprofit, donation, petition)

*Fits when* the action costs the visitor something and returns nothing
material.

- **Strong at**: specificity — one person, one place, one number that a
  donation changes.
- **Weak at**: abstraction. "Help us fight injustice" converts nobody;
  "£30 covers one week of tutoring for one student in Leeds" does.
- **Keep**: one concrete beneficiary, where the money goes stated plainly,
  a suggested amount with a reason.
- **Cut**: the mission statement paragraph. Show, then ask.
- **Objection it must answer**: *will this actually help?* Answer with the
  mechanism of the help and what you report back.

### Portfolio — and why it is usually not a landing page

A portfolio serves several audiences with several actions (hire me, buy a
print, read my writing, follow me). That is a small website, not a landing
page, and forcing it into one argument will make it worse. If you truly have
one action — "book a discovery call" — then it is a **lead capture** page with
your work as the proof section.

---

## Templates: where to get one, and how to judge it

A template gives you a layout. It does not give you an argument, and the
argument is the whole job. Treat any template as a starting skeleton to be cut
down, not a finished page to be filled in.

### A source worth knowing

- **PaulleDemon/awesome-landing-pages** —
  https://github.com/PaulleDemon/awesome-landing-pages
  Around forty free, open-source landing page templates built on Tailwind,
  grouped by use case (SaaS, app, restaurant, real estate, attorney, portfolio,
  nonprofit). Actively maintained as of mid-2026. Its license file governs the
  templates; read it before shipping one. It is a good place to see the
  *shapes* above rendered as real pages, and to grab a starting layout for a
  lead capture or SaaS page.

This skill does not vendor or reproduce any of those templates. Fetch the list,
pick one that matches your shape, and run it through the checker below.

### Ten-minute evaluation of any template

Before adopting a template, save its HTML and run:

```bash
python3 scripts/check_landing.py template.html
```

Most templates fail. That is fine — the point is to know *what* fails before you
build on it. Then read the page with these questions:

1. **Does the fold have an outcome headline, or a category label?** Most
   templates ship with "The modern solution for X". You will rewrite it; check
   that the layout leaves room for a real sentence.
2. **How many buttons compete above the fold?** Two equal buttons is the
   template default. You will demote one.
3. **What proof is there?** Nearly all templates ship with an invented logo
   wall and three fake testimonials. Delete them on day one; do not "replace
   later".
4. **Is there a section for the objection your product actually faces?**
   Templates give you features and pricing. If your objection is trust or
   switching cost, you will need to add a section the template does not have.
5. **What does it load?** Count the external requests in `<head>`. A template
   that pulls fonts, icons and a CSS framework from three CDNs will fail the
   performance budget before you have written a word.
6. **Mobile fold at 375 px** — is the action still visible without scrolling?

If a template passes questions 1, 2 and 5 after ten minutes of edits, keep it.
If it fights you on all three, the layout is working against the argument, and
`assets/skeleton.html` will get you further faster.

---

## If you still do not know what to argue

Write three sentences, in this order, before touching any layout:

1. *"The person who needs this is ___ and right now they ___."*
2. *"After they use it, ___ is different."*
3. *"The reason they will not believe that is ___."*

Sentence 2 is your headline. Sentence 1 is your problem section. Sentence 3
tells you which shape and which proof you need. If you cannot write sentence 3,
ask three people who fit sentence 1 — that is cheaper than any template.
