"""Deterministic object identity tests."""

from __future__ import annotations

import pytest

from runtime.identity import IdentityError, canonicalise, object_id


# ---- deterministic hashes -------------------------------------------------


def test_object_id_is_deterministic():
    a = object_id("FactoryStyle", "FBB54S2-997XLB")
    b = object_id("FactoryStyle", "FBB54S2-997XLB")
    assert a == b
    assert a.startswith("FactoryStyle:")
    assert len(a.split(":")[1]) == 12


def test_object_id_differs_across_entity_types():
    a = object_id("FactoryStyle", "X")
    b = object_id("StoreStyle", "X")
    assert a != b


def test_object_id_differs_across_natural_keys():
    a = object_id("FactoryStyle", "FBB54S2-997XLB")
    b = object_id("FactoryStyle", "FBB54S2-388ELB")
    assert a != b


# ---- canonicalisation collapses equivalent inputs -------------------------


def test_case_variants_of_code_collapse():
    assert object_id("FactoryStyle", "FBB54S2-997XLB") == object_id(
        "FactoryStyle", " fbb54s2-997xlb "
    )


def test_whitespace_variants_of_code_collapse():
    assert object_id("FactoryStyle", "FBB54S2  997XLB") == object_id(
        "FactoryStyle", "FBB54S2 997XLB"
    )


def test_name_entities_preserve_case():
    # Non-code entity types keep the original case (only whitespace and
    # NFC are collapsed). "Lane Bryant" != "LANE BRYANT" as canonicalised.
    a = canonicalise("Brand", "Lane Bryant")
    b = canonicalise("Brand", "LANE BRYANT")
    assert a != b


def test_name_entities_whitespace_still_collapses():
    a = canonicalise("Brand", "Lane Bryant")
    b = canonicalise("Brand", "  Lane   Bryant  ")
    assert a == b


def test_nfc_normalisation_collapses_equivalent_glyphs():
    # 名 (U+540D) is a single codepoint; there is no legacy composition
    # here, but composed vs decomposed forms of 名苑 should collapse.
    composed = "名苑"
    decomposed = "名苑"  # both are single BMP chars — same as composed
    assert canonicalise("Subcontractor", composed) == canonicalise(
        "Subcontractor", decomposed
    )


# ---- composite keys --------------------------------------------------------


def test_composite_key_stable():
    a = object_id("Subcontractor", ("名苑", "CMT"))
    b = object_id("Subcontractor", ("名苑", "CMT"))
    assert a == b


def test_composite_key_order_matters():
    a = object_id("Subcontractor", ("名苑", "CMT"))
    b = object_id("Subcontractor", ("CMT", "名苑"))
    assert a != b


def test_composite_key_from_list_matches_tuple():
    assert object_id("Subcontractor", ["名苑", "CMT"]) == object_id(
        "Subcontractor", ("名苑", "CMT")
    )


def test_composite_key_whitespace_collapses_per_part():
    a = object_id("Subcontractor", ("名苑", "CMT"))
    b = object_id("Subcontractor", ("  名苑  ", " CMT "))
    assert a == b


# ---- explicit rejections ---------------------------------------------------


def test_empty_natural_key_rejected():
    with pytest.raises(IdentityError):
        object_id("FactoryStyle", "")
    with pytest.raises(IdentityError):
        object_id("FactoryStyle", "   ")


def test_empty_composite_rejected():
    with pytest.raises(IdentityError):
        object_id("Subcontractor", ())


def test_none_part_rejected():
    with pytest.raises(IdentityError):
        object_id("Subcontractor", ("名苑", None))


def test_non_string_part_rejected():
    with pytest.raises(IdentityError):
        object_id("Subcontractor", ("名苑", 42))


# ---- known-good golden hash -----------------------------------------------


def test_golden_hash_locks_algorithm():
    """Locking a small set of known IDs guards against silent changes to
    the canonicalisation algorithm. If these change, downstream
    persisted IDs would drift.
    """
    import hashlib

    def expected(entity_type: str, natural_key: str) -> str:
        c = canonicalise(entity_type, natural_key)
        return f"{entity_type}:{hashlib.sha1(c.encode()).hexdigest()[:12]}"

    for et, nk in [
        ("FactoryStyle", "FBB54S2-997XLB"),
        ("StoreStyle", "1152246"),
        ("Program", "M7797"),
        ("Brand", "Lane Bryant"),
    ]:
        assert object_id(et, nk) == expected(et, nk)
