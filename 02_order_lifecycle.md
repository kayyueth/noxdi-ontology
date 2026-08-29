# 02 — Order Lifecycle (理单 process)

Scope: what happens to an order from inquiry through invoicing, expressed as **stages × actors × artifacts**. Evidence base = the 9 structured files in `01_data_inventory.md`, updated by the clarifications in `02_corrections.md`.

Confidence tags as before: **OBSERVED** = directly present in the sources, **INFERRED_HIGH** = strong inference, **INFERRED_LOW** = plausible but unverified.

---

## 0. Actors and supply-chain tiers

```
甲方  Retailer / Brand ─── Lane Bryant
        │
乙方₁  Vendor / Importer ── BCI Brands           ← records in F7 客户
        │
乙方₂  Sourcing / Trading ─ 锦秀 (merchandiser 胡颖洁 / 郑飞飞 …)   ← records in F1/F4/F5 客户
        │
丙方   Factory (us) ─────── 润悦 (宁波润悦服饰有限公司)
        │
        ├─ Knit subcontractor ── 林海织造          ← F5b, F5c 织造加工
        ├─ Dye / scour ─────── (in-house or 林海) ← F5c
        ├─ Embroidery / print ── 家顺 (per style)  ← F4 协作单位
        ├─ CMT / sewing ────── 名苑 (canonical)   ← F1 成衣工厂, F4 生产工厂, F7 header
        └─ Wash (occasional) ── 红水              ← F1 水洗厂
```

Every subcontractor lives one hop below 润悦. All identifiers observed today are informal (Chinese short names, no codes). **INFERRED_HIGH**: a formal vendor master does not exist yet.

---

## 1. Stage map

The lifecycle below is the union of what the 9 structured files record. Not every order touches every stage (`水洗` is rare; embroidery/print only fires when the style has art).

