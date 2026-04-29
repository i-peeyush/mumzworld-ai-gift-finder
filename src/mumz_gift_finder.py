import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"


ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
TOKEN_RE = re.compile(r"[a-zA-Z0-9]+|[\u0600-\u06ff]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "my",
    "need",
    "of",
    "old",
    "the",
    "to",
    "under",
    "with",
    "who",
}

EN_SYNONYMS = {
    "baby": ["newborn", "infant", "child", "kid"],
    "mom": ["mother", "mama", "mum", "postpartum"],
    "gift": ["present", "hamper", "thoughtful"],
    "cheap": ["budget", "affordable", "under"],
    "travel": ["stroller", "car", "portable"],
    "sleep": ["bedtime", "routine", "soother"],
    "food": ["feeding", "weaning", "meal"],
}

AR_HINTS = {
    "هدية": "gift",
    "طفل": "baby",
    "رضيع": "baby",
    "حديث": "newborn",
    "أم": "mom",
    "سفر": "travel",
    "نوم": "sleep",
    "طعام": "feeding",
    "استحمام": "bath",
    "سيارة": "car",
    "رخيص": "budget",
}


@dataclass
class Request:
    raw: str
    language: str
    budget_aed: int | None
    age_months: int | None
    country: str | None
    query_tokens: list[str]


