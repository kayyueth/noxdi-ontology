# 02 — Field Lineage (narrative)

Per-concept trace of where each field first appears, where it is copied, and where it drifts. Same evidence base as `02_order_lifecycle.md`; complements the machine-readable `02_field_lineage.csv`.

Confidence tags OBSERVED / INFERRED_HIGH / INFERRED_LOW as before.

---

## 1. Identifiers

### 1.1 factory_style_code (`款号`)

- **Originates**: F2 `STYLE` at quote time.
- **Copied to**: F1 `款号` at order entry, then to every downstream doc (F3, F4, F5a/b/c, F6, F7, F8, F9).
- **Drift**: F1 often appends free text to the cell (`翻单`, `小码翻单`, `版型同OR072`, program prefix `M7797 ...`). F6/F7/F8/F9 store it inside a dual-code cell with the store style. **INFERRED_HIGH**: any join key must regex-extract the code (`[A-Z]{3}\d{2}[A-Z]\d-\d{3}[A-Z]{2,3}`), not use raw cell text.

### 1.2 store_style_code (`商店款号`, 7-digit)

- **Originates**: F7 (tab name and header). Also on F6, F8, F9.
- **Never appears** in F1 or F2, which are internal-facing docs.
- **Drift**: In F3/F6 the buyer-facing dual-cell is `factory_code（商店款号NNNNNNN）`; in F7/F8/F9 it is `NNNNNNN（factory_code）`. Same information, opposite ordering — reflects which team authored the sheet (INFERRED_HIGH).

### 1.3 program_code (`PROGRAM#` — e.g. `M7797`)

- **Originates**: F7 header (buyer program).
- **Copied to**: F3, F6 (and F6 filename).
- **Not** a formal column in F1, but leaks into F1 `款号` free text as a prefix (`M7797  BJB65Q2-746US`, `M7743    FNL86R2-246EM`).
- **INFERRED_HIGH**: PROGRAM is the natural grouping key for multi-style shipments; today it must be extracted from F1's `款号` text.

### 1.4 po_number (`PO#` / `CUSTOMER PO#`)

- **Originates conceptually**: F7 (as `CUSTOMER PO#`), but observed values are `待定` — the PO is issued by the buyer after contract, so F7 has a slot but no value.
- **First actually populated**: F6 `主表` (once POs come in) — e.g. `728274`, `728275`, `729503`, `729504`, `729499`.
- **Copied to**: F3 packing list per carton block.
- **Not** in F1 — F1 has no PO column at all. This is a notable gap: a same-style order split across 2 POs shows up as **one line in F1** with the combined qty (2839), but as two blocks in F3/F6/F7.

### 1.5 upc (`包装` numeric in F3, `包装和UPS#` in F7)

- **Originates conceptually**: F7 `包装和UPS#` (label is a typo of `UPC#`), values `待定`.
- **First actually populated**: F3 packing list, embedded inside a column called `包装` (which reads as "packing" not "UPC"). Values are 9-digit numbers per size (`601567949` for size 14/16, `601567944` for size 18/20, etc.).
- **Drift**: There is no column named `UPC` anywhere; the value hides under a Chinese header that also connotes "packing mode". Programmatic extraction must be by value pattern, not header.

### 1.6 dept

- **Originates**: F3 `Dept` (e.g. `502`). Nowhere else structured.
- **INFERRED_HIGH**: Lane Bryant / BCI department code; carton-marking only.

### 1.7 dye_lot (`批号`)

- **Originates**: F5c `拷布单` `批号` = `524`.
- **Copied to**: F4 `裁剪计划单` `批号/色样` = `524`.
- **Semantic role**: only cross-document key that links **fabric** (S6-S9) to **garment** (S10+). It is the natural fabric traceability key.

### 1.8 art_asset_id (`画稿`)

- **Originates**: F9 `色卡安排` `画稿` = `997X`, `230E`, `185E`, `220E`.
- **Links to**: F13 `.ai` art master files (e.g. `997X` ↔ `997X Football sequins EMB.ai`). **Confirmed by user (C5)**.
- **Drift**: The `.ai` filename embeds `997X`; the workbook cell also stores `997X`. The link is exact, but nowhere is `画稿` present as a formal key with a schema constraint.

### 1.9 carton_number (`箱号`)

- **Originates**: F3 only. Can be a single number or a range (`1-13`).
- **Uniqueness scope**: within a (style, PO) block — same box numbers appear again in the second PO's block on the same sheet.

---

## 2. Party / vendor fields (rewritten after C1 / C7)

