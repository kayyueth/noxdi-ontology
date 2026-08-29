# Runtime Architecture — v0

Executable substrate for ontology v0.1. Sized for **one case**
(`FBB54S2-997XLB / 1152246 / M7797 / Lane Bryant`), 10 structured docs
(D0–D10) plus 8 attachments (A1–A8).

Success criterion: after loading the case, the runtime can reconstruct
the timeline in [02_case_lifecycle.md](../02_case_lifecycle.md) and the
cross-doc reconciliations in
[02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv) from
its own storage, without re-reading the source spreadsheets.

## Non-goals

- No dashboard, no UI, no agents, no LLM extraction. Extraction is
  hand-authored JSON per document; the runtime treats those as the
  input surface.
- No production concerns: no auth, no multi-tenant, no migrations
  beyond `schema_version`, no distributed anything.
- The runtime does not reshape the ontology to be easier to execute.
  When the ontology is inconvenient (composite grains, coexisting
  variant names, revisions), the runtime absorbs the inconvenience.

## Shape

A single-process Python 3.11+ program over a single SQLite file, driven
by a CLI. Everything the runtime knows lives in one directory:

```
runtime/
  schema/               # ontology loaded into memory at startup
    entities.py         # parsed from ../03_entities.csv
    attributes.py       # parsed from ../03_attributes.csv
    relationships.py    # parsed from ../03_relationships.csv
    events.py           # parsed from ../03_event_model.md event catalog
  store/
    db.py               # SQLite open/close, migrations
    schema.sql          # 6 tables (see §Storage)
  ingest/
    documents.py        # register D0..D10, A1..A8 as Document objects
    facts.py            # load per-document extraction JSON → facts
    resolver.py         # entity resolution (aliases, canonicalisation)
  validate/
    checks.py           # required / enum / cardinality / ref / conflict
  query/
    reconstruct.py      # timeline, source-of-truth matrix, per-object view
  cli.py                # `python -m runtime <command>`
fixtures/
  documents/            # metadata for each D#/A# (path, kind, date, author)
  extractions/          # one JSON per document — hand-authored, cell-anchored
  aliases.json          # 茗苑→名苑, 锦秀公司→锦秀, etc.
  case.db               # SQLite output; regenerable from fixtures
```

Justification for these choices, briefly:

- **SQLite over Postgres / a graph DB.** One case, one file, one
  process. SQL is enough for the queries we need. A graph DB would add
  operations without adding capability at this scale — we simulate
  graph traversal with recursive CTEs.
- **Python.** The ontology CSVs and the extraction JSONs need to be
  parsed and cross-checked; Python's stdlib does that with no
  dependencies beyond `sqlite3`, `csv`, `json`, `pathlib`.
- **Hand-authored extractions.** The task says do not optimise LLM
  extraction. Extractions are the input format, not something the
  runtime produces. Each `fixtures/extractions/D5.json` records the
  cells the human (or a later extractor) read and the facts they yield,
  with cell addresses. This lets us test the ontology-side of the
  system in isolation.

## Storage — six tables

Everything the runtime persists is one of these six shapes. Nothing
lives outside them; there are no ORM classes with hidden state.

