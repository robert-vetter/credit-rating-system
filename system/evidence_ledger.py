"""Normalize cached SEC facts and link them to local filing elements, without I/O.

Written by OpenAI Codex, directed by Robert Vetter, 2026-09-17.
Inputs: decoded companyfacts, source metadata, observation boundary and periods.
Outputs: machine-proposed evidence with availability checks and source lineage.
No fetching, rating labels, accounting adjudication or implicit writes.
"""
import hashlib
import math
from datetime import date
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser

POLICY = "accounting-evidence-v1"
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
REVENUE = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
           "SalesRevenueNet")
REVENUE_COMPONENTS = ("SalesRevenueGoodsNet", "SalesRevenueServicesNet")
GROSS_INTEREST = ("InterestExpense", "InterestExpenseNonoperating", "InterestAndDebtExpense")
NET_INTEREST = ("InterestIncomeExpenseNet", "InterestIncomeExpenseNonoperatingNet")
INTEREST_COMPONENTS = ("InterestExpenseDebt", "InterestExpenseLongTermDebt",
                       "FinanceLeaseInterestExpense")
CASH_INTEREST = ("InterestPaid", "InterestPaidNet")
DEBT = ("LongTermDebt", "LongTermDebtNoncurrent", "LongTermDebtCurrent", "DebtCurrent",
        "ShortTermBorrowings", "CommercialPaper", "LineOfCredit",
        "LongTermDebtAndCapitalLeaseObligations",
        "LongTermDebtAndCapitalLeaseObligationsCurrent")
LEASES = tuple(f"{kind}LeaseLiability{part}" for kind in ("Finance", "Operating")
               for part in ("", "Current", "Noncurrent"))
TAGS = set(REVENUE + REVENUE_COMPONENTS + GROSS_INTEREST + NET_INTEREST + INTEREST_COMPONENTS + CASH_INTEREST
           + DEBT + LEASES + ("OperatingIncomeLoss", "NetCashProvidedByUsedInOperatingActivities",
                              "PaymentsToAcquirePropertyPlantAndEquipment"))
