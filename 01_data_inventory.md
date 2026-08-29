# 01 — Data Inventory (理单数据)

Scope: every file located under `/Users/k/Desktop/noxdi/pilot/理单/` on 2026-08-28.
Two layers of data are present:

- **Portfolio layer** — a master workbook and a quotation workbook covering many styles.
- **Single-style dossier** — folder `FBB54S2-997XLB/` containing the full document package for **one** style/order.

Confidence tags used below: **OBSERVED** = directly present, **INFERRED_HIGH** = strong inference from cell content, **INFERRED_LOW** = plausible but unverified.

---

## 0. File-level index

| # | Path | Type | Sheets | Approx. rows w/ data | Role (inferred) |
|---|------|------|--------|----------------------|-----------------|
| F1 | `2026年订单汇总表.xlsx` | Excel | `汇总表` (1) | 453 rows, ~415 substantive order lines | Master order register / running log (OBSERVED) |
| F2 | `报价2026.2.2.xlsx` | Excel | `Sheet1` (1) | 17 rows, 4 distinct STYLEs, multi-row per style | Cost sheet / quotation worksheet (INFERRED_HIGH) |
| F3 | `FBB54S2-997XLB/FBB54S2-997XLB款装箱单.xlsx` | Excel | `Sheet1`, `FBB54S2-997XLB` (2) | 35 rows on real sheet, 2 PO blocks (36 carton rows total) | Finished-goods packing list (OBSERVED) |
| F4 | `FBB54S2-997XLB/FBB54S2-997XLB裁剪计划单.xls` | Excel | `YRYTTE` (empty), `FBB54S2-997XLB` (2) | 15 rows | Cutting plan (OBSERVED) |
| F5 | `FBB54S2-997XLB/FBB54S2-997XLB计划单.xls` | Excel | `投料计划`, `织造计划单`, `拷布单` (3) | 15 / 14 / 7 rows | Yarn-feeding / knitting / dyeing plan (OBSERVED) |
| F6 | `FBB54S2-997XLB/LANE BRYANT_M7797_1152246辅料清单 更新4.3.xlsx` | Excel | `主表`, `胶袋警告语`, `纸箱-独色独码 BULK`, `追踪标主标洗标`, `价格牌袋贴`, `油光纸参考` (6) | Main table: 6 substantive rows (5 PO × color combos across 3 styles) | Trims / labels / packaging spec book (OBSERVED) |
| F7 | `FBB54S2-997XLB/M7797 茗苑合同 1.30.xls` | Excel | `1152246`, `1152530`, `1152527`, `1152492` (4) | ~15 rows per sheet, one contract per store style | Factory contract per store style (OBSERVED) |
| F8 | `FBB54S2-997XLB/M7797 茗苑色卡 1.30.xlsx` | Excel | `色卡安排` (1) | 4 style rows | LAB-DIP colour-sample brief (OBSERVED) |
| F9 | `FBB54S2-997XLB/M7797 茗苑花片 1.30.xlsx` | Excel | `色卡安排` (1) | 4 style rows | Print/embroidery art brief (OBSERVED) |
| F10 | `FBB54S2-997XLB/1152246_001_PP Production_VND2160.pdf` | PDF | — | 4.4 MB | Buyer pre-production / production spec (INFERRED_HIGH) |
| F11 | `FBB54S2-997XLB/规格样997XLB(FBB54S2-388ELB) 1ST FIT EVAL 1.21.26.pdf` | PDF | — | 2.0 MB | Buyer 1st-fit evaluation for spec sample (INFERRED_HIGH) |
| F12 | `FBB54S2-997XLB/997XLB(FBB54S2-388ELB).dxf` / `.rul` | CAD | — | pattern files | Cut pattern (OBSERVED filename), grading rule (INFERRED_HIGH) |
| F13 | `FBB54S2-997XLB/997X Football sequins EMB.ai` | Illustrator | — | 26 MB | Embroidery/sequin art master (INFERRED_HIGH) |
| F14 | `FBB54S2-997XLB/997X 珠片绣花稿.jpg`, `997XLB色卡确认.jpg`, `绣花片确认.png` | Image | — | reference photos | Confirmed art / confirmed colour card / confirmed embroidery sample (OBSERVED filename) |

