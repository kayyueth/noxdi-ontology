# Implementation Plan — Runtime v0

Steps are ordered so each one is independently testable and each
extends what came before. Every step names its acceptance test — a
concrete assertion runnable against the artefacts produced by that
step alone. Nothing later than "Step N test" depends on features from
"Step N+1".

Assumed layout is the one in [ARCHITECTURE.md](ARCHITECTURE.md).

**Definition of done for the whole plan:** after Steps 1–14, the CLI
can reconstruct the case timeline in
[02_case_lifecycle.md](../02_case_lifecycle.md) §2 and the
source-of-truth reconciliations in
[02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv) using
only `case.db` and the fixtures directory.

---

## Step 1 — Bootstrap: SQLite store + schema DDL

- Create `runtime/store/schema.sql` with the six tables from
  ARCHITECTURE.md §Storage.
- Create `runtime/store/db.py` with `open_db(path)` and `init_db(path)`
  that runs the DDL idempotently and stamps `schema_version = 1` in a
  `meta` table.
- Wire `python -m runtime init` to call `init_db("fixtures/case.db")`.

**Test.** After `init`, all six tables exist; running `init` twice is
a no-op; `meta.schema_version = 1`.

---

## Step 2 — Ontology loader (read-only)

- Parse [03_entities.csv](../03_entities.csv),
  [03_attributes.csv](../03_attributes.csv),
  [03_relationships.csv](../03_relationships.csv), and the event-type
  enum from [03_event_model.md](../03_event_model.md) §3 into
  Python dataclasses (`Entity`, `Attribute`, `Relationship`,
  `EventType`).
- Nothing is written to SQLite. This is a validated in-memory schema
  used by ingest and validation.
- Reject malformed rows loudly — e.g. an attribute referencing an
  unknown entity fails startup.

**Test.** `len(entities) == 30` (30 distinct entity rows including
`Document` and `Provenance`); every attribute's `entity` resolves to
an entity; every relationship's `subject`/`object` resolves; the 17
event types are parsed.

---

## Step 3 — Deterministic object IDs

- Implement `object_id(entity_type, natural_key)` per
  ARCHITECTURE.md §Object IDs (sha1[:12]).
- Implement `canonicalise(entity_type, raw_key)` that applies:
  uppercase for factory-style codes and PO numbers; whitespace
  collapse for names; join composite tuples with `|`.

**Test.** Golden fixtures: given `("FactoryStyle","FBB54S2-997XLB")`
and `("FactoryStyle"," fbb54s2-997xlb ")` produce the same ID.
`("Subcontractor",("名苑","CMT"))` produces a stable known hash.

---

## Step 4 — Document registry

- Create `fixtures/documents/documents.yaml` listing D0–D10 and A1–A8
  with `path`, `document_kind`, `document_date`, `author_party` — all
  drawn from
  [02_case_lifecycle.md](../02_case_lifecycle.md) §1.
- `runtime/ingest/documents.py` reads it and writes one `object` row
  per document (`entity_type='Document'`), plus one fact per Document
  attribute (`file_path`, `document_kind`, `document_date`,
  `author_party_ref`) with self-provenance (the fact's provenance
  document is itself; extraction_method='direct').
- Wire `python -m runtime load-documents`.

**Test.** After `init` + `load-documents`, `object` has 18 Document
rows and `fact` has ≥ 54 rows (3+ attributes × 18 docs). Each fact has
exactly one `provenance` row.

---

## Step 5 — Alias table

- Create `fixtures/aliases.json` from
  [02_corrections.md](../02_corrections.md) §"Consequence of C3":
  `茗苑→名苑`, `锦秀公司→锦秀`, `象山锦秀服饰有限公司鄞州分公司→锦秀`,
  `BCI→BCI Brands`, `LANE BRYANT→Lane Bryant`.
- `load-aliases` writes them into `alias`.

**Test.** `SELECT COUNT(*) FROM alias >= 5`. `resolver.canonical("Subcontractor","茗苑") == "名苑"`; unknown variant returns input unchanged.

---

## Step 6 — Fact ingest (single-document round-trip)

- Author `fixtures/extractions/D2.json` (just the `1152246` sheet)
  covering brand, vendor, sourcing company, contract, size scheme,
  colour, testing, delivery date. Roughly 25 facts.
