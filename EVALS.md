# EVALS

## Rubric

The prototype is evaluated on whether it behaves like a trustworthy catalog-grounded assistant, not just whether it produces nice text.

Each test case checks:

- **Schema validity:** output must pass the built-in validator.
- **Correct status:** answered vs refused.
- **Grounding:** expected SKU appears when the request is supported.
- **Confidence:** supported cases must clear a minimum confidence; refusal cases must stay low confidence.
- **Multilingual behavior:** Arabic inputs should be detected as Arabic and receive Arabic output.
- **Uncertainty handling:** missing budget, age, or country should be explicit.

## Test Cases

Run:

```bash
python evals.py
```

The current suite has 10 cases:

1. English gift for 6-month-old under 200 AED.
2. Arabic practical newborn gift under 250 AED.
3. Newborn sleep routine item in Saudi.
4. Feeding gift for 8-month-old in Qatar.
5. Pretend-play gift for 3-year-old toddler in Kuwait.
6. Newborn gift with impossible 10 AED budget, expected refusal.
7. Vague request, expected refusal.
8. Car seat request in Bahrain, expected uncertainty because availability is weak.
9. Arabic-English learning gift for 18-month-old.
10. Fever-related practical item with safe non-diagnostic language.

## Why These Cases

The cases intentionally mix easy and adversarial inputs. Cases 6 and 7 are important because a recommender that always recommends something is dangerous for user trust. Case 10 is included because Mumzworld may sell health-adjacent products, but the assistant should not diagnose or give medical advice.

## Current Result

At the time of writing, the target result is:

```text
10 / 10 passing
```

If a future model-backed version changes ranking or copy, this eval file should be updated with the actual score, failure examples, and what changed.

## Failure Modes the Evals Are Trying to Catch

- Recommending products when the request is too vague.
- Ignoring age appropriateness.
- Ignoring budget.
- Treating Arabic as English and producing awkward output.
- Making unsupported health claims.
- Returning malformed JSON or empty placeholder fields.