INSTANT_TAGS = set(DEBT + LEASES)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pointer_token(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def normalize(raw, source, as_of, ends):
    """Keep all relevant alternatives; quarantine bad facts before any selection.

    Duration is elapsed calendar days (end minus start). The duration label is a
    candidate classification only: an exact fiscal interval is still required.
    """
    boundary = date.fromisoformat(as_of)
    records = []
    for namespace, concepts in sorted(raw.get("facts", {}).items()):
        for tag, blob in sorted(concepts.items()):
            if tag not in TAGS:
                continue
            for unit, values in sorted(blob.get("units", {}).items()):
                for index, fact in enumerate(values):
                    if fact.get("end") not in ends:
                        continue
                    pointer = "/facts/{}/{}/units/{}/{}".format(
                        pointer_token(namespace), pointer_token(tag), pointer_token(unit), index)
                    record = {k: fact.get(k) for k in
                              ("start", "end", "val", "accn", "filed", "form", "fy", "fp", "frame")}
                    record.update({"id": digest((source["sha256"] + pointer).encode())[:24],
                                   "issuer": raw.get("entityName"), "cik": raw.get("cik"),
                                   "namespace": namespace, "tag": tag, "unit": unit,
                                   "source": {**source, "pointer": pointer}, "as_of": as_of,
                                   "policy": POLICY, "review_status": "pending_human_review",
                                   "origin": "machine_proposed", "issues": [],
                                   "filing_locator": {"status": "filing_locator_unavailable"}})
                    issues = record["issues"]
                    if namespace != "us-gaap":
                        issues.append("unsupported_namespace")
                    if unit != "USD":
                        issues.append("unsupported_unit")
                    if record["form"] not in FORMS:
                        issues.append("unsupported_form")
                    if not record["accn"]:
                        issues.append("missing_accession")
                    value = record["val"]
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                        issues.append("invalid_value")
                        record["val"] = None
                        record["invalid_raw_value"] = repr(value)
                    try:
                        end = date.fromisoformat(record["end"])
                        filed = date.fromisoformat(record["filed"])
                        if filed > boundary:
                            issues.append("filed_after_observation")
                        if end > filed:
                            issues.append("period_after_filing")
                        if tag in INSTANT_TAGS:
                            record["duration_kind"] = "instant"
                            if record["start"] is not None:
                                issues.append("instant_has_start")
                        else:
                            start = date.fromisoformat(record["start"])
                            days = (end - start).days
                            record["elapsed_days"] = days
                            record["duration_kind"] = (
                                "quarter_length" if 75 <= days <= 110 else
                                "annual_length" if 330 <= days <= 380 else
                                "ytd_or_other_duration")
                            if days < 0:
                                issues.append("reversed_period")
                    except (ValueError, TypeError):
                        issues.append("missing_or_invalid_date")
                    record["availability"] = "eligible" if not issues else "quarantined"
                    records.append(record)
    return records


def select(records, tags, start, end):
    """Exact interval, USD and availability first; abstain on conflicting values.

    Multiple preferred/alternative tags with different values are a conflict,
    not license to choose a favourable answer. Identical observations select the
    first listed concept then earliest publication. All candidates remain linked.
    """
    candidates = [r for r in records if r["availability"] == "eligible"
                  and r["tag"] in tags and r["start"] == start and r["end"] == end]
    base = {"status": "missing", "value": None, "evidence_ids": [r["id"] for r in candidates],
            "selected_id": None, "start": start, "end": end, "unit": "USD",
            "review_status": "pending_human_review"}
    if not candidates:
        return {**base, "reason": "No eligible fact for this exact concept and interval."}
    if len({r["val"] for r in candidates}) != 1:
        return {**base, "status": "conflict", "reason": "Conflicting available values; review revisions/concepts."}
    chosen = min(candidates, key=lambda r: (tags.index(r["tag"]), r["filed"], r["accn"], r["id"]))
    return {**base, "status": "passed", "value": chosen["val"], "selected_id": chosen["id"],
            "filed": chosen["filed"], "tag": chosen["tag"],
            "reason": "Exact-period structured fact selected; accounting meaning still requires review."}


class FilingIndex(HTMLParser):
    """Index numeric inline-XBRL elements and their contexts, without page prose."""
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.contexts, self.units, self.numbers = {}, {}, []
        self.active = None
        self.stack = []
        self.line_offsets = [0]
        for line in text.splitlines(keepends=True):
            self.line_offsets.append(self.line_offsets[-1] + len(line))
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        local = tag.split(":")[-1]
        if self.active is None and local in ("context", "unit", "nonfraction"):
            line, column = self.getpos()
            self.active = {"root": tag, "attrs": attrs, "text": [], "parts": {},
                           "dimensioned": False, "offset": self.line_offsets[line - 1] + column,
                           "line": line, "identifier_scheme": None}
            self.stack = [tag]
        elif self.active is not None:
            self.stack.append(tag)
        if self.active is not None:
            if local in ("explicitmember", "typedmember", "segment", "scenario"):
                self.active["dimensioned"] = True
            if local == "identifier":
                self.active["identifier_scheme"] = attrs.get("scheme")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.active is not None:
            self.active["text"].append(data)
            if self.stack:
                key = self.stack[-1].split(":")[-1]
                self.active["parts"].setdefault(key, []).append(data)

    def handle_endtag(self, tag):
        if self.active is None:
            return
        if tag == self.active["root"]:
            item = self.active
            item["text"] = "".join(item["text"]).strip()
            item["parts"] = {k: "".join(v).strip() for k, v in item["parts"].items()}
            kind = tag.split(":")[-1]
            if kind == "context":
                self.contexts[item["attrs"].get("id")] = item
            elif kind == "unit":
                self.units[item["attrs"].get("id")] = item
            else:
                self.numbers.append(item)
            self.active, self.stack = None, []
        elif self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def locate(self, record, source):
        matches = []
        for item in self.numbers:
            attrs = item["attrs"]
            if attrs.get("name") != record["namespace"] + ":" + record["tag"]:
                continue
            context = self.contexts.get(attrs.get("contextref"))
            unit = self.units.get(attrs.get("unitref"))
            if not context or context["dimensioned"] or not unit:
                continue
            parts = context["parts"]
            if parts.get("instant", parts.get("enddate")) != record["end"] or parts.get("startdate") != record["start"]:
                continue
            if context["identifier_scheme"] not in ("http://www.sec.gov/CIK", "https://www.sec.gov/CIK"):
                continue
            try:
                if int(parts.get("identifier", "")) != int(record["cik"]):
                    continue
            except (ValueError, TypeError):
                continue
            if unit["parts"].get("measure") != "iso4217:USD" or "divide" in unit["parts"]:
                continue
            fmt = attrs.get("format", "").split(":")[-1]
            if fmt not in ("", "num-dot-decimal", "numdotdecimal", "zerodash", "num-zero"):
                continue
            try:
                text = item["text"].replace(",", "").replace(" ", "").strip()
                value = Decimal(0) if text in ("-", "—", "–") and fmt in ("zerodash", "num-zero") else Decimal(text)
                value *= Decimal(10) ** int(attrs.get("scale", "0"))
                if attrs.get("sign") == "-":
                    value = -value
                if not value.is_finite() or value != Decimal(str(record["val"])):
                    continue
            except (InvalidOperation, ValueError, OverflowError):
                continue
            matches.append({"element_id": attrs.get("id"), "context_ref": attrs.get("contextref"),
                            "line": item["line"], "character_offset": item["offset"],
                            "displayed_text": item["text"], "scale": attrs.get("scale", "0"),
                            "sign": attrs.get("sign"), "format": attrs.get("format")})
        if not matches:
            return {"status": "filing_locator_unavailable", "reason": "No exact consolidated inline fact match."}
        return {"status": "matched_inline_fact", "source": source, "matches": matches,
                "scope": "Numeric tag, period, entity and unit match only; not accounting adjudication."}