PDF/CAD/AI/image files (F10–F14) are unstructured; they are catalogued only. All structured-data claims below draw from F1–F9.

---

## 1. F1 — `2026年订单汇总表.xlsx` · sheet `汇总表`

- Shape: 453 × 16. Row 0 is header; rows 1–2 are blank/banner ("2025年订单汇总"); actual records begin at row 3.
- The workbook mixes 2025 and 2026 orders in one sheet, separated by banner rows (**INFERRED_HIGH**: multiple banner rows like row 2 likely repeat further down).

### Columns

| Idx | Header | Type (inferred) | Non-null (of 450 body rows) | Example |
|-----|--------|-----------------|-----------------------------|---------|
| 0 | `客户` | text (agent + merchandiser, sometimes brand) | 370 | `锦秀/胡颖洁`, `锦维/利百加`, `亿德小仇 杰杰男装`, `长隆/毛益波` |
| 1 | `下单时间` | text-formatted date, inconsistent (`12.1`, `12/10`, `8/9`, `3.5`) | 237 | `12.1`, `12/10` |
| 2 | `款号` | text, factory style code (often carries free-text suffixes) | 385 | `FBB54S2-997XLB`, `106M324U014     小码翻单`, `DPM0174翻单2黑色卫衣`, `M7743    FNL86R2-246EM大码` |
| 3 | ` 款式图` (leading space) | embedded image via `=DISPIMG(...)` formula | 60 | `=DISPIMG("ID_...")` (WPS embedded image) |
| 4 | `面料` | free text, fabric spec with weight/composition/finish | 394 | `大身：55%棉40%涤4%氨纶绒布1%金属丝 ，270克` |
| 5 | `颜色 ` (trailing space) | free text, Chinese + English + swatch code | 412 | `Navy Duke 藏青色 + 银色金属丝 PTS9392-A`, `25T9731-C藏青2` |
| 6 | `数量/件` | integer (件) | 421 | `552`, `8202` |
| 7 | `交货期` | Excel serial date (integer) — **INFERRED_HIGH**: `45716` ≈ 2025-03-07 | 421 | `45716`, `46091` |
| 8 | `样衣进度` | free-text status with dates | 228 | `4/13寄产前样，车间生产中` |
| 9 | `面料进度` | free-text status with dates | 262 | `8/27投料`, `品质OK，色样3.26OK，面料织造中` |
| 10 | `水洗厂` | text, laundry vendor name (mostly blank) | 22 | `红水` |
| 11 | `成衣工厂` | text with date (garment plant + ship note) | 393 | `3.7出货`, `10/10(郁建东做)名苑发货` |
| 12 | `开票情况` | text with date (invoice status) | 348 | `3.24开票`, `4/18开票` |
| 13 | *unnamed* | numeric (currency) — **INFERRED_HIGH**: unit price (元/件) | 264 | `49.4`, `35.85`, `52.8` |
| 14 | *unnamed* | numeric (currency) — **INFERRED_HIGH**: line total = qty × price | 264 | `27268.8`, `129268.0` |
| 15 | *unnamed* | free text (notes / overflow) | 33 | — |

Row grain: **one row = one style × colour combination on an order** — supported by cases like rows 12–13 where 客户/下单时间/款号 are blank but colour and qty repeat (**INFERRED_HIGH**: same style, second colour, inherited from row above).

---

## 2. F2 — `报价2026.2.2.xlsx` · sheet `Sheet1`

- Shape: 17 × 18. Row 0 headers; body rows are grouped in **blocks of ~5 rows per style** — one summary row plus indented rows for extra fabrics/processes.

### Columns (row 0)

