"""Conservative accounting checks over dated evidence; no ratings or model calls.

Written by OpenAI Codex, directed by Robert Vetter, 2026-09-17.
Input: normalized evidence and exact fiscal interval. Output: review rows with
linked operands, mechanical status and separate pending-human-review status.
"""
from evidence_ledger import (REVENUE, REVENUE_COMPONENTS, GROSS_INTEREST, NET_INTEREST, CASH_INTEREST,
                             INTEREST_COMPONENTS, DEBT, LEASES, select)


def row(metric, result, reason=None):
    return {"metric": metric, **result,
            **({"reason": result.get("reason", "") + " " + reason} if reason else {})}


def reconcile(records, total_tag, current_tag, noncurrent_tag, end):
    """Check one total against its two components; never add total to components."""
    operands = [select(records, (tag,), None, end)
                for tag in (total_tag, current_tag, noncurrent_tag)]
    ids = [o["selected_id"] for o in operands if o["selected_id"]]
    base = {"value": None, "evidence_ids": list(dict.fromkeys(i for o in operands for i in o["evidence_ids"])),
            "operands": operands, "review_status": "pending_human_review",
            "unit": "USD", "start": None, "end": end,
            "formula": "total - current - noncurrent", "dependencies": ids}
    if any(o["status"] == "conflict" for o in operands):
        return {**base, "status": "conflict", "reason": "Conflicting component evidence."}
    if any(o["status"] != "passed" for o in operands):
        return {**base, "status": "missing", "reason": "Incomplete reconciliation; missing is not zero."}
    if any(o["value"] < 0 for o in operands):
        return {**base, "status": "needs_review", "reason": "Negative liability requires source review."}
    residual = operands[0]["value"] - operands[1]["value"] - operands[2]["value"]
    return {**base, "value": residual, "status": "passed" if residual == 0 else "conflict",
            "filed": max(o["filed"] for o in operands),
            "reason": "Zero residual reconciles arithmetic only. Do not add the total again to its components."}


def annual_checks(records, start, end):
    rows = [row("annual_revenue", select(records, REVENUE, start, end)),
            row("operating_income", select(records, ("OperatingIncomeLoss",), start, end)),
            row("gross_interest_expense", select(records, GROSS_INTEREST, start, end))]
    gross = rows[-1]
    if gross["status"] == "passed" and gross["value"] < 0:
        gross.update(status="needs_review", reason="Negative gross expense; never apply abs().")
    for tag in REVENUE_COMPONENTS + NET_INTEREST + CASH_INTEREST + INTEREST_COMPONENTS:
        result = select(records, (tag,), start, end)
        if result["status"] != "missing":
            rows.append(row(tag, result, "Separate component/concept, not an automatic substitute for the requested total."))
    for tag in DEBT + LEASES:
        result = select(records, (tag,), None, end)
        if result["status"] != "missing":
            rows.append(row(tag, result, "Component inventory only; inclusion and overlap need source review."))
    for prefix in ("LongTermDebt", "FinanceLeaseLiability", "OperatingLeaseLiability"):
        rows.append(row(prefix + "_reconciliation",
                        reconcile(records, prefix, prefix + "Current", prefix + "Noncurrent", end)))
    rows.append({"metric": "lease_inclusive_total_debt", "value": None, "status": "needs_review",
                 "reason": "No combined total: borrowing completeness and finance-lease inclusion need review. Missing borrowing tags do not mean zero debt.",
                 "evidence_ids": [r["selected_id"] for r in rows if r.get("selected_id") and r.get("tag") in DEBT + LEASES],
                 "review_status": "pending_human_review", "start": None, "end": end, "unit": "USD"})
    return rows
