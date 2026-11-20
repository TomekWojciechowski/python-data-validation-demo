-- Independent snapshot from a simulated downstream system (all amounts in PLN cents).
CREATE TABLE ledger (
    transaction_id TEXT PRIMARY KEY NOT NULL,
    direction TEXT NOT NULL,
    signed_cents INTEGER NOT NULL
);
INSERT INTO ledger VALUES
    ('TX-001', 'in', 12540),
    ('TX-002', 'out', -998),
    ('TX-003', 'in', 5);
