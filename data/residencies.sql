BEGIN TRANSACTION;
CREATE TABLE checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT,
    checked_at TEXT,
    ok INTEGER,
    status TEXT,
    via TEXT,
    n_items INTEGER,
    changed INTEGER
);
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT,
    source_id TEXT,
    finding_id TEXT,
    type TEXT,            -- new_posting | new_date | now_open | upgraded | removed | page_changed | source_failing | source_recovered
    level TEXT,           -- high | medium | low
    message TEXT,
    url TEXT,
    notified INTEGER DEFAULT 0
);
CREATE TABLE findings (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    system_id TEXT,
    kind TEXT,            -- posting | snippet
    title TEXT,
    url TEXT,
    cohort TEXT,          -- dates mentioned, e.g. "October 2027"
    relevance TEXT,       -- target | maybe | unknown | early | late
    signal TEXT,          -- open | closed | ''
    hospital_id TEXT,
    first_seen TEXT,
    last_seen TEXT,
    active INTEGER DEFAULT 1,
    missed INTEGER DEFAULT 0
);
CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    system_id TEXT,
    url TEXT,
    kind TEXT,
    baseline_done INTEGER DEFAULT 0,
    last_checked TEXT,
    last_ok TEXT,
    last_status TEXT,
    last_error TEXT,
    last_via TEXT,
    last_hash TEXT,
    page_signal TEXT,
    n_items INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0
);
DELETE FROM "sqlite_sequence";
COMMIT;
