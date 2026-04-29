# MumzGift AI: Bilingual Gift Finder for Mumzworld

Track: **A - AI Engineering Intern**

MumzGift AI is a small AI engineering prototype for Mumzworld shoppers and customer-support agents. A user writes a natural-language gift or product request in English or Arabic, and the system returns a validated JSON shortlist of catalog-backed recommendations with confidence, evidence, and uncertainty notes. It refuses vague or unsupported requests instead of inventing products.

## Why This Problem

Mumzworld has a large catalog and serves parents across the GCC in English and Arabic. A common high-intent shopping moment is: "I need a thoughtful gift for a child of this age, in this country, under this budget." Search filters can help, but shoppers often describe needs in human terms: age, relationship, budget, situation, and preference.

This prototype targets that moment. It is useful because it can reduce browsing friction, support customer-service agents, and create reusable structured recommendation data for future product surfaces.

## AI Engineering Features

- Retrieval over a messy synthetic product catalog, including age ranges, countries, price, tags, safety notes, and bilingual product copy.
- Structured output with explicit validation in `validate_output`.
- Multilingual handling for English and Arabic queries.
- Uncertainty handling: missing budget, missing age, missing country, low evidence, and refusal cases.
- Evals with 10 cases covering easy, Arabic, ambiguous, low-budget, unavailable-country, and safety-sensitive requests.

## Setup

Requires Python 3.11+.

```bash
python --version
```

No package installation is required for the baseline prototype.

## Run

From the repo root:

```bash
python src/mumz_gift_finder.py "Thoughtful gift for my friend with a 6-month-old baby in Dubai, under 200 AED" --pretty
```

Arabic example:

```bash
python src/mumz_gift_finder.py "أريد هدية عملية لطفل حديث الولادة في الإمارات أقل من 250 درهم" --pretty
```

Refusal example:

```bash
python src/mumz_gift_finder.py "I want something nice" --pretty
```

## Run Evals

```bash
python evals.py
```

Expected result: `10 / 10` passing. The evaluator checks status, confidence thresholds, language detection, refusal behavior, and whether the expected catalog SKU appears in the shortlist.

## Output Contract

The prototype returns JSON with this shape:

```json
{
  "schema_version": "1.0",
  "input_language": "en",
  "understood": {
    "budget_aed": 200,
    "age_months": 6,
    "country": "AE"
  },
  "status": "answered",
  "overall_confidence": 0.66,
  "shortlist": [],
  "uncertainty": [],
  "message": "Shortlist generated from supported catalog evidence."
}
```

If the request is unsupported, `status` becomes `refused` and `shortlist` must be empty.

## Tooling

I used Codex / ChatGPT as an AI pair-programming assistant to read the assignment, choose Track A scope, generate the first implementation, and create README/eval/tradeoff notes. I kept the prototype dependency-light so reviewers can run it in under 5 minutes. The current runnable baseline is deterministic rather than API-dependent; a production version would use OpenRouter or another model gateway for richer language understanding and final copy generation, while keeping the same retrieval, schema, and eval harness.

Key prompt shape used:

```text
Build a Track A Mumzworld AI engineering prototype that is scoped to 5 hours,
uses retrieval + structured output validation + multilingual EN/AR behavior,
and includes honest evals and uncertainty handling.
```

## Known Limitations

- The catalog is synthetic and small because the brief says not to scrape retailer sites.
- Arabic handling uses lightweight hints, not a true Arabic language model.
- The baseline ranker is interpretable but simple; it will miss nuanced intent.
- The copy is template-based. It is safe and grounded, but not yet marketing-quality.
- Country availability is treated as a ranking signal rather than a hard blocker, so agents can still see near-matches with evidence.

## Submission Checklist

- Track: A
- GitHub repo: add your repo URL here after uploading.
- 3-minute Loom: show the five demo inputs from `SUBMISSION_NOTES.md`.
- Evals: `python evals.py`, current score `10 / 10`.
- Markdown deliverables: this README, `EVALS.md`, and `TRADEOFFS.md`.

## AI Usage Note

Used Codex / ChatGPT to read the brief, pick a Track A problem, pair-program the Python prototype, generate eval cases, and draft documentation. I reviewed and adjusted the eval failures manually, especially budget refusal and category-specific retrieval. No retailer sites were scraped; catalog data is synthetic.

## Time Log

- 0:00-0:30: Read brief and chose Track A gift-finder scope.
- 0:30-1:30: Designed catalog schema, retrieval signals, and output schema.
- 1:30-2:45: Built CLI prototype and validation.
- 2:45-3:45: Added evals, ran failures, tuned retrieval/refusal behavior.
- 3:45-5:00: Wrote README, EVALS, TRADEOFFS, and Loom notes.

## What I Would Build Next

- Add an OpenRouter-compatible LLM step that converts raw user intent into a richer structured query.
- Add embeddings for retrieval over larger catalog data.
- Add a small web UI for customer-service agents.
- Add product images as multimodal inputs, especially for "find similar" or duplicate catalog workflows.
- Add human feedback capture: accepted recommendation, edited recommendation, skipped recommendation.
