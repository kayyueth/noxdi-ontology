# 02 — Case Lifecycle: FBB54S2-997XLB / 1152246 / M7797 / Lane Bryant

**Scope of case.** All available structured and unstructured records that reference:
- Factory Style = `FBB54S2-997XLB`
- Store Style = `1152246`
- Program = `M7797`
- Brand = Lane Bryant
- Trading company = 锦秀 (merchandiser: 胡颖洁)
- Vendor/importer = BCI Brands
- CMT subcontractor = 名苑

Guiding question: **how does one customer order progressively become an executable manufacturing order inside this factory?**

Confidence tags **OBSERVED** / **INFERRED_HIGH** / **INFERRED_LOW** as before.

---

## 1. Documents in scope of the case

Ten structured Excel files, five unstructured attachments (PDF, DXF, RUL, AI, image). "Loc" = where FBB54S2-997XLB / 1152246 evidence appears inside that file.

| ID | File | Loc for this case | Type | Purpose (business) |
|----|------|-------------------|------|--------------------|
| **D0** | `报价2026.2.2.xlsx` (F2) | rows 1 & 6 (STYLE=FBB54S2-997XLB, qty 2679 + 160) | Quotation / costing worksheet | Factory computes cost and offers price to 锦秀 |
| **D1** | `2026年订单汇总表.xlsx` (F1) — sheet `汇总表` | rows 171 (qty 2679, ¥28) & 172 (qty 160, ¥31) | Internal order register | 润悦 logs a booked line item and tracks it through to invoice |
| **D2** | `M7797 茗苑合同 1.30.xls` (F7) — sheet `1152246` | whole sheet | Formal contract | 锦秀 → 名苑 CMT purchase order for the whole style |
| **D3** | `M7797 茗苑色卡 1.30.xlsx` (F8) | row for 1152246 | LAB DIP brief | Colour-approval submission plan |
| **D4** | `M7797 茗苑花片 1.30.xlsx` (F9) | row for 1152246 with `画稿=997X` | Art / embroidery brief | Print/embroidery approval plan, linking to `.ai` master |
| **D5** | `FBB54S2-997XLB计划单.xls` (F5) — sheet `投料计划` | whole sheet | Yarn / greige feed plan | Purchases yarn and books greige fabric quantity |
| **D6** | same file (F5) — sheet `织造计划单` | whole sheet | Knit plan | Places knit order with 林海织造 |
| **D7** | same file (F5) — sheet `拷布单` | whole sheet | Dye/scour plan | Assigns dye lot 524 to the fabric |
| **D8** | `FBB54S2-997XLB裁剪计划单.xls` (F4) — sheet `FBB54S2-997XLB` | whole sheet | Cutting plan | Cuts pieces per size, with wastage surplus and embroidery-size versions; ships pieces to 家顺 for embroidery, then to 名苑 for sewing |
| **D9** | `LANE BRYANT_M7797_1152246辅料清单 更新4.3.xlsx` (F6) — sheet `主表` + child sheets | rows 2 & 3 (POs 728274 / 728275) | Trims / labels / packaging spec | Buyer's label + packaging spec, per PO |
| **D10** | `FBB54S2-997XLB款装箱单.xlsx` (F3) — sheet `FBB54S2-997XLB` | rows 5–14 (PO 728274) + rows 22–34 (PO 728275) | Packing list | Per-carton pack: qty, weight, dimensions, UPC per size |
| A1 | `1152246_001_PP Production_VND2160.pdf` (F10) | filename carries store style | Buyer PP Production Package | Buyer's approved production spec, distributed pre-production (**INFERRED_HIGH**) |
| A2 | `规格样997XLB(FBB54S2-388ELB) 1ST FIT EVAL 1.21.26.pdf` (F11) | filename | Buyer 1st fit evaluation | Sizing/spec evaluation on the first sample |
| A3 | `997XLB(FBB54S2-388ELB).dxf` (F12a) | filename | Cut pattern | Machine-readable pattern for automated cutting |
| A4 | `997XLB(FBB54S2-388ELB).rul` (F12b) | filename | Grading rules (**INFERRED_HIGH**) | Size-grading rules |
| A5 | `997X Football sequins EMB.ai` (F13) | filename `997X` == D4 画稿 | Embroidery art master | Illustrator master file for sequin embroidery |
| A6 | `997X 珠片绣花稿.jpg` (F14a) | filename | Embroidery sequin scan | Working scan for factory |
| A7 | `997XLB色卡确认.jpg` (F14b) | filename | Confirmed colour card | Buyer sign-off image |
| A8 | `绣花片确认.png` (F14c) | filename | Confirmed embroidery pattern piece | Buyer sign-off image |

