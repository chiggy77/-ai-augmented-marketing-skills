---
name: newsletter-qa
description: Check and improve a marketing newsletter or editorial draft against a tone guide and an automated lint (subject length, word count, reading grade, long sentences, one call-to-action, buzzwords, sourced numbers). Use when writing, editing or reviewing newsletters, landing-page copy or short articles.
---

# Newsletter QA

## Steps
1. Write the draft in markdown: first line `Subject: ...`, then the body, one `[call to action](https://...)` link, and a `Source:` line for any number.
2. Run: `python scripts/newsletter_lint.py draft.md`
3. Fix every FAIL, then re-run until the result is PASS.
4. Read `references/tone-guide.md` and make the final human pass: does it say something specific, is the tone right, is every claim supported?

## Rules
- Lead with the finding, not the background.
- One idea per paragraph, one call to action.
- Every figure needs a source and its limits.
- The lint checks form, not truth. A person must verify the claims.
