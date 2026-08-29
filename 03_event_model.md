# 03 — Event Model (Layer 6)

Workflow is modelled as **first-class `StageEvent` objects**, not as scattered status columns. This document catalogs the 17 event types v0.1 supports, their evidence anchor for the case, and the discipline for distinguishing planned / actual / deadline states.

Scope rule (repeated for emphasis): **do not fabricate an event that only has planning evidence**. If a document tells us the plan but no cell records that the plan happened, we record a `StageEvent` with `status=PLANNED` and `actual_date=null`, not a completed event.

---

## 1. `StageEvent` schema

```
StageEvent {
  event_id            : composite
  event_type          : enum (17 values, §3)
  affected_object_ref : ref(any) — the entity this event happens to
  planned_date        : date | null
  actual_date         : date | null
  status              : enum (PLANNED | IN_PROGRESS | DONE | REVISED | CANCELLED)
  source_document_ref : ref(Document)
  raw_evidence_text   : text — the raw cell / field the date came from
  confidence          : enum (OBSERVED | INFERRED_HIGH | INFERRED_LOW)
}
```

`StageDeadline` is a **specialisation** with `event_type` ending in `_DEADLINE`, `actual_date` always `null`, `status = PLANNED`. Deadlines exist to model D7's `成衣交期 = 4/25` and D8's `交货期 = 5/7` under the C4 clarification — they are internal targets, not delivery dates.

---

## 2. Status semantics

| Status | When to use | Data pattern |
|--------|-------------|--------------|
| PLANNED | Only a planning doc exists; no execution evidence. | `planned_date` present, `actual_date` null. |
| IN_PROGRESS | Status text says work has started but not completed. | E.g. D1 `样衣进度` free text says "车间生产中". |
| DONE | Actual completion is captured. | `actual_date` present. |
| REVISED | A later document changes a date already recorded. | E.g. D2 交期 4/20 → D1 交货期 5/22. Model as **two events**: original DONE-PLANNED at 4/20 REVISED, plus a new event with the new date. |
| CANCELLED | The step is not going to happen. | E.g. WASH for this style — explicitly `不水洗` in D0 and D2. |

---

## 3. Event-type catalog (17)

Each row lists the event type, the entity it usually affects, and the strongest evidence for the case FBB54S2-997XLB / 1152246 / M7797. When the case yields only a plan and no actual, that is noted explicitly.

| # | event_type | affected entity | planned_date evidence | actual_date evidence | status observed for this case |
|---|-----------|-----------------|----------------------|----------------------|-------------------------------|
| 1 | `QuoteIssued` | `PricingLine` | D0 filename `2026.2.2` | D0 (act of issuing the quote) | DONE at 2026-02-02 |
| 2 | `OrderBooked` | `StyleOrder` | D1 `下单时间 = 1/31` | D1 `下单时间 = 1/31` (booking is the act itself) | DONE at 2026-01-31 |
| 3 | `ContractConfirmed` | `Contract` | D2 filename `1.30` | D2 filename `1.30` (contract signing is the act) | DONE at 2026-01-30 |
| 4 | `SampleSubmitted` | `FactoryStyle` (spec sample) | A2 filename `1.21.26` | A2 file (submission is the act) | DONE at 2026-01-21 (spec sample); no separate PP submit event observed |
| 5 | `SampleApproved` | `FactoryStyle` | — | D1 `样衣进度 = 珠片绣OK，色卡OK，产前样4/3-4/16OK`; A1 mtime 4/16 | DONE at 2026-04-16 (PP approved) |
| 6 | `ColorApproved` | `ColorSpecification` | D3 filename `1.30` | D1 `样衣进度` fragment `色卡OK` | DONE — actual date not precise; INFERRED_HIGH within 4/3-4/16 window |
| 7 | `ArtworkApproved` | `Artwork` (997X) | D4 filename `1.30` | D1 `样衣进度` fragment `珠片绣OK`; A6/A8 confirmation photos | DONE — INFERRED_HIGH within 4/3-4/16 |
| 8 | `MaterialPlanned` | `MaterialRequirement` | D5 footer `2026.3.10` | D5 (issuing the plan is the act) | DONE at 2026-03-10 |
| 9 | `KnittingStarted` | `KnittingPlan` | D6 footer `2026.3.19` | D1 `面料进度 = 3/11投料` | DONE at 2026-03-11 (yarn issued to knitter — start-of-work) |
| 10 | `DyeLotAssigned` | `DyeLot 524` | D7 `日期 2026.3.10` | D7 (assignment is the act) | DONE at 2026-03-10 |
| 11 | `FabricReady` | `FabricBatch` / `DyeLot` | (D7 `成衣交期 = 4/25` → `StageDeadline`) | not captured for this case | **PLANNED only** — no `实拷KG` in D7; no fabric-in-QC actual in D1 |
| 12 | `CuttingPlanned` | `CuttingPlan` | D8 mtime `2026-03-21` | D8 (planning is the act) | DONE at 2026-03-21 |
| 13 | `EmbroideryCompleted` | `EmbroideryJob` | (implicit before PP-approval window 4/3-4/16) | D1 `样衣进度 = 珠片绣OK` | DONE — INFERRED_HIGH (embroidery on PP samples is complete by 4/16; bulk embroidery actual not captured) |
| 14 | `SewingCompleted` | `SewingJob` | (implicit before ship) | not captured — only ship note in D1 | **INFERRED_HIGH DONE** by 2026-05-22 (ship implies sewing done) |
| 15 | `PackingCompleted` | `PackingJob` | D10 mtime `2026-04-26` | D10 (packing list finalisation) | DONE at 2026-04-26 |
| 16 | `ShipmentCompleted` | `Shipment` | (D2 交期 4/20 → `StageDeadline`) | D1 `成衣工厂 = 5/22 郁建东发货`; D1 交货期 46164 = 5/22 | DONE at 2026-05-22 |
| 17 | `InvoiceIssued` | `Invoice` | — | D1 `开票情况 = 6/3开票` | DONE at 2026-06-03 |

