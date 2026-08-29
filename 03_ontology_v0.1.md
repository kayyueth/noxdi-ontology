# Ontology v0.1 — 润悦 (this factory) apparel-order model

> **Scope note (do not delete on future revisions).** This ontology is a provisional model of **how this specific factory (宁波润悦服饰有限公司) understands and operationalises an apparel order**. It is grounded in:
> - one complete style dossier: `FBB54S2-997XLB` / `1152246` / M7797 / Lane Bryant;
> - the 2026 order register (`2026年订单汇总表.xlsx`);
> - the portfolio-level quotation (`报价2026.2.2.xlsx`).
>
> It is **not** a model of the apparel industry. Case-specific structures observed once are marked PROVISIONAL. Anything unsupported by this dataset is out of scope for v0.1.

Confidence tags used throughout: **OBSERVED** / **INFERRED_HIGH** / **INFERRED_LOW**. Modelling status per element: **CONFIRMED** (post user clarifications C1–C7) / **PROVISIONAL** (evidence in ≥1 case) / **UNRESOLVED** (flagged, decision deferred).

Applied user modelling decisions M1–M7 (no universal OrderLine, three prices, three delivery dates, PO first-class, Colour multi-key, Program first-class, four decisions preserved as UNRESOLVED).

---

## 0. How to read this ontology

- Section 1 gives the six layers with entity summaries.
- Sections 2–7 walk each layer with entity definitions, key attributes, and evidence anchors.
- Section 8 covers events (also expanded in `03_event_model.md`).
- Section 9 covers provenance.
- Section 10 lists relationship families.
- Complete listings live in `03_entities.csv`, `03_relationships.csv`, `03_attributes.csv`, `03_ontology_v0.1.json`.
- Trimmed diagram in `03_ontology_graph.mermaid`.

---

## 1. Six layers at a glance

| Layer | Purpose | Entities (major only) |
|-------|---------|-----------------------|
| L1 · Party / Organisation | Who is who, in the four-tier supply chain we serve | Brand · VendorImporter · SourcingTradingCompany · Factory · Subcontractor · MerchandiserPerson |
| L2 · Commercial | The commitment side — Program, styles, price, PO | Program · StoreStyle · FactoryStyle · Contract · StyleOrder · PricingLine · Price · PurchaseOrder |
| L3 · Product specification | What the garment is | Product · ColorSpecification · SizeScheme · Size · FabricSpecification · MaterialComponent · Artwork · EmbroiderySpecification · LabelSpecification · PackagingSpecification · TestingRequirement |
| L4 · Manufacturing / execution | Planned and actual production steps | MaterialRequirement · YarnRequirement · KnittingPlan · FabricBatch · DyeLot · CuttingPlan · EmbroideryJob · SewingJob · PackingJob · Shipment · Invoice |
| L5 · Logistics / allocation | Where pieces end up | SizeAllocation · CartonAllocation · Carton |
| L6 · Events / workflow | Time-based state transitions | StageEvent (17 event types, see §8 and `03_event_model.md`) |
| Cross-cutting | Provenance | Document · Provenance |

---

## 2. Layer 1 — Party / Organisation

We model **four supply-chain tiers** and **three subcontractor roles**, with explicit named relationships rather than a generic `customer_of` predicate.

### Entities

| Entity | Definition | Primary identifier |
|--------|------------|--------------------|
| `Brand` | Retailer that sells the finished garment. **甲方** in Chinese usage. | `brand_name` (`Lane Bryant`) |
| `VendorImporter` | The brand's US-side vendor/importer. Sits between the brand and the sourcing agent. **CONFIRMED per C7**. | `vendor_name` (`BCI Brands`) |
| `SourcingTradingCompany` | The Chinese trading company that sources from us on behalf of the vendor. **乙方** vis-à-vis this factory. **CONFIRMED per C1**. | `company_short_name` (`锦秀`) |
| `Factory` | Us. `宁波润悦服饰有限公司`. **丙方**. | `factory_short_name` (`润悦`) |
| `Subcontractor` | Any downstream shop we outsource to. Has a `role ∈ {CMT, KNIT, EMBROIDERY, WASH, DYE}`. **CONFIRMED per C3**: `名苑` is the canonical spelling. | `subcontractor_name` + `role` |
| `MerchandiserPerson` | Named individual at a `SourcingTradingCompany` who owns the order end-to-end. | `person_name` |