- `runtime/ingest/facts.py`:
  - Reads the JSON.
  - For each fact: resolve subject via alias + `object_id`; create the
    object if new; write a `fact` row and one `provenance` row.
  - Rejects unknown predicates against the ontology attribute set for
    that entity type.
- Wire `python -m runtime ingest <path>`.

**Test.** After ingesting D2 alone: 1 Brand, 1 VendorImporter, 1
SourcingTradingCompany, 1 Contract, 1 SizeScheme, 1 ColorSpec, 1
Program object exist; every fact has provenance; querying
`fact WHERE predicate='brand_name'` returns `Lane Bryant` with
provenance pointing at D2 sheet `1152246`, cell `商店`.

---

## Step 7 — Multi-document ingest with corroboration

- Author `fixtures/extractions/D0.json`, `D1.json`, `D5.json`
  covering the same fabric spec / factory style / colour concepts.
- Ingest all three (plus D2 from Step 6). Do **not** yet run conflict
  resolution.

**Test.** `FactoryStyle:FBB54S2-997XLB` has one object row and 4
`provenance` rows on its `factory_style_code` fact (one per doc). The
fabric spec facts appear as multiple co-existing rows with the same
`(subject, predicate)` and distinct `raw_value`s — visible pre-
resolution.

---

## Step 8 — Full-case ingest (D0–D10 + A1–A8)

- Author remaining extractions: D3, D4, D6, D7, D8, D9, D10 and the
  attachment facts (art asset id from A5–A8 filenames, buyer PP from
  A1, fit report from A2).
- Grain choices to encode (from
  [03_ontology_v0.1.json](../03_ontology_v0.1.json) M1–M7):
  - Two PricingLine facts per StyleOrder (regular / plus).
  - Three Price facts per PricingLine (target / quoted / booked) —
    each with its own `price_type` enum and its own document provenance.
  - Two PurchaseOrder objects (728274, 728275) with per-size
    SizeAllocation and per-carton-range CartonAllocation.
- Some facts marked UNRESOLVED with `reason='U-5'` (PO issuer),
  `reason='U-10'` (FabricBatch scope) etc.

**Test.** Object counts match the case: 1 Program, 1 StoreStyle, 1
FactoryStyle, 1 Contract, 1 StyleOrder, 2 PricingLine, 6 Price, 2 PO,
16 SizeAllocation (8 sizes × 2 POs), ≥ 20 CartonAllocation rows, 1
DyeLot (`524`), 1 CuttingPlan, 1 SewingJob, 2 PackingJob, 1 Shipment,
1 Invoice. Total 2839 pieces balance across every level:
  ```sql
  SELECT SUM(pieces_planned) FROM fact WHERE predicate='pieces_planned'
  ```
  returns 2839 (D9 sum) and matches `Contract.contract_quantity`.

---

## Step 9 — Event materialisation

- `runtime/ingest/events.py`: for each event type in the catalog with
  evidence in this case (17 events + 3 deadlines per
  [03_event_model.md](../03_event_model.md) §3), create a `StageEvent`
  object with a fact for `event_type`, `planned_date`, `actual_date`,
  `status`, `affected_object_ref`, and one row in `event_index`.
- Events driven by parsed status text (D1 `样衣进度`, `面料进度`,
  `成衣工厂`, `开票情况`) come from `fixtures/extractions/D1_events.json`
  — hand-authored to sidestep NLP.

**Test.** `SELECT event_type, actual_date FROM event_index ORDER BY
COALESCE(actual_date, planned_date)` returns the 20-row timeline
from [03_event_model.md](../03_event_model.md) §5, in order,
including the `ContractDelivery_DEADLINE` at 2026-04-20 and
`ShipmentCompleted` at 2026-05-22.

---

## Step 10 — Validation: required, enum, cardinality, ref

Four checks first (§Validation 1–4 in ARCHITECTURE.md). Conflicts
and unresolved come in Step 12.

- Iterate objects; for each, look up its entity's attributes; verify
  every `required=Y` predicate has at least one fact.
- Enum: for each attribute whose ontology type is `enum(…)`, verify
  every fact's value is in the enum set.
- Cardinality: for each relationship, count `value_ref` facts per
  subject; verify against `1..1|0..1|1..N|0..N`.
- Ref integrity: every `value_ref` targets an existing object whose
  `entity_type` matches the relationship's object type.