### Deadlines observed (as `StageDeadline`)

| deadline event_type | affects | planned_date | source |
|---------------------|---------|--------------|--------|
| `ContractDelivery_DEADLINE` | `Shipment` | 2026-04-20 | D2 交期 (per C4) |
| `DyeCompletion_DEADLINE` | `DyeLot` | 2026-04-25 | D7 成衣交期 (per C4 — an internal target) |
| `CuttingCompletion_DEADLINE` | `CuttingPlan` | 2026-05-07 | D8 交货期 (per C4 — an internal target) |

The `ShipmentCompleted` actual (5/22) is one month later than `ContractDelivery_DEADLINE` (4/20). Ontology models this as one deadline event + one completion event with a **32-day slip**, not as two mutable "delivery_date" fields.

---

## 4. Events **not** modelled (deliberately)

Because there is no evidence for them in this case, v0.1 does not include:

- Yarn purchase actual confirmation (yarn was ordered; no supplier receipt in the file set).
- Knit completion actual (D6 planned; no D1 fabric-in QC entry).
- Dye run actual (D7 lot assigned; `实拷KG` blank).
- 3rd-party test (`BV`) submission or result — only requirement text in D2.
- Warehouse in/out events.
- Cutting completion actual, sewing start actual, embroidery return actual.

Adding any of these would violate the scope rule. They are candidates for future extension if additional docs (e.g. per-batch QC forms, test reports, receiving logs) appear.

---

## 5. Timeline (case)

Merged view of the 17 event types plus 3 deadlines, sorted by best-known date. Where actual_date is missing but PLANNED-only status was recorded, that is marked.

```
2026-01-21  DONE       SampleSubmitted             (A2 1st fit)
2026-01-28  ?          (D3/D4 footer serial 46052 — request origin, INFERRED_LOW)
2026-01-30  DONE       ContractConfirmed           (D2)
2026-01-30  DONE       ColorApproved (brief)       (D3)  ← the brief is issued; approval is later
2026-01-30  DONE       ArtworkApproved (brief)     (D4)  ← the brief is issued; approval is later
2026-01-31  DONE       OrderBooked                 (D1 R171/R172 下单时间)
2026-02-02  DONE       QuoteIssued                 (D0)
2026-03-10  DONE       MaterialPlanned             (D5)
2026-03-10  DONE       DyeLotAssigned              (D7 batch 524)
2026-03-11  DONE       KnittingStarted             (D1 面料进度 3/11投料)
2026-03-19  DONE       KnittingPlan issued         (D6)  ← plan-issue not the same as start
2026-03-21  DONE       CuttingPlanned              (D8)
2026-04-03  DONE       (Trims spec updated to v4.3)(D9)
2026-04-03..04-16 DONE SampleApproved (PP)         (D1 样衣进度 产前样4/3-4/16OK)
2026-04-16  DONE       (Buyer PP file received)    (A1 mtime)
2026-04-20  DEADLINE   ContractDelivery_DEADLINE   (D2 交期)  — slipped
2026-04-25  DEADLINE   DyeCompletion_DEADLINE      (D7 成衣交期)  — internal target
2026-04-26  DONE       PackingCompleted            (D10)
2026-05-07  DEADLINE   CuttingCompletion_DEADLINE  (D8 交货期)  — internal target
2026-05-22  DONE       ShipmentCompleted           (D1 成衣工厂 5/22 郁建东发货)
2026-06-03  DONE       InvoiceIssued               (D1 开票情况 6/3开票)
```

---

## 6. Why events are first-class

Two motivations from the case:

1. **Date revisions are semantically important.** The contract-vs-actual delivery slip (4/20 → 5/22) is not a data error; it is a real business event. A schema with a single mutable `delivery_date` field would lose the fact that both dates were once valid.

2. **Status text carries multi-event narratives.** D1's `样衣进度 = 珠片绣OK，色卡OK，产前样4/3-4/16OK` compresses 3 events into one cell. Materialising them as `StageEvent` rows lets downstream reporting query per event type and per date without re-parsing text.

The current model captures event *facts*; it does **not** claim to be a full state machine (no transitions or guards). That is a v0.2 topic once the completeness of D1's status text across more orders is understood.