### Relationships (named, not generic)

- `Brand served_by VendorImporter` (1..N; observed 1..1 for Lane Bryant→BCI)
- `VendorImporter sourced_through SourcingTradingCompany` (1..N)
- `SourcingTradingCompany contracts_with Factory` (1..N)
- `Factory subcontracts_to Subcontractor` (1..N, discriminated by `role`)
- `SourcingTradingCompany employs MerchandiserPerson` (1..N)

We deliberately do **not** introduce a top-level `Customer` role. The word `客户` in the source data is **tier-relative** (per C1): the same field means different tiers in different documents. In this model, the relation "my direct customer" is derived from the tier chain and not stored as a raw attribute.

### Evidence anchors
- Brand: D2 `商店 = Lane Bryant`; D6 filename.
- VendorImporter: D2 `客户 = BCI` (only place it appears).
- SourcingTradingCompany: D1 `客户`, D5–D8 `客户`, D2 header `象山锦秀服饰有限公司鄞州分公司`.
- Factory: D5–D8 document headers.
- Subcontractor: D8 `生产工厂 = 名苑` (CMT); D6/D7 `织造加工 = 林海织造` (KNIT); D8 `协作单位 = 家顺` (EMBROIDERY); D1 `水洗厂 = 红水` (WASH).
- MerchandiserPerson: D1 `客户` suffix, D3/D4 footer (`胡颖洁`).

---

## 3. Layer 2 — Commercial objects

### 3.1 Program

- **Definition**: a buyer-initiated grouping (identifier looks like `M####`) that spans several `StoreStyle`s shipped as one commercial campaign. Sits **above** styles. **PROVISIONAL first-class entity per M6**.
- **Grain**: one per buyer program code.
- **Primary identifier**: `program_code` (e.g. `M7797`).
- **Attributes**: `program_code`, `for_brand`, `initiated_by_vendor`, `first_seen_date`.
- **Evidence**: D2 `PROGRAM# = M7797` on 4 sheets; D9 covers same M7797 across 3 store styles; D1 rows 169–192 span 12 SKU-lines all tagged `M7797`.
- **Note**: In D1 the program code leaks into the `款号` free-text cell as a prefix (`M7797    FBB54S2-997XLB 1152246`). Extraction rule: regex.

### 3.2 StoreStyle

- **Definition**: the buyer's own style/SKU identifier (7-digit numeric for Lane Bryant).
- **Primary identifier**: `store_style_code` (`1152246`).
- **Attributes**: `store_style_code`, `brand`, `program`.
- **Evidence**: D2 sheet names; D3/D4/D6/D9/D10 embed it in dual cells; A1 filename.
- **Note**: In D2/D3/D4 the cell is `1152246（FBB54S2-997XLB）`; in D9/D10 it is `FBB54S2-997XLB（商店款号1152246）`. Both orderings coexist.

### 3.3 FactoryStyle

- **Definition**: our internal style code (`FBB54S2-997XLB`).
- **Primary identifier**: `factory_style_code`. Regex-extractable pattern: `[A-Z]{3}\d{2}[A-Z]\d-\d{3}[A-Z]{2,3}`.
- **Attributes**: `factory_style_code`, `product_type`, `size_scheme_ref`, `revision_of` (see UNRESOLVED-9).
- **Evidence**: D0 `STYLE`; D1 embedded; every other doc.
- **Relationship to StoreStyle**: `StoreStyle realized_as FactoryStyle` — **cardinality UNRESOLVED** (see U-1). This case shows 1↔1, but A2 references a superseded factory code `FBB54S2-388ELB` for the spec-sample sharing the same `997XLB` root — suggesting **style revisions** may share a store style. Interim: `FactoryStyle` carries an optional `revision_of` link to the prior code.

### 3.4 Contract

