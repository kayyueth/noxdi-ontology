# 01 — Ambiguities, Synonyms & Inconsistencies

This file catalogues (a) fields that appear to mean the same thing under different names, (b) duplicated / conflicting values, and (c) columns whose meaning cannot be inferred with confidence. It **does not resolve** any of them — that is ontology work.

Confidence tags: **OBSERVED**, **INFERRED_HIGH**, **INFERRED_LOW** — as in `01_data_inventory.md`.

---

## A. Likely synonyms (same concept, different names/spellings)

### A.1 Style number — factory-internal

Appears as `款号`, `款  号`, `STYLE`, `Style No.` (never seen literally but implied by column position). All observed examples share the pattern `XXX##X#-###X##` (e.g. `FBB54S2-997XLB`, `FJB66S5-185ELB`, `DNL14R6-410SM`).

- F1 col 2 `款号`
- F2 col 0 `STYLE`
- F3/F4/F5/F6/F7 header field `款号`
- F1 sometimes carries **extra free text** in the same cell: `106M324U014     小码翻单`, `SLIP109版型同SLIP095`, `M7797    FNL86R2-246EM大码` — the appended text mixes **program code + factory style code + note** in one cell (OBSERVED).

### A.2 Style number — buyer store SKU

Appears as `商店款号`, `1152246`, and standalone tab names in F7. Pattern: 7-digit numeric.

- F3/F6/F7 embed it as `（商店款号1152246）` inside the same `款号` cell as the factory code.
- F7 uses **the buyer SKU** as the primary style label and puts the factory code in parentheses — the reverse of F3/F6.
- F8/F9 also carry the dual code with buyer-first ordering.

Both codes point to the same physical style but the primary key **flips depending on which internal team owns the document** (INFERRED_HIGH).

### A.3 Program

- `PROGRAM`, `PROGRAM#`, `M7797`, `M5747`, `M7528`, `M7743`, `M7866`. Buyer program grouping several styles. Present in F3/F6/F7 header and embedded in some F1 `款号` cells (e.g. `M7797 FNL86R2-246EM`). No column in F1 explicitly named `PROGRAM` (OBSERVED).

### A.4 Customer / buyer / brand / agent (highly overloaded field)

The single field `客户` carries at least **four different concept-types** across the dataset:

| Source | `客户` value example | What it actually is |
|--------|--------------------|---------------------|
| F1 | `锦秀/胡颖洁`, `锦维/利百加`, `亿德小仇 杰杰男装` | **Trading company + merchandiser name** (agent, not end brand) |
| F4/F5 | `锦秀公司/胡颖洁` | Same — trading company + merchandiser |
| F7 | `BCI` | **Cotton certification standard** (Better Cotton Initiative) — this is not a customer at all (INFERRED_HIGH mismatch) |
| Implicit | `Lane Bryant` | Brand / end retailer — appears in F7 as `商店` and in F6 filename |

The end brand also surfaces under separate fields: `商店` (F7), `STORE` (F6). And the trading company (锦秀) is what F1 calls `客户`. So the same word `客户` denotes different things in different files. **Confidence: OBSERVED overlap; INFERRED_HIGH on the "BCI is misuse of 客户 field" reading.**

### A.5 Colour

