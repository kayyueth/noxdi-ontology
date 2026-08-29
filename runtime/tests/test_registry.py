"""OntologyRegistry tests."""

from __future__ import annotations

import pytest

from .conftest import PROJECT_ROOT
from runtime.ontology import OntologyError, OntologyRegistry


@pytest.fixture(scope="module")
def registry():
    return OntologyRegistry.from_path(PROJECT_ROOT)


# ---- lookups --------------------------------------------------------------


def test_get_entity_ok(registry):
    e = registry.get_entity("FactoryStyle")
    assert e.name == "FactoryStyle"
    # layer lives in 03_ontology_v0.1.json, not 03_entities.csv; the
    # registry surfaces the CSV columns.
    assert e.primary_identifier == "factory_style_code"


def test_get_entity_missing(registry):
    with pytest.raises(OntologyError):
        registry.get_entity("NoSuchEntity")


def test_get_attributes_returns_declared(registry):
    attrs = registry.get_attributes("FactoryStyle")
    names = {a.name for a in attrs}
    assert "factory_style_code" in names


def test_get_attribute_specific(registry):
    a = registry.get_attribute("Price", "price_type")
    assert a.type.kind == "enum"
    assert a.type.enum_values == ("target", "quoted", "booked")


def test_get_relationships_for_entity(registry):
    rels = registry.get_relationships("Contract")
    predicates = {r.predicate for r in rels}
    # Contract → StyleOrder (booked_as) is in the ontology.
    assert "booked_as" in predicates


def test_get_relationship_returns_all_declarations(registry):
    # `performed_by` is declared on KnittingPlan, EmbroideryJob, SewingJob —
    # get_relationship is scoped by subject.
    r_knit = registry.get_relationship("KnittingPlan", "performed_by")
    assert len(r_knit) == 1
    assert r_knit[0].object == "Subcontractor"


def test_get_relationship_missing(registry):
    with pytest.raises(OntologyError):
        registry.get_relationship("KnittingPlan", "no_such_predicate")


def test_get_event_type_base_and_deadline(registry):
    base = registry.get_event_type("ShipmentCompleted")
    assert base.name == "ShipmentCompleted"
    assert base.is_deadline is False
    dl = registry.get_event_type("ShipmentCompleted_DEADLINE")
    assert dl.is_deadline is True


def test_get_event_type_unknown(registry):
    with pytest.raises(OntologyError):
        registry.get_event_type("NonsenseEvent")


# ---- validate_attribute ---------------------------------------------------


def test_validate_attribute_enum_accepts_declared(registry):
    registry.validate_attribute("Price", "price_type", "quoted")


def test_validate_attribute_enum_rejects_undeclared(registry):
    with pytest.raises(OntologyError, match="not in enum"):
        registry.validate_attribute("Price", "price_type", "invoice_price")


def test_validate_attribute_integer_type(registry):
    registry.validate_attribute("Carton", "pieces_in_carton", 95)
    with pytest.raises(OntologyError, match="expected integer"):
        registry.validate_attribute("Carton", "pieces_in_carton", "95")
    # bools are not integers here.
    with pytest.raises(OntologyError, match="expected integer"):
        registry.validate_attribute("Carton", "pieces_in_carton", True)


def test_validate_attribute_text_type(registry):
    registry.validate_attribute("Brand", "brand_name", "Lane Bryant")
    with pytest.raises(OntologyError, match="expected text"):
        registry.validate_attribute("Brand", "brand_name", 42)


def test_validate_attribute_null_is_accepted(registry):
    # A None value maps to an UNRESOLVED fact at ingest time — schema
    # validation must not reject it.
    registry.validate_attribute("Price", "price_type", None)


# ---- validate_relationship ------------------------------------------------


def test_validate_relationship_ok(registry):
    registry.validate_relationship("Contract", "booked_as", "StyleOrder")


def test_validate_relationship_bad_object_type(registry):
    with pytest.raises(OntologyError):
        registry.validate_relationship("Contract", "booked_as", "Carton")


def test_validate_relationship_polymorphic_accepts_any_known_entity(registry):
    # StageEvent.affects → any → any declared entity qualifies.
    registry.validate_relationship("StageEvent", "affects", "FactoryStyle")
    registry.validate_relationship("StageEvent", "affects", "PurchaseOrder")


def test_validate_relationship_unknown_target_entity(registry):
    with pytest.raises(OntologyError, match="not a known entity"):
        registry.validate_relationship("StageEvent", "affects", "Nothing")
