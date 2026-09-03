# Provenance

This document exists so that anyone adopting or forking this repository can see
where the material came from. It is a factual record, not legal advice.

## Authored from scratch

Every file in this repository was written for it. No text, structure, rule list,
checklist, prompt, or code was copied or adapted from another skill, plugin,
prompt library, book, course, or blog post.

At the time of writing, the author's environment also contained several
third-party agent skills covering adjacent ground (general frontend design,
design critique, UI component guidance). **None of them were opened, consulted,
or referenced while writing this repository.** The subject matter overlaps
because the underlying design ideas are common knowledge in the field; the
expression here is original.

## What is referenced rather than reproduced

The guidance cites publicly documented standards and facts. These are referred
to by name and value; none of their text is reproduced here.

| Referenced | Nature |
|---|---|
| WCAG 2.2 success criteria (1.4.3, 1.4.4, 2.5.8) | W3C standard, cited by number |
| Core Web Vitals thresholds (LCP, CLS, INP) | Published metric definitions |
| Apple HIG / Material Design touch target minimums | Published platform guidance, cited as numbers |
| FTC endorsement rules; EU Unfair Commercial Practices Directive | Law, described in general terms |

Facts, measurements, and ideas are not protected by copyright; only a particular
expression of them is. Nothing here reuses anyone's expression.

## Third-party code and assets

**None.** The repository ships:

- `scripts/check_landing.py` — original, Python standard library only, no
  dependencies.
- `assets/skeleton.html` — original markup and CSS. System font stack only; no
  webfont, image, icon set, CSS framework, or JavaScript library is bundled or
  fetched.

There is therefore no third-party licence to comply with, and no attribution
notice other than this project's own.

## Naming

`landing-craft` is a descriptive name. Before it was chosen, the npm registry
had no package under that name and no prominent GitHub project used it. It is
not intended to suggest any association with, or endorsement by, any existing
product, company, or the vendor of any AI assistant this skill happens to run
on. If a conflict emerges later, renaming a skill directory is cheap — do it
rather than argue.

## On patents

Instructions written in prose for an AI agent do not implement a patented
method, and design principles are not patentable subject matter. Patent
infringement is not a realistic exposure for this repository. Copyright — that
is, copying someone else's *wording* — is the risk that actually applies to work
of this kind, and the section above addresses it directly.

## If you contribute

Contribute only material you wrote yourself. If you want to bring in something
from another project, open an issue first with the source and its licence so the
attribution can be recorded properly. Do not paste text from a source whose
licence you have not read.
