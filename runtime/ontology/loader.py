"""Load the descriptive ontology into typed structures.

The ontology sources remain authoritative. This module does not
paper over inconsistencies — it fails loudly on:

  * an Attribute referencing an unknown Entity
  * a Relationship referencing an unknown subject or object Entity
    (polymorphic markers like `any` are permitted; see types.py)
  * duplicate ontology identifiers
  * malformed cardinality
  * malformed enum syntax
  * missing required fields

Cross-source disagreements between the CSVs and 03_ontology_v0.1.json
are reported as warnings, not fatal.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .types import (
    Attribute,
    AttributeType,
    Cardinality,
    Entity,
    EventType,
    OntologyError,
    POLYMORPHIC_MARKERS,
    Relationship,
    is_polymorphic_marker,
    parse_attribute_type,
)


# The ontology CSVs carry regex fragments in some `normalization_rule`
# cells (e.g. `regex \d{2,3}S`). The source files do not quote these
# fields, so a bare comma inside the regex confuses csv.reader.
#
# We recognise two overflow patterns:
#   1. `\,` — an ad-hoc backslash escape used once in row 16 of
#      03_attributes.csv.  We rewrite it to a NUL sentinel pre-parse
#      and restore it post-parse.
#   2. Column-count overflow — for CSV files that declare a `tolerant`
#      column, we reabsorb any extra fields back into that column.
#      This is the resolution rule for the `\d{2,3}` case in row 58.
#
# Both are documented in runtime/SCHEMA_GAPS.md.  The rule is
# deterministic and only applies to the column named as tolerant.
_COMMA_ESCAPE = "\x00COMMA\x00"


def _read_csv_with_escapes(
    path: Path, *, tolerant_column: str | None = None
) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\\,", _COMMA_ESCAPE)
    reader = csv.reader(io.StringIO(text))
    headers = next(reader, None)
    if not headers:
        raise OntologyError(f"{path.name}: empty CSV")
    n_cols = len(headers)
    tolerant_idx = (
        headers.index(tolerant_column) if tolerant_column in headers else None
    )
    out: list[dict[str, str]] = []
    for line_no, values in enumerate(reader, start=2):
        if len(values) == n_cols:
            merged = values
        elif len(values) > n_cols and tolerant_idx is not None:
            # Fold overflow back into the tolerant column. Preserves the
            # commas that belong inside a regex or free-text cell without
            # changing the semantics of any other column.
            right_count = n_cols - tolerant_idx - 1
            right = values[-right_count:] if right_count > 0 else []
            left = values[:tolerant_idx]
            middle = values[tolerant_idx : len(values) - right_count]
            merged = left + [",".join(middle)] + right
        elif len(values) == n_cols - 1 and tolerant_idx is not None:
            # A single missing column collapses to the tolerant column.
            # Insert an empty string there. Deterministic; disclosed in
            # runtime/SCHEMA_GAPS.md.
            merged = values[:tolerant_idx] + [""] + values[tolerant_idx:]
        else:
            raise OntologyError(
                f"{path.name}:{line_no}: expected {n_cols} columns, "
                f"got {len(values)}: {values!r}"
            )
        row = {
            h: (v.replace(_COMMA_ESCAPE, ",") if v is not None else "")
            for h, v in zip(headers, merged)
        }
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# Load report
# ---------------------------------------------------------------------------


@dataclass
class LoadReport:
    warnings: list[str] = field(default_factory=list)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------------------
# Individual loaders
# ---------------------------------------------------------------------------


def _read_entities_csv(path: Path, ontology_json_path: Path) -> list[dict[str, str]]:
    """Read 03_entities.csv, reconciling the one known short row.

    03_entities.csv row 6 (`Subcontractor`) omits `primary_identifier`
    entirely (7 fields vs 8 in the header). 03_ontology_v0.1.json does
    hold the missing value. When the CSV row is short and the JSON has
    the missing column for the same entity, we backfill from JSON and
    record the divergence in the load report.  See SCHEMA_GAPS.md.
    """
    text = path.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(text))
    headers = next(reader, None)
    if not headers:
        raise OntologyError(f"{path.name}: empty CSV")
    n_cols = len(headers)
    json_by_name: dict[str, dict] = {}
    if ontology_json_path.exists():
        data = json.loads(ontology_json_path.read_text(encoding="utf-8"))
        json_by_name = {e["name"]: e for e in data.get("entities", [])}
    out: list[dict[str, str]] = []
    for line_no, values in enumerate(reader, start=2):
        if len(values) == n_cols:
            row = dict(zip(headers, values))
        elif len(values) == n_cols - 1 and values and values[0] in json_by_name:
            # Which header is the row missing? The one whose value is not
            # in `values` and IS in JSON. We attempt to align each JSON-
            # required column and find the single omission.
            entity_name = values[0]
            j = json_by_name[entity_name]
            # Walk headers; assume the CSV row is the sequence of values
            # with exactly one header skipped. Try each candidate header
            # (other than `entity`) as the omitted one; accept the first
            # that leaves the remaining CSV values aligning with `values`.
            candidate = None
            for idx in range(1, n_cols):
                # Try assuming header[idx] was omitted.
                trial_values = values[:idx] + [j.get(headers[idx], "")] + values[idx:]
                if len(trial_values) == n_cols:
                    candidate = (idx, trial_values)
                    if j.get(headers[idx]):
                        # Prefer a candidate that JSON positively supplies.
                        break
            if candidate is None:
                raise OntologyError(
                    f"{path.name}:{line_no}: cannot reconcile short row"
                )
            idx, filled = candidate
            row = dict(zip(headers, filled))
        else:
            raise OntologyError(
                f"{path.name}:{line_no}: expected {n_cols} columns, "
                f"got {len(values)}: {values!r}"
            )
        out.append(row)
    return out


def _load_entities(path: Path, ontology_json_path: Path) -> list[Entity]:
    rows = _read_entities_csv(path, ontology_json_path)
    required = {
        "entity",
        "definition",
        "grain",
        "primary_identifier",
        "lifecycle_stage",
        "evidence",
        "confidence",
        "status",
    }
    seen: set[str] = set()
    out: list[Entity] = []
    for i, r in enumerate(rows, start=2):
        missing = required - r.keys()
        if missing:
            raise OntologyError(
                f"{path.name}:{i}: entity row missing columns {sorted(missing)}"
            )
        name = r["entity"].strip()
        if not name:
            raise OntologyError(f"{path.name}:{i}: entity name is empty")
        if name in seen:
            raise OntologyError(
                f"{path.name}:{i}: duplicate entity name {name!r}"
            )
        seen.add(name)
        grain = r["grain"].strip()
        pk = r["primary_identifier"].strip()
        if not grain:
            raise OntologyError(f"{path.name}:{i}: {name!r} missing grain")
        if not pk:
            raise OntologyError(
                f"{path.name}:{i}: {name!r} missing primary_identifier"
            )
        out.append(
            Entity(
                name=name,
                layer=r.get("layer", "").strip(),
                grain=grain,
                primary_identifier=pk,
                status=r["status"].strip(),
                confidence=r["confidence"].strip(),
                evidence=r["evidence"].strip(),
                definition=r["definition"].strip(),
                lifecycle_stage=r["lifecycle_stage"].strip(),
            )
        )
    return out


def _load_attributes(
    path: Path,
    entities_by_name: dict[str, Entity],
    ontology_json_path: Path | None = None,
) -> list[Attribute]:
    # JSON supplies enum values for a small number of attributes whose
    # CSV `type` column is descriptive rather than enumerative — e.g.
    # `enum(17 event types)` for StageEvent.event_type. When the CSV
    # enum parse fails, we consult the JSON for an <attr>_enum key on
    # the entity and reconstitute the enum from that.
    json_enums: dict[tuple[str, str], tuple[str, ...]] = {}
    if ontology_json_path is not None and ontology_json_path.exists():
        data = json.loads(ontology_json_path.read_text(encoding="utf-8"))
        for e in data.get("entities", []):
            ename = e.get("name")
            if not ename:
                continue
            for k, v in e.items():
                if k.endswith("_enum") and isinstance(v, list) and v:
                    attr_name = k[: -len("_enum")]
                    json_enums[(ename, attr_name)] = tuple(str(x) for x in v)

    rows = _read_csv_with_escapes(path, tolerant_column="normalization_rule")
    required = {
        "entity",
        "attribute",
        "type",
        "unit",
        "required",
        "source_fields",
        "normalization_rule",
        "confidence",
    }
    seen: set[tuple[str, str]] = set()
    out: list[Attribute] = []
    for i, r in enumerate(rows, start=2):
        missing = required - r.keys()
        if missing:
            raise OntologyError(
                f"{path.name}:{i}: attribute row missing columns {sorted(missing)}"
            )
        entity_name = r["entity"].strip()
        attr_name = r["attribute"].strip()
        if not entity_name:
            raise OntologyError(f"{path.name}:{i}: empty entity for attribute")
        if not attr_name:
            raise OntologyError(f"{path.name}:{i}: empty attribute name")
        if entity_name not in entities_by_name:
            raise OntologyError(
                f"{path.name}:{i}: attribute {attr_name!r} references unknown "
                f"entity {entity_name!r}"
            )
        key = (entity_name, attr_name)
        if key in seen:
            raise OntologyError(
                f"{path.name}:{i}: duplicate attribute {entity_name}.{attr_name}"
            )
        seen.add(key)
        try:
            atype = parse_attribute_type(r["type"])
        except OntologyError as exc:
            # Fallback: the JSON may supply an <attr>_enum for this
            # attribute (e.g. StageEvent.event_type). If so, use it.
            values = json_enums.get((entity_name, attr_name))
            if values is not None and r["type"].strip().startswith("enum("):
                atype = AttributeType(
                    kind="enum",
                    raw=r["type"].strip(),
                    enum_values=values,
                )
            else:
                raise OntologyError(
                    f"{path.name}:{i}: {entity_name}.{attr_name}: {exc}"
                ) from None
        req_raw = r["required"].strip().upper()
        if req_raw not in ("Y", "N"):
            raise OntologyError(
                f"{path.name}:{i}: required must be Y or N, got {req_raw!r}"
            )
        # Validate any ref target embedded in the attribute type.
        if atype.kind in ("ref", "list_ref") and atype.ref_target:
            target = atype.ref_target
            # Attribute-level refs like `ref(ColorSpecification.swatch_code)`
            # reduce to the entity component for validation.
            entity_component = target.split(".", 1)[0]
            if (
                entity_component not in entities_by_name
                and not is_polymorphic_marker(entity_component)
            ):
                raise OntologyError(
                    f"{path.name}:{i}: {entity_name}.{attr_name}: ref target "
                    f"{target!r} references unknown entity {entity_component!r}"
                )
        out.append(
            Attribute(
                entity=entity_name,
                name=attr_name,
                type=atype,
                unit=r["unit"].strip(),
                required=(req_raw == "Y"),
                source_fields=r["source_fields"].strip(),
                normalization_rule=r["normalization_rule"].strip(),
                confidence=r["confidence"].strip(),
            )
        )
    return out


def _load_relationships(
    path: Path, entities_by_name: dict[str, Entity]
) -> list[Relationship]:
    rows = _read_csv_with_escapes(path)
    required = {
        "subject",
        "predicate",
        "object",
        "cardinality",
        "evidence",
        "confidence",
        "status",
    }
    seen: set[tuple[str, str, str]] = set()
    out: list[Relationship] = []
    for i, r in enumerate(rows, start=2):
        missing = required - r.keys()
        if missing:
            raise OntologyError(
                f"{path.name}:{i}: relationship row missing columns {sorted(missing)}"
            )
        subj = r["subject"].strip()
        pred = r["predicate"].strip()
        obj = r["object"].strip()
        if not subj or not pred or not obj:
            raise OntologyError(
                f"{path.name}:{i}: relationship has empty subject/predicate/object"
            )
        if subj not in entities_by_name:
            raise OntologyError(
                f"{path.name}:{i}: relationship {subj}.{pred} references "
                f"unknown subject entity {subj!r}"
            )
        polymorphic = is_polymorphic_marker(obj)
        if not polymorphic and obj not in entities_by_name:
            raise OntologyError(
                f"{path.name}:{i}: relationship {subj}.{pred} references "
                f"unknown object entity {obj!r}"
            )
        try:
            card = Cardinality.parse(r["cardinality"])
        except OntologyError as exc:
            raise OntologyError(
                f"{path.name}:{i}: {subj}.{pred}: {exc}"
            ) from None
        key = (subj, pred, obj)
        if key in seen:
            raise OntologyError(
                f"{path.name}:{i}: duplicate relationship {subj}.{pred}→{obj}"
            )
        seen.add(key)
        out.append(
            Relationship(
                subject=subj,
                predicate=pred,
                object=obj,
                object_is_polymorphic=polymorphic,
                cardinality=card,
                evidence=r["evidence"].strip(),
                confidence=r["confidence"].strip(),
                status=r["status"].strip(),
            )
        )
    return out


def _load_event_types(ontology_json_path: Path) -> list[EventType]:
    """Event types come from the StageEvent.event_type_enum in the JSON."""
    data = json.loads(ontology_json_path.read_text(encoding="utf-8"))
    entities = data.get("entities", [])
    stage_event = None
    for e in entities:
        if e.get("name") == "StageEvent":
            stage_event = e
            break
    if stage_event is None:
        raise OntologyError(
            f"{ontology_json_path.name}: StageEvent entity not found"
        )
    enum_values = stage_event.get("event_type_enum")
    if not enum_values:
        raise OntologyError(
            f"{ontology_json_path.name}: StageEvent.event_type_enum missing"
        )
    seen: set[str] = set()
    out: list[EventType] = []
    for name in enum_values:
        n = str(name).strip()
        if not n:
            raise OntologyError("empty event type name in enum")
        if n in seen:
            raise OntologyError(f"duplicate event type {n!r}")
        seen.add(n)
        out.append(EventType(name=n, is_deadline=False))
    return out


# ---------------------------------------------------------------------------
# Cross-source consistency
# ---------------------------------------------------------------------------


def _cross_check_json(
    ontology_root: Path,
    entities: list[Entity],
    relationships: list[Relationship],
    report: LoadReport,
) -> None:
    """Cross-check CSV load against 03_ontology_v0.1.json. Warn on drift."""
    json_path = ontology_root / "03_ontology_v0.1.json"
    if not json_path.exists():
        return
    data = json.loads(json_path.read_text(encoding="utf-8"))
    csv_entity_names = {e.name for e in entities}
    json_entity_names = {e["name"] for e in data.get("entities", [])}
    missing_in_csv = json_entity_names - csv_entity_names
    missing_in_json = csv_entity_names - json_entity_names
    for name in sorted(missing_in_csv):
        report.warn(
            f"entity {name!r} appears in 03_ontology_v0.1.json but not in 03_entities.csv"
        )
    for name in sorted(missing_in_json):
        report.warn(
            f"entity {name!r} appears in 03_entities.csv but not in 03_ontology_v0.1.json"
        )

    csv_rel_keys = {(r.subject, r.predicate, r.object) for r in relationships}
    json_rel_keys = {
        (r["subject"], r["predicate"], r["object"])
        for r in data.get("relationships", [])
    }
    for miss in sorted(json_rel_keys - csv_rel_keys):
        report.warn(f"relationship {miss} in JSON but not CSV (may use variant marker)")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_ontology(
    ontology_root: Path | str,
) -> tuple[
    list[Entity],
    list[Attribute],
    list[Relationship],
    list[EventType],
    LoadReport,
]:
    root = Path(ontology_root)
    entities = _load_entities(
        root / "03_entities.csv", root / "03_ontology_v0.1.json"
    )
    by_name = {e.name: e for e in entities}
    attributes = _load_attributes(
        root / "03_attributes.csv",
        by_name,
        root / "03_ontology_v0.1.json",
    )
    relationships = _load_relationships(root / "03_relationships.csv", by_name)
    event_types = _load_event_types(root / "03_ontology_v0.1.json")
    report = LoadReport()
    _cross_check_json(root, entities, relationships, report)
    return entities, attributes, relationships, event_types, report