**Test.** On the fully-loaded case, all four checks return zero
ERROR findings. Introduce a temporary bad fixture (drop the
`Contract.contract_delivery_date` fact); re-run: one ERROR finding
appears; restore fixture; re-run: zero.

---

## Step 11 — Query commands: object view, facts, timeline

Simple read commands, no new storage:

- `query object <object_id>` — prints the object plus every current
  fact and its provenance.
- `query facts --subject X --predicate Y` — prints all facts,
  current and superseded.
- `query timeline` — prints the event_index ordered by best-known
  date, in the format of `03_event_model.md` §5.
- `query source-of-truth <predicate>` — returns every fact for that
  predicate across the case, with source docs — the input to the
  source-of-truth matrix.

**Test.** `query timeline` output diffs against the 20-row block in
[03_event_model.md](../03_event_model.md) §5 — same events, same
dates, same statuses.

---

## Step 12 — Conflict detection + source-of-truth resolution

- Load
  [02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv)
  as an in-memory table keyed by canonical concept name.
- Map each ontology attribute to a matrix row via a hand-authored
  `fixtures/matrix_mapping.json` (e.g.
  `Product.product_type_normalized → product_type`).
- For every `(subject, predicate)` with more than one fact in the
  same `variant_group`, mark all but the matrix-winning fact as
  `is_current=0, status='CONFLICT'`.
- Predicates not in the matrix: WARN, leave both current.
- `query conflicts` prints them.
- `resolve-conflicts` is idempotent.

**Test.** Before resolve: `product_type` returns 3 co-current facts
(`T恤`, `女式T恤`, `女式T`). After resolve: one `is_current=1`, matching
the matrix decision, and `query conflicts` explains why. Restart /
re-ingest / re-resolve is a no-op.

---

## Step 13 — Unresolved-value support

- Extend `validate` with the sixth check (unresolved).
- For each U-# in the ontology's `unresolved` array that applies to
  this case (U-1, U-2, U-3, U-4, U-5, U-9, U-10, U-11 all apply),
  verify either a resolved fact exists **or** an UNRESOLVED fact with
  `reason=U-#` exists.
- `query unresolved` groups by U-#.

**Test.** After validate, every applicable U-# is accounted for.
`query unresolved` matches the U-# entries and cites the affected
object (e.g. U-5 → PurchaseOrder issuer facts).

---

## Step 14 — Reconstruction check (integration test)

The single end-to-end assertion the whole system exists to pass:

- Delete `case.db`.
- Run: `init → load-documents → load-aliases → ingest * →
  resolve-conflicts → validate`.
- Run three reconstruction queries and diff against the corresponding
  ontology-provenance docs:
  1. `query timeline` vs. [03_event_model.md](../03_event_model.md) §5.
  2. `query source-of-truth product_type` (and 5 other concepts) vs.
     the matching rows in
     [02_source_of_truth_matrix.csv](../02_source_of_truth_matrix.csv).
  3. `query object FactoryStyle:…` returns the full case's attribute
     bundle: brand, vendor chain, contract, prices (3 types × 2
     brackets), delivery dates (contract vs expected vs actual),
     dye lot 524, ship 5/22, invoice 6/3.

**Pass criterion.** Zero ERROR findings in `validation_finding`; the
three reconstruction diffs are semantically equal to their source-doc
rows (exact string equality is not required — set equality on
(concept, source_doc, value) tuples is).

---

## Notes on ordering

- Steps 1–5 build capability with no data assertions of the case; they
  are cheap and each takes < 100 LOC.
- Steps 6–8 progressively load the case. If Step 8 blows up, most of
  the fix will be in the extraction JSON, not the runtime — a
  deliberate consequence of moving extraction into the fixture layer.
- Steps 10, 12, 13 are three separate validation passes on the *same*
  storage, staged so each pass's failure mode is easy to attribute.
- Step 14 is the reconstruction validity check the task asks for. It
  fails loudly if any earlier step regressed.

## Out of scope for this plan (deliberately)

- Extraction from raw Excel / PDF. The runtime consumes JSON; anything
  upstream is a separate program.
- A second case. Multi-case would need a `case_id` column on every
  table and a small routing layer; both are trivial additions later.
- Query beyond SQL — no traversal DSL, no GraphQL, no client SDK.
- Migrations beyond `schema_version=1`. If the ontology changes shape,
  the plan restarts at Step 1 with a new version stamp.