| # | Stage | Owner | Primary artifact(s) | Key output |
|---|-------|-------|---------------------|------------|
| S1 | **询价 / 报价** Quote | 润悦 → 锦秀 | F2 `报价2026.2.2.xlsx` | Per-style quote: fabric, yardage/weight, cost breakdown, FOB price, target price |
| S2 | **接单 / 合同** Order booked | 锦秀 → 润悦 | F1 `2026年订单汇总表.xlsx` (line entry); F7 `M7797 茗苑合同 1.30.xls` (formal contract 锦秀→名苑 for the CMT tier) | Order record with 款号, 颜色, 数量, 单价, 金额, 交货期; separate CMT contract with size ratios and PO list |
| S3 | **产前样 / 样衣** Sampling | 润悦 (own sample room) → 锦秀 → BCI/LB | F1 col `样衣进度` free-text status; PDFs F10, F11 (buyer 1st-fit & PP evaluation) | Sample approval / spec sign-off |
| S4 | **色卡 (LAB DIP)** Colour approval | 润悦 dye lab → 锦秀 → 甲/乙方 | F8 `M7797 茗苑色卡 1.30.xlsx` | LAB-DIP submission brief, one row per store style |
| S5 | **花片 / 印绣花稿** Art approval | 润悦 → 家顺 / print vendor → buyer | F9 `M7797 茗苑花片 1.30.xlsx`; F13 `997X Football sequins EMB.ai`; F14 confirmation photos | Approved art (画稿 code links workbook row to `.ai` master) |
| S6 | **投料 / 购纱** Yarn purchasing | 润悦 → yarn supplier | F5a `投料计划` sheet | Yarn requirement (kg) — e.g. 32S CVC竹节 950 KG |
| S7 | **织造** Knitting | 润悦 → 林海织造 | F5b `织造计划单` sheet | Greige fabric (kg, width), per fabric + colour |
| S8 | **染色 / 拷布** Dyeing / scouring | 润悦 dye plan → 林海 (or in-house) | F5c `拷布单` sheet | Dye lot 批号 (e.g. 524) linked to colour + swatch |
| S9 | **面料到厂 / 检验** Fabric in | 润悦 QC | F1 col `面料进度` free-text status | Fabric ready flag |
| S10 | **裁剪** Cutting | 润悦 cutting room | F4 `裁剪计划单` | Per-size 计划发货数 + 计划裁剪数 (with ~4% surplus; embroidery pieces use 100%/110% small/large-size versions) |
| S11 | **印绣花** Embroidery/print (subcontract) | 润悦 → 家顺 (per F4) | F4 header `协作单位` + `联系方式`; embroidered pieces confirmed via F14 photos | Embroidered/printed cut pieces returned |
| S12 | **车缝 (CMT)** Sewing | 润悦 → 名苑 | F1 `成衣工厂` free-text status text (e.g. "10/10 名苑发货"); F7 header `茗苑`→ 名苑 | Finished garments |
| S13 | **水洗** Wash (conditional) | 润悦 → 红水 | F1 `水洗厂` (only 22 of 450 rows) | Washed garments |
| S14 | **测试** Testing | 3rd party (BV per F7 `测试要求`) | F7 `测试要求` free-text | Test report (unstructured; not stored in these files) |
| S15 | **辅料 / 贴标 / 包装** Trims & pack | 名苑 (using 辅料清单 issued by 润悦) | F6 `LANE BRYANT_M7797_1152246辅料清单 更新4.3.xlsx` — main table + 5 spec sheets | Labels, hangtags, polybag stickers, cartons |
| S16 | **装箱** Cartoning | 名苑 | F3 `FBB54S2-997XLB款装箱单.xlsx` (real sheet, ignoring template Sheet1) | Per-carton pack: PO#, 箱号, 尺码搭配, 每箱件数, 毛/净重, 尺寸, 体积 |
| S17 | **出货** Shipping | 名苑 → 锦秀 → BCI → LB | F1 col `成衣工厂` free-text with ship note (e.g. "3.7 出货", "5/2 出货") | Shipment date |
| S18 | **开票** Invoicing | 润悦 accounting | F1 col `开票情况` free-text with date (e.g. "3.24开票"); F1 cols 13/14 = 单价, 金额 | Invoice date and amount |

