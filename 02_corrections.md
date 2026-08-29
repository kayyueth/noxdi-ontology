# 02 — Corrections to Prior Interpretations

Applied from user's authoritative clarifications. Cross-reference: `01_data_inventory.md`, `01_ambiguities.md`.

| # | Prior reading (in 01_*) | Corrected reading | Source of correction |
|---|-------------------------|-------------------|----------------------|
| C1 | F1 `客户` "sometimes brand" — read as overloaded across brand / agent / merchandiser. | F1 `客户` = **外贸公司 (乙方) + 理单员 (merchandiser)**. Never brand. The three-party chain is 品牌 (甲方) → 外贸公司 (乙方) → 工厂 (丙方 = 我们 = 润悦). `客户` in every operational document authored by us (F1, F4, F5) is the vendor + their merchandiser. | User. |
| C2 | F7 `商店 = Lane Bryant` labelled "end brand" tentatively. | Confirmed: `商店 / STORE = 品牌`. Lane Bryant is the brand (甲方). | User. |
| C3 | `名苑` vs `茗苑` — flagged as probable typo; canonical spelling unknown. | Confirmed same entity. **Canonical spelling = 名苑**. `茗苑` in F7 headers is a variant to normalise. | User. |
| C4 | Three dates for FBB54S2-997XLB (F7 4/20, F5c 4/25, F4 5/7) — read as possible schedule slippage or per-stage deadlines. | **交期 = 4/20** (the F7 contract date). 4/25 and 5/7 are internal stage targets (dye completion, cutting completion), not changes to the customer-facing delivery date. | User. |
| C5 | `画稿` codes (997X / 230E / 185E / 220E) — tagged INFERRED_HIGH as likely art asset ids. | Confirmed. `画稿` **is** the linking ID to the `.ai` art master files (e.g. `997X` ↔ `997X Football sequins EMB.ai`). | User. |
| C6 | F1 columns 13 & 14 — unheaded, tagged INFERRED_HIGH as unit price / line total. | Confirmed. **Col 13 = 单价 (¥/pc)**, **Col 14 = 金额 (¥ line total)**. | User. |
| C7 | F7 `客户 = BCI` — read as likely misuse of the `客户` field (BCI mistaken for a cotton certification, or a data-entry error). | **Wrong.** `BCI` here is **BCI Brands** — a North-American apparel vendor/importer that sits between Lane Bryant (retailer/brand) and 锦秀 (sourcing/trading). The `客户` field on the contract form is filled correctly: it records the up-chain customer of the sourcing agent. The chain is: **Lane Bryant (甲方 / retailer / brand) → BCI Brands (vendor / importer) → 锦秀 (sourcing / trading, 乙方 vis-à-vis 名苑) → 润悦 (us / 丙方) → 名苑 (CMT subcontractor)**. | User. |

## Consequences of C1 + C7 (semantic shift)

Before the clarification, `客户` looked like a single overloaded field. It is actually **two structurally different fields** with the same name:

- In **our-authored documents** (F1 汇总表, F4 裁剪计划单, F5 计划单) `客户` = **our direct customer** = the 外贸公司 that placed the order with us = 锦秀 (and its merchandiser).
- In **vendor-authored documents** (F7 茗苑合同, authored by 锦秀 as PO to the sewing factory 名苑) `客户` = **the vendor's direct customer** = one hop up the chain = **BCI Brands**. The brand itself (Lane Bryant) is recorded separately as `商店`.

This is not overloading; it is the **same relational role ("my direct customer") applied at different tiers of the supply chain**. Both are correct within their respective document scopes. Any downstream data model must therefore keep the tier explicit rather than collapsing everything into a single `customer` attribute.

## Consequence of C3 (name normalisation)

Canonical vendor names to adopt going forward:

| Canonical | Variants observed | Role |
|-----------|-------------------|------|
| 名苑 | 名苑, 茗苑 | CMT (sewing) subcontractor |
| 润悦 | (宁波)润悦服饰有限公司 | Us — the primary factory / 丙方 |
| 林海织造 | 林海, 林海织造 | Knitter (织造加工) |
| 家顺 | 家顺 | Embroidery subcontractor |
| 红水 | 红水 | Wash-house (rare) |
| 锦秀 | 锦秀, 锦秀公司, 象山锦秀服饰有限公司鄞州分公司 | External trading company (this order) |
| BCI Brands | BCI | Vendor/importer (Lane Bryant's vendor) |
| Lane Bryant | Lane Bryant, LANE BRYANT | Brand / retailer |

## Consequence of C4 (single delivery date)

For the FBB54S2-997XLB dossier the authoritative delivery date is **2026-04-20**.
- `2026-04-25` in F5c 拷布单 = internal target for dye/scouring completion.
- `2026-05-07` in F4 裁剪计划单 = internal target for cutting completion.

Generalisation (INFERRED_HIGH from this correction): dates written on internal planning documents (裁剪计划单, 拷布单, 织造计划单, 投料计划) should be treated as **stage deadlines**, not customer commitments. Only F7 `交期` and F1 `交货期` carry the customer-facing delivery date.

## Consequence of C6 (F1 pricing columns are structural)

F1 columns 13 and 14 are not overflow — they are the transactional value columns and must be treated as first-class fields (`单价 ¥/pc`, `金额 ¥`) in any downstream schema, even though they carry no header text.