- **Definition**: a formal CMT purchase between the SourcingTradingCompany (as buyer) and a Subcontractor(CMT) (as seller), for one `StoreStyle`. Instantiated by D2 (`M7797 茗苑合同 1.30.xls`, one sheet per store style).
- **Grain**: 1 per (StoreStyle, CMT_Subcontractor).
- **Primary identifier**: composite (program_code, store_style_code, cmt_subcontractor_name).
- **Attributes**: `contract_date`, `contract_delivery_date` (per M3), `quantity_contract`, `testing_requirements`, `process_requirements`, `no_wash_flag`, `raw_fabric_bom_text`.
- **Evidence**: D2. `交期 = 2026-04-20` is the customer-facing commitment.

### 3.5 StyleOrder

- **Definition**: our own record that a booking exists for one (factory_style, contract) pair. It aggregates one or more PricingLines with different price brackets. **Not** the same as the buyer's PurchaseOrder — the PO layer comes later (from Brand→BCI→锦秀), and one StyleOrder may be split across multiple PurchaseOrders (this case: 2 POs).
- **Grain**: 1 per (contract, factory_style, colour).
- **Primary identifier**: composite (contract_ref, factory_style_ref, color_ref).
- **Attributes**: `booked_order_date` (D1 `下单时间`), `sourcing_trading_ref`, `merchandiser_ref`.
- **Evidence**: D1 R171 + R172 collectively = one StyleOrder (same style/colour, different pricing brackets).

### 3.6 PricingLine

- **Definition**: **per M1**, a distinct commercial line at the grain **StyleOrder × pricing bracket** (regular vs plus-size premium). Do **not** merge with PurchaseOrder or SizeAllocation.
- **Grain**: 1 per (StyleOrder, pricing_bracket).
- **Primary identifier**: composite (style_order_ref, pricing_bracket).
- **Attributes**: `pricing_bracket` ∈ {`regular`, `plus_size_premium`, ...}, `quantity_priced`, `sizes_covered` (a subset of sizes eligible for this bracket).
- **Evidence**: D1 R171 (`2679 @ ¥28`, regular) vs R172 (`160 @ ¥31`, plus). D0 rows 1 vs 6 mirror the same split.
- **Note**: `sizes_covered` is not directly given; inferred from D0/D1 co-occurring size brackets (see UNRESOLVED-11).

### 3.7 Price

- **Definition**: an individual price value attached to a PricingLine, discriminated by `price_type ∈ {target, quoted, booked}`. **Per M2** — never one canonical value.
- **Grain**: 1 per (PricingLine, price_type). Multiple `quoted` values may exist across quote revisions.
- **Attributes**: `amount`, `currency` (`RMB`), `unit` (`per_piece`), `price_type`, `document_ref`, `document_date`, `is_current`.
- **Evidence**:
  - regular PricingLine: target=27 (D0), quoted=28.5 (D0), booked=28.0 (D1 col 13);
  - plus PricingLine: target=31, quoted=32, booked=31.
- **CONFIRMED**: D1 col 13 = booked_unit_price, col 14 = derived line amount (per C6).

### 3.8 PurchaseOrder

- **Definition**: a buyer-issued Purchase Order. First-class per M4. Origin unresolved (Brand vs VendorImporter vs SourcingTradingCompany) — see UNRESOLVED-5.
- **Grain**: 1 per PO number.
- **Primary identifier**: `po_number` (`728274`).
- **Attributes**: `po_number`, `buyer_dept` (`502`, D10), `store_style_ref`, `color_ref`, `packing_mode` (`BULK独码`), `po_quantity`.
- **Evidence**: D9 `PO#`, D10 `PO#`. D2 `CUSTOMER PO#` slot exists but is `待定` at contract time — so **PO is not populated at contract stage**.

---

## 4. Layer 3 — Product specification

### 4.1 Product

- **Definition**: the product type designation (`女式T恤` / `T恤` / `绒衫`). Attaches to FactoryStyle.
- **Attributes**: `product_type_normalized`, `raw_variants[]` (preserves `T恤`, `女式T恤`, `女式T`).
- **Evidence**: D2 `品名`, D8 `品名`, D10 `品名`.