Stages S3–S15 can overlap; S6–S8 run in parallel per fabric per colour. Stages S10 and S11 interleave because embroidery is done on cut pieces (INFERRED_HIGH from F4's `绣花小版(100%) / 绣花大版(110%)` note that already knows garment size at cut).

---

## 2. Timeline (this dossier: FBB54S2-997XLB / M7797 / 1152246, LB)

Reconstructed from date fields across F1–F7 (dates in text form kept as-is):

| Date | Stage | Evidence |
|------|-------|----------|
| 2026-02-02 | S1 Quote issued | F2 filename (`报价2026.2.2.xlsx`) |
| 2026-01-30 | S2 Contract prep | F7 filename (`M7797 茗苑合同 1.30.xls`); F8/F9 same-day briefs |
| 2026-03-10 | S6/S8 Plans issued | F5a `投料计划` footer `2026.3.10`; F5c 拷布单 `日期 2026.3.10` |
| 2026-03-19 | S7 Knit plan | F5b `织造计划单` footer `2026.3.19` |
| 2026-03-21 | S10 Cutting plan prepared | F4 file mtime `Mar 21 14:51` |
| 2026-04-03 | S15 Trims booklet updated | F6 filename tail `更新4.3.xlsx` |
| 2026-04-16 | Buyer PP evaluation | F10 file mtime |
| 2026-04-20 | **S17 Contract 交期** | F7 `交期 = 2026-04-20` (**authoritative**, per C4) |
| 2026-04-25 | S8 dye-completion internal target | F5c `成衣交期 2026.4.25` (mis-labelled — it is an internal deadline, not the shipping date) |
| 2026-04-25 / 04-26 | S16 Packing list prepared | F3 file mtime `Apr 26 08:12` |
| 2026-05-07 | S10 Cutting-completion internal target | F4 `交货期 2026.5.7` (internal, not customer date) |

The three "delivery-like" dates therefore fan out backwards from **04-20** into stage-level checkpoints; earlier internal analysis that treated them as three competing delivery dates is retracted (see C4).

---

## 3. Data hand-off matrix

Rows = document types, columns = who authors → who consumes.

| Doc | Authored by | Handed to | Round-trip? |
|-----|-------------|-----------|-------------|
| F2 报价 | 润悦 (报价员) | 锦秀 | Yes — updated on requote |
| F1 汇总表 | 润悦 (理单员) | Internal only (锦秀 does not read this) | No — running log |
| F7 茗苑合同 | 锦秀 (merchandiser 胡颖洁) | 名苑 (via 润悦) | Signed once, not versioned in-file |
| F8 茗苑色卡 | 锦秀 | 润悦 dye lab | One-shot brief |
| F9 茗苑花片 | 锦秀 | 润悦 / embroidery vendor | One-shot brief |
| F5a/b/c 计划单 | 润悦 (计划员) | 林海 (knit), in-house dye, purchasing | Not versioned; one-shot |
| F4 裁剪计划单 | 润悦 (cutting) | 家顺 (embroidery), 名苑 (sewing) | One-shot |
| F6 辅料清单 | 名苑 / buyer + 锦秀 | 名苑 | Versioned in filename (`更新4.3`) |
| F3 装箱单 | 名苑 | 锦秀 → BCI → LB | Filled after packing complete |

Everything is passed as an **Excel/PDF file** by messaging / email. There is no shared database. **INFERRED_HIGH**: this is the mechanism by which the same fact (交期, 数量, 款号) gets duplicated into 8+ documents.

---

## 4. Where new information first appears vs is re-keyed

`+` = the field originates at this stage; `=` = the field is copied in / restated; `*` = derived (calculated).

| Field | S1 报价 | S2 接单/合同 | S3-S5 样/色/花 | S6-S9 面料 | S10 裁剪 | S12 CMT | S15 辅料 | S16 装箱 | S17-S18 出货/开票 |
|-------|--------|-------------|---------------|-----------|---------|---------|---------|---------|-------------------|
| 款号 (factory) | + | = | = | = | = | = | = | = | = |
| 商店款号 | — | + (F7 header) | = | — | — | — | = | = | — |
| PROGRAM# | — | + (F7) | — | — | — | — | = | = | — |
| 品牌 (Lane Bryant) | + (implicit, style code prefix)| + (F7 商店) | — | — | — | — | = (F6 filename) | — | — |
| BCI (vendor) | — | + (F7 客户) | — | — | — | — | — | — | — |
| 锦秀 (外贸公司) | + (F2 recipient) | + (F1 客户) | + | + | + | + | + | + | + |
| 名苑 (CMT) | — | + (F7 茗苑) | — | — | + (F4 生产工厂) | + | + | + (F3 header 锦秀) | + (F1 成衣工厂) |
| 林海 (knit) | — | — | — | + (F5b) | — | — | — | — | — |
| 家顺 (embroidery) | — | — | + (F9 via art) | — | + (F4 协作单位) | — | — | — | — |
| 面料 spec | + (F2) | = (F7 BOM 本身布) | = (F8 面料信息) | = (F5) | = (F4) | — | — | — | — |
| 颜色 (English + code) | — | + (F7) | = (F8 客样) | + (F5c 批号) | = (F4) | — | = (F6) | = (F3) | — |
| 批号 (dye lot) | — | — | — | + (F5c) | = (F4) | — | — | — | — |
| 数量 (bulk) | + (F2 数量) | = (F7 数量) | — | = (F5a 成衣数量) | = (F4 大货数量) | — | = (F6 总件数) | = (F3 合计) | — |
| 尺码配比 (10/12..38/40) | — | + (F7) | — | — | = (F4) | — | = (F6) | = (F3, exploded per carton) | — |
| PO# | — | + (F7 CUSTOMER PO#) | — | — | — | — | = (F6 PO#) | = (F3 PO#) | — |
| UPC (`包装` numeric) | — | + (F7 包装和UPS#, often 待定) | — | — | — | — | — | + (F3 `包装`) | — |
| Dept | — | — | — | — | — | — | — | + (F3 Dept) | — |
| 单件用料/克重 | + (F2 客户用料码, 光坯用料) | — | — | = (F5a 单件用料/KG) | — | — | — | — | — |
| 毛门幅 | + (F2 客户门幅) | — | — | = (F5a/b) | — | — | — | — | — |
| 单价 ¥/pc | + (F2 价格) | — | — | — | — | — | — | — | = (F1 col13) |
| 金额 ¥ (line) | — | — | — | — | — | — | — | — | * (F1 col14 = qty × col13) |
| 每箱毛/净重, 体积 | — | — | — | — | — | — | — | + (F3) | — |
| 主标 / 洗标 / 价格牌 / 胶袋 spec | — | — | — | — | — | — | + (F6) | — | — |
| 测试要求 (BV) | — | + (F7) | — | — | — | — | — | — | — |
| 样衣进度 | — | — | + (F1 样衣进度 free text) | — | — | — | — | — | — |
| 面料进度 | — | — | — | + (F1 面料进度) | — | — | — | — | — |
| 出货日期 | — | — | — | — | — | — | — | — | + (F1 成衣工厂 free text) |
| 开票日期 | — | — | — | — | — | — | — | — | + (F1 开票情况) |

Observations:
- **Six fields originate in F1 alone**: 客户 (external vendor+merchandiser), 下单时间, 单价, 金额, 出货 status text, 开票 status text. None are re-emitted downstream.
- **Six fields originate in F7 alone**: PROGRAM#, 商店款号, 品牌 (商店), BCI (客户), 测试要求, CUSTOMER PO#.
- **Fabric spec, colour, and quantity** are re-keyed into 5+ documents. This is the primary drift risk.
- **UPC** is created only at packing (F3). The F7 slot for it is almost always `待定`.
- **The dye lot 批号** is the only fabric-level identifier that reaches the cutting doc, and it is the natural fabric-to-garment traceability key (INFERRED_HIGH).

---

## 5. Where the process breaks (as-is)

Not recommendations — just what the current file set already reveals.

1. **No shared identifier for a "line item"**. An order line for (`FBB54S2-997XLB`, `BLUE INDIGO`, PO 728274) has no persistent id. Every document restates the compound key by copying columns.
2. **UPC is missing at contract time** (`待定` in F7) and is instead first written into packing (F3). Anything that needs UPC before packing is blocked.
3. **Delivery / stage dates are conflated** into one label (`交期` / `交货期`). C4 says only F7's is customer-facing, but the internal docs (F4, F5c) reuse the same word for stage deadlines. Nothing in the schema itself distinguishes the two.
4. **Vendor names live as free text**, including transliteration variants (名苑 / 茗苑) and homophone typos (毛益波 / 毛意波). Joining on vendor requires fuzzy matching.
5. **Cost, quote, and invoice live in different files** with no explicit link. Cross-checking quoted price (F2 `价格`) vs invoiced unit price (F1 col 13) has to be done manually.
6. **F1's ` 款式图` column** carries `=DISPIMG(...)` formulas, which do not export cleanly outside WPS; the visual key most humans use to identify a style is not machine-readable.
7. **F3 leaves a template `Sheet1`** for an unrelated style intact. The dossier folder is a copy of a template; other style dossiers likely carry the same "leftover" contamination (INFERRED_HIGH).
8. **F6 covers 3 styles, F7 covers 4 styles, and one style (`1152526`) appears only in F6 not F7**. Program-level completeness cannot be checked from any single file.

These are the structural facts that any ontology / data model has to solve for. Design work follows in step 03.