Note the store style `1152246` in the D9 filename and the store style `1152530` and `1152526` embedded inside D9's rows demonstrate that **D9 is a program-wide file mislabelled as style-specific** — the same is true of D2 (4 tabs, one per store style).

---

## 2. Evidence-driven timeline for this case

Dates are pulled directly from cells, filenames, and file mtimes. Format: `YYYY-MM-DD (source)`.

| Date | Event | Evidence | Confidence |
|------|-------|----------|------------|
| 2026-01-21 | Buyer 1st fit evaluation on `997XLB (FBB54S2-388ELB)` | A2 filename `1.21.26` | OBSERVED |
| 2026-01-30 | D2 contract signed; D3 LAB DIP brief issued; D4 art brief issued | D2/D3/D4 filenames all `1.30` | OBSERVED |
| 2026-01-31 | 润悦 books the order line in D1 | D1 R171/R172 `下单时间 = 1/31` | OBSERVED |
| 2026-02-02 | Quote/costing worksheet saved | D0 filename `2026.2.2` | OBSERVED |
| 2026-03-10 | Yarn plan (D5) and dye plan (D7) issued | D5 footer `2026.3.10`, D7 `日期 2026.3.10` | OBSERVED |
| 2026-03-11 | Yarn actually issued to knitter | D1 `面料进度 = 3/11投料` | OBSERVED |
| 2026-03-19 | Knit plan (D6) issued | D6 footer `2026.3.19` | OBSERVED |
| 2026-03-21 | Cutting plan (D8) prepared | D8 mtime | OBSERVED |
| 2026-04-03 → 04-16 | PP samples cleared with buyer | D1 `样衣进度 = 珠片绣OK，色卡OK，产前样4/3-4/16OK` | OBSERVED |
| 2026-04-03 | Trims book updated (D9 version tag `更新4.3`) | D9 filename | OBSERVED |
| 2026-04-16 | Buyer PP Production package received | A1 mtime | INFERRED_HIGH |
| **2026-04-20** | **Contract 交期 (customer commitment)** | D2 `交期 = 2026-04-20` | OBSERVED (authoritative per C4) |
| 2026-04-25 | Internal dye-completion stage deadline | D7 `成衣交期 = 2026.4.25` | INFERRED_HIGH per C4 |
| 2026-04-26 | Packing list (D10) prepared | D10 mtime | OBSERVED |
| 2026-05-07 | Internal cutting-completion stage deadline | D8 `交货期 = 2026.5.7` | INFERRED_HIGH per C4 |
| **2026-05-22** | **Actual ship date** | D1 `成衣工厂 = 5/22 郁建东发货`; D1 `交货期` Excel serial 46164 = 2026-05-22 | OBSERVED |
| 2026-06-03 | Invoice | D1 `开票情况 = 6/3开票` | OBSERVED |

**Two "delivery" dates emerge from the evidence.** D2's 4/20 is the contractual commitment; D1's 5/22 is the actual (revised) delivery. This is not a data inconsistency — it is a **stage-specific value with a revision** (see §5.7).

