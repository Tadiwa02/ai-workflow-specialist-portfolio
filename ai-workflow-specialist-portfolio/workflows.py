"""Core workflow logic kept separate from the user interface."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

STOPWORDS = {
    "the","and","for","with","you","your","are","our","this","that","from",
    "will","have","has","was","were","not","but","can","all","who","what",
    "when","where","how","into","their","they","them","about","using","use",
    "job","role","work","team","ability","skills","experience","required",
    "preferred","including","such","than","then","also","more","support"
}

def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def job_match(cv: str, description: str) -> dict[str, Any]:
    cv_terms = set(tokenize(cv))
    job_terms = set(tokenize(description))
    matched = sorted(cv_terms & job_terms)
    missing = sorted(job_terms - cv_terms)
    score = round(100 * len(matched) / max(1, len(job_terms)))
    return {
        "score": score,
        "matched_terms": matched[:30],
        "terms_to_address": missing[:30],
        "job_term_count": len(job_terms),
    }

def triage_ticket(message: str) -> dict[str, str]:
    text = (message or "").lower()
    categories = {
        "Access / login": ["login", "password", "locked out", "access", "sign in", "2fa"],
        "Billing": ["invoice", "charged", "payment", "refund", "billing", "subscription"],
        "Bug / technical issue": ["error", "bug", "crash", "not working", "broken", "failed"],
        "Account / profile": ["account", "profile", "change my email", "update details"],
    }
    matches = [(category, sum(term in text for term in terms)) for category, terms in categories.items()]
    category, count = max(matches, key=lambda item: item[1]) if matches else ("General enquiry", 0)
    urgent_terms = ["urgent", "asap", "production down", "data loss", "security breach", "can't access"]
    high_terms = ["today", "blocked", "multiple users", "deadline", "cannot work"]
    if any(term in text for term in urgent_terms):
        priority = "High"
    elif any(term in text for term in high_terms):
        priority = "Medium"
    else:
        priority = "Low"
    team = {
        "Access / login": "IT Support",
        "Billing": "Finance / Billing",
        "Bug / technical issue": "Technical Support",
        "Account / profile": "Customer Operations",
        "General enquiry": "Customer Support",
    }[category]
    return {"category": category, "priority": priority, "team": team,
            "rule_matches": str(count)}

def validate_orders(df):
    """Return a copied dataframe with computed totals and transparent validation notes."""
    import pandas as pd

    out = df.copy()
    required = ["order_id", "customer", "email", "product", "quantity", "unit_price", "status"]
    for column in required:
        if column not in out.columns:
            out[column] = ""
    out["quantity_num"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["unit_price_num"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out["order_total"] = out["quantity_num"] * out["unit_price_num"]

    def issues(row):
        problems = []
        for field in ["order_id", "customer", "email", "product", "status"]:
            if pd.isna(row[field]) or not str(row[field]).strip():
                problems.append(f"Missing {field}")
        if pd.isna(row["quantity_num"]):
            problems.append("Invalid quantity")
        elif row["quantity_num"] <= 0:
            problems.append("Quantity must be greater than zero")
        if pd.isna(row["unit_price_num"]):
            problems.append("Invalid unit price")
        elif row["unit_price_num"] < 0:
            problems.append("Unit price cannot be negative")
        if row["email"] and "@" not in str(row["email"]):
            problems.append("Email may be invalid")
        return "; ".join(problems) if problems else "OK"

    out["validation"] = out.apply(issues, axis=1)
    out["needs_review"] = out["validation"].ne("OK")
    return out
