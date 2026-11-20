import sqlite3
from io import StringIO

import pytest

from reconcile import DATA, discrepancies, expected_rows


@pytest.fixture
def ledger():
    connection = sqlite3.connect(":memory:")
    connection.executescript((DATA / "processed.sql").read_text(encoding="utf-8"))
    yield connection
    connection.close()


def compare(ledger):
    with (DATA / "source.csv").open(encoding="utf-8", newline="") as source:
        return discrepancies(source, ledger)


@pytest.fixture
def matching_ledger(ledger):
    ledger.execute("UPDATE ledger SET signed_cents = -999 WHERE transaction_id = 'TX-002'")
    return ledger


def test_reports_one_cent_discrepancy(ledger):
    assert compare(ledger) == ["TX-002 | signed_cents | expected -999 | actual -998"]


def test_matching_ledger_passes(matching_ledger):
    assert compare(matching_ledger) == []


def test_direction_mapping(matching_ledger):
    matching_ledger.execute("UPDATE ledger SET direction = 'out' WHERE transaction_id = 'TX-001'")
    assert compare(matching_ledger) == ["TX-001 | direction | expected in | actual out"]


def test_missing_and_unexpected_transactions(matching_ledger):
    matching_ledger.execute("DELETE FROM ledger WHERE transaction_id = 'TX-003'")
    matching_ledger.execute("INSERT INTO ledger VALUES ('TX-004', 'in', 5)")
    assert compare(matching_ledger) == ["TX-003 | missing from ledger", "TX-004 | unexpected ledger row"]


def test_duplicate_source_ids_are_rejected():
    source = StringIO("transaction_id,side,amount\nA,CREDIT,1.00\nA,DEBIT,2.00\n")
    with pytest.raises(ValueError, match="duplicate transaction ID"):
        expected_rows(source)


@pytest.mark.parametrize("amount", ["0.001", "-1.00", "NaN"])
def test_invalid_amount_is_rejected(amount):
    source = StringIO(f"transaction_id,side,amount\nA,CREDIT,{amount}\n")
    with pytest.raises(ValueError, match="Invalid amount"):
        expected_rows(source)
