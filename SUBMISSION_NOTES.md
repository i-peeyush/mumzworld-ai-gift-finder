# Submission Notes and Learning Guide

This file is for you while recording the Loom and explaining the project. You can include it in the repo, but the core required files are `README.md`, `EVALS.md`, and `TRADEOFFS.md`.

## One-Paragraph Summary

I built MumzGift AI, a bilingual catalog-grounded gift finder for Mumzworld. It helps shoppers or customer-support agents turn natural-language requests like "gift for a friend with a 6-month-old under 200 AED" into a structured shortlist of products in English or Arabic. The system retrieves from a synthetic Mumzworld-style catalog, validates the JSON output, shows confidence and evidence, and refuses vague or unsupported requests instead of inventing answers.

## Five Loom Demo Inputs

Use these in the 3-minute Loom:

```bash
python src/mumz_gift_finder.py "Thoughtful gift for my friend with a 6-month-old baby in Dubai, under 200 AED" --pretty
```

```bash
python src/mumz_gift_finder.py "أريد هدية عملية لطفل حديث الولادة في الإمارات أقل من 250 درهم" --pretty
```

```bash
python src/mumz_gift_finder.py "Gift for a 3 year old toddler in Kuwait under 400 AED who likes pretend play" --pretty
```

```bash
python src/mumz_gift_finder.py "Gift for a newborn in UAE under 10 AED" --pretty
```

```bash
python src/mumz_gift_finder.py "I want something nice" --pretty
```

Then run:

```bash
python evals.py
```

## Loom Structure

Aim for this flow:

1. **0:00-0:25 - Problem:** "Mumzworld shoppers often know the situation, not the SKU. I built a bilingual gift finder for age, budget, country, and use case."
2. **0:25-0:55 - Architecture:** "The system parses intent, retrieves from catalog data, ranks products, validates JSON, and refuses low-confidence cases."
3. **0:55-2:15 - Demo:** Run 5 inputs. Include English, Arabic, toddler, impossible budget, and vague refusal.
4. **2:15-2:45 - Evals:** Run `python evals.py` and show 10/10 passing.
5. **2:45-3:00 - Tradeoffs:** "I kept it dependency-free for easy review; next I would add LLM parsing and multilingual embeddings."

## What to Say if Asked Why This Is AI Engineering

This is more than a prompt wrapper because the useful behavior comes from system design:

- retrieval over catalog records,
- ranking with interpretable signals,
- structured output validation,
- multilingual handling,
- uncertainty and refusal logic,
- evals that catch named failure modes.

An LLM could improve language understanding and final copy, but the application should still own retrieval, validation, and evals.

## What to Say About Arabic

The prototype detects Arabic and returns Arabic product names and reasons. For the 5-hour scope, Arabic understanding uses lightweight hints rather than a full Arabic model. That is honest and visible in the tradeoffs. A production version should use a multilingual model or embeddings and native Arabic copy review.

## What to Say About Data

The catalog is synthetic because the assignment says not to scrape retailer sites. The fields are realistic for an e-commerce catalog: SKU, names, category, age range, price, country availability, tags, safety notes, and descriptions.

## Important Lessons

- Good AI prototypes need refusal behavior, not just happy-path demos.
- Evals should exist before calling the work complete.
- JSON validation protects downstream systems from malformed model output.
- Grounding matters: every recommendation should trace back to product data.
- Scope matters: a small reliable system beats a broad unreliable one in a 5-hour assignment.