**Filename dates predate order intake for D2/D3/D4.** D2 (contract) and D3/D4 (colour/art briefs) are dated 1/30 while D1 (our order log) records 1/31 and D0 (our quote) is dated 2/2. **INFERRED_HIGH**: 锦秀 was already committed to BCI/LB before formally engaging us; our quote is a post-hoc costing worksheet against a price already negotiated verbally. Do not assume "quote precedes contract" in this dataset.

---

## 3. Stage-by-stage lifecycle (derived from evidence, not from a textbook)

Each stage below is only listed if it has at least one document or at least one field-level artifact in this case.

### T1. Commercial contract (upstream)

- **Docs**: D2 (contract 锦秀↔名苑), D3 (LAB DIP brief), D4 (art brief).
- **Purpose**: 锦秀 formalises the CMT purchase with 名苑 and hands the factory the buyer's colour, art, testing, size ratio, and BOM specs.
- **Inputs**: PROGRAM# (M7797), store style, factory style, brand, vendor/importer (BCI), qty, sizes, colour, testing requirements, art file refs (`画稿`).
- **New information created here**: linking of `store style ↔ factory style ↔ program`, `商店 = Lane Bryant`, `客户 = BCI`, `画稿 = 997X / 230E / 185E / 220E`, size ratio 10/12..38/40, `测试要求` = BV test spec.
- **Copied from upstream**: buyer-issued PP fit report (A2) implicitly informs spec but is not merged into D2 fields.
- **Transformed / calculated**: none.
- **Downstream dependencies**: D5–D10 all consume D2's colour, size ratio, qty, and BOM. D9 also consumes program-level identifiers.

### T2. Order intake (our books)

