# Financial transaction reconciliation

[![Reconciliation tests](https://github.com/TomekWojciechowski/python-data-validation-demo/actions/workflows/tests.yml/badge.svg)](https://github.com/TomekWojciechowski/python-data-validation-demo/actions/workflows/tests.yml)

A synthetic payment of PLN 9.99 was booked as PLN 9.98. This Python example shows how to catch that one-cent difference by comparing a source CSV with an independently seeded SQLite ledger.

## Run the example

From the repository root with Python 3.12:

```sh
python reconcile.py
```

Expected output:

```text
TX-002 | signed_cents | expected -999 | actual -998
Discrepancies: 1
```

The example exits with status **1** because it found a mismatch. To try a clean run, change the seeded amount for TX-002 in `data/processed.sql` from `-998` to `-999`, then rerun the command. A match exits with status **0**. Restore the original fixture before running the test suite.

## What is checked

| Source rule | Expected ledger value |
| --- | --- |
| CREDIT or DEBIT | `in` or `out`, respectively |
| Non-negative PLN amount, precise to the cent | Positive cents for a credit and negative cents for a debit, calculated with decimal arithmetic |
| Transaction ID | Exactly one source row and one ledger row per ID |

[Source transactions](data/source.csv) and the [ledger snapshot](data/processed.sql) are fictional. SQLite runs in memory. The demo uses only the Python standard library.

## Run the tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The [tests](tests/test_reconcile.py) check the known discrepancy, a fully matching ledger, incorrect direction, missing and unexpected transactions, duplicate source IDs and invalid amounts. GitHub Actions runs the suite on pushes and pull requests.
