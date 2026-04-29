# TRADEOFFS

## Problem Choice

I chose a bilingual gift finder because it is a real Mumzworld use case: parents and friends often shop by situation rather than SKU. A query like "gift for a friend with a 6-month-old under 200 AED" has multiple constraints: age, price, country, purpose, and tone. This is a good AI engineering problem because the answer should combine retrieval, ranking, structured output, multilingual handling, and uncertainty.

I rejected a pure PDP copy generator because it can become a single-prompt writing task. I also rejected pediatric symptom triage because it is higher risk and would need stricter medical safety work than a 5-hour prototype can honestly provide.

## Architecture

The system has four simple stages:

1. Parse the request for language, budget, child age, and country.
2. Retrieve and rank products from a synthetic catalog.
3. Generate a shortlist with evidence and confidence.
4. Validate the output schema and refuse low-evidence requests.

This keeps the logic inspectable. The most important design choice is that the model or ranker does not get to invent unsupported product claims. Every recommendation carries evidence from catalog fields.

## Model Choice

The submitted baseline is deterministic and dependency-free so it can run without a paid API key. In a production-like version, I would add:

- a small/cheap LLM through OpenRouter to parse nuanced intent into structured fields,
- embeddings for retrieval over a larger catalog,
- a stronger model only for final bilingual copy polishing.

I would still keep the schema validator and eval suite outside the model, because those are control surfaces the application owns.

## Uncertainty Handling

The system lowers confidence when budget, child age, or country is missing. If confidence drops below the threshold, it refuses and asks for more specific information. Refusal is not treated as failure; for vague requests it is the correct behavior.

## What I Cut

- Live Mumzworld scraping, because the brief forbids scraping retailer sites.
- A web UI, because the scoring rubric puts more weight on working AI behavior and evals.
- True Arabic generation with an LLM, because requiring a model key would make the project harder to run in under 5 minutes.
- Image input, because the gift-finder problem is better served first by catalog retrieval and structured output.

## Next Steps

- Add `OPENROUTER_API_KEY` support for LLM-based intent parsing and bilingual copy.
- Replace token overlap with multilingual embeddings.
- Add a small customer-service UI with "accept", "edit", and "reject" feedback.
- Expand evals to 50+ cases with per-country inventory and edge cases.
- Log anonymized failure cases to improve retrieval and thresholds.