```sql
-- 1. every entity instance in the graph
CREATE TABLE object (
  object_id       TEXT PRIMARY KEY,       -- deterministic hash (see §IDs)
  entity_type     TEXT NOT NULL,          -- e.g. 'FactoryStyle'
  natural_key     TEXT NOT NULL,          -- canonical form of primary_identifier
  created_from    TEXT NOT NULL,          -- Document.object_id of first sighting
  created_at      TEXT NOT NULL           -- ISO timestamp
);
CREATE INDEX object_type_key ON object(entity_type, natural_key);

-- 2. every atomic assertion about an object.  Attribute values AND
--    relationship endpoints are both 'facts' — a relationship is a
--    fact whose value is a ref(object_id).
CREATE TABLE fact (
  fact_id         TEXT PRIMARY KEY,
  subject_id      TEXT NOT NULL REFERENCES object(object_id),
  predicate       TEXT NOT NULL,          -- attribute or relationship name
  value_kind      TEXT NOT NULL,          -- text|int|dec|date|bool|enum|ref|null
  value_text      TEXT,                   -- populated per value_kind
  value_num       REAL,
  value_date      TEXT,                   -- ISO date
  value_ref       TEXT REFERENCES object(object_id),
  raw_value       TEXT,                   -- pre-normalisation source text
  status          TEXT NOT NULL,          -- OBSERVED|INFERRED_HIGH|INFERRED_LOW
                                          -- |UNRESOLVED|CONFLICT
  variant_group   TEXT,                   -- groups co-existing values (§Variants)
  supersedes      TEXT REFERENCES fact(fact_id),   -- revision chain
  is_current      INTEGER NOT NULL DEFAULT 1,
  observed_at     TEXT NOT NULL,          -- when we recorded it
  reason          TEXT                    -- unresolved reason / conflict note
);
CREATE INDEX fact_subj_pred ON fact(subject_id, predicate);
CREATE INDEX fact_current   ON fact(subject_id, predicate) WHERE is_current=1;

-- 3. provenance per fact (1..N: a fact can be attested by multiple docs
--    — that is how we detect a conflict vs a corroboration)
CREATE TABLE provenance (
  provenance_id       TEXT PRIMARY KEY,
  fact_id             TEXT NOT NULL REFERENCES fact(fact_id),
  document_id         TEXT NOT NULL REFERENCES object(object_id), -- Document object
  source_sheet        TEXT,
  source_location     TEXT,               -- cell address / row/col / footer
  extraction_method   TEXT NOT NULL,      -- direct|regex|parse|manual
  document_date       TEXT,
  confidence          TEXT NOT NULL       -- OBSERVED|INFERRED_HIGH|INFERRED_LOW
);
CREATE INDEX prov_fact ON provenance(fact_id);

-- 4. events are objects (entity_type='StageEvent' or 'StageDeadline')
--    but need one denormalised row for timeline queries
CREATE TABLE event_index (
  event_id            TEXT PRIMARY KEY REFERENCES object(object_id),
  event_type          TEXT NOT NULL,      -- one of the 17 catalog values
  affected_object_id  TEXT REFERENCES object(object_id),
  planned_date        TEXT,
  actual_date         TEXT,
  status              TEXT NOT NULL       -- PLANNED|IN_PROGRESS|DONE|REVISED|CANCELLED
);

-- 5. alias table for entity resolution
CREATE TABLE alias (
  entity_type   TEXT NOT NULL,
  variant       TEXT NOT NULL,
  canonical     TEXT NOT NULL,
  reason        TEXT,                     -- 'C3 name normalization', etc.
  PRIMARY KEY(entity_type, variant)
);

-- 6. validation report (rebuilt on every validate run)
CREATE TABLE validation_finding (
  finding_id    TEXT PRIMARY KEY,
  check_name    TEXT NOT NULL,            -- 'required_attr'|'enum'|'cardinality'|'ref'|'conflict'
  severity      TEXT NOT NULL,            -- ERROR|WARN|INFO
  subject_id    TEXT REFERENCES object(object_id),
  predicate     TEXT,
  fact_ids      TEXT,                     -- JSON array
  message       TEXT NOT NULL,
  produced_at   TEXT NOT NULL
);
```

## The five required capabilities, mapped to storage

| Capability | Where it lives |
|---|---|
| **Object** | `object` table. One row per entity instance. `entity_type` cross-checks against the ontology's entity catalog. |
| **Relationship** | `fact` rows with `value_kind='ref'`, `value_ref` pointing at another object. No separate relationship table — a relationship *is* an attribute whose value is a ref. This lets the same provenance mechanism cover both. |
| **Attribute / State** | `fact` rows with a scalar `value_kind`. State transitions (e.g. `KnittingPlan.state = PLANNED → ACTUAL`) are new facts that `supersedes` the earlier one; both remain queryable, only one has `is_current=1`. |
| **Event** | `object` (`entity_type='StageEvent'` or `'StageDeadline'`) + `event_index` for fast timeline queries. `affected_object_ref` is a `fact` row like any other relationship. |
| **Provenance** | `provenance` table, keyed on `fact_id`. A fact with two provenance rows from D0 and D2 is a corroboration; the same fact with two different values across two docs is a conflict (see §Conflicts). |

## Object IDs

Stable, deterministic, human-decipherable when possible:

```
object_id = f"{entity_type}:{sha1(canonical_natural_key)[:12]}"
```

- `entity_type` is the ontology name (e.g. `FactoryStyle`,
  `StoreStyle`, `StageEvent`).
- `canonical_natural_key` is the entity's `primary_identifier` after
  alias resolution and normalisation (uppercased for codes,
  whitespace-collapsed for names). For composite keys we join fields
  with `|` in the order the ontology declares.

Example:
- `FactoryStyle:e3f9…` for `FBB54S2-997XLB`
- `Subcontractor:a17c…` for `名苑|CMT` (composite of name + role, per
  ontology grain).
- `StageEvent:9b02…` for `(event_type=ShipmentCompleted,
  affected_object=Shipment#…, source=D1)`.

Determinism means re-ingesting the same fixtures produces the same
graph; a diff of `case.db` after re-ingest should be empty.

## Fact-level provenance

The provenance schema in the ontology attaches to *every normalised
attribute*, not to the object as a whole. The storage mirrors that:
one `fact` row = one atomic assertion, one or more `provenance` rows
= where we saw it.

Two consequences:

1. When D0 and D2 both say `product_type = T恤` and D8 says `女式T恤`,
   the runtime holds **two facts** (`T恤` and `女式T恤`) in the same
   `variant_group`, each with its own provenance rows. Source-of-truth
   selection (per
   [02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv))
   marks one `is_current=1`; the others remain queryable.
2. When D0 quotes `28.5` and D1 books `28`, both facts are held —
   distinguished by their `Price.price_type` enum (`quoted` vs
   `booked`). This is a *different-fact-same-object* case, not a
   conflict.

## Variants (coexisting values)

The `ColorSpecification` entity has four coexisting names
(`buyer_color_name`, `factory_color_name`, `swatch_code`,
`raw_color_text`). The ontology says none is universal (M5). Encoded
as four facts on the same `ColorSpecification` object with distinct
predicates. `variant_group` is used when the *same predicate* has
multiple accepted values — e.g. `Subcontractor.subcontractor_name`
has `raw_variants=['名苑','茗苑']`; both facts are stored, both
provenance-tracked, and `is_current=1` on the canonical spelling.

## Revisions

The ontology's example is delivery date: D2 says 4/20,
D1 says 5/22 (revision), D1 status text records 5/22 as actual ship.
Encoded as:

- `Contract.contract_delivery_date` fact valued `2026-04-20`, provenance D2.
- `StyleOrder.expected_delivery_date` fact valued `2026-05-22`,
  provenance D1, `supersedes` NULL (they are different predicates on
  different objects, per M3).
- `StageEvent(event_type=ShipmentCompleted).actual_date = 2026-05-22`
  and `StageDeadline(event_type=ContractDelivery_DEADLINE).planned_date
  = 2026-04-20`.

`supersedes` is reserved for the case where the *same* (subject,
predicate) legitimately changes value under a later document — e.g. a
plan revision. The runtime never overwrites; every version is kept
and only `is_current` flips.

## Unresolved values

Facts with `status='UNRESOLVED'` and `value_kind='null'` carry the
ontology's `U-#` identifier in `reason`. Example: for this case
`PurchaseOrder.issued_by = ?` is stored as an UNRESOLVED fact with
`reason='U-5: PO issuer'`. Queries default to excluding UNRESOLVED
facts; validation reports them as INFO.

`FabricBatch` under U-10 is handled by allowing an entity to be marked
`optional` in the ontology loader. If the ingest for this case never
creates a `FabricBatch`, that is not a validation error — but the
`KnittingPlan.produces_greige` relationship carries an UNRESOLVED
placeholder fact rather than being silently absent.

## Conflicts

Two facts on the same (subject, predicate) with the same
`variant_group` but different values are a **conflict**. Detection is
a validation check, not an ingest-time rule: ingest is permissive so
we can see the raw disagreement.

Resolution rule for v0:
- Consult
  [02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv) —
  loaded as an in-memory table keyed by ontology attribute name.
- The document listed as `source_of_truth` wins; its fact gets
  `is_current=1` and `status=OBSERVED`; the loser gets
  `is_current=0` and `status='CONFLICT'` with `reason` pointing at
  the matrix row.
- If the attribute is not in the matrix, both facts remain
  `is_current=1` and a WARN finding is written.

