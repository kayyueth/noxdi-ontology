"""Ontology loader tests."""

from __future__ import annotations

import io
import textwrap
from pathlib import Path

import pytest

from .conftest import PROJECT_ROOT
from runtime.ontology import (
    OntologyError,
    load_ontology,
)
from runtime.ontology.types import (
    Cardinality,
    parse_attribute_type,
    is_polymorphic_marker,
)


# ---------------------------------------------------------------------------
# Attribute type parser
# ---------------------------------------------------------------------------


def test_parse_simple_types():
    for t in ("text", "integer", "decimal", "boolean", "date", "timestamp", "any"):
        assert parse_attribute_type(t).kind == t


def test_parse_enum_ok():
    at = parse_attribute_type("enum(target|quoted|booked)")
    assert at.kind == "enum"
    assert at.enum_values == ("target", "quoted", "booked")


def test_parse_enum_single_value_ok():
    at = parse_attribute_type("enum(per_piece)")
    assert at.kind == "enum"
    assert at.enum_values == ("per_piece",)


def test_parse_enum_malformed_rejected():
    # This is the concrete case from 03_attributes.csv line 146:
    # `enum(17 event types)` is descriptive, not enumerative.
    with pytest.raises(OntologyError):
        parse_attribute_type("enum(17 event types)")


def test_parse_ref_ok():
    at = parse_attribute_type("ref(Document)")
    assert at.kind == "ref"
    assert at.ref_target == "Document"


def test_parse_list_ref_ok():
    at = parse_attribute_type("list[ref(Size)]")
    assert at.kind == "list_ref"
    assert at.ref_target == "Size"


def test_parse_map_ok():
    at = parse_attribute_type("map[size→int]")
    assert at.kind == "map"
    assert at.map_key == "size"
    assert at.map_value == "int"


def test_parse_unknown_type_rejected():
    with pytest.raises(OntologyError):
        parse_attribute_type("wibble(foo)")


# ---------------------------------------------------------------------------
# Cardinality parser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,lo,hi",
    [
        ("1..1", 1, 1),
        ("0..1", 0, 1),
        ("1..N", 1, None),
        ("0..N", 0, None),
    ],
)
def test_parse_cardinality_ok(raw, lo, hi):
    c = Cardinality.parse(raw)
    assert c.min == lo
    assert c.max == hi


@pytest.mark.parametrize("bad", ["", "1", "2..3", "1..2", "1-N", "A..B"])
def test_parse_cardinality_rejects(bad):
    with pytest.raises(OntologyError):
        Cardinality.parse(bad)


# ---------------------------------------------------------------------------
# Polymorphic marker recognition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "any",
        "any_execution_entity",
        "any_attribute",
        "{various}",
        "{any attribute}",
        "{Fabric|Cutting|Embroidery|Sewing|Ship}",
    ],
)
def test_polymorphic_markers(raw):
    assert is_polymorphic_marker(raw)


@pytest.mark.parametrize("raw", ["Document", "FactoryStyle", "Contract"])
def test_polymorphic_markers_reject_regular_names(raw):
    assert not is_polymorphic_marker(raw)


def test_party_treated_as_polymorphic_documented_gap():
    """Party is not a defined ontology entity but is referenced by
    Document.author_party_ref. Runtime treats it as polymorphic;
    see runtime/SCHEMA_GAPS.md §G1.
    """
    assert is_polymorphic_marker("Party")


# ---------------------------------------------------------------------------
# End-to-end load of the real ontology
# ---------------------------------------------------------------------------


def test_load_real_ontology_returns_all_four_lists():
    entities, attrs, rels, events, report = load_ontology(PROJECT_ROOT)
    # From 03_entities.csv (45 rows).
    assert len(entities) >= 40, f"expected ~45 entities, got {len(entities)}"
    # All attributes resolve to a known entity (checked in loader; we
    # additionally assert the invariant holds on the returned lists).
    names = {e.name for e in entities}
    for a in attrs:
        assert a.entity in names, f"orphan attribute: {a.entity}.{a.name}"
    for r in rels:
        assert r.subject in names, f"orphan rel subject: {r}"
        if not r.object_is_polymorphic:
            assert r.object in names, f"orphan rel object: {r}"
    # 17 base event types from StageEvent.event_type_enum.
    assert len(events) == 17
    # Cross-source drift is warned, not fatal.
    assert isinstance(report.warnings, list)


def test_all_relationships_have_valid_cardinality():
    _, _, rels, _, _ = load_ontology(PROJECT_ROOT)
    for r in rels:
        assert r.cardinality.min in (0, 1)
        assert r.cardinality.max in (1, None)


# ---------------------------------------------------------------------------
# Fail-loud behaviour under synthetic bad inputs
# ---------------------------------------------------------------------------


def _write_tmp_ontology(tmp_path: Path, *, entities: str, attrs: str, rels: str,
                       ontology_json: str | None = None) -> Path:
    (tmp_path / "03_entities.csv").write_text(entities, encoding="utf-8")
    (tmp_path / "03_attributes.csv").write_text(attrs, encoding="utf-8")
    (tmp_path / "03_relationships.csv").write_text(rels, encoding="utf-8")
    if ontology_json is None:
        ontology_json = (
            '{"entities":[{"name":"StageEvent",'
            '"event_type_enum":["Foo"]}]}'
        )
    (tmp_path / "03_ontology_v0.1.json").write_text(ontology_json, encoding="utf-8")
    return tmp_path


_HEADERS_ENT = "entity,definition,grain,primary_identifier,lifecycle_stage,evidence,confidence,status\n"
_HEADERS_ATTR = "entity,attribute,type,unit,required,source_fields,normalization_rule,confidence\n"
_HEADERS_REL = "subject,predicate,object,cardinality,evidence,confidence,status\n"


def test_attribute_referencing_unknown_entity_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR + "Bogus,name,text,,Y,,,\n"
    rels = _HEADERS_REL
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="unknown entity"):
        load_ontology(tmp_path)


def test_relationship_referencing_unknown_subject_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR
    rels = _HEADERS_REL + "Ghost,points_to,Foo,1..1,,,\n"
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="unknown subject"):
        load_ontology(tmp_path)


def test_relationship_referencing_unknown_object_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR
    rels = _HEADERS_REL + "Foo,points_to,Ghost,1..1,,,\n"
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="unknown object"):
        load_ontology(tmp_path)


def test_duplicate_entity_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\nFoo,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR
    rels = _HEADERS_REL
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="duplicate entity"):
        load_ontology(tmp_path)


def test_duplicate_attribute_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR + "Foo,name,text,,Y,,,\nFoo,name,text,,Y,,,\n"
    rels = _HEADERS_REL
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="duplicate attribute"):
        load_ontology(tmp_path)


def test_malformed_cardinality_fails(tmp_path):
    ents = _HEADERS_ENT + "Foo,,1,fk,,,,\nBar,,1,fk,,,,\n"
    attrs = _HEADERS_ATTR
    rels = _HEADERS_REL + "Foo,points_to,Bar,1-1,,,\n"
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="cardinality"):
        load_ontology(tmp_path)


def test_missing_required_column_fails(tmp_path):
    ents = "entity,grain,primary_identifier\nFoo,1,fk\n"
    attrs = _HEADERS_ATTR
    rels = _HEADERS_REL
    _write_tmp_ontology(tmp_path, entities=ents, attrs=attrs, rels=rels)
    with pytest.raises(OntologyError, match="missing columns"):
        load_ontology(tmp_path)
