# 02 — Unresolved Business Questions (case: FBB54S2-997XLB / 1152246 / M7797)

Every open question below is grounded in a specific piece of evidence from the case files. None are speculative wishlist items. Rank:

- **P0** — blocks ontology design (must resolve before entity model can be finalised)
- **P1** — important but ontology can proceed with an interim decision
- **P2** — minor clarification, cosmetic or edge-case

P0 count capped at 10 per instructions.

---

## P0 — blocking questions (max 10)

### P0-1. Is there a canonical "line item" identity below (style × colour × PO)?

Evidence: `D1 R171` (2679 pc @ ¥28) and `D1 R172` (160 pc @ ¥31) are the same style, same colour, same PO group, but split into two lines by **size-bracket premium pricing**. Meanwhile, D9 splits the same 2839 pcs into two lines by **PO number** (728274 = 1189; 728275 = 1650). Two different "line item" concepts coexist:
- **pricing line** (regular vs plus-size bracket)
- **PO line** (buyer's PO split)

Neither cross-references the other. Which is the ontology's canonical "OrderLine" — or does the model need both?

Blocks: `OrderLine` entity design, pricing model.

### P0-2. Which price is the "committed" price — quote, target, or booked?

Evidence for regular bracket: `D0 价格 = 28.5`, `D0 目标价 = 27`, `D1 col13 = 28.0`. For plus: `D0 价格 = 32`, `D0 目标价 = 31`, `D1 col13 = 31.0`. The **booked** price in D1 matches the buyer's target for plus and sits between quote and target for regular. No single document declares one canonical.

Blocks: `Price` entity design, quote-to-invoice reconciliation.

### P0-3. What is the authoritative delivery-date concept — commitment, expected, or actual?

Post-C4 we know 4/20 is the **contract commitment** and 5/22 is the **actual ship**. Between them, D1 already stored 5/22 as `交货期` (Excel serial 46164) — i.e. the log field was updated to reflect the revision. Ontology must decide whether to model:
- (a) one `delivery_date` field that gets overwritten as revisions land, or
- (b) `contract_delivery_date` + `expected_delivery_date` + `actual_ship_date` as three distinct concepts.

Evidence for (b) is stronger (D2's 4/20 was never overwritten; D1's 5/22 was authored later). Ambiguity: at what event does D1's 交货期 get set — at initial booking or at revision?

Blocks: `Order` / `Shipment` schema, revision-tracking pattern.

### P0-4. Is the pair (锦秀, 名苑) always fixed at the program level, or per-style?

Evidence: this case has 锦秀 as sourcing and 名苑 as CMT for **every** style in M7797 (D2 has 4 tabs all headed 茗苑; D8 生产工厂 = 名苑). But we cannot tell from one case whether the vendor pair is chosen per-program or per-style. Impacts whether `(sourcing_trading, cmt_subcontractor)` attaches to `Program`, `Style`, or `Order`.

Blocks: party-model attachment level.

### P0-5. Is `买家 PO` an attribute of the order or of the shipment?

Evidence: D2's `CUSTOMER PO#` slot is present but `待定`. PO numbers 728274 / 728275 first appear at D9 (trims spec, dated 4/3) and are then reused in D10 (packing, dated 4/26). This is **long after** the fabric/dye/cut plans (D5/D7/D8, dated 3/10-3/21) which never carry PO. So PO cannot join to fabric or cutting rows at all. Is PO a shipment/packing attribute rather than an order attribute?

Blocks: whether `PO` sits under `Order` or under `Shipment`.

### P0-6. What is the natural key for `Colour` — English trade name, Chinese common name, or swatch code?

Evidence: same physical colour surfaces as `BLUE INDIGO` (D2/D9/D10 — buyer-facing), `藏青` (D5/D6 — planning), `丈青` (D7/D8/D1 — dye/cut), `26C12344-D` (D7/D8/D1 — swatch). The **only** cell where all four coexist is D1's free-text `颜色` cell `26C12344-D色丈青` (partially). No document declares `BLUE INDIGO = 26C12344-D`.

Blocks: `Colour` entity key.

### P0-7. Is `Dye lot 批号` scoped to (style × colour) or is it a fabric-level identifier that can be reused across styles?

Evidence: `批号 524` appears only in D7 and D8 in this case. Its scope beyond this order cannot be seen. If it is fabric-level (one dye run may cut multiple styles), the ontology must attach it to `FabricBatch`, not `Style`.

Blocks: dye-lot entity level.

### P0-8. Is `Program` an attribute of the order or a first-class entity across orders?

Evidence: `M7797` groups 4 store styles (per D2 tabs) but D6 shows F1 rows for `M7797` at various 下单时间 within a range (1/31 to 2/5) — i.e. one program spans several booked orders. Yet no document treats Program as a standalone record; it always tags a style.

Blocks: whether `Program` is a top-level entity with lifecycle events, or just a tag.

### P0-9. Is `store_style_code` (1152246) always 1-to-1 with `factory_style_code` (FBB54S2-997XLB), or can one map to many?

Evidence: this case shows 1-to-1. But A2 (`规格样997XLB(FBB54S2-388ELB)`) references a **different** factory style code (`FBB54S2-388ELB`) as the "spec sample" underlying the same 997XLB base. It looks like the spec sample used a superseded factory code and the current bulk uses the new one. If store style ↔ factory style is 1-to-many across style revisions, the ontology needs a `StyleRevision` layer.

Blocks: style hierarchy.

### P0-10. How is `size_ratio_scheme` chosen — per brand, per program, or per style?

Evidence: this case uses buyer plus-size ratios `10/12..38/40`. F3's leftover `Sheet1` for a **different** style (`DNL14R6-410SM`) uses `XS/S/M/L/XL/XXL`. Both come out of the same factory. Whether the size scheme attaches to `Brand` / `Program` / `Style` decides where the enum lives.

Blocks: `SizeScheme` attachment level.

---

## P1 — important, but ontology can proceed with an interim decision

### P1-1. Are 家顺 (embroidery) and 林海 (knit) assigned per-style or per-program?

Only present for this style; other cases would help decide.

### P1-2. What is the exact rule for `计划裁剪数 = 计划发货数 × k`?

Observed k values in D8: 88.4/85 = 1.040, 586.56/564 = 1.040, 816.4/785 = 1.040, 755.04/726 = 1.040, 609.44/586 = 1.040, 51/48 = 1.0625, 30/27 = 1.111, 21/18 = 1.166. The wastage multiplier **rises for small size counts** — bespoke minimums, not a flat 4%. What is the rule?

### P1-3. Is `品名` (T恤 vs 女式T恤 vs 女式T) enumerable, or free-text?

Only three variants seen for one physical product. Ontology needs a controlled vocabulary or must accept text.

### P1-4. Is the `包装` mode `BULK独码` an enum or free text?

D9/D10 both use `BULK独码 绝对不能短装`. Other packing modes are hinted at (mixed-pack, ratio pack) but not evidenced in this case.

### P1-5. Is `Dept 502` a Lane Bryant department code or a routing code?

Only in D10. If it applies to whole PO×style rows, it should attach to `PO`; if per-carton, to `Carton`.

### P1-6. Does `郁建东` in D1 status text denote a person, a warehouse, or a shipping vendor?

Row 100 in F1 already showed `10/10(郁建东做)名苑发货` — where `郁建东做` reads as "made by 郁建东", suggesting a CMT operator. For this case, `5/22 郁建东发货` — is 郁建东 the operator or the shipper?

### P1-7. What links `画稿 997X` to the `.dxf` pattern file `997XLB(FBB54S2-388ELB).dxf`?

Both filenames share `997X` / `997XLB`. Is `997XLB` a factory-family code that groups art + pattern + style?

### P1-8. Is `购纱要求 950 kg` inclusive of buffer, or exact?

D5 计算: 0.324 × 2839 + 12 = 931.836. Actual yarn purchase: 950 kg = ~2% buffer above the computed greige. Is 2% a policy or an approximation?

### P1-9. How are 主标 / 洗标 / 价格牌 stored — as a template referenced by style, or as inline text per PO?

D9 says `内容见附页` — the actual label content lives outside the main table. Ontology should probably model `LabelTemplate` as an external reference.

### P1-10. Is the `不含新疆棉` clause a program-wide compliance flag or per-style?

Only baked into D5's header for this order. Does it apply program-wide (M7797), brand-wide (Lane Bryant), or per-style?

---

## P2 — minor clarifications

### P2-1. Excel serial `46052` in the footer of D3 and D4 — order-request date, doc number, or something else?

Excel serial 46052 = 2026-01-28. Could be the request-received date (2 days before the doc was authored on 1/30).

### P2-2. Spelling of merchandiser: `胡颖洁` — is this the same person as `胡颖洁` elsewhere in F1 (e.g. R100, R150, R200)?

Almost certainly yes (identical characters). Confirming avoids duplicate person records.

### P2-3. Are the `每箱毛重` and `每箱净重` per-carton values templates keyed off `(size, pieces_per_carton, packing_material)`?

E.g. size 22/24 @ 68 pcs → 13 kg gross / 12 kg net (D10 R8). If yes, gross/net can be derived rather than stored.

### P2-4. Is the `绣花大版(110%)` vs `绣花小版(100%)` mapping consistent for all sizes across all styles?

Only two size groups labelled in D8. May be a per-style rule.

### P2-5. Are the confirmation photos (A6/A7/A8) filed against a single approval "event" or multiple?

Three files, three moments (色卡, 花片, 珠片绣) captured in D1's 样衣进度 as `珠片绣OK，色卡OK`. Ontology may want an `Approval` entity that groups the photos with a timestamp per approval type.

---

## Summary

- **10 P0 questions** — all trace to a real ambiguity visible in this case's evidence.
- **10 P1 questions** — can proceed with a marked interim assumption.
- **5 P2 questions** — cosmetic; will only affect edge modelling choices.

All P0/P1/P2 items are proposed for user validation before ontology design begins.