Example: `product_type` = `T恤` (D2, canonical) vs `女式T恤` (D8, WIN
under matrix "revision — progressive enrichment") vs `女式T` (D10,
truncation). Runtime holds all three; matrix selects one as current.

## Entity resolution

Three tiers, in order:

1. **Exact match on canonical natural key.** After
   normalisation (uppercase codes, whitespace collapse), if the key
   already exists in `object`, reuse it.
2. **Alias table.** `茗苑 → 名苑`, `锦秀公司 → 锦秀`, etc. Populated
   from
   [02_corrections.md](../02_corrections.md) §C3 into
   `fixtures/aliases.json`. Applied before step 1.
3. **Composite-key match.** For entities whose primary_identifier is
   composite, the resolver hashes the tuple in ontology-declared field
   order. No fuzzy matching in v0 — every alias is explicit.

Everything the resolver does is logged; ingest is re-runnable and
inspectable.

## Validation checks (v0)

Six checks, each returns findings into `validation_finding`:

1. **required_attribute** — every fact whose ontology entry has
   `required=Y` must exist on every object of that entity type.
2. **enum** — facts whose ontology attribute declares an enum must
   have a value from that enum.
3. **cardinality** — for each relationship, count `fact_ref` rows per
   subject and verify against the relationship's `cardinality`
   (`1..1`, `1..N`, `0..1`, `0..N`).
4. **ref_integrity** — every `value_ref` points at an existing object,
   and the target object's `entity_type` matches the relationship's
   `object` type.
5. **conflict** — as §Conflicts.
6. **unresolved** — every ontology `U-#` slot that applies to this
   case has either a resolved fact or an UNRESOLVED fact recording
   the U-# id.

Findings are advisory. `validate` never mutates `fact` or `object`;
it only writes to `validation_finding`.

## The extraction interface

Each document under `fixtures/extractions/` looks like this
(illustrative, D2 sheet `1152246`):

```json
{
  "document_id": "Document:d2_m7797_myuan_contract",
  "facts": [
    { "subject_ref": {"entity_type":"Brand","natural_key":"Lane Bryant"},
      "predicate": "brand_name",
      "value": "Lane Bryant",
      "raw_value": "Lane Bryant",
      "source_sheet": "1152246",
      "source_location": "商店",
      "extraction_method": "direct",
      "confidence": "OBSERVED" },
    { "subject_ref": {"entity_type":"VendorImporter","natural_key":"BCI Brands"},
      "predicate": "vendor_name",
      "value": "BCI Brands",
      "raw_value": "BCI",
      "source_sheet": "1152246",
      "source_location": "客户",
      "extraction_method": "manual",
      "confidence": "OBSERVED",
      "note": "C7: BCI = BCI Brands, expanded via alias" }
  ]
}
```

Whoever authors this file (human, spreadsheet parser, or later an
LLM) is doing the extraction; the runtime is *not* doing extraction.
This keeps ingest deterministic and reviewable, and keeps the
ontology's fidelity to source cells first-class.

## CLI surface

```
python -m runtime init                           # create empty case.db, load ontology
python -m runtime load-documents                 # register D0..D10, A1..A8
python -m runtime load-aliases                   # populate alias table
python -m runtime ingest fixtures/extractions/*  # write facts + provenance
python -m runtime resolve-conflicts              # apply source-of-truth matrix
python -m runtime validate                       # write validation_finding
python -m runtime query timeline                 # reconstruct 02_case_lifecycle.md §2
python -m runtime query object FactoryStyle:e3f9…
python -m runtime query facts --subject … --predicate …
python -m runtime query conflicts
python -m runtime query unresolved
python -m runtime dump                           # emit case.jsonl for review
```

## What is *not* here (and where it would go later)

- **Multi-case.** A `case_id` column on `object` would open the door;
  today, a single database is one case, and this suits the pilot.
- **State machines / event transitions.** The event model is a fact
  catalog, not a machine. v0.2 (per §6 of `03_event_model.md`) would
  add transition rules; the runtime already stores planned/actual/
  revised, so guards can be added without reshaping storage.
- **Full-text extraction.** Out of scope; the extraction interface is
  the seam. Any later extractor (parser, LLM, human) emits the same
  JSON shape.
