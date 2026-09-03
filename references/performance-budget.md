# Performance budget

A landing page is judged in the first few seconds by a reader who has no
investment in waiting. Slow is not a technical problem here; it is the argument
failing before it is read.

## Targets

Aim for the "good" threshold of each Core Web Vital at the 75th percentile of
real visits, not on your own machine:

| Metric | Good | What it means here |
|---|---|---|
| LCP — Largest Contentful Paint | ≤ 2.5 s | When the headline or hero image is actually readable |
| CLS — Cumulative Layout Shift | ≤ 0.1 | Whether the text jumps as assets land |
| INP — Interaction to Next Paint | ≤ 200 ms | How the CTA feels when tapped |

INP replaced FID in March 2024; if a tool still reports FID, it is out of date.

Field data beats lab data. Lab tools run on a fast machine on a fast network;
your visitor is on a phone on mobile data.

## LCP: what actually delays it

The largest element above the fold is usually the headline or the hero image.
Almost every LCP problem is one of four things:

1. **A render-blocking stylesheet from another origin.** Nothing paints until a
   third party responds. Inline the critical CSS; self-host the rest.
2. **A synchronous script in `<head>`.** Blocks parsing before anything is on
   screen. Add `defer`, or move it to the end of `<body>`.
3. **The hero image lazy-loaded or unprioritised.** Never `loading="lazy"` above
   the fold. Add `fetchpriority="high"` to the hero, and consider `<link
   rel="preload">`. A hero set as a CSS `background-image` cannot be discovered
   by the preload scanner at all — use `<img>`.
4. **A webfont without `display: swap`.** The headline stays invisible while the
   font downloads. Self-host, subset, and preload the one face used above the
   fold.

## CLS: reserve the space

- `width` and `height` attributes on every `<img>` and `<iframe>`. CSS can still
  resize them; the attributes give the browser the aspect ratio up front.
- No content injected above existing content after load — banners, notices,
  consent bars. If one must appear, reserve its height.
- Fonts: match the fallback's metrics with `size-adjust` and
  `ascent-override`, or the swap itself becomes a shift.

## INP: keep the main thread free

- Landing pages rarely need a framework. If the interactivity is a menu, an
  accordion and a form, plain JavaScript costs a few kilobytes rather than a few
  hundred.
- Defer analytics and any chat or consent widget until after first paint. Third
  party scripts are the usual cause of a slow tap.
- Animate `transform` and `opacity` only. Animating layout properties forces
  reflow on every frame.

## A budget worth holding

For a static landing page, on a mid-range phone over 4G:

- HTML ≤ 30 KB compressed
- Critical CSS inline, ≤ 14 KB
- JavaScript ≤ 50 KB compressed, all deferred
- Hero image ≤ 150 KB, in AVIF or WebP, sized to the layout with `srcset`
- Webfonts: at most two faces, subset, preloaded, `display: swap`
- Third-party requests before first paint: zero

The last line is the one that matters most and is the first to be traded away.

## Measuring

- Lab: Lighthouse or WebPageTest, on a throttled mobile profile.
- Field: the Chrome UX Report, or your own `web-vitals` collection. Field data
  is the only kind that reflects your actual visitors.
- Re-measure after adding any third-party script. The tag that marketing added
  last week is the usual explanation for a regression nobody can account for.