### 2.1 brand (甲方 = Lane Bryant)

- **Originates**: F7 `商店`.
- **Also in**: F6 filename (`LANE BRYANT_M7797_...`).
- **Not** present in F1, F2, F3 (aside from the leftover template Sheet1's implicit references), F4, F5. Any brand-level query today must join through PROGRAM# or store style.

### 2.2 vendor_importer (BCI Brands) — **new tier introduced by C7**

- **Originates**: F7 `客户`.
- **Only in F7**. Does not propagate anywhere else in the dataset.
- **Consequence**: The full up-chain (BRAND → VENDOR → SOURCING) is documented only inside the contract file. Every other document collapses BRAND+VENDOR into an implicit context and records only the direct customer (锦秀).

### 2.3 sourcing_trading (乙方 = 锦秀)

- **Originates**: F1 `客户` = `锦秀/胡颖洁` (with merchandiser suffix).
- **Also in**: F4, F5a, F5b, F5c `客户`; F7 header (`象山锦秀服饰有限公司鄞州分公司`).
- **Corrected reading (C1)**: this is always the direct customer relative to the document's author; it is never the brand.

### 2.4 merchandiser (`胡颖洁`, `郑飞飞`, `毛益波`/`毛意波`)

- **Originates**: embedded in the `客户` cell in F1/F4/F5, separated by `/`.
- **Also in**: F8/F9 footer as a plain name line.
- **Drift**: same person spelled two ways (毛益波 vs 毛意波). Only present as sub-string of another field; needs deterministic extraction.

### 2.5 factory_us (丙方 = 润悦 = us)

- **Originates**: F5a/F5b/F5c/F4 header text `宁波润悦服饰有限公司`.
- **Never** appears as a value field — always as a document header. Implicit in every internal document.

### 2.6 cmt_subcontractor (`名苑`, canonical per C3)

- **Originates**: F4 `生产工厂` = `名苑`.
- **Also in**: F1 `成衣工厂` cell as free text (`10/10(郁建东做)名苑发货`); F7 header `茗苑` (variant spelling to normalise).
- **Drift**: name spelled two ways; embedded in status text mixed with operator names and ship notes.

### 2.7 knit_subcontractor (`林海织造`)

- **Originates**: F5b `织造加工`.
- **Also in**: F5c `织造加工` (dyeing plan echoes the knitter).
- **Not** in F1, F4 (which is downstream of fabric).

### 2.8 embroidery_subcontractor (`家顺`)

- **Originates**: F4 `协作单位` + `联系方式`. Only in F4.

### 2.9 wash_subcontractor (`红水`)

- **Originates**: F1 `水洗厂`. Only 22 of 450 rows.

---

## 3. Style attributes (fabric / colour / product)

### 3.1 fabric_spec

Rekeyed into 7 files. See table §3.5 for details.

| Location | Field | Example |
|---|---|---|
| F2 (origin) | 面料克重/成份 | `Self: CVC SLUB jersey 170GSM 大身CVC 竹节汗布` |
| F1 | 面料 | `32SCVC60/40 竹节汗布170G` |
| F7 | 面辅料 / 本身布 | `蓝色，染棉，CVC 60棉40涤竹节汗布` |
| F5a/b/c | 面料质地 (+`/不含新疆棉` in F5a) | `32S CVC60/40竹节汗布170G(成衣）` |
| F4 | 面料质地 | same |
| F8/F9 | 面料信息 | `本身布：蓝色，染棉，...` |

Each restatement is prose — none of these are ISO-normalised. Composition, gauge (32S), blend (60/40), weight (170G), fabric family (竹节汗布 = slub jersey), fibre certification (BCI cotton clause, no-Xinjiang clause) all live inside one free-text cell.

### 3.2 colour_order vs colour_swatch_code

- **colour_order** (used by buyer / packing): English name in F7/F6/F3 (`BLUE INDIGO`), Chinese in parentheses.
- **colour_swatch_code** (used by dye / cut): swatch/dye code in F5c/F4 (`26C12344-D色丈青`).
- **F1 mixes both** in one cell.
- Nothing formally connects `BLUE INDIGO` to `26C12344-D` except that they appear together on the same order.

### 3.3 product_type

- Values: `T恤`, `绒衫`, `女式T恤`, `女式T`. Text-only, per document, minor variants. No controlled vocabulary.

### 3.4 yardage_per_pc, weight_per_pc_kg, fabric_width

- Originate in F2 (`客户用料码` in yd/pc, `光坯用料` in kg/pc, `客户门幅` in inches).
- Restated in F5a in kg/pc and cm — unit conversion is implicit and not tracked. E.g. F2 `0.315 kg/pc` vs F5a `0.324 kg/pc` — small drift, likely different scope (garment vs part).

### 3.5 fabric_spec propagation summary

| Concept origin | Direct copies | Restatements | Notes |
|---|---|---|---|
| F2 面料克重/成份 | F1 面料, F5a/b/c 面料质地, F4 面料质地, F7 面辅料, F8/F9 面料信息 | 7 | Same fabric described in 7 different phrasings, no shared vocabulary |

Any change in fabric spec after S1 must be manually propagated to 7 places. INFERRED_HIGH: this is a primary drift source.

---

## 4. Quantities (four grains, one word)

The word `数量` denotes four different measures depending on document:

| Grain | Origin | Also in | Field name |
|---|---|---|---|
| bulk (style total) | F2 数量 (per size bracket) | F1 数量/件, F7 数量, F5a 成衣数量, F4 大货数量, F6 总件数 | 6 places |
| per PO | F6 数量 | F3 共计数量 | 2 places |
| per size | F7 10/12..38/40 | F4 计划发货数, F6 10/12..38/40, F3 10/12..38/40 (per carton) | 4 places |
| per carton | F3 每箱件数 | — | 1 place |

Derived: F4 `计划裁剪数` = `计划发货数 × (1 + wastage%)`, F3 `每箱体积` from dims, F1 `金额` from qty × 单价.

**No enforced constraint** exists that Σ(per size across POs) = bulk. Consistency for this dossier's 2839 pcs is real (verified in `01_ambiguities.md §D.2`) but not structural.

---

## 5. Dates

| Concept | Origin | Format | Confidence |
|---|---|---|---|
| order_date (`下单时间`) | F1 | `12.1`, `12/10` shorthand; year not encoded | OBSERVED |
| delivery_date_customer (`交期`) | F7 (authoritative per C4) | `2026-04-20` datetime | OBSERVED |
| delivery_date_customer (`交货期`) | F1 | Excel serial `45716` | OBSERVED |
| stage_deadline_dye | F5c `成衣交期` | text `2026.4.25` | INFERRED_HIGH (per C4) |
| stage_deadline_cut | F4 `交货期` | text `2026.5.7` | INFERRED_HIGH (per C4) |
| plan_date_yarn | F5a footer | `2026.3.10` | OBSERVED |
| plan_date_dye | F5c `日期` | `2026.3.10` | OBSERVED |
| plan_date_knit | F5b footer | `2026.3.19` | OBSERVED |
| ship_date | F1 `成衣工厂` free text | `3.7出货`, `10/10 名苑发货` | OBSERVED |
| invoice_date | F1 `开票情况` free text | `3.24开票` | OBSERVED |

Post-C4 clarification: the label `交期`/`交货期`/`成衣交期` is not, on its own, a reliable indicator of what the date means. Semantics is determined by **which document** the field lives in, not by the label.

---

## 6. Money

| Concept | Origin | Also in |
|---|---|---|
| unit_price_rmb quoted | F2 `价格` | — |
| unit_price_rmb booked | F1 col 13 (per C6) | — |
| target_price | F2 `目标价` | — |
| line_amount_rmb | F1 col 14 (per C6) = qty × col13 | — |
| cost buckets (fabric, CMT, burnout, print/emb, trims) | F2 columns 9-14 | — |

**Not linked**: quoted `价格` and booked `单价` (F1 col 13) live in different files with no explicit key. Reconciliation of quote vs invoice is manual.

---

## 7. Packing / carton / label attributes

Effectively **F3 owns packing measurements** (per-carton weight/dim/volume) and **F6 owns label/trim specs** (main label, care label, hangtag, polybag). These two files together carry the entire shipping-side attribute set; no other file duplicates them.

---

## 8. Status fields (free text, all in F1)

Four columns in F1 are the only place where operational status lives:

- `样衣进度` — sample progress (S3).
- `面料进度` — fabric progress (S6-S9).
- `成衣工厂` — CMT + ship note (S12/S17).
- `开票情况` — invoice status (S18).

All are free-text and mix a date with a fragment of narrative. Any timeline dashboard has to text-parse these cells; no dedicated status enum exists.

---

## 9. Fields with NO downstream trace (originate and stop)

Fields that appear in exactly one document and are never restated anywhere else — high-value candidates for "hidden" data that only that one team sees:

| Field | Only in |
|---|---|
| 目标价, 客户用料码, 光坯用料, all cost buckets | F2 (quote) |
| 测试要求 (BV testing spec) | F7 |
| BCI (vendor_importer identity) | F7 |
| Dept (buyer department code) | F3 |
| 主标 / 洗标 / 价格牌 / 胶袋贴纸 / 胶袋 / 油光纸 / 包装方法 | F6 |
| Carton dimensions, weight, volume | F3 |
| 家顺 (embroidery subcontractor + phone) | F4 |
| 林海织造 (knit + dye vendor) | F5 |
| 红水 (wash vendor) | F1 (single column, 22 rows) |
| Style image (`=DISPIMG`) | F1 (60 rows) |
| Buyer PP/fit PDFs, .ai art, .dxf pattern, .rul grading | Non-Excel files |

For each of these, if the file is lost, the information is lost. There is no redundancy.

---

## 10. Where the same fact drifts (summary of documented drift)

| Fact | Drift form | Files |
|---|---|---|
| Factory style code | Free-text suffixes appended | F1 |
| Factory + store style pairing | Order flipped, punctuation varies | F3/F6 vs F7/F8/F9 |
| CMT factory name | 名苑 vs 茗苑 | F4/F1 vs F7 |
| Merchandiser name | 毛益波 vs 毛意波 | F1 |
| Fabric spec | 7 different phrasings | F1/F2/F4/F5/F6/F7/F8/F9 |
| Colour | English trade name vs swatch/dye code, mixed in F1 | F1/F3/F4/F5c/F6/F7 |
| Quantity | 4 different grains under the word 数量 | F1/F2/F3/F4/F5/F6/F7 |
| Delivery date | Contract vs stage deadlines share label 交期/交货期 | F1/F4/F5a/F5c/F7 |
| Weight per pc | 0.315 kg (F2) vs 0.324 kg (F5a) | F2/F5a |
| Program membership | Style 1152526 in F6 but not F7; 1152527 in F7 but not F6 | F6 vs F7 |

Each of these is a specific place where a data model has to make a normalisation choice. That is the input to step 03.

---

## 11. Trace-completeness scorecard (this dossier)

For the FBB54S2-997XLB / 1152246 order — what fraction of lifecycle stages produce a persisted, structured record?

| Stage | Structured record present? |
|---|---|
| S1 Quote | ✅ F2 |
| S2 Order (internal) | ✅ F1 |
| S2 Contract | ✅ F7 |
| S3 Sampling | ⚠️ status only (F1); PDFs unstructured |
| S4 LAB DIP | ✅ F8 |
| S5 Art | ✅ F9 (+ external .ai) |
| S6 Yarn | ✅ F5a |
| S7 Knit | ✅ F5b |
| S8 Dye | ✅ F5c |
| S9 Fabric-in QC | ⚠️ status only (F1) |
| S10 Cut | ✅ F4 |
| S11 Embroidery | ⚠️ subcontractor named (F4), no per-run record |
| S12 CMT | ⚠️ ship-note text only (F1) |
| S13 Wash | n/a (not applicable to this style) |
| S14 Testing | ⚠️ requirements only (F7); no test-result record |
| S15 Trims/Labels | ✅ F6 |
| S16 Packing | ✅ F3 |
| S17 Ship | ⚠️ ship-note text only (F1) |
| S18 Invoice | ⚠️ text status (F1) + 单价/金额 numeric (F1 col13/14) |

10 stages fully structured, 7 partially, 1 not applicable. The gap-shaped part of the lifecycle is **status / actual-event capture** (sampling, fabric-in QC, embroidery run, CMT run, shipping, testing). Planning documents exist; execution actuals do not.

---

## Handoff to step 03

Deliverables of this step:
- **`02_corrections.md`** — C1–C7 corrections applied.
- **`02_order_lifecycle.md`** — S1–S18 stages × actors × artifacts + hand-off matrix + as-is break points.
- **`02_field_lineage.csv`** — one row per (concept, source, stage, role, origin/copy/derived).
- **`02_field_lineage.md`** — this file.

Together these give the evidence base for step 03 ontology design:
- Canonical concepts with tier-explicit party model (甲方 / vendor_importer / 乙方 / 丙方 / subcontractors).
- Which fields are the natural join keys (factory_style_code + store_style_code + program_code + po_number + dye_lot + carton_number).
- Which grains a `Quantity` entity must support (bulk / per_po / per_size / per_carton).
- Which fields must be extracted from free-text cells (merchandiser out of `客户`, factory style out of `款号`, English colour vs swatch code out of `颜色`).
- Which lifecycle stages currently lack any structured actuals — the places an ontology will need to *create* room for, not just map existing data into.
