import re
from typing import Dict, Any, List

from transformers import pipeline

# NOTE: This is a prototype. Replace the model with a dedicated phishing classifier.
_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "password",
    "account",
    "login",
    "click",
    "bank",
    "secure",
    "update",
    "confirm",
    "wire transfer",
    "ssn",
    "social security",
]


def extract_links(text: str) -> List[str]:
    return re.findall(r"https?://[\w\-./?=&%#]+", text)


def suspicious_words_in(text: str) -> List[str]:
    t = text.lower()
    return [w for w in SUSPICIOUS_KEYWORDS if w in t]


def analyze_text(text: str, sender: str | None = None) -> Dict[str, Any]:
    # classifier returns label and score
    truncated = text if len(text) <= 2000 else text[:2000]
    try:
        cls = _classifier(truncated[:1000])[0]
        label = cls.get("label")
        score = float(cls.get("score", 0.0))
    except Exception:
        label = "UNKNOWN"
        score = 0.0

    links = extract_links(text)
    suspicious_words = suspicious_words_in(text)

    # Heuristic scoring (0.0 - 1.0)
    link_score = min(1.0, 0.2 * len(links))
    keyword_score = min(1.0, 0.15 * len(suspicious_words))

    sender_score = 0.0
    if sender:
        s = sender.lower()
        # suspicious if sender includes many digits or uncommon domains
        if re.search(r"\d{4,}", s):
            sender_score = 0.2
        if any(d in s for d in ["@service", "@no-reply", "@noreply"]):
            sender_score = max(sender_score, 0.1)

    # Use classifier output weakly (prototype): treat POSITIVE/NEGATIVE as signals
    clf_score = 0.0
    if label == "NEGATIVE":
        clf_score = 0.1 * score
    elif label == "POSITIVE":
        clf_score = 0.05 * (1 - score)

    risk_score = min(1.0, link_score + keyword_score + sender_score + clf_score)

    if risk_score >= 0.7:
        level = "high"
    elif risk_score >= 0.4:
        level = "medium"
    else:
        level = "low"

    reasons: List[str] = []
    if links:
        reasons.append(f"Contains {len(links)} link(s)")
    if suspicious_words:
        reasons.append(f"Suspicious keywords: {', '.join(suspicious_words)}")
    if sender_score > 0:
        reasons.append("Suspicious sender pattern")
    if label != "UNKNOWN":
        reasons.append(f"Text classifier: {label} (score {score:.2f})")

    return {
        "risk_score": round(risk_score, 3),
        "risk_level": level,
        "reasons": reasons,
        "details": {
            "classifier_label": label,
            "classifier_score": score,
            "links": links,
            "suspicious_words": suspicious_words,
        },
    }
