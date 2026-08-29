# Schema Gaps

Issues discovered while implementing Phase 1 (Steps 1–3 + minimal
persistence) of the runtime. Each entry is classified:

- **ONTOLOGY_INCONSISTENCY** — the source files disagree with each
  other or with themselves in a way a machine cannot silently resolve.
- **ONTOLOGY_AMBIGUITY** — the ontology is internally consistent but
  under-specifies a modelling decision the runtime has to make.
- **RUNTIME_DESIGN_ISSUE** — a decision the runtime had to take
  because the ontology's serialization is imperfect; the ontology
  itself may be sound.

Every runtime workaround listed here is deterministic, disclosed, and
narrow. None reshapes the ontology's semantics.

---

## G1. `Party` referenced but not defined — ONTOLOGY_INCONSISTENCY

**Location.**
[03_attributes.csv](../03_attributes.csv):157 —
`Document,author_party_ref,ref(Party),,N,derived,map by document_kind,INFERRED_HIGH`

**Problem.** `Party` is not one of the 45 entities declared in
[03_entities.csv](../03_entities.csv) or
[03_ontology_v0.1.json](../03_ontology_v0.1.json). Six candidate
supertypes exist and are all treated as parties in practice: `Brand`,
`VendorImporter`, `SourcingTradingCompany`, `Factory`,
`Subcontractor`, `MerchandiserPerson`. The ontology seems to intend
`Party` as an abstract role covering these six, but never declares it.

**Runtime resolution.** The loader treats `Party` as a documented
polymorphic marker
([runtime/ontology/types.py::POLYMORPHIC_MARKERS](ontology/types.py)),
identical to how `any` / `any_execution_entity` / `any_attribute`
are treated. Attribute-ref validation therefore does not fail on
`ref(Party)`.

**Recommended ontology fix.** Either
(a) declare `Party` as an abstract entity in
[03_entities.csv](../03_entities.csv) and
[03_ontology_v0.1.json](../03_ontology_v0.1.json), listing the six
concrete party entities as its subtypes; or
(b) change `Document.author_party_ref` to `ref(any)`, matching how
`StageEvent.affects` handles polymorphism.

---

## G2. `StageEvent.event_type` enum body is descriptive — ONTOLOGY_INCONSISTENCY

**Location.**
[03_attributes.csv](../03_attributes.csv):146 —
`StageEvent,event_type,enum(17 event types),...`

**Problem.** The `type` column is written as human-readable prose,
not as a machine-parseable enum body. The 17 event types themselves
live in [03_ontology_v0.1.json](../03_ontology_v0.1.json) at
`entities[…].event_type_enum` on the StageEvent entity.

**Runtime resolution.** The loader's attribute parser, on failing to
parse an `enum(…)` body, consults the JSON for a matching `<attr>_enum`
key on the same entity. If present, that list is used as the enum's
values. This is a deterministic reconciliation between the CSV and
JSON, disclosed here and warned in
[runtime/ontology/loader.py](ontology/loader.py). This mechanism also
covers `role_enum`, `price_type_enum`, `label_type_enum`,
`state_enum` — all supplementary enums the JSON supplies but the CSV
does not.

**Recommended ontology fix.** Write the 17 event types out in the
CSV's `type` column: `enum(QuoteIssued|OrderBooked|…|InvoiceIssued)`.
Keep the JSON list as a duplicate or delete it.

---

## G3. `StageDeadline.event_type` has no declared enum — ONTOLOGY_AMBIGUITY

**Location.**
[03_ontology_v0.1.json](../03_ontology_v0.1.json) — `StageDeadline`
does not carry an `event_type_enum`;
[03_event_model.md](../03_event_model.md) uses ad-hoc names like
`ContractDelivery_DEADLINE`, `DyeCompletion_DEADLINE`,
`CuttingCompletion_DEADLINE`.

**Problem.** The naming convention `<Base>_DEADLINE` is stated in
[03_event_model.md](../03_event_model.md) §1 but never enumerated.
Deadline events therefore have no canonical name set.

**Runtime resolution.** `OntologyRegistry.get_event_type(name)`
accepts any name of the form `<base>_DEADLINE` where `<base>` is one of
the 17 declared event types, returning a synthetic `EventType(name,
is_deadline=True)`. This makes deadline validation checkable without
inventing a new enum.

**Recommended ontology fix.** Enumerate the deadline event types
explicitly, or declare `StageDeadline.event_type` as free-form text
so the ambiguity is honest.

---

## G4. `03_entities.csv` row 6 is missing `primary_identifier` — ONTOLOGY_INCONSISTENCY

**Location.**
[03_entities.csv](../03_entities.csv):6 — the `Subcontractor` row has
seven fields; the header declares eight. The missing column is
`primary_identifier`.
[03_ontology_v0.1.json](../03_ontology_v0.1.json) does supply
`"primary_identifier":"composite"` for this entity.

**Runtime resolution.** When an entities CSV row is one column short,
the loader inspects the entity's JSON record. If the JSON has a value
for the missing header, it is backfilled with a warning. Disclosed;
narrow (only applies when JSON positively supplies the missing value).

**Recommended ontology fix.** Add a `composite` value to the
`primary_identifier` column in
[03_entities.csv](../03_entities.csv):6.

---

## G5. `03_attributes.csv` row 119 is missing a column — ONTOLOGY_INCONSISTENCY

**Location.**
[03_attributes.csv](../03_attributes.csv):119 —
`PackingJob,state,enum(PLANNED|REVISED|ACTUAL),,Y,D10 populated → ACTUAL,OBSERVED` has seven fields; the header declares eight.

