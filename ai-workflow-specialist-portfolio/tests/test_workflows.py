import pandas as pd
from workflows import job_match, triage_ticket, validate_orders

def test_job_match_finds_overlap():
    result = job_match("Python automation workflow", "Python workflow specialist")
    assert result["score"] > 0
    assert "python" in result["matched_terms"]

def test_urgent_ticket_is_high_priority():
    result = triage_ticket("Urgent: I am locked out and can't access my account")
    assert result["priority"] == "High"
    assert result["category"] == "Access / login"

def test_csv_validation_flags_missing_customer():
    df = pd.DataFrame([{
        "order_id": "1", "customer": "", "email": "a@example.com",
        "product": "Test", "quantity": 1, "unit_price": 2, "status": "paid"
    }])
    report = validate_orders(df)
    assert bool(report.iloc[0]["needs_review"])
    assert "Missing customer" in report.iloc[0]["validation"]
