# 03 — Unresolved Ontology Decisions (carried forward from v0.1)

Each item is grounded in specific evidence. None are speculative. Ranked into three categories per instruction:

- **NEEDS_DOMAIN_EXPERT** — someone at 润悦 must answer; evidence alone cannot decide.
- **NEEDS_MORE_ORDER_EXAMPLES** — the current case + F1 register is not enough; more style dossiers would settle it.
- **PURE_MODELLING_DECISION** — the evidence is clear enough; the answer is a design choice we can make with the user.

---

## NEEDS_DOMAIN_EXPERT

### DE-1. Scope of `DyeLot` (`批号`)
- **Evidence**: Batch `524` appears in D7 and D8 for this case only, tied to fabric `32S CVC 60/40 竹节汗布 170G` and colour `26C12344-D`.
- **Question**: Is a 批号 always specific to (fabric, colour) — one batch per dye run per style — or can one batch serve multiple styles that share fabric+colour?
- **Impact**: attaches `DyeLot` to `FabricBatch` × `ColorSpec` (fabric-family scope) vs `StyleOrder` (order scope). Also decides whether `批号` is a globally-unique identifier or scoped.

### DE-2. `PurchaseOrder` issuer
- **Evidence**: D9 has PO numbers `728274 / 728275`; D2's `CUSTOMER PO#` slot is `待定`.
- **Question**: Who actually issues these POs — Lane Bryant, BCI Brands, or 锦秀?
- **Impact**: `PurchaseOrder issued_by` predicate object (Brand / VendorImporter / SourcingTradingCompany).

### DE-3. Which price is "committed" under revisions
- **Evidence**: For this case, quoted 28.5 → target 27 → booked 28.0. Booked ≠ quoted ≠ target.
- **Question**: When quoted and target differ, which becomes the customer-facing committed price? Is `booked_price` always the invoiceable price?
- **Impact**: Whether `Price.price_type = booked` is always the settle price, and how to model quote revisions.

### DE-4. `SizeScheme` attachment
- **Evidence**: `LB_PLUS_10_TO_40` used for LB M7797; `STANDARD_XS_XXL` used for the other style (`DNL14R6-410SM` in F3 template).
- **Question**: Is the size scheme chosen by Brand (LB always plus), by Program, by Style, or by Order?
- **Impact**: attachment level for `sized_by`.

### DE-5. Wastage rule in `CuttingPlan`
- **Evidence**: D8 shows planned_cut / planned_ship ≈ 1.040 for larger counts but rises to 1.166 for tiny counts (18 → 21).
- **Question**: Is wastage a flat % with an integer floor, or size-specific rules, or per-embroidery-availability?
- **Impact**: derivation of `wastage_pct_by_size` and whether we can regenerate `planned_cut_qty_by_size` from other fields.

### DE-6. Testing lifecycle
- **Evidence**: D2 `测试要求 = 大货测试要求：（BV测试公司）...`. No test result observed anywhere.
- **Question**: Where do BV test results live — in an external portal, another workbook, PDFs? Is there a test-result event we should model?
- **Impact**: whether to add `TestingResult` entity and `TestSubmitted / TestPassed / TestFailed` events.

### DE-7. Handler person 郁建东
- **Evidence**: D1 status text `5/22 郁建东发货`. Elsewhere `10/10(郁建东做)名苑发货`.
- **Question**: Is 郁建东 a CMT operator, a shipping handler, both roles, or a warehouse coordinator?
- **Impact**: whether `Shipment.handler_person` and `SewingJob.operator_person` collapse or stay distinct.

### DE-8. Art-family code `997XLB`
- **Evidence**: `.ai` = `997X Football sequins EMB.ai`; `.dxf` = `997XLB(FBB54S2-388ELB).dxf`; art brief `画稿 = 997X`; factory style `FBB54S2-997XLB`. Four artifacts share the `997X(LB)` substring.
- **Question**: Is `997XLB` a factory-family code that groups art master + cut pattern + FactoryStyle revisions?
- **Impact**: adds a `StyleFamily` entity if yes.

### DE-9. Wash step semantics for `不水洗`
- **Evidence**: D0 `克重 = 不水洗`; D2 `大货不需要水洗`.
- **Question**: For styles marked `不水洗`, do we still instantiate a Wash step in the pipeline (with status CANCELLED) or omit it entirely?
- **Impact**: whether Wash is a conditional stage or a normal stage that can be marked N/A.

### DE-10. Compliance flags scope
- **Evidence**: D5 header baked-in `/不含新疆棉`. Cotton certification (BCI) implied by vendor name.
- **Question**: Are `不含新疆棉` / `BCI cotton` compliance flags per-style, per-program, or per-brand?
- **Impact**: attachment level for compliance list.

---

## NEEDS_MORE_ORDER_EXAMPLES

### MO-1. `StoreStyle ↔ FactoryStyle` cardinality
- **Evidence**: 1↔1 in this case. A2 filename references superseded factory code `FBB54S2-388ELB` while current is `FBB54S2-997XLB` under the same store style `1152246`.
- **Question**: Is 1↔N (store style has revisions of factory style) a common pattern, or a one-off?
- **Impact**: whether `FactoryStyleRevision` is mandatory. See U-1.