**Problem.** Either `normalization_rule` or `source_fields` is
omitted, and the CSV format itself cannot say which.

**Runtime resolution.** For attribute rows that come in one column
short, the loader inserts an empty string at the position of the
declared tolerant column (`normalization_rule`). Deterministic;
disclosed here.

**Recommended ontology fix.** Fill in the missing cell so the row has
eight columns.

---

## G6. Unquoted commas inside regex normalisation rules — ONTOLOGY_INCONSISTENCY

**Locations.**
[03_attributes.csv](../03_attributes.csv):16 —
`normalization_rule` = `regex [A-Z]{3}\d{2}[A-Z]\d-\d{3}[A-Z]{2\,3}`
(uses `\,` as an ad-hoc escape).
[03_attributes.csv](../03_attributes.csv):58 —
`normalization_rule` = `regex \d{2,3}S` (bare comma inside a regex
quantifier).

**Problem.** Bare commas inside unquoted CSV fields break the CSV
format. Line 16 attempts to escape with `\,`, which is non-standard;
line 58 does not escape at all.

**Runtime resolution.**
- `\,` is unescaped to `,` before csv parsing.
- Column-count overflow (when a row's field count exceeds the header)
  is folded back into a declared tolerant column
  (`normalization_rule`). Both rules are deterministic and disclosed
  in [runtime/ontology/loader.py](ontology/loader.py).

**Recommended ontology fix.** Quote the affected fields with
double-quotes per RFC 4180. Both rows would then be legal CSV.

---

## G7. Attribute-scoped ref target — ONTOLOGY_AMBIGUITY

**Location.**
[03_attributes.csv](../03_attributes.csv):103 —
`DyeLot,swatch_code_ref,ref(ColorSpecification.swatch_code),...`

**Problem.** All other refs point at an entity; only this one points
at an entity's specific attribute. It is unclear whether this means
"a value equal to some ColorSpecification's swatch_code" (a foreign
key on a non-key attribute) or "a reference to the ColorSpecification
object identified by that swatch_code" (an ordinary object ref).

**Runtime resolution.** The loader accepts `ref(X.attr)` and reduces
it to `ref(X)` for entity-existence validation, but preserves the
original text on the AttributeType so downstream code can decide.

**Recommended ontology fix.** Pick one semantics. Either drop the
`.swatch_code` suffix (making it an object ref), or introduce a
first-class `Swatch` entity whose primary_identifier is `swatch_code`
and point at that.

---

## G8. CSV-vs-JSON drift on polymorphic markers — ONTOLOGY_INCONSISTENCY

**Locations.**
[03_relationships.csv](../03_relationships.csv):66 —
`StageEvent,affects,{various},...` vs.
[03_ontology_v0.1.json](../03_ontology_v0.1.json) — `"object":"any"`.
Similar drift for
`StageDeadline.deadline_for` (`{Fabric|Cutting|Embroidery|Sewing|Ship}`
vs. `any_execution_entity`) and `Provenance.of_fact` (`{any attribute}`
vs. `any_attribute`).

**Runtime resolution.** All curly-brace-wrapped values are recognised
as polymorphic markers regardless of content. Three warnings are
emitted on load; the CSV rows are treated as canonical.

**Recommended ontology fix.** Align the CSV and JSON on a single
polymorphic vocabulary. `any` alone is enough; the constrained set
in the `deadline_for` shorthand can move into a comment.

---

## G9. Entity `layer` field missing from CSV — RUNTIME_DESIGN_ISSUE

[03_ontology_v0.1.json](../03_ontology_v0.1.json) carries a `layer`
key on each entity (`L1_party` etc.); the CSV omits it. `Entity.layer`
is exposed but empty for CSV-only loads. Not a defect — just a note
that layer is a JSON-only fact.

---

## G10. Composite `primary_identifier` is opaque — ONTOLOGY_AMBIGUITY

Many entities declare `primary_identifier: composite` without listing
the ordered field tuple. `object_id` accepts a tuple in caller-defined
order, so ingest is responsible for consistency. Not a runtime
blocker, but every composite-keyed entity needs a documented tuple
before real ingest to avoid caller drift.

Affected entities:
`Subcontractor`, `Contract`, `StyleOrder`, `PricingLine`, `Price`,
`ColorSpecification`, `FabricSpecification`, `MaterialComponent`,
`EmbroiderySpecification`, `LabelSpecification`,
`PackagingSpecification`, `TestingRequirement`, `MaterialRequirement`,
`YarnRequirement`, `KnittingPlan`, `FabricBatch`, `CuttingPlan`,
`EmbroideryJob`, `SewingJob`, `PackingJob`, `Shipment`, `Invoice`,
`SizeAllocation`, `CartonAllocation`, `Carton`, `UPC`, `StageEvent`,
`StageDeadline`, `Provenance`, `FactoryStyleRevision`, `Size`.

---

## Summary

| Class | Count |
|---|---|
| ONTOLOGY_INCONSISTENCY | 6 (G1, G2, G4, G5, G6, G8) |
| ONTOLOGY_AMBIGUITY | 3 (G3, G7, G10) |
| RUNTIME_DESIGN_ISSUE | 1 (G9) |

**Runtime status.** The ontology loads successfully in the
runtime substrate. Every workaround here is deterministic, narrow,
and disclosed; none silently changes the ontology's meaning. Two
gaps (G1, G7) touch semantics and must be resolved before ingest can
be trusted; the rest are hygiene fixes to the source files.