### 4.2 ColorSpecification (multi-key per M5)

- **Definition**: a colour concept for a style, held in four coexisting names. **No single value is elevated as universal key.**
- **Grain**: 1 per (StoreStyle, colour concept).
- **Attributes** (all preserved, none dominant):
  - `buyer_color_name` (`BLUE INDIGO`) — buyer-facing English.
  - `factory_color_name` (`藏青` / `丈青`) — planning-doc Chinese common name.
  - `swatch_code` (`26C12344-D`) — dye-lab swatch identifier.
  - `raw_color_text[]` — every raw cell where the colour appeared (`26C12344-D色丈青`, `BLUE INDIGO（蓝色）`, `按客样`, …).
  - `dye_method` (`单染棉` / `单染涤` / `双染` / `不水洗` — free enum from data).
- **Evidence**: D2 order block (English); D5/D6 planning (Chinese common); D7 拷布单 (swatch code); D1 (all mixed).
- **Key selection at query time**: match by whichever attribute the caller supplies.

### 4.3 SizeScheme

- **Definition**: a controlled vocabulary of sizes used for a given (Brand, product_type). Two schemes present: `LB_PLUS_10_TO_40` (`10/12`, `14/16`, `18/20`, `22/24`, `26/28`, `30/32`, `34/36`, `38/40`) and `STANDARD_XS_XXL` (from D3's leftover template).
- **Attachment**: **UNRESOLVED per M7** (U-4). Interim: attach to `FactoryStyle`, with `derives_from` pointer to Brand (dataset supports this attribution).
- **Evidence**: D2/D8/D9/D10 for `LB_PLUS_10_TO_40`; D3 Sheet1 for `STANDARD_XS_XXL`.

### 4.4 Size

- **Definition**: one bucket of a SizeScheme (e.g. `14/16`).
- **Primary identifier**: composite (`size_scheme_id`, `size_label`).

### 4.5 FabricSpecification (**decomposed per M — see architecture requirement**)

- **Definition**: description of one fabric used in a garment. Preserves raw text; **also** extracts structured atoms.
- **Attributes**:
  - `raw_spec_text` — verbatim from source cell.
  - `yarn_count` (`32S`) — INFERRED_HIGH extractable.
  - `fibre_composition` — text list, e.g. `{cotton: 60%, polyester: 40%}` — INFERRED_HIGH.
  - `blend_ratio` — as above, dimensionally same but kept as its own field per spec.
  - `fabric_type` (`竹节汗布` / `slub jersey`) — INFERRED_HIGH.
  - `gsm` (`170`) — INFERRED_HIGH.
  - `width_greige_cm` (`185`) — INFERRED_HIGH (may be missing).
  - `width_customer_inch` (`66`) — INFERRED_HIGH (may be missing).
  - `finish` (`不水洗` / `烂花水洗` / `染棉` / `染涤`) — INFERRED_HIGH.
  - `compliance_requirements[]` (`不含新疆棉`, `BCI cotton`) — INFERRED_HIGH.
- **Evidence**: D0 `面料克重/成份`; D2 `面辅料`; D5–D8 `面料质地`.
- **Rule**: raw text is authoritative; structured fields are extraction with confidence tags in each row's Provenance record.

### 4.6 MaterialComponent

- **Definition**: BOM line: which garment part uses which FabricSpecification, at what per-piece consumption.
- **Grain**: 1 per (FactoryStyle, garment_part).
- **Attributes**: `garment_part` (`大身/袖子/领子`, `袖口，领口，下摆罗纹`, `后包领`), `fabric_ref`, `consumption_kg_per_pc` (D5 `单件用料/KG`), `raw_bom_line`.
- **Evidence**: D5 (0.324 for body/sleeve/collar; 0.004 for rib collar tape); D2 `序号 / 部位 / 面辅料`.

### 4.7 Artwork

- **Definition**: an embroidery/print art asset that appears on the garment. `画稿` linking id per C5.
- **Attributes**: `art_asset_id` (`997X`), `art_type` (`embroidery`|`print`|`beading`), `art_file_refs[]` (list of external file paths: `.ai`, `.jpg`, `.png`), `position_on_garment` (`前片珠片绣`).
- **Evidence**: D4 `画稿 = 997X`; A5 `997X Football sequins EMB.ai`; A6/A8 confirmation photos.

### 4.8 EmbroiderySpecification

- **Definition**: a per-style rule for how embroidery is executed. Includes size-scaled version handling.
- **Attributes**: `has_small_version_100pct`, `has_large_version_110pct`, `applies_to_sizes[]`, `subcontractor_ref` (defaults to `家顺`).
- **Evidence**: D8 `绣花小版(100%)` / `绣花大版(110%)`; D4.

### 4.9 LabelSpecification

- **Definition**: a specification block for one label kind. Distinct sub-types.
- **Sub-types**: `main_label`, `care_tracker_label`, `hangtag`, `side_label` (D9 mentions `1152530` needs one).
- **Attributes**: `template_ref` (points to external spec sheet, D9 says `内容见附页`), `position_description`, `attachment_method` (`透明枪针`, `车缝`).
- **Evidence**: D9 `主标 / 洗标和追踪标 / 价格牌`.

### 4.10 PackagingSpecification

- **Definition**: how the garment is packaged. Two levels: per garment (polybag) and per carton.
- **Attributes**: `polybag_type` (`PE自封口`, `2个气孔`), `polybag_sticker_ref`, `glassine_paper_required` (bool), `polybag_stack_method`, `carton_type` (`三瓦楞 ETC≥21.8KG`), `carton_marking_ref`.
- **Evidence**: D9 sheets `胶袋警告语`, `油光纸参考`, `纸箱-独色独码 BULK`.

### 4.11 TestingRequirement

- **Definition**: 3rd-party test spec (currently only BV observed).
- **Attributes**: `testing_agency` (`BV测试公司`), `test_categories[]`, `raw_requirement_text`.
- **Evidence**: D2 `测试要求` (verbatim).

---

## 5. Layer 4 — Manufacturing / execution

Each execution entity carries a `state ∈ {PLANNED, REVISED, ACTUAL}` where the data supports the distinction.

### 5.1 MaterialRequirement

- Aggregate: for one (StyleOrder, colour) what greige quantities and yarn quantities are needed. State = PLANNED.
- Evidence: D5 `投料计划`.

### 5.2 YarnRequirement

- **Grain**: 1 per (StyleOrder, colour, yarn spec).
- **Attributes**: `yarn_type` (`32S CVC 60/40 竹节纱`), `required_kg` (`950`), `computed_from_greige_kg` (`931.836`).
- State = PLANNED. **INFERRED_HIGH** that 950 = 932 + buffer.

### 5.3 KnittingPlan

- **Grain**: 1 per fabric spec × colour, subcontracted to a KnitSubcontractor.
- **Attributes**: `subcontractor_ref` (`林海织造`), `greige_kg` (`920 + 12`), `greige_width_cm` (`185`), state = PLANNED.
- Evidence: D6.
- **ACTUAL state**: not present in this dataset. D1 `面料进度 = 3/11投料` records a trigger event but no actuals.

### 5.4 FabricBatch

- **Definition**: a run of greige fabric produced by one KnittingPlan. Physical batch of undyed fabric.
- **Grain**: 1 per (KnittingPlan, batch).
- **Attributes**: `greige_qty_kg`, `width_cm`.
- **Note**: this is the entity that gets **dyed into a DyeLot**.
- **INFERRED_LOW**: the dataset does not distinguish "greige batch" from "yarn purchase" clearly. This entity may collapse into KnittingPlan on next revision.

### 5.5 DyeLot

- **Definition**: a batch of fabric dyed to one colour, identified by `批号`.
- **Grain**: **UNRESOLVED per M7** (U-2). Interim: 1 per (fabric_spec, colour, batch_number). This case: batch `524` = one lot for FBB54S2-997XLB / BLUE INDIGO / 26C12344-D.
- **Attributes**: `batch_number` (`524`), `dyed_kg`, `swatch_code_ref` (`26C12344-D`), `dye_method` (`单染棉`), state ∈ {PLANNED, ACTUAL}.
- **Evidence**: D7 `批号`; D8 `批号/色样`.
- **Note**: D7's `实拷KG` (actual scoured kg) is blank in this case → only PLANNED state observed.

### 5.6 CuttingPlan

- **Grain**: 1 per (StyleOrder, DyeLot).
- **Attributes**: `bulk_qty`, `planned_ship_qty_by_size{size→qty}`, `planned_cut_qty_by_size{size→qty}` (with computed wastage), `subcontractor_cmt_ref` (`名苑`), `embroidery_ref` (points to EmbroideryJob).
- **Evidence**: D8. `计划裁剪数 / 计划发货数 ≈ 1.04` for large sizes, larger for tiny counts (see UNRESOLVED-13).
- State = PLANNED. ACTUAL cuts are not captured.

### 5.7 EmbroideryJob

- **Grain**: 1 per (CuttingPlan, Artwork).
- **Attributes**: `subcontractor_ref` (`家顺`), `contact` (`13806640517`), `pieces_out`, state ∈ {PLANNED, ACTUAL}.
- **Evidence**: D8 `协作单位`; A5 `.ai`.

### 5.8 SewingJob

- **Grain**: 1 per (CuttingPlan × colour).
- **Attributes**: `subcontractor_ref` (`名苑`), `operator_person` (`郁建东` — INFERRED_LOW per UNRESOLVED-15), state ∈ {PLANNED, ACTUAL}.
- **Evidence**: D8; D1 status text `5/22 郁建东发货` (mixes ship+operator).

### 5.9 PackingJob

- **Grain**: 1 per (SewingJob, PurchaseOrder). This is where PO first becomes a hard constraint on physical pieces.
- **Attributes**: `packing_mode` (`BULK独码`), state.
- **Evidence**: D10.

### 5.10 Shipment

- **Definition**: a completed dispatch of one or more PurchaseOrders' cartons.
- **Attributes**: `actual_ship_date` (`2026-05-22`), `raw_status_text` (`5/22 郁建东发货`), `origin_factory_ref`, `handler_person`.
- **Evidence**: D1 `成衣工厂` cell interpreted as shipment record.

### 5.11 Invoice

- **Definition**: our invoice to the SourcingTradingCompany.
- **Attributes**: `invoice_date` (`2026-06-03`), `amount_rmb` (`75012 + 4960 = 79972`), `raw_status_text` (`6/3开票`).
- **Evidence**: D1 `开票情况`, cols 13 & 14 (per C6).

---

## 6. Layer 5 — Logistics / allocation

Grain hierarchy strictly:

```
StyleOrder
  → PurchaseOrder
    → SizeAllocation      (grain: PurchaseOrder × Size)
      → CartonAllocation  (grain: PurchaseOrder × Size × 箱号)
        → Carton          (physical box, 1..1 with CartonAllocation once packed)
```

### 6.1 SizeAllocation

- **Grain**: PurchaseOrder × Size.
- **Attributes**: `pieces_planned`, `pieces_packed`.
- **Evidence**: D9 per-PO per-size table; D10 per-carton rows sum to this.

### 6.2 CartonAllocation

- **Grain**: PurchaseOrder × Size × 箱号 (or 箱号 range).
- **Attributes**: `carton_number_from`, `carton_number_to`, `carton_count`, `pieces_per_carton`, `size_ratio_per_carton` (if mixed), `upc_ref`.
- **Evidence**: D10 rows.

### 6.3 Carton

- **Definition**: a physical box.
- **Attributes**: `carton_number`, `pieces_in_carton`, `gross_weight_kg`, `net_weight_kg`, `length_cm`, `width_cm`, `height_cm`, `volume_m3` (CALCULATE).
- **Attached**: `UPC` per (Carton, Size) — D10 stores UPC in the ambiguously-named `包装` column.

---

## 7. Layer 6 — Events / workflow

See `03_event_model.md` for the full 17-event catalog. Summary here:

- Events are first-class objects (`StageEvent`).
- Every event has `event_type`, `affected_object_ref`, `planned_date`, `actual_date`, `status ∈ {PLANNED, IN_PROGRESS, DONE, REVISED, CANCELLED}`, `source_document_ref`, `raw_evidence_text`, `confidence`.
- A `StageDeadline` is a specialisation of `StageEvent` with `event_type = *_DEADLINE`, `actual_date = null`. This is how D7's 4/25 and D8's 5/7 are represented — as internal deadlines, not delivery dates.

---

## 8. Provenance (cross-cutting)

Every normalized fact carries a `Provenance` record:

- `normalized_value`
- `raw_value`
- `source_document` (D0..D10, A1..A5)
- `source_sheet`
- `source_location` (`row/col` or `cell address` or `field label`)
- `extraction_method` (`direct` / `regex` / `parse` / `manual`)
- `confidence` (`OBSERVED` / `INFERRED_HIGH` / `INFERRED_LOW`)
- `observed_at` (timestamp of extraction)
- `document_date` (mtime or filename date)

Documents themselves are represented as `Document` entities so events and facts can point to them.

---

## 9. Relationship families (naming conventions)

We avoid the generic `has_*`. Business-explicit predicates:

- Party: `served_by`, `sourced_through`, `contracts_with`, `subcontracts_to`, `employs`, `assigned_to_program`.
- Commercial: `initiated_by`, `for_brand`, `contains` (Program→StoreStyle), `realized_as` (StoreStyle→FactoryStyle), `governed_by` (StoreStyle→Contract), `booked_as` (Contract→StyleOrder), `comprises` (StyleOrder→PricingLine), `priced_at` (PricingLine→Price), `covers_sizes`, `covers_color`.
- Product: `specifies_fabric`, `specifies_color`, `specifies_size_scheme`, `applies_art`, `applies_label`, `applies_packaging`, `applies_testing`.
- Manufacturing: `requires` (StyleOrder→MaterialRequirement), `plans_yarn`, `plans_knitting`, `produces_greige`, `dyed_into`, `plans_cutting`, `consumes_dyelot`, `produces_pieces_for` (Cut→Emb→Sew), `packed_by`, `dispatched_as`, `billed_as`.
- Logistics: `allocates_to_po`, `allocates_by_size`, `allocates_by_carton`, `instantiates_carton`, `labeled_with_upc`.
- Events: `records_event`, `deadline_for`, `evidenced_by`.
- Provenance: `sourced_from`, `raw_from_cell`.

Full list in `03_relationships.csv`.

---

## 10. Explicitly UNRESOLVED (carried in `03_unresolved_ontology_decisions.md`)

Named upfront so downstream users know what is deferred:

- **U-1** Cardinality StoreStyle ↔ FactoryStyle (1-to-many across revisions?).
- **U-2** Scope of DyeLot (fabric-only vs (fabric, colour) vs order).
- **U-3** Party attachment scope: are (锦秀, 名苑) chosen per Program, per Style, or per Order?
- **U-4** SizeScheme attachment: Brand / Program / Style / Order.
- **U-5** PurchaseOrder issuer: Brand vs VendorImporter vs SourcingTradingCompany.
- **U-6** Colour natural key.
- **U-7** Program-as-entity vs Program-as-tag.
- **U-8** Which price is "committed"?
- **U-9** How to reconcile delivery-date revisions across documents.
- **U-10** Whether FabricBatch and KnittingPlan should collapse.

Additional UNRESOLVED items are catalogued in the separate file.

---

## 11. Deliverables list (for this step)

- `03_ontology_v0.1.md` — this file.
- `03_entities.csv` — all entities with grain, key, evidence, confidence, status.
- `03_relationships.csv` — all relationships with cardinality, evidence, status.
- `03_attributes.csv` — attributes per entity with source-field mapping and normalisation rules.
- `03_ontology_v0.1.json` — machine-readable ontology.
- `03_ontology_graph.mermaid` — trimmed diagram of the most important entities.
- `03_event_model.md` — events / workflow catalog.
- `03_unresolved_ontology_decisions.md` — carried-forward decisions.

**Non-goals**: v0.1 does not attempt validation rules, migration/ETL mapping, or physical schema (SQL/graph DB tables). Those come after user review of what is captured here.
