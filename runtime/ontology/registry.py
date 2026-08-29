"""OntologyRegistry — in-memory query and validation surface."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from .loader import LoadReport, load_ontology
from .types import (
    Attribute,
    Cardinality,
    Entity,
    EventType,
    OntologyError,
    Relationship,
)


class OntologyRegistry:
    """The one place to answer schema-level questions.

    Construct from an ontology directory (via `from_path`) or from
    already-parsed lists (via the initialiser). The ontology source
    files remain authoritative — the registry does not persist any
    schema mutations.
    """

    def __init__(
        self,
        entities: Iterable[Entity],
        attributes: Iterable[Attribute],
        relationships: Iterable[Relationship],
        event_types: Iterable[EventType],
        report: Optional[LoadReport] = None,
    ) -> None:
        self._entities: dict[str, Entity] = {}
        for e in entities:
            if e.name in self._entities:
                raise OntologyError(f"duplicate entity: {e.name}")
            self._entities[e.name] = e

        self._attributes_by_entity: dict[str, list[Attribute]] = defaultdict(list)
        self._attribute_index: dict[tuple[str, str], Attribute] = {}
        for a in attributes:
            if a.entity not in self._entities:
                raise OntologyError(
                    f"attribute {a.entity}.{a.name} references unknown entity"
                )
            key = (a.entity, a.name)
            if key in self._attribute_index:
                raise OntologyError(
                    f"duplicate attribute: {a.entity}.{a.name}"
                )
            self._attribute_index[key] = a
            self._attributes_by_entity[a.entity].append(a)

        self._outgoing_rels: dict[str, list[Relationship]] = defaultdict(list)
        self._rel_index: dict[tuple[str, str], list[Relationship]] = defaultdict(list)
        for r in relationships:
            if r.subject not in self._entities:
                raise OntologyError(
                    f"relationship {r.subject}.{r.predicate} references unknown subject"
                )
            if not r.object_is_polymorphic and r.object not in self._entities:
                raise OntologyError(
                    f"relationship {r.subject}.{r.predicate} references unknown object {r.object!r}"
                )
            self._outgoing_rels[r.subject].append(r)
            self._rel_index[(r.subject, r.predicate)].append(r)

        self._event_types: dict[str, EventType] = {}
        for et in event_types:
            if et.name in self._event_types:
                raise OntologyError(f"duplicate event type: {et.name}")
            self._event_types[et.name] = et

        self._report: LoadReport = report or LoadReport()

    # ---- construction -----------------------------------------------------

    @classmethod
    def from_path(cls, ontology_root: Path | str) -> "OntologyRegistry":
        entities, attrs, rels, events, report = load_ontology(ontology_root)
        return cls(entities, attrs, rels, events, report=report)

    @property
    def load_report(self) -> LoadReport:
        return self._report

    # ---- lookups ----------------------------------------------------------

    def entity_names(self) -> list[str]:
        return list(self._entities.keys())

    def get_entity(self, name: str) -> Entity:
        try:
            return self._entities[name]
        except KeyError:
            raise OntologyError(f"unknown entity: {name!r}") from None

    def get_attributes(self, entity_type: str) -> list[Attribute]:
        self.get_entity(entity_type)  # validates existence
        return list(self._attributes_by_entity.get(entity_type, ()))

    def get_attribute(self, entity_type: str, name: str) -> Attribute:
        try:
            return self._attribute_index[(entity_type, name)]
        except KeyError:
            raise OntologyError(
                f"unknown attribute: {entity_type}.{name}"
            ) from None

    def get_relationships(self, entity_type: str) -> list[Relationship]:
        self.get_entity(entity_type)
        return list(self._outgoing_rels.get(entity_type, ()))

    def get_relationship(
        self, subject_type: str, predicate: str
    ) -> list[Relationship]:
        """Return every relationship declaration for (subject, predicate).

        Multiple entries are possible (e.g. `performed_by` is declared on
        KnittingPlan, EmbroideryJob, SewingJob) — call sites pass the
        subject_type to disambiguate.
        """
        self.get_entity(subject_type)
        rels = self._rel_index.get((subject_type, predicate), [])
        if not rels:
            raise OntologyError(
                f"no relationship {subject_type}.{predicate}"
            )
        return list(rels)

    def get_event_type(self, name: str) -> EventType:
        # Accept the base name or the deadline suffix (StageDeadline
        # objects reuse the same catalog with a `_DEADLINE` suffix).
        if name in self._event_types:
            return self._event_types[name]
        if name.endswith("_DEADLINE"):
            base = name[: -len("_DEADLINE")]
            if base in self._event_types:
                return EventType(name=name, is_deadline=True)
        raise OntologyError(f"unknown event type: {name!r}")

    def event_type_names(self) -> list[str]:
        return list(self._event_types.keys())

    # ---- validation -------------------------------------------------------

    def validate_attribute(
        self, entity_type: str, predicate: str, value: Any
    ) -> None:
        """Raise OntologyError if `value` cannot legally be assigned to
        `entity_type.predicate`. Returns None on success.
        """
        attr = self.get_attribute(entity_type, predicate)
        t = attr.type

        if value is None:
            # A null is legal at ingest — the fact records status=UNRESOLVED.
            return

        k = t.kind
        if k == "text":
            if not isinstance(value, str):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected text, got {type(value).__name__}"
                )
        elif k == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected integer, got {type(value).__name__}"
                )
        elif k == "decimal":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected decimal, got {type(value).__name__}"
                )
        elif k == "boolean":
            if not isinstance(value, bool):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected boolean, got {type(value).__name__}"
                )
        elif k == "date":
            if not isinstance(value, (date, str)):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected date, got {type(value).__name__}"
                )
        elif k == "timestamp":
            if not isinstance(value, (datetime, str)):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected timestamp, got {type(value).__name__}"
                )
        elif k == "enum":
            if value not in t.enum_values:
                raise OntologyError(
                    f"{entity_type}.{predicate}: {value!r} not in enum "
                    f"{list(t.enum_values)}"
                )
        elif k == "ref":
            if not isinstance(value, str):
                raise OntologyError(
                    f"{entity_type}.{predicate}: ref expects an object_id string"
                )
        elif k == "list_text":
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected list of text"
                )
        elif k == "list_ref":
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected list of ref (object_id strings)"
                )
        elif k == "map":
            if not isinstance(value, dict):
                raise OntologyError(
                    f"{entity_type}.{predicate}: expected map"
                )
        elif k == "any":
            return
        else:  # pragma: no cover — parse_attribute_type gates this
            raise OntologyError(
                f"{entity_type}.{predicate}: unhandled type kind {k!r}"
            )

    def validate_relationship(
        self, subject_type: str, predicate: str, object_type: str
    ) -> None:
        """Raise OntologyError if the (subject_type, predicate, object_type)
        triple is not declared in the ontology.

        Polymorphic relationships (`object` marker `any` etc.) accept any
        declared entity as `object_type`; the caller is responsible for
        recording the concrete type in provenance.
        """
        rels = self.get_relationship(subject_type, predicate)
        if object_type not in self._entities:
            raise OntologyError(
                f"{subject_type}.{predicate}→{object_type}: object_type is not a known entity"
            )
        for r in rels:
            if r.object_is_polymorphic:
                return
            if r.object == object_type:
                return
        allowed = [r.object for r in rels]
        raise OntologyError(
            f"{subject_type}.{predicate}: {object_type!r} not among declared "
            f"target(s) {allowed}"
        )
