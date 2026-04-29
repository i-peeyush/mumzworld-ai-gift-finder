import json
from dataclasses import dataclass

from src.mumz_gift_finder import answer


@dataclass
class Case:
    name: str
    query: str
    expect_status: str
    must_include_any_sku: list[str]
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    language: str | None = None


CASES = [
    Case(
        name="english_gift_under_budget_for_6_month_old",
        query="Thoughtful gift for my friend with a 6-month-old baby in Dubai, under 200 AED",
        expect_status="answered",
        must_include_any_sku=["MW-TOY-006M-002", "MW-FEED-004M-003", "MW-SLEEP-000M-004"],
        min_confidence=0.45,
        language="en",
    ),
    Case(
        name="arabic_newborn_practical_gift",
        query="أريد هدية عملية لطفل حديث الولادة في الإمارات أقل من 250 درهم",
        expect_status="answered",
        must_include_any_sku=["MW-DIAPER-000M-009", "MW-NURSERY-000M-012", "MW-BATH-000M-005"],
        min_confidence=0.45,
        language="ar",
    ),
    Case(
        name="sleep_routine_query",
        query="Need something for sleep routine for a newborn in Saudi under 200 AED",
        expect_status="answered",
        must_include_any_sku=["MW-SLEEP-000M-004", "MW-NURSERY-000M-012"],
        min_confidence=0.45,
    ),
    Case(
        name="feeding_for_8_month_old",
        query="Feeding gift for 8 month old in Qatar below 150 AED",
        expect_status="answered",
        must_include_any_sku=["MW-FEED-004M-003"],
        min_confidence=0.5,
    ),
    Case(
        name="toddler_pretend_play",
        query="Gift for a 3 year old toddler in Kuwait under 400 AED who likes pretend play",
        expect_status="answered",
        must_include_any_sku=["MW-TOY-024M-010"],
        min_confidence=0.5,
    ),
    Case(
        name="budget_too_low_refusal",
        query="Gift for a newborn in UAE under 10 AED",
        expect_status="refused",
        must_include_any_sku=[],
        max_confidence=0.34,
    ),
    Case(
        name="too_vague_refusal",
        query="I want something nice",
        expect_status="refused",
        must_include_any_sku=[],
        max_confidence=0.34,
    ),
    Case(
        name="unavailable_country_uncertainty",
        query="Need a car seat for newborn in Bahrain under 800 AED",
        expect_status="answered",
        must_include_any_sku=["MW-CAR-000M-008"],
        min_confidence=0.35,
    ),
    Case(
        name="bilingual_book",
        query="Arabic English learning gift for 18 month baby in UAE under 80 AED",
        expect_status="answered",
        must_include_any_sku=["MW-BOOK-012M-007"],
        min_confidence=0.45,
    ),
    Case(
        name="health_item_with_safe_language",
        query="Practical fever item for newborn in Qatar under 100 AED",
        expect_status="answered",
        must_include_any_sku=["MW-HEALTH-000M-011"],
        min_confidence=0.45,
    ),
]


def evaluate_case(case: Case) -> dict:
    output = answer(case.query)
    skus = [item["sku"] for item in output["shortlist"]]
    checks = {
        "status": output["status"] == case.expect_status,
        "confidence_floor": output["overall_confidence"] >= case.min_confidence,
        "confidence_ceiling": output["overall_confidence"] <= case.max_confidence,
        "language": True if case.language is None else output["input_language"] == case.language,
        "sku": True if not case.must_include_any_sku else any(sku in skus for sku in case.must_include_any_sku),
        "valid_refusal": output["status"] != "refused" or not output["shortlist"],
    }
    return {
        "name": case.name,
        "passed": all(checks.values()),
        "checks": checks,
        "query": case.query,
        "status": output["status"],
        "confidence": output["overall_confidence"],
        "skus": skus,
    }


def main() -> None:
    results = [evaluate_case(case) for case in CASES]
    passed = sum(result["passed"] for result in results)
    print(json.dumps({"passed": passed, "total": len(results), "results": results}, indent=2))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