### MO-2. Party assignment scope (锦秀 ↔ 名苑 pairing)
- **Evidence**: All 4 styles in this program use 锦秀 + 名苑. F1 shows the same pair on many orders.
- **Question**: Does 锦秀 sourcing always route through 名苑, or does the pairing vary per program or per order?
- **Impact**: whether Subcontractor(CMT) attaches to Program or to StyleOrder.

### MO-3. `PricingLine` bracket enumeration
- **Evidence**: 2 brackets here (`regular`, `plus_size_premium`). D0 hints there could be more (e.g. weight-based or process-based brackets).
- **Question**: Is there a stable enumeration of pricing brackets, or is it emergent per style?
- **Impact**: enum vs open text for `pricing_bracket`.

### MO-4. Program cardinality upstream
- **Evidence**: M7797 for LB; F1 shows others (M5747, M7528, M7743, M7866).
- **Question**: Does a Program always belong to one Brand+VendorImporter, or can it span?
- **Impact**: multiplicity on `Program.for_brand` and `initiated_by`.

### MO-5. Whether one `StyleOrder` can span multiple `DyeLot`s
- **Evidence**: This case: 1 style-order = 1 dye lot. But if fabric is reordered mid-production (e.g. shortfall), multiple lots per order are plausible.
- **Question**: Should `StyleOrder → DyeLot` be 1..1 or 1..N?
- **Impact**: cardinality on `CuttingPlan.consumes_dyelot`.

### MO-6. Multiple colours per `StyleOrder`
- **Evidence**: This case: 1 colour per style-order. D2 tabs are one colour per store style. But nothing prohibits multi-colour orders in F1 rows.
- **Question**: Can one `StyleOrder` carry multiple colours, or is one order always mono-colour?
- **Impact**: cardinality on `StyleOrder → ColorSpecification` (currently 1..1).

### MO-7. Whether `StageDeadline` count varies by document
- **Evidence**: For this case: 3 deadlines (contract 4/20, dye 4/25, cut 5/7). Some styles may have more (embroidery deadline, sewing deadline).
- **Question**: Is there a full deadline set per stage that some orders record and others don't?
- **Impact**: completeness expectations for the deadline catalog.

---

## PURE_MODELLING_DECISION

### MD-1. Colour natural key (U-6)
- **Options**: (a) `swatch_code` primary — most technically precise; (b) `buyer_color_name` primary — most stable across buyer-facing docs; (c) composite `(store_style_code, buyer_color_name)` — no single global key.
- **Recommendation** (deferred): (c) — matches how the data actually appears; retrieval joins on all four names.

### MD-2. Program-as-entity vs Program-as-tag (U-7)
- Currently first-class per M6.
- **Options**: keep first-class, or downgrade to a `program_code` tag on `StoreStyle` and `Contract`.
- **Recommendation** (deferred): keep first-class because it has an `initiated_by`, `for_brand`, and lifecycle-anchoring role.

### MD-3. Delivery-date revision representation (U-9)
- **Options**: (a) mutable `delivery_date` on `Shipment` (loses history); (b) event log (`ContractDelivery_DEADLINE` + `ShipmentCompleted`) with `Δdays`; (c) both `contract_delivery_date` and `expected_delivery_date` attributes plus event log.
- **Recommendation**: (b) alone — attributes duplicate what events carry.

### MD-4. Collapse `FabricBatch` into `KnittingPlan` (U-10)
- Evidence for a distinct `FabricBatch` entity is thin (INFERRED_LOW). Options: collapse now, or keep as placeholder until multi-batch orders appear.
- **Recommendation** (deferred): collapse for v0.1; re-introduce when evidence requires.

### MD-5. Where `packing_mode` attaches
- Currently on `PurchaseOrder` (D9 records it per PO) and echoed on `PackingJob`. Duplication.
- **Recommendation** (deferred): PO owns it; PackingJob dereferences.

### MD-6. Whether `Subcontractor` uses subtypes or a single role attribute
- Currently one entity with `role` enum. Alternative: subtypes `CMTSubcontractor`, `KnitSubcontractor`, etc.
- **Recommendation** (deferred): keep single entity + role — simpler; only branch on subtypes if attributes diverge (e.g. knit-vs-CMT-specific fields).

### MD-7. `Provenance` granularity
- Currently one Provenance per fact. Alternative: one per document handoff (multi-fact bundling).
- **Recommendation** (deferred): keep per-fact — allows selective re-extraction.

### MD-8. Where `raw_variants[]` lives (e.g. name spellings)
- Currently on the entity (e.g. `Subcontractor.raw_variants = [名苑, 茗苑]`). Alternative: a separate `NameAlias` entity.
- **Recommendation** (deferred): keep on entity for v0.1; promote to `NameAlias` only if raw variants need their own provenance.

---

## Reading list carried over from step 02

Two case-level questions still relevant here but ranked as ontology-neutral:

- P0-9 (case): factory-style revision (`388ELB` ↔ `997XLB`) → MO-1 above.
- P0-5 (case): PO placement → DE-2 above.

---

## Summary count

- NEEDS_DOMAIN_EXPERT: 10 items.
- NEEDS_MORE_ORDER_EXAMPLES: 7 items.
- PURE_MODELLING_DECISION: 8 items.

None are blockers for using v0.1 as an integration surface; all are candidates to resolve before publishing v1.0.