Appears as `颜色`, `颜色 ` (trailing space), `COLOR`, `款式图` (in F2's data rows — colour name placed under the "style image" header, INFERRED_LOW that the header was mis-used). Values mix:

- English trade name: `BLUE INDIGO`, `ASCENA BLACK`, `JET BLACK`, `OATMEAL`, `HOLLYHOCK`
- Chinese common name: `藏青色`, `黑色`, `燕麦色`, `紫色`
- Swatch/dye code: `PTS9392-A`, `26C12344-D`, `25T9731-C`, `EF2515-C`
- Bilingual composites: `Navy Duke 藏青色 + 银色金属丝 PTS9392-A`, `BLUE INDIGO（蓝色）`
- Comparative references: `黑色-颜色同SLIP95款黑色`, `EF2515-C蓝色`
- Instructions: `按客样`, `配大身` (not a colour, an instruction) — appears in F7 BOM lines under a column also called `颜色` (INFERRED_HIGH: same header, different semantics — colour value vs colour instruction).

### A.6 Quantity

- F1 col 6 `数量/件`
- F2 col 1 `数量`
- F3 `每箱件数` / `共计数量` / `合计` (carton-level and total)
- F4 `大货数量` / `合计` / `计划发货数` / `计划裁剪数` (bulk qty / plan-ship / plan-cut — different grains!)
- F5a `成衣数量`
- F6 `数量` (PO subtotal) / `总件数` (style total)
- F7 `数量` (contract total) / `总计` (colour total per contract)

All are "pieces" but the **grain differs** (per PO, per colour, per carton, per style, per plan-ship vs plan-cut). Same name ≠ same concept (OBSERVED).

### A.7 Delivery date

- F1 col 7 `交货期` — stored as **Excel serial integer** (`45716`)
- F4 `交货期` — stored as **text string** `2026.5.7`
- F5a `交期` — text `2026.4.20`
- F5c `成衣交期` — text `2026.4.25` (a different date than F5a for the same style — see D.1)
- F7 `交期` — proper **datetime** `2026-04-20 00:00:00`

Same concept, four storage formats (OBSERVED).

### A.8 Fabric

- F1 col 4 `面料`
- F2 col 3 `面料克重/成份`
- F4/F5 `面料质地` (+ suffix `/不含新疆棉` — "no Xinjiang cotton" clause added to header, INFERRED_HIGH: a sourcing compliance flag baked into a header string)
- F7 `面辅料`, `本身布` (row-level part label)
- F8/F9 `面料信息`

### A.9 Factory / CMT

- F1 col 11 `成衣工厂`
- F4 `生产工厂` = `名苑`
- F7 header marker = `茗苑`
- F5 mentions `茗苑` and `林海`

The garment factory is spelled **两种写法**: `茗苑` (F7 header, filename) vs `名苑` (F1 status text, F4). Almost certainly the same entity — a homophone typo (INFERRED_HIGH). Both need to normalise to one canonical name.

### A.10 PO / order number

- F3/F6 `PO#`
- F6 alt row `包装` cells contain `601567949`-style numbers — likely **UPC/GTIN**, not PO (INFERRED_LOW)
- F7 `CUSTOMER PO#` (with values `待定`)
- F1 has no PO field at all

### A.11 Size buckets

- Buyer plus-size ratios `10/12`, `14/16`, `18/20`, `22/24`, `26/28`, `30/32`, `34/36`, `38/40` — used in F3 (this file's real sheet), F4, F6, F7.
- Regular ratios `XS`, `S`, `M`, `L`, `XL`, `XXL` — used in F3's `Sheet1` (template leftover from another style/PROGRAM).

Two disjoint size systems coexist depending on the buyer/style (OBSERVED).

### A.12 Merchandiser

Merchandiser name (`胡颖洁`, `郑飞飞`, `毛益波`, `毛意波`) is embedded inside the `客户` field with a `/` separator in F1/F4/F5 (`锦秀/胡颖洁`) and shows up bare in F8 (`胡颖洁` in footer). **`毛益波` vs `毛意波` in F1** is almost certainly the same person, transcribed differently (INFERRED_HIGH).

---

## B. Duplicated or near-duplicated fields inside one source

- **F1 columns 13 & 14**: unnamed. Numerically consistent with `unit price` and `qty × price`. No header exists → duplicated concept (price) or paired concept (unit vs total) — cannot decide without asking (INFERRED_HIGH: unit vs total).
- **F3 sheet `Sheet1`**: an entire leftover template for a **different style** (`DNL14R6-410SM`, PROGRAM `M5747`, XS–XXL). Duplicated schema at the wrong content grain (OBSERVED).
- **F7**: each sheet duplicates `款号` twice — once in the header (row 1) and again inside the size-ratio block (row 11) (OBSERVED). Same value both times, but if edited only in one place they will drift.
- **F6 `主表`**: fields `包装方法` (col 21) and `包装` (col 5) both refer to packing but with different grain (method text vs packing mode). Adjacent to `胶袋` (col 22) which also concerns bagging. Near-duplication (OBSERVED).
- **F4**: `计划发货数` and `计划裁剪数` are two rows keyed by the same size columns — a wide-format duplication of the size axis (INFERRED_HIGH: intentional plan-vs-cut variant, not accidental).
- **F8** and **F9** are structurally identical (same sheet name `色卡安排`, same key columns) but F9's semantics differ from F8's — different meaning under the same schema (OBSERVED).

---

## C. Ambiguous / unknown columns

| Location | Field | Ambiguity |
|----------|-------|-----------|
| F1 col 13 | (unnamed) | **INFERRED_HIGH** unit price; header missing |
| F1 col 14 | (unnamed) | **INFERRED_HIGH** amount; header missing |
| F1 col 15 | (unnamed) | Rare notes; concept unclear |
| F2 col 2 | `款式图` | Header says "style image" but data rows carry **colour names** (`深蓝`, `本白`). Mis-labeled header, or the sheet expects an image and someone typed a colour label — cannot tell without asking |
| F2 col 4 | `克重` | Sometimes contains `不水洗` (a process instruction, not a weight). Header vs content mismatch |
| F2 col 6 | `客户门幅` | Sometimes contains `包领` (a garment part, not a width). Similar mismatch |
| F2 col 13 | `印绣花` | A cost bucket — but is it print + embroidery combined? Or one column reused for either? Not stated |
| F2 col 15 vs col 10 | `合计成本` vs `每件成本` | Both look like per-piece totals; relationship not stated |
| F3 `包装` | text like `601567949` | UPC? GTIN? PO variant? — column header just says `包装` (packing) but value is numeric SKU-shaped |
| F3 `每箱配比` | text like `95` or repeated pattern | Not clear whether this is a ratio, a pack-per-carton count, or a redundant echo of `每箱件数` |
| F6 `STORE` | column present but all empty in sample rows | Meaning unclear; possibly reserved for a store code |
| F6 `包装` vs `包装方法` vs `胶袋` | three overlapping columns | Semantics not disambiguated in the source |
| F7 `包装和UPS#` | typo — likely `UPC#`. All observed values `待定` | Cannot confirm without a filled sample |
| F7 sheet `1152246` R1 `客户` = `BCI` | BCI = Better Cotton Initiative certification, **not** a customer name | Field is being reused to record a certification standard, or someone misfiled a value here (INFERRED_HIGH) |
| F8 `色号` = `按照客样颜色出色卡` | value is an **instruction** not an ID | Header says "colour number" but the cell holds a directive. Same pattern in F7 BOM `颜色` |
| F8 footer `46052` | Numeric, no label | Could be internal serial or Excel date-serial for 2026-01-28. INFERRED_LOW |
| F9 `画稿` values `997X / 230E / 185E / 220E` | Pattern matches design filenames (`997X Football sequins EMB.ai`) but not spelled out | INFERRED_HIGH: art asset id abbreviation |
| F1 `下单时间` `12.1`, `12/10`, `3.5`, `8/9` | Year is not encoded | Cannot determine year without contextual position in the sheet (2025 vs 2026 sections) |

---

## D. Cross-source inconsistencies (same fact, different values)

### D.1 Delivery date for style FBB54S2-997XLB

- F7 contract → `2026-04-20`
- F5a 投料计划 → `2026.4.20` (matches)
- F5c 拷布单 → `成衣交期 2026.4.25` (five days later)
- F4 裁剪计划单 → `2026.5.7` (17 days later)

Same style, three different `交期` values. **INFERRED_HIGH** interpretation: contract date < dyeing plan date < cutting-plan actual (schedule has slipped). But could equally be per-stage internal deadlines. Cannot decide without asking (OBSERVED discrepancy).

### D.2 Bulk quantity for FBB54S2-997XLB

- F7 contract → `2839`
- F4 裁剪 `大货数量` → `2839` ✓
- F5a 投料 `成衣数量` → `2839` ✓
- F3 packing → PO 728274 = 1189 pcs, PO 728275 = 1650 pcs; **sum = 2839** ✓
- F6 辅料 → PO 728274 `数量 1189` + PO 728275 `数量 1650`, `总件数 2839` ✓
- F2 quotation → `2679` + `160` = 2839 ✓ (but split by size bracket, not PO)

Internally consistent across F2–F7 (OBSERVED). Good.

### D.3 Store style 1152526 in F6 but not in F7

- F6 has a row for `FBB83S9-294CB` / `1152526` / JET BLACK / 950 pcs.
- F7 has **no sheet** for 1152526; instead it has 1152527 (which does not appear in F6).

Cannot tell whether:
- 1152526 was added late (only trims book updated), or
- 1152527 was cancelled (only contract shows it), or
- these are two co-existing styles in the same program at different completion stages.
**Confidence: OBSERVED discrepancy; INFERRED_LOW on the reason.**

### D.4 Factory name

- `茗苑` — used in F7 sheets, F6 filename references
- `名苑` — used in F1 status text `10/10(郁建东做)名苑发货`, F4 `生产工厂`

Almost certainly one entity. **INFERRED_HIGH** typo/variant.

### D.5 Merchandiser name

- `毛益波` (F1 row 12) vs `毛意波` (F1 row 250). Different characters (益 vs 意). Likely the same person. **INFERRED_HIGH**.

### D.6 `款号` cell content varies

Same style code appears in six different textual forms:

- `FBB54S2-997XLB` (plain)
- `FBB54S2-997XLB\n（商店款号1152246）` (factory-first dual)
- `1152246\n（FBB54S2-997XLB）` (store-first dual)
- `FBB54S2-997XLB（商店款号1152246）` (single-line dual)
- `M7797  FBB54S2-997XLB` (program + style)
- Free-text-suffixed variants like `106M324U014     小码翻单`

Grouping styles by exact `款号` string would fail; grouping by regex-extracted `款号` code would succeed (INFERRED_HIGH).

---

## E. Structural issues that will affect any downstream modelling

1. **Header-block vs tabular sheets are mixed**. F1, F2, F6 are (roughly) tabular. F3, F4, F5, F7, F8, F9 are printable form layouts where the same conceptual key (e.g. `款号`) is written as a labelled cell, not a column. Field extraction must handle both.
2. **Multi-line cell values are the norm**, not the exception. `款号` cells embed the store style number and even PROGRAM; `面料` cells embed weight+composition+finish; `颜色` embeds English name + Chinese name + swatch code. Any normalised store needs to preserve raw text and separately extract structured fields.
3. **Continuation rows** (`客户`/`款号`/`下单时间` blank on rows 2..N of a multi-colour order) are implicit "same-as-above" — will need forward-fill on ingestion (INFERRED_HIGH: this is the WPS/Excel author's intent).
4. **Section banners** in F1 (`2025年订单汇总`, and presumably a `2026年订单汇总` banner further down that wasn't in the first 15-row peek) mean the year of `下单时间` is only recoverable from row position, not from the cell.
5. **Embedded images** (`=DISPIMG(...)` in F1 col 3, plus image slots in F6/F7) are WPS-Office specific and won't round-trip cleanly through generic Excel tooling.
6. **The `Sheet1` in F3** is a leftover for an unrelated style — evidence that this dossier folder is a *copy of a template*, not a purpose-built package. Other folders in the wider dataset likely have similar leftover templates (INFERRED_LOW, generalisation).

---

## F. Open questions to resolve with the user before ontology design

These are **not assumptions** — they are candidates for clarification.

1. In F1, is `客户` intended to mean the **trading company** (锦秀 / 锦维 / 亿德 / 长隆) or the **end brand** (Lane Bryant, BILLIE, etc.)?
2. Is `商店` (F7) the same concept as `STORE` (F6, empty) and as "end brand" in the user's mental model?
3. Are `茗苑` and `名苑` the same factory? If yes, what is the canonical spelling?
4. For F1 columns 13 & 14: are these `unit price ¥/pc` and `line total ¥` — or something else?
5. What is `Dept` in the F3 packing list (`502`)? Buyer department code? Cost centre?
6. In F7 `客户 = BCI` — was BCI meant to record a cotton certification, or is this a data-entry error?
7. Which delivery date is the **committed** one for FBB54S2-997XLB — the F7 contract date (`4.20`), the F5c dye plan date (`4.25`), or the F4 cutting plan date (`5.7`)? Or are these stage deadlines by design?
8. Store style 1152527 (F7) vs 1152526 (F6) — is one of them cancelled, added, or is the program mid-transition?
9. Are `画稿` codes (`997X`, `230E`, `185E`, `220E`) the canonical id used to link back to the `.ai` art files (`997X Football sequins EMB.ai`)?
10. Does the dye-lot `批号 524` (F4/F5c) have a lifecycle beyond this one order (reused across programs), or is it single-use per programme?
