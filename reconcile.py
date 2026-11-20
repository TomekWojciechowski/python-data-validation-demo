"""Compare a synthetic source CSV with a downstream SQLite ledger."""
import csv
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
DIRECTIONS = {"CREDIT": ("in", 1), "DEBIT": ("out", -1)}


def expected_rows(source):
    rows = {}
    for row in csv.DictReader(source):
        key = row["transaction_id"]
        if not key or key in rows:
            raise ValueError(f"Missing or duplicate transaction ID: {key!r}")
        direction, sign = DIRECTIONS[row["side"]]
        cents = Decimal(row["amount"]) * 100
        if not cents.is_finite() or cents < 0 or cents != cents.to_integral_value():
            raise ValueError(f"Invalid amount for {key}: {row['amount']}")
        rows[key] = (direction, sign * int(cents))
    return rows


def discrepancies(source, connection):
    expected = expected_rows(source)
    actual = {
        key: (direction, cents)
        for key, direction, cents in connection.execute(
            "SELECT transaction_id, direction, signed_cents FROM ledger"
        )
    }
    issues = []
    for key in sorted(expected.keys() | actual.keys()):
        if key not in actual:
            issues.append(f"{key} | missing from ledger")
        elif key not in expected:
            issues.append(f"{key} | unexpected ledger row")
        else:
            for field, wanted, found in zip(
                ("direction", "signed_cents"), expected[key], actual[key], strict=True
            ):
                if wanted != found:
                    issues.append(f"{key} | {field} | expected {wanted} | actual {found}")
    return issues


def main():
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.executescript((DATA / "processed.sql").read_text(encoding="utf-8"))
        with (DATA / "source.csv").open(encoding="utf-8", newline="") as source:
            issues = discrepancies(source, connection)
    for issue in issues:
        print(issue)
    print(f"Discrepancies: {len(issues)}")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