- **Doc**: D1 rows 171, 172.
- **Purpose**: 润悦 records that 锦秀 has booked two SKU-like variants of the same style (regular qty 2679 @ ¥28, plus-size qty 160 @ ¥31) and begins tracking the line through to invoice.
- **New information created**: booked unit price (`col 13 = 28 / 31`), booked amount (`col 14 = 75012 / 4960`), 下单时间 (1/31), later status text (样衣进度, 面料进度, 成衣工厂, 开票情况).
- **Copied from upstream**: 款号 (embedded with PROGRAM# prefix `M7797    FBB54S2-997XLB 1152246`), 面料, 颜色, 数量, 交货期 (as Excel serial 46164 = 2026-05-22 — already the revised date, not the 4/20 contract date), 成衣工厂 (subcontractor).
- **Transformed / calculated**: 金额 = 数量 × 单价 (D1 col 14 = col 6 × col 13, verified: 2679 × 28 = 75012 ✓, 160 × 31 = 4960 ✓).
- **Downstream dependencies**: none in this file set. D1 is a **terminal aggregator**, not an upstream source.

### T3. Costing / quotation (parallel with T2)

- **Doc**: D0 rows 1 & 6.
- **Purpose**: line-by-line cost build-up for the two size brackets (regular 2679, plus 160). Records fabric usage in yards and kg, fabric unit price, CMT, print/embroidery, and both a proposed `价格` and a `目标价`.
- **New information created**: `客户用料码` (1.041 / 1.334 yd/pc), `光坯用料` (0.315 / 0.405 kg/pc), fabric unit price 42, cost buckets, `价格` (28.5 / 32), `目标价` (27 / 31).
- **Copied from upstream**: STYLE, qty, fabric spec.
- **Transformed / calculated**: `每件成本 = 面料成本 + 做工 + 印绣花 + 辅料` etc.
- **Downstream dependencies**: informs T2's booked `单价` (28 ≈ target 27; 31 = target 31) — but there is no explicit link in the file set (**INFERRED_HIGH**: match by qty-bracket).

### T4. Sampling / approvals (partially structured)

- **Docs**: A2 (buyer 1st fit), A1 (buyer PP package), F14a/b/c (confirmation photos).
- **Purpose**: the buyer signs off on fit, colour card, embroidery pattern. Our internal record of this is a **status string** in D1 (`珠片绣OK，色卡OK，产前样4/3-4/16OK`), not a table row per sample event.
- **New information created**: sample-approval statuses (free text), buyer PP file content (unstructured).
- **Copied from upstream**: — .
- **Transformed / calculated**: — .
- **Downstream dependencies**: D8 begins cutting only after PP OK — implicit precedence (**INFERRED_HIGH**).

### T5. Fabric planning (yarn → knit → dye)

Three tightly coupled sheets in one workbook:

- **D5 (投料计划)** — computes greige-fabric requirement: `单件用料/KG` × `成衣数量` = `毛坯用料合计` (0.324 × 2839 = 919.836 kg body + 12 kg trims → 931.836 kg → `购纱 950 kg`). Buffers for scouring loss (**INFERRED_HIGH**).
- **D6 (织造计划单)** — issues the knit PO to 林海织造 with the same fabric and colour.
- **D7 (拷布单)** — assigns dye lot `批号 524` to the fabric and colour `26C12344-D色丈青`.

- **New information here**: `毛门幅` (185 cm greige), `单件用料/KG` (0.324), yarn purchase spec (`32S CVC竹节 950 KG`), dye lot number (524), knit vendor (林海织造).
- **Copied from upstream**: 款号, 颜色 (with swatch code), fabric spec, 成衣数量, 客户.
- **Transformed / calculated**: yarn kg, greige kg, dye lot allocation.
- **Downstream dependencies**: D8 (cutting) consumes the dye lot; D1 `面料进度 = 3/11 投料` records the trigger event.

### T6. Cutting planning

- **Doc**: D8.
- **Purpose**: distribute the 2839 pcs across size buckets 10/12..38/40 with wastage surplus for the pieces going to embroidery; identify subcontractor 家顺 (embroidery) and 名苑 (sewing).
- **New information created**: per-size `计划发货数` and `计划裁剪数` (with ~4% wastage: 85 → 88.4, etc.), `绣花小版(100%)` and `绣花大版(110%)` embroidery scaling, 家顺 phone (13806640517).
- **Copied from upstream**: 款号, 颜色 (with swatch), 批号 (524, from D7), fabric spec, 大货数量 (2839, from D2/D5), 交货期 (5/7 stage deadline, not customer date), 生产工厂 (名苑).
- **Transformed / calculated**: `计划裁剪数 = 计划发货数 × (1 + wastage%)`.
- **Downstream dependencies**: physical cut pieces go to 家顺 → back to 名苑 → sewing → packing.

### T7. Trims / labels / packaging planning

- **Doc**: D9.
- **Purpose**: consolidate the buyer's label, hangtag, polybag, and carton-marking specs across the M7797 program.
- **New information created**: per-PO qty split (PO 728274 = 1189, PO 728275 = 1650, sum = 2839 ✓); per-size qty per PO; label copy references; hangtag placement; polybag stickering; carton marking spec.
- **Copied from upstream**: PROGRAM#, 款号, 商店款号, 颜色, 数量 (from D2), size ratio (from D2).
- **Transformed / calculated**: PO-level splits.
- **Downstream dependencies**: D10 uses PO#, colour, size ratio, and carton spec.

### T8. Packing execution

- **Doc**: D10.
- **Purpose**: record the actual pack — box by box — for the two POs.
- **New information created**: 箱号, 箱数 per row, `包装` (UPC — 601567949, 601567944, 601567886, 601567945, 601567948, 601567946, 601567950, 601567951), 每箱件数, 每箱毛重, 每箱净重, 长*宽*高, 每箱体积. Also carries `Dept = 502`.
- **Copied from upstream**: PROGRAM#, 款号, 商店款号, PO#, COLOR, size ratio (from D9).
- **Transformed / calculated**: 共计数量 = 箱数 × 每箱件数; 合计毛/净重 similarly; 体积 from dims.
- **Downstream dependencies**: shipping manifest (not in this file set).

### T9. Ship & invoice (recorded only in D1)

- **Doc**: D1 rows 171/172, columns 成衣工厂 and 开票情况.
- **Purpose**: mark the terminal statuses.
- **New information created**: actual ship date (5/22 via `5/22 郁建东发货`), invoice date (6/3), — 单价 & 金额 were created at T2.
- **Copied from upstream**: — .
- **Transformed / calculated**: — .

### Absent stages (not evidenced)

- **QC / testing actuals** — D2 records `测试要求` (BV) but no test result is in this file set.
- **In-process CMT actuals** — no per-lot cut/sew production log.
- **Wash actuals** — D0/D2 explicitly say `不水洗` for this style, so absence is by design not by gap.

---

## 4. What the file set says about "order → executable manufacturing order"

The transformation is not a single step but a **chain of specifications tightening one level at a time**:

```
Buyer commitment (BCI ← Lane Bryant)
   │  (unstructured; PDFs A1, A2)
   ▼
锦秀↔名苑 CMT contract (D2)     ← style, colour, size ratio, BOM, PP+testing spec
   │
   ├──► LAB DIP brief (D3) → dye lab work
   ├──► Art brief (D4) → embroidery vendor 家顺
   │
   ▼
Yarn purchase (D5) → Knit PO (D6) → Dye lot allocation (D7)     ← fabric identity fixed
   │
   ▼
Cutting plan (D8)     ← garment identity per size fixed
   │
   ▼
Trims/labels/packaging spec (D9) → PO split, per-size per-PO qty fixed
   │
   ▼
Packing list (D10)     ← carton identity + UPC per size + weight/volume fixed
   │
   ▼
Ship + invoice (D1 status fields)
```

Each stage **narrows the identity** of the physical product:
- After D2: identity is `(style, colour, qty)`.
- After D5–D7: identity is `(style, colour, dye_lot 524, greige batch)`.
- After D8: identity is `(style, colour, dye_lot, size)`.
- After D9: identity is `(style, colour, dye_lot, size, PO#)`.
- After D10: identity is `(style, colour, dye_lot, size, PO#, UPC, 箱号)`.

The only per-piece traceable identifier in the file set is at the carton level (箱号). Below carton, garments are fungible within (style, colour, size, PO).

---

## 5. Cross-doc reconciliation for this case

### 5.1 Quantity — 2839 pcs total (all files internally consistent)

| Doc | Field | Value | Grain |
|-----|-------|-------|-------|
| D0 | 数量 | 2679 + 160 = **2839** | per size bracket |
| D1 | 数量/件 | 2679 (R171) + 160 (R172) = **2839** | per SKU-like row |
| D2 | 数量 (sheet 1152246) | **2839** | contract total |
| D5 | 成衣数量 | **2839** | garment count for fabric calc |
| D8 | 大货数量 & 合计 | **2839** | cutting plan total |
| D9 | 总件数 | **2839** = 1189 (PO 728274) + 1650 (PO 728275) | style total; sums PO qty |
| D10 | 合计 across two PO blocks | 1189 + 1650 = **2839** | packed |

**Confidence: OBSERVED — internally consistent across seven documents.**

### 5.2 Size ratio — same 10/12..38/40 buckets, three grains

| Doc | Grain | Example |
|-----|-------|---------|
| D2 | contract qty per size, per colour | 313/338/288/250 for one colour row |
| D8 | plan-ship qty per size (across POs) | 85/564/785/726/586/48/27/18 = 2839 |
| D9 | contract qty per size, per PO | PO 728274 across sizes; PO 728275 across sizes |
| D10 | pieces per carton per size | one column per carton row |

D8's per-size total = 2839 ✓ matches D2 sheet total. **The per-PO/per-size cross-check in D9 is the natural finest-grained scheduling identity.**

### 5.3 Delivery dates — three values, three grains (post-C4 reading)

| Doc | Field | Value | Meaning |
|-----|-------|-------|---------|
| D2 | 交期 | 2026-04-20 | Contract commitment (甲/乙方-facing) — authoritative per C4 |
| D7 | 成衣交期 | 2026-04-25 | Internal dye-completion stage deadline (INFERRED_HIGH per C4) |
| D8 | 交货期 | 2026-05-07 | Internal cutting-completion stage deadline (INFERRED_HIGH per C4) |
| D1 | 交货期 | Excel 46164 = 2026-05-22 | **Revised expected delivery** as of log entry; matches actual ship (INFERRED_HIGH) |

Under C4 the 4/20 date is the authoritative contract commitment. The **5/22 date in D1 is a real schedule slip** captured in the log, not a stage deadline. **Confidence: OBSERVED for values; INFERRED_HIGH for the "slip vs stage deadline" reading.**

### 5.4 Colour — English trade name vs swatch code

| Layer | Value | Docs |
|-------|-------|------|
| Buyer-facing English | `BLUE INDIGO` (with Chinese `蓝色`) | D2, D9, D10 |
| Chinese common | `藏青` / `藏青色` / `丈青` | D1, D5, D6 |
| Dye swatch code | `26C12344-D` | D1, D7, D8 |
| Compound in D1 | `26C12344-D色丈青` | D1 |

Fact link: `BLUE INDIGO = 26C12344-D色丈青` is only made in D1 (which contains both), and even there it is embedded in one free-text cell.

### 5.5 客户 across tiers (post-C1/C7 reading)

| Doc | 客户 field | Refers to |
|-----|-----------|-----------|
| D0 | (recipient implicit) | 锦秀 (INFERRED_HIGH) |
| D1 | `锦秀/胡颖洁` | 锦秀 (乙方) + merchandiser |
| D2 | `BCI` | BCI Brands (vendor/importer; 锦秀's up-chain customer) |
| D2 | `商店 = Lane Bryant` | Brand (甲方) |
| D5/D6/D7/D8 | `锦秀公司/胡颖洁` | 锦秀 (乙方) + merchandiser |

Documents authored by us (D0, D1, D5, D6, D7, D8) put 锦秀 in `客户`; the one document authored by 锦秀 (D2) puts BCI in `客户` and 品牌 in `商店`. **The relation "my direct customer" is stable; the value it takes depends on the author.**

### 5.6 款号 across docs — dual code with variable ordering

| Doc | Cell content in this case |
|-----|---------------------------|
| D0 | `FBB54S2-997XLB` (bare) |
| D1 | `M7797    FBB54S2-997XLB 1152246` (PROGRAM# + factory + store, whitespace-separated) |
| D2 (tab) | `1152246` (store style is the sheet name) |
| D2 (cells) | `1152246（FBB54S2-997XLB）` (store-first dual, `款号` field) |
| D3, D4 | `1152246（FBB54S2-997XLB）` (store-first) |
| D5, D6, D7, D8 | `FBB54S2-997XLB` (bare) |
| D9, D10 | `FBB54S2-997XLB（商店款号1152246）` (factory-first, explicit label) |

Any join must extract both codes from the cell text; raw string equality won't work.

### 5.7 Delivery date — the one confirmed drift (revision, not error)

- Contract commit (D2, 1/30) = 4/20.
- Log entry (D1, dated 1/31 for order, updated later) = 5/22.
- Difference = ~32 days.
- Actual ship (D1 status text) = 5/22 = matches the log's revised date, not the contract date.

**Reading**: at contract time delivery was 4/20; the log was updated with a revised date as the schedule slipped; the actual ship matched the revision. This is a **revision**, not a data-error and not a stage-deadline duplicate.

**Consequence for ontology**: `contract_delivery_date` and `expected_delivery_date` are two distinct concepts, both authoritative in their own moment; a third `actual_ship_date` is captured in status text.