| Idx | Header | Type | Example |
|-----|--------|------|---------|
| 0 | `STYLE` | text, factory style code | `FBB54S2-997XLB`, `FJB66S5-009YLB` |
| 1 | `数量` | integer | `2679`, `160`, `950` |
| 2 | `款式图` | text (colour name in these rows) | `深蓝`, `本白` |
| 3 | `面料克重/成份` | multi-line text (composition + weight) | `Self: CVC SLUB jersey 170GSM 大身CVC 竹节汗布` |
| 4 | `克重` | text/number (grams or note) | `不水洗`, `1.4` |
| 5 | `客户用料\n码` | number (yards per garment) | `1.041`, `1.423` |
| 6 | `客户门幅` | text (fabric width) | `66"`, `58"`, `包领` |
| 7 | `光坯用料` | number (kg per garment) | `0.315`, `0.4`, `0.004` |
| 8 | `面料单价` | numeric currency | `42` |
| 9 | `面料成本` | numeric currency | `13.23` |
| 10 | `每件成本` | numeric currency | `13.4`, `17.2` |
| 11 | `做工` | numeric currency (CMT cost) | `3.8`, `4` |
| 12 | `烂花` | numeric (burnout finish cost) | `9` |
| 13 | `印绣花` | numeric (print/embroidery cost) | `6`, `2.6` |
| 14 | `辅料` | numeric (trims cost) | `1.8` |
| 15 | `合计成本` | numeric currency | — |
| 16 | `价格` | numeric currency (FOB price) — **INFERRED_HIGH** | `28.5`, `36` |
| 17 | `目标价` | numeric currency (buyer target) | `27`, `35` |

Row-grain: block-oriented; the first row of each block carries STYLE + qty + primary fabric line, subsequent indented rows list additional fabrics/processes for the **same style×size-bracket combination** (**INFERRED_HIGH**: pairs like FBB54S2-997XLB @ 2679 vs 160 are the same style at two size brackets — regular vs plus).

---

## 3. F3 — `FBB54S2-997XLB款装箱单.xlsx`

Two sheets:
- `Sheet1` — a leftover packing-list template for a different style (`DNL14R6-410SM`, PROGRAM `M5747`, buyer size XS–XXL) — appears to be an unfiltered template (**INFERRED_HIGH**).
- `FBB54S2-997XLB` — the working packing list for this style. Shape 35 × 31; the sheet contains **two PO blocks** (rows 5–14 for PO 728274, rows 22–34 for PO 728275) — same header repeated (**OBSERVED**).

### Header fields (per block)

| Field | Example | Notes |
|-------|---------|-------|
| `PROGRAM` | `M7797` | Buyer program (OBSERVED) |
| `COLOR` | `BLUE INDIGO` | English colour (OBSERVED) |
| `品名` | `女式T` (truncated), `女式T恤` | Product type (OBSERVED) |
| `款号` | `FBB54S2-997XLB（商店款号1152246）` | Dual style code (OBSERVED — one cell, two ids) |
| `PO#` | `728274`, `728275` | Buyer PO (OBSERVED) |
| `Dept` | `502` | Buyer department code (OBSERVED) |

### Per-carton row fields