def load_catalog(path: Path = CATALOG_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_language(text: str) -> str:
    return "ar" if ARABIC_RE.search(text) else "en"


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def expand_tokens(tokens: list[str]) -> list[str]:
    expanded = [token for token in tokens if token not in STOPWORDS]
    for token in tokens:
        expanded.extend(EN_SYNONYMS.get(token, []))
        expanded_token = AR_HINTS.get(token)
        if expanded_token:
            expanded.append(expanded_token)
    return expanded


def parse_budget(text: str) -> int | None:
    lowered = text.lower()
    numbers = [int(n) for n in re.findall(r"\b\d{2,4}\b", lowered)]
    if not numbers:
        return None
    if any(word in lowered for word in ["under", "below", "less", "budget", "aed", "درهم", "أقل"]):
        return max(numbers)
    return None


def parse_age_months(text: str) -> int | None:
    lowered = text.lower()
    patterns = [
        (r"(\d+)\s*[- ]?month", 1),
        (r"(\d+)\s*mo\b", 1),
        (r"(\d+)\s*[- ]?year", 12),
        (r"(\d+)\s*سن", 12),
        (r"(\d+)\s*شهر", 1),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, lowered)
        if match:
            return int(match.group(1)) * multiplier
    if "newborn" in lowered or "حديث" in lowered:
        return 0
    return None


def parse_country(text: str) -> str | None:
    lowered = text.lower()
    aliases = {
        "uae": "AE",
        "dubai": "AE",
        "abu dhabi": "AE",
        "الإمارات": "AE",
        "saudi": "SA",
        "ksa": "SA",
        "riyadh": "SA",
        "السعودية": "SA",
        "qatar": "QA",
        "doha": "QA",
        "قطر": "QA",
        "kuwait": "KW",
        "الكويت": "KW",
        "bahrain": "BH",
        "البحرين": "BH",
    }
    for alias, code in aliases.items():
        if alias in lowered:
            return code
    return None


def parse_request(text: str) -> Request:
    tokens = expand_tokens(tokenize(text))
    return Request(
        raw=text,
        language=detect_language(text),
        budget_aed=parse_budget(text),
        age_months=parse_age_months(text),
        country=parse_country(text),
        query_tokens=tokens,
    )


def product_text(product: dict[str, Any]) -> str:
    fields = [
        product["name_en"],
        product["name_ar"],
        product["category"],
        product["description_en"],
        product["description_ar"],
        " ".join(product["tags"]),
        " ".join(product["safety_notes"]),
    ]
    return " ".join(fields).lower()


def score_product(request: Request, product: dict[str, Any]) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0
    product_tokens = set(tokenize(product_text(product)))
    overlap = sorted(set(request.query_tokens) & product_tokens)
    if overlap:
        score += min(len(overlap), 6) * 0.12
        reasons.append(f"keyword match: {', '.join(overlap[:5])}")

    if "car" in request.query_tokens and "seat" in request.query_tokens:
        if product["category"] == "car-seats":
            score += 0.5
            reasons.append("exact category intent")
        else:
            score -= 0.2

    if request.budget_aed is not None:
        if product["price_aed"] <= request.budget_aed:
            score += 0.25
            reasons.append("within budget")
        else:
            over_by = product["price_aed"] - request.budget_aed
            score -= min(0.35, over_by / max(request.budget_aed, 1))
            reasons.append("over budget")

    if request.age_months is not None:
        if product["age_min_months"] <= request.age_months <= product["age_max_months"]:
            score += 0.25
            reasons.append("age appropriate")
        else:
            distance = min(
                abs(request.age_months - product["age_min_months"]),
                abs(request.age_months - product["age_max_months"]),
            )
            score -= min(0.4, distance / 48)
            reasons.append("age mismatch")

    if request.country is not None:
        if request.country in product["country_availability"]:
            score += 0.15
            reasons.append("available in requested country")
        else:
            score -= 0.25
            reasons.append("not available in requested country")

    if any(token in request.query_tokens for token in ["gift", "present", "هدية"]):
        if "gift" in product["tags"]:
            score += 0.12
            reasons.append("giftable")

    return max(0.0, min(score, 1.0)), reasons


def shortlist(request: Request, catalog: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    scored = []
    for product in catalog:
        score, reasons = score_product(request, product)
        if score > 0:
            scored.append((score, reasons, product))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {"score": round(score, 2), "reasons": reasons, "product": product}
        for score, reasons, product in scored[:limit]
    ]


def confidence_from_results(request: Request, results: list[dict[str, Any]]) -> float:
    if not results:
        return 0.0
    top = results[0]["score"]
    missing = sum(
        value is None for value in [request.budget_aed, request.age_months, request.country]
    )
    confidence = top - (missing * 0.08)
    return round(max(0.0, min(confidence, 0.95)), 2)


def build_item(result: dict[str, Any], language: str) -> dict[str, Any]:
    product = result["product"]
    if language == "ar":
        reason = arabic_reason(product, result["reasons"])
        name = product["name_ar"]
    else:
        reason = english_reason(product, result["reasons"])
        name = product["name_en"]
    return {
        "sku": product["sku"],
        "name": name,
        "price_aed": product["price_aed"],
        "category": product["category"],
        "confidence": result["score"],
        "reason": reason,
        "evidence": {
            "age_range_months": [product["age_min_months"], product["age_max_months"]],
            "availability": product["country_availability"],
            "matched_signals": result["reasons"],
        },
    }


def english_reason(product: dict[str, Any], reasons: list[str]) -> str:
    if "age appropriate" in reasons and "within budget" in reasons:
        return f"Fits the child age and budget, with a practical use case: {product['description_en']}"
    if "giftable" in reasons:
        return f"Gift-friendly choice grounded in the catalog: {product['description_en']}"
    return f"Relevant catalog match: {product['description_en']}"


def arabic_reason(product: dict[str, Any], reasons: list[str]) -> str:
    if "age appropriate" in reasons and "within budget" in reasons:
        return f"مناسب لعمر الطفل وضمن الميزانية، وفائدته واضحة: {product['description_ar']}"
    if "giftable" in reasons:
        return f"اختيار مناسب كهدية بناء على بيانات المنتج: {product['description_ar']}"
    return f"اقتراح مرتبط بطلبك من بيانات الكتالوج: {product['description_ar']}"


def refusal_message(language: str) -> str:
    if language == "ar":
        return "لا أملك معلومات كافية من الطلب والكتالوج لأقترح منتجات بثقة. أضف عمر الطفل والميزانية والبلد."
    return "I do not have enough supported catalog evidence to recommend products confidently. Add child age, budget, and country."


def answer(query: str, catalog: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    catalog = catalog or load_catalog()
    request = parse_request(query)
    results = shortlist(request, catalog)
    confidence = confidence_from_results(request, results)
    has_any_within_budget = (
        True
        if request.budget_aed is None
        else any(product["price_aed"] <= request.budget_aed for product in catalog)
    )
    if not has_any_within_budget:
        confidence = min(confidence, 0.2)
    should_refuse = confidence < 0.35 or not results or not has_any_within_budget
    output = {
        "schema_version": "1.0",
        "input_language": request.language,
        "understood": {
            "budget_aed": request.budget_aed,
            "age_months": request.age_months,
            "country": request.country,
        },
        "status": "refused" if should_refuse else "answered",
        "overall_confidence": confidence,
        "shortlist": [] if should_refuse else [build_item(item, request.language) for item in results],
        "uncertainty": [],
    }
    if request.budget_aed is None:
        output["uncertainty"].append("budget_missing")
    if request.age_months is None:
        output["uncertainty"].append("age_missing")
    if request.country is None:
        output["uncertainty"].append("country_missing")
    if not has_any_within_budget:
        output["uncertainty"].append("budget_below_catalog_floor")
    if should_refuse:
        output["message"] = refusal_message(request.language)
    else:
        output["message"] = (
            "تم إنشاء قائمة مختصرة من المنتجات المدعومة ببيانات الكتالوج."
            if request.language == "ar"
            else "Shortlist generated from supported catalog evidence."
        )
    validate_output(output)
    return output


def validate_output(output: dict[str, Any]) -> None:
    required = {
        "schema_version": str,
        "input_language": str,
        "understood": dict,
        "status": str,
        "overall_confidence": float,
        "shortlist": list,
        "uncertainty": list,
        "message": str,
    }
    for key, expected_type in required.items():
        if key not in output:
            raise ValueError(f"Missing required field: {key}")
        if not isinstance(output[key], expected_type):
            raise TypeError(f"Field {key} must be {expected_type.__name__}")
    if output["status"] not in {"answered", "refused"}:
        raise ValueError("status must be answered or refused")
    if not 0 <= output["overall_confidence"] <= 1:
        raise ValueError("overall_confidence must be between 0 and 1")
    if output["status"] == "refused" and output["shortlist"]:
        raise ValueError("refused outputs must not include recommendations")
    for item in output["shortlist"]:
        for key in ["sku", "name", "price_aed", "category", "confidence", "reason", "evidence"]:
            if key not in item:
                raise ValueError(f"Recommendation missing {key}")
        if not item["sku"] or not item["name"] or not item["reason"]:
            raise ValueError("Recommendation fields cannot be empty")


def run_cli() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Mumzworld bilingual gift finder prototype")
    parser.add_argument("query", nargs="*", help="Natural-language shopping request")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    query = " ".join(args.query).strip()
    if not query:
        query = input("Describe the gift/product need: ").strip()
    result = answer(query)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    run_cli()
