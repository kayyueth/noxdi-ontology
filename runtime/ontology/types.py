"""Typed representations of the descriptive ontology.

Types are intentionally strict. Anything that cannot be represented
faithfully raises `OntologyError`; workarounds belong in SCHEMA_GAPS.md,
not in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class OntologyError(Exception):
    """Raised when the ontology sources are inconsistent or malformed."""


# Values in the relationship `object` column, or attribute `ref(...)`
# target, that mean "polymorphic — the ontology deliberately does not
# fix a single target entity."  Most are honest design decisions (see
# 03_ontology_v0.1.json). `Party` is a documented ontology gap
# (Document.author_party_ref) — treated as polymorphic here so the
# runtime can load. See runtime/SCHEMA_GAPS.md §G1.
POLYMORPHIC_MARKERS: frozenset[str] = frozenset(
    {
        "any",
        "any_execution_entity",
        "any_attribute",
        "Party",  # documented gap — SCHEMA_GAPS.md §G1
    }
)


def is_polymorphic_marker(value: str) -> bool:
    v = value.strip()
    if v in POLYMORPHIC_MARKERS:
        return True
    # CSV variants: `{various}`, `{any attribute}`,
    # `{Fabric|Cutting|Embroidery|Sewing|Ship}`.
    if v.startswith("{") and v.endswith("}"):
        return True
    return False


# ---------------------------------------------------------------------------
# Attribute types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AttributeType:
    """Parsed representation of the `type` column in 03_attributes.csv.

    `kind` is the top-level shape. Additional fields describe the shape:
      - enum: `enum_values` populated
      - ref / list_ref: `ref_target` populated
      - map: `map_key`, `map_value` populated
    """

    kind: str  # text | integer | decimal | boolean | date | timestamp
    # | enum | ref | list_text | list_ref | map | any
    raw: str
    enum_values: tuple[str, ...] = ()
    ref_target: Optional[str] = None
    map_key: Optional[str] = None
    map_value: Optional[str] = None

    def is_polymorphic_ref(self) -> bool:
        return self.kind in ("ref", "list_ref") and self.ref_target == "any"


_SIMPLE_TYPES = {
    "text",
    "integer",
    "decimal",
    "boolean",
    "date",
    "timestamp",
    "any",
}


def parse_attribute_type(raw: str) -> AttributeType:
    """Parse the `type` column into an AttributeType.

    Raises OntologyError on malformed enum syntax or unknown constructors.
    """
    text = (raw or "").strip()
    if not text:
        raise OntologyError("empty attribute type")

    if text in _SIMPLE_TYPES:
        return AttributeType(kind=text, raw=text)

    if text.startswith("enum(") and text.endswith(")"):
        body = text[len("enum(") : -1].strip()
        if not body:
            raise OntologyError(f"empty enum body: {raw!r}")
        # Malformed: descriptive text like `enum(17 event types)`.
        if "|" not in body:
            # Accept single-value enums like `enum(per_piece)`.
            if any(ch.isspace() for ch in body) or body.isdigit():
                raise OntologyError(
                    f"enum body has no `|` separators and is not a single "
                    f"literal token: {raw!r}"
                )
            values = (body,)
        else:
            values = tuple(v.strip() for v in body.split("|") if v.strip())
            if not values:
                raise OntologyError(f"enum yields zero values: {raw!r}")
        return AttributeType(kind="enum", raw=text, enum_values=values)

    if text.startswith("ref(") and text.endswith(")"):
        target = text[len("ref(") : -1].strip()
        if not target:
            raise OntologyError(f"empty ref target: {raw!r}")
        return AttributeType(kind="ref", raw=text, ref_target=target)

    if text.startswith("list[") and text.endswith("]"):
        inner = text[len("list[") : -1].strip()
        if inner == "text":
            return AttributeType(kind="list_text", raw=text)
        if inner.startswith("ref(") and inner.endswith(")"):
            target = inner[len("ref(") : -1].strip()
            return AttributeType(kind="list_ref", raw=text, ref_target=target)
        raise OntologyError(f"unsupported list element type: {raw!r}")

    if text.startswith("map[") and text.endswith("]"):
        inner = text[len("map[") : -1].strip()
        # Accept both `→` and `->` separators.
        if "→" in inner:
            k, v = inner.split("→", 1)
        elif "->" in inner:
            k, v = inner.split("->", 1)
        else:
            raise OntologyError(f"map type missing `->` / `→`: {raw!r}")
        return AttributeType(
            kind="map", raw=text, map_key=k.strip(), map_value=v.strip()
        )

    raise OntologyError(f"unrecognised attribute type: {raw!r}")


# ---------------------------------------------------------------------------
# Cardinality
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Cardinality:
    """Parsed cardinality like `1..1`, `0..1`, `1..N`, `0..N`."""

    min: int
    max: Optional[int]  # None = unbounded (N)
    raw: str

    @classmethod
    def parse(cls, text: str) -> "Cardinality":
        s = (text or "").strip()
        if ".." not in s:
            raise OntologyError(f"cardinality missing `..`: {text!r}")
        lo, hi = s.split("..", 1)
        lo_s = lo.strip()
        hi_s = hi.strip()
        if lo_s not in ("0", "1"):
            raise OntologyError(
                f"cardinality lower bound must be 0 or 1, got {lo_s!r} in {text!r}"
            )
        lo_i = int(lo_s)
        if hi_s == "N":
            hi_i: Optional[int] = None
        elif hi_s == "1":
            hi_i = 1
        else:
            raise OntologyError(
                f"cardinality upper bound must be 1 or N, got {hi_s!r} in {text!r}"
            )
        if hi_i is not None and hi_i < lo_i:
            raise OntologyError(f"cardinality upper < lower: {text!r}")
        return cls(min=lo_i, max=hi_i, raw=s)


# ---------------------------------------------------------------------------
# Entity / Attribute / Relationship / EventType
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Entity:
    name: str
    layer: str
    grain: str
    primary_identifier: str
    status: str
    confidence: str
    evidence: str
    definition: str = ""
    lifecycle_stage: str = ""

    def has_composite_key(self) -> bool:
        v = self.primary_identifier.strip().lower()
        return v.startswith("composite")


@dataclass(frozen=True)
class Attribute:
    entity: str
    name: str
    type: AttributeType
    unit: str
    required: bool
    source_fields: str
    normalization_rule: str
    confidence: str


@dataclass(frozen=True)
class Relationship:
    subject: str
    predicate: str
    object: str
    object_is_polymorphic: bool
    cardinality: Cardinality
    evidence: str = ""
    confidence: str = ""
    status: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.subject, self.predicate)


@dataclass(frozen=True)
class EventType:
    """One of the 17 base event types (see 03_ontology_v0.1.json)."""

    name: str
    is_deadline: bool = False  # deadlines are a naming convention
    # applied to StageDeadline objects; the base 17 are not deadlines.
