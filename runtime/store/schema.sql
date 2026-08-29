-- Runtime v0 storage. Six tables plus `meta` for schema versioning.
-- See runtime/ARCHITECTURE.md §Storage for the mapping from these tables
-- to the ontology's Object / Relationship / Attribute-State / Event /
-- Provenance concepts.

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- 1. every entity instance in the graph
CREATE TABLE IF NOT EXISTS object (
  object_id     TEXT PRIMARY KEY,
  entity_type   TEXT NOT NULL,
  natural_key   TEXT NOT NULL,
  created_from  TEXT NOT NULL,   -- Document.object_id of first sighting
  created_at    TEXT NOT NULL    -- ISO timestamp
);
CREATE INDEX IF NOT EXISTS object_type_key ON object(entity_type, natural_key);

-- 2. every atomic assertion. Attribute values AND relationship endpoints
--    are both facts; a relationship is a fact whose value_kind='ref'.
CREATE TABLE IF NOT EXISTS fact (
  fact_id       TEXT PRIMARY KEY,
  subject_id    TEXT NOT NULL REFERENCES object(object_id),
  predicate     TEXT NOT NULL,
  value_kind    TEXT NOT NULL,   -- text|integer|decimal|boolean|date|timestamp|enum|ref|list_text|list_ref|map|any|null
  value_text    TEXT,
  value_num     REAL,
  value_date    TEXT,
  value_ref     TEXT REFERENCES object(object_id),
  raw_value     TEXT,
  status        TEXT NOT NULL,   -- OBSERVED|INFERRED_HIGH|INFERRED_LOW|UNRESOLVED|CONFLICT
  variant_group TEXT,
  supersedes    TEXT REFERENCES fact(fact_id),
  is_current    INTEGER NOT NULL DEFAULT 1,
  observed_at   TEXT NOT NULL,
  reason        TEXT
);
CREATE INDEX IF NOT EXISTS fact_subj_pred ON fact(subject_id, predicate);
CREATE INDEX IF NOT EXISTS fact_current
  ON fact(subject_id, predicate) WHERE is_current = 1;

-- 3. provenance per fact
CREATE TABLE IF NOT EXISTS provenance (
  provenance_id     TEXT PRIMARY KEY,
  fact_id           TEXT NOT NULL REFERENCES fact(fact_id),
  document_id       TEXT NOT NULL REFERENCES object(object_id),
  source_sheet      TEXT,
  source_location   TEXT,
  extraction_method TEXT NOT NULL,    -- direct|regex|parse|manual
  document_date     TEXT,
  confidence        TEXT NOT NULL     -- OBSERVED|INFERRED_HIGH|INFERRED_LOW
);
CREATE INDEX IF NOT EXISTS prov_fact ON provenance(fact_id);

-- 4. event index — denormalised StageEvent / StageDeadline view for
--    fast timeline queries. The events themselves live in `object`.
CREATE TABLE IF NOT EXISTS event_index (
  event_id           TEXT PRIMARY KEY REFERENCES object(object_id),
  event_type         TEXT NOT NULL,
  affected_object_id TEXT REFERENCES object(object_id),
  planned_date       TEXT,
  actual_date        TEXT,
  status             TEXT NOT NULL     -- PLANNED|IN_PROGRESS|DONE|REVISED|CANCELLED
);

-- 5. alias table for entity resolution
CREATE TABLE IF NOT EXISTS alias (
  entity_type TEXT NOT NULL,
  variant     TEXT NOT NULL,
  canonical   TEXT NOT NULL,
  reason      TEXT,
  PRIMARY KEY (entity_type, variant)
);

-- 6. validation report (rebuilt on every `validate` run)
CREATE TABLE IF NOT EXISTS validation_finding (
  finding_id  TEXT PRIMARY KEY,
  check_name  TEXT NOT NULL,           -- required_attr|enum|cardinality|ref|conflict|unresolved
  severity    TEXT NOT NULL,           -- ERROR|WARN|INFO
  subject_id  TEXT REFERENCES object(object_id),
  predicate   TEXT,
  fact_ids    TEXT,                    -- JSON array
  message     TEXT NOT NULL,
  produced_at TEXT NOT NULL
);