| Field | Example |
|-------|---------|
| `箱号` | `1`, `4`, `5`, `8`, `9`, ... (carton no. or range like `1-13`) |
| `箱数` | `3`, `1`, `2` (# of cartons in this row) |
| `包装` | `601567949` (**INFERRED_LOW**: UPC/GTIN/SKU) |
| `尺码/颜色搭配` split into columns for buyer size buckets `10/12`, `14/16`, `18/20`, `22/24`, `26/28`, `30/32`, `34/36`, `38/40` | numbers = pieces per carton at that size |
| `每箱 配比` | qty pattern per box |
| `每箱 件数` | pieces per box |
| `共计 数量` | line total pieces |
| `每箱毛重(公斤)`, `每箱净重(公斤)` | kg |
| `合计毛重(公斤)`, `合计净重(公斤)` | kg |
| `长*宽*高(公分)` | e.g. `58*40*38` |
| `每箱体积(立方米)` | e.g. `0.08816` |

Row grain: one row = one carton or one range of identical cartons; final row per block is `合计：` (subtotal).

---

## 4. F4 — `FBB54S2-997XLB裁剪计划单.xls` · sheet `FBB54S2-997XLB`

Header-block layout (not a flat table). Fields:

| Field | Example | Confidence |
|-------|---------|------------|
| `客户` | `锦秀公司/胡颖洁` | OBSERVED |
| `款号` | `FBB54S2-997XLB` | OBSERVED |
| `品名` | `女式T恤` | OBSERVED |
| `交货期` | `2026.5.7` | OBSERVED (as text) |
| `大货数量` | `2839` | OBSERVED |
| `印绣花 / 部位 / 协作单位 / 联系方式` | `前片绣花` / `家顺` / `13806640517` | OBSERVED — outsourced embroidery vendor + phone |
| `部位` | `大身/袖子` | OBSERVED |
| `面料质地` | `32S CVC60/40竹节汗布170G(成衣）` | OBSERVED |
| `颜色` | `单染棉 26C12344-D色丈青` | OBSERVED |
| `批号/色样` | `524` | OBSERVED (dye lot no.) |
| Size buckets `10/12`..`38/40` with rows `计划发货数` and `计划裁剪数` | e.g. planned ship 85 → planned cut 88.4 (~4% surplus) | INFERRED_HIGH: surplus % for wastage |
| `合计` | `2839` / `2957.84` | OBSERVED |
| `生产工厂` | `名苑` | OBSERVED — **note**: elsewhere spelled `茗苑` |

Also lists `绣花小版(100%)` and `绣花大版(110%)` (**INFERRED_HIGH**: embroidery small/large size scaling).

---

## 5. F5 — `FBB54S2-997XLB计划单.xls`

Three sheets, one document each (header-block layout, not tabular).

### 5a. `投料计划` (yarn/greige-fabric feed plan)

Fields: `款号`, `款式简况`, `款式图`, `颜色`, `面料质地/不含新疆棉`, `毛门幅` (greige width), `部位`, `单件用料/KG`, `成衣数量`, `毛坯用料合计` (total greige kg), `备注`.
Also derives `购纱：32S CVC60/40 竹节纱：950 KG` (INFERRED_HIGH: yarn purchase requirement).

### 5b. `织造计划单` (knitting plan)

Fields: `客户`, `款号`, `织造加工` (knitter — `林海织造`), `面料质地`, `颜色`, `毛门幅`, `32S纱数量`, `毛坯布数量(KG)`, `备注`, `款式图`.

### 5c. `拷布单` (dye plan — literally "fabric scouring/dyeing sheet")

Fields: `客户`, `款号`, `成衣交期`, `日期`, `织造加工`, `批号` (dye lot), `颜色`, `面料质地`, `毛门幅`, `重量KG`, `只数` (# of rolls), `实拷KG` (actual scoured kg), `备注`.
Batch `524` reappears here — **OBSERVED cross-doc key** with F4 `批号/色样`.

---

## 6. F6 — `LANE BRYANT_M7797_1152246辅料清单 更新4.3.xlsx`

- Sheet `主表` shape 20 × 24. Actual headers on **row 1**, banner on row 0, data rows 2–6.
- Additional sheets are picture-heavy spec sheets (`胶袋警告语`, `纸箱-独色独码 BULK`, `追踪标主标洗标`, `价格牌袋贴`, `油光纸参考`); low structured content, high image content (**INFERRED_HIGH**: images inline).

### `主表` columns (row 1)

| Field | Example |
|-------|---------|
| `PHOTO` | image slot |
| `PROGRAM#` | `M7797` |
| `款号` | `FBB54S2-997XLB\n（商店款号1152246）` |
| `颜色` | `BLUE INDIGO`, `ASCENA BLACK`, `JET BLACK` |
| `PO#` | `728274`, `728275`, `729503`, `729504`, `729499` |
| `包装` | `BULK独码 绝对不能短装` |
| `10/12` … `38/40` | pieces at each buyer size |
| `数量` | PO subtotal (pieces) |
| `总件数` | style-level total pieces |
| `主标` | main-label spec (free text) |
| `洗标和追踪标` | care/tracker label spec |
| `价格牌` | hangtag spec |
| `胶袋贴纸` | polybag sticker spec |
| `油光纸` | glassine paper spec |
| `包装方法` | packing method spec |
| `胶袋` | polybag spec |
| `STORE` | (empty in observed data) |

Row-grain: **one row = one style × colour × PO** (**OBSERVED**: rows 2–3 are same style/colour, two POs).

**Cross-style scope**: this workbook covers **3 factory styles** (`FBB54S2-997XLB` / `FBB95S4-230ELB` / `FBB83S9-294CB`) = 3 store styles (`1152246` / `1152530` / `1152526`) — despite the filename naming only 1152246 (**INFERRED_HIGH**: file is scoped to the whole M7797 program).

---

## 7. F7 — `M7797 茗苑合同 1.30.xls`

- 4 sheets, tab names are **buyer store style numbers**: `1152246`, `1152530`, `1152527`, `1152492`. Each sheet is a printable contract (header block, not a flat table).

### Fields per contract sheet

| Field | Example |
|-------|---------|
| `PROGRAM#` | `M7797` |
| `款号` | `1152246\n（FBB54S2-997XLB）` — **dual code** in one cell |
| `客户` | `BCI` — **inconsistent usage**: BCI is a cotton certification, not a customer (see §Ambiguities) |
| `商店` | `Lane Bryant` |
| `品名` | `T恤`, `绒衫` |
| `数量` | `2839`, `1300`, `1200`, `4718` |
| `交期` | `2026-04-20 00:00:00` (proper date) |
| `测试要求` | free text |
| `款式图` (banner) | image slot |
| `工艺要求` | e.g. `1.裁片前片珠片绣` / `1.裁片印花` / `1.成衣烂花+成衣印花` |
| `序号 / 部位 / 面辅料 / 颜色` | material lines (本身布, 罗纹, ...) |
| `颜色` (label) | `BLUE INDIGO（蓝色）`, `BLACK（黑色）`, `OATMEAL（燕麦色）`, `HOLLYHOCK（紫色）` |
| `CUSTOMER PO#` | PO number (some `待定`) |
| `包装和UPS#` | packing + UPC (**INFERRED_HIGH**: "UPS#" is a typo of "UPC#") |
| Size buckets `10/12`..`38/40` | pieces per size |
| `总计` | style×colour total |
| `茗苑` | factory brand marker (**OBSERVED**) |

Sheet-per-store-style is the grain. Multiple colour blocks per sheet.

**Store style ↔ factory style pairs observed here**:

| 商店款号 | 款号 (factory) | Colour | Qty |
|----------|----------------|--------|-----|
| 1152246 | FBB54S2-997XLB | BLUE INDIGO | 2839 (2679 + 160) |
| 1152530 | FBB95S4-230ELB | BLACK | 1300 (1140 + 160) |
| 1152527 | FJB66S5-185ELB | OATMEAL | 1200 |
| 1152492 | FJB66S5-220ELB | HOLLYHOCK | 4718 (4558 + 160) |

Note: F6 also references `1152526 / FBB83S9-294CB / JET BLACK` at 950 pcs — **not present as a sheet in F7** (**OBSERVED discrepancy**; see Ambiguities).

---

## 8. F8 — `M7797 茗苑色卡 1.30.xlsx` · sheet `色卡安排` (LAB DIP)

- Shape ~12 × 4. Headers on row 2.

| Field | Example |
|-------|---------|
| `面料信息` | `本身布：蓝色，染棉，CVC 60棉40涤竹节汗布，克重170gsm` |
| `客样` | `有客样` / `有客样烂后色标` |
| `色号` | `按照客样颜色出色卡` |
| `款号` | `1152246\n（FBB54S2-997XLB）` |

One row per store style; also mentions merchandiser `胡颖洁` and a serial number `46052` (**INFERRED_LOW**: internal request number or Excel date-serial ~2026-01-28).

---

## 9. F9 — `M7797 茗苑花片 1.30.xlsx` · sheet `色卡安排`

Same layout as F8 (sheet name is left over — **INFERRED_HIGH**: copied template).

| Field | Example |
|-------|---------|
| `面料信息` | (same fabric strings as F8) |
| `画稿` | `997X`, `230E`, `185E`, `220E` — art file references (**INFERRED_HIGH**: match design filenames like `997X Football sequins EMB.ai`) |
| `要求` | `按照客样绣花位置品质和颜色安排最类似的5个花片给客人确认` |
| `款号` | dual code, same as F8 |

---

## 10. Nested / hierarchical structure (as observed)

```
Buyer (Lane Bryant)                              [F6, F7]
 └─ PROGRAM (M7797)                              [F6, F7, F3]
     └─ Store Style / 商店款号 (1152246)          [F6, F7, F8, F9]
         ├─ Factory Style / 款号 (FBB54S2-997XLB) [F1, F2, F3, F4, F5, F6, F7]
         │   ├─ Color (BLUE INDIGO / 藏青)        [F1, F3, F4, F6, F7]
         │   │   └─ PO# (728274, 728275)          [F3, F6, F7]
         │   │       └─ Size bucket (10/12 … 38/40) → qty  [F3, F6, F7]
         │   │           └─ Carton (箱号 1..N)     [F3]
         │   ├─ BOM lines (本身布 / 罗纹 / 辅料 …) [F2, F7]
         │   ├─ Cutting plan (dye lot 524)        [F4]
         │   ├─ Yarn plan / Knit plan / Dye plan  [F5]
         │   ├─ LAB DIP request                   [F8]
         │   └─ Print/embroidery art request      [F9]
         └─ Vendors: 名苑/茗苑 (CMT), 林海 (knit),
                     红水 (wash), 家顺 (embroidery) [F1, F4, F5]
```

Row-grain summary per source:

| Source | One row = |
|--------|-----------|
| F1 汇总表 | one style × colour on an order (line item) |
| F2 报价 | one cost line of a style; blocks group into one style×size-bracket quote |
| F3 装箱单 | one carton (or a run of identical cartons) |
| F4 裁剪计划单 | header block; each fabric×colour is a row, then plan-ship vs plan-cut sub-rows |
| F5-a 投料计划 | one fabric/component of a style |
| F5-b 织造计划单 | one fabric of a style at one knitter |
| F5-c 拷布单 | one dye lot |
| F6 辅料主表 | one style × colour × PO for trims/labels/packaging |
| F7 合同 | one sheet = one store style; body rows = colour/PO lines |
| F8/F9 | one store style (LAB-DIP / art request) |

---

## 11. Frequency of missing / sparse values (F1, computed)

Body = rows 3–452 (450 rows).

| Column | Non-null / 450 | % filled |
|--------|----------------|----------|
| 客户 | 370 | 82% |
| 下单时间 | 237 | 53% |
| 款号 | 385 | 86% |
| 款式图 | 60 | 13% |
| 面料 | 394 | 88% |
| 颜色 | 412 | 92% |
| 数量/件 | 421 | 94% |
| 交货期 | 421 | 94% |
| 样衣进度 | 228 | 51% |
| 面料进度 | 262 | 58% |
| 水洗厂 | 22 | 5% |
| 成衣工厂 | 393 | 87% |
| 开票情况 | 348 | 77% |
| col13 (≈单价) | 264 | 59% |
| col14 (≈金额) | 264 | 59% |
| col15 (notes) | 33 | 7% |

Interpretation (**INFERRED_HIGH**): blanks in 客户/下单时间/款号 mostly reflect "same-as-row-above" continuation for multi-colour orders, not true missing data. 水洗厂 low fill = most orders don't need washing. col13/14 nulls likely reflect quotes not yet booked.

For F2–F9 the row counts are small enough that missing-value % is not meaningful; sparse cells are documented per-field above.

---

## 12. What is **not** here

- No transactional shipping / invoice ledger separate from F1's 开票情况 text status.
- No structured customer / vendor master (all names are free-text inside cells).
- No SKU/UPC master table — UPC numbers appear inside `包装` cells in F3 and inside `包装和UPS#` in F7 but never as a normalized field.
- No time-series QC / test-result data — only free-text 测试要求.
- No accounting / receivables data — 开票情况 is a status note only.

This inventory is descriptive; it does not attempt to reconcile identifiers or design an ontology (that is the next step).
