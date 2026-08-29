"""Deterministic object identity.

`object_id(entity_type, natural_key)` produces a stable ID for any
entity instance. The ID is a hash of the canonical natural key —
identical canonical keys produce identical IDs, always.

Canonicalisation is explicit and testable. There is no fuzzy matching
in v0: aliases (e.g. 茗苑→名苑) are applied separately by the ingest
resolver, not here.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Iterable, Union

NaturalKey = Union[str, tuple, list]

# Entity types whose primary identifier is a code (letters + digits, often
# machine-generated). Codes are uppercased during canonicalisation so
# case variation cannot spawn duplicate objects.
_CODE_ENTITY_TYPES: frozenset[str] = frozenset(
    {
        "FactoryStyle",
        "StoreStyle",
        "Program",
        "PurchaseOrder",
        "Artwork",
        "DyeLot",
        "UPC",
        "Document",
    }
)

_WS_RE = re.compile(r"\s+")


class IdentityError(ValueError):
    """Raised when a natural key cannot be canonicalised."""


def _normalise_token(entity_type: str, part: str) -> str:
    """Apply the canonicalisation rules for a single string token.

    Rules (per ARCHITECTURE.md §Object IDs):
      1. Unicode NFC normalisation (so 名 vs 名 collapse).
      2. Strip surrounding whitespace and collapse internal runs.
      3. For code-bearing entities, uppercase.
      4. Never returns an empty string — that raises IdentityError.
    """
    if part is None:
        raise IdentityError(f"{entity_type}: natural key part is None")
    if not isinstance(part, str):
        raise IdentityError(
            f"{entity_type}: natural key parts must be str, got {type(part).__name__}"
        )
    s = unicodedata.normalize("NFC", part)
    s = _WS_RE.sub(" ", s.strip())
    if not s:
        raise IdentityError(f"{entity_type}: natural key part is empty")
    if entity_type in _CODE_ENTITY_TYPES:
        s = s.upper()
    return s


def canonicalise(entity_type: str, natural_key: NaturalKey) -> str:
    """Return the canonical string form of a natural key.

    Composite keys (passed as tuple or list) are joined with `|` after
    each part is independently canonicalised. The join order is the
    order the caller passes.
    """
    if not entity_type or not isinstance(entity_type, str):
        raise IdentityError(f"invalid entity_type: {entity_type!r}")
    if isinstance(natural_key, (list, tuple)):
        if len(natural_key) == 0:
            raise IdentityError(
                f"{entity_type}: composite natural key has zero parts"
            )
        parts = [_normalise_token(entity_type, p) for p in natural_key]
        return "|".join(parts)
    return _normalise_token(entity_type, natural_key)


def object_id(entity_type: str, natural_key: NaturalKey) -> str:
    """Return the deterministic object_id for (entity_type, natural_key).

    Format: `<EntityType>:<sha1[:12]>` where the sha1 is over the UTF-8
    canonical key.
    """
    canonical = canonicalise(entity_type, natural_key)
    digest = hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:12]
    return f"{entity_type}:{digest}"


def code_entity_types() -> frozenset[str]:
    """Expose the set of entity types treated as code-bearing (for tests)."""
    return _CODE_ENTITY_TYPES
