"""Build the source-bound IKS graph and its audit reports."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.namespace import DCTERMS, OWL, SKOS

from .errors import BuildError
from .sources import (
    ROOT,
    SOURCE_DIR,
    Source,
    canonical_hash,
    find_span,
    find_tsv_row_span,
    load_sources,
    tsv_row_spans,
    witness_text,
)
from .translit import normalize_for_source, normalize_iast, to_devanagari, to_iast, to_slp1

IKS = Namespace("urn:iks:")
DATA_DIR = ROOT / "data"
SCHEMA_DIR = ROOT / "schema"
DIST_DIR = ROOT / "dist"
REPORT_DIR = ROOT / "reports"

KIND_CLASS = {
    "Veda": IKS.Veda,
    "Vedanga": IKS.Vedanga,
    "Upaveda": IKS.Upaveda,
    "Darsana": IKS.Darsana,
    "Purana": IKS.Purana,
    "Kala": IKS.Kala,
    "KnowledgeSystem": IKS.KnowledgeSystem,
}

CLAIM_TYPES = {
    "membership": IKS.MembershipClaim,
    "textual_count": IKS.CountClaim,
    "textual_definition": IKS.DefinitionClaim,
    "textual_attestation": IKS.AttestationClaim,
    "textual_crosscheck": IKS.AttestationClaim,
    "lexical_attestation": IKS.AttestationClaim,
    "dataset_attestation": IKS.AttestationClaim,
    "dataset_crosscheck": IKS.AttestationClaim,
    "doxographic_coverage": IKS.AttestationClaim,
    "editorial_gloss": IKS.EditorialClaim,
    "editorial_taxonomy": IKS.EditorialClaim,
    "editorial_identification": IKS.EditorialClaim,
}


def _node(identifier: str) -> URIRef:
    return IKS[identifier]


def _lit(value: str, lang: str | None = None) -> Literal:
    return Literal(value, lang=lang) if lang else Literal(value)


def _int(value: int) -> Literal:
    return Literal(value, datatype=XSD.integer)


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


class Builder:
    def __init__(self) -> None:
        self.g = Graph()
        self.g.bind("iks", IKS)
        self.g.bind("skos", SKOS)
        self.g.bind("dcterms", DCTERMS)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
        self.g.parse(SCHEMA_DIR / "iks-kg.ttl", format="turtle")
        self.sources = load_sources()
        self.taxonomy = _load_json("taxonomy.json")
        self.kalas = _load_json("kalas.json")
        self.rules_data = _load_json("rules.json")["rules"]
        self.terms_data = _load_json("terms_vyakarana.json")["terms"]
        self.selection = _load_json("dhatu_selection.json")
        self.texts_data = _load_json("texts.json")["texts"]
        self.entities = self.taxonomy["entities"] + self.kalas["entities"]
        self.lists = self.taxonomy["lists"] + self.kalas["lists"]
        self.labels: dict[str, str] = {}
        self._claim_seq = 0
        self._dhatu_aux: dict[str, dict[str, Any]] = {}
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        ids = [e["id"] for e in self.entities] + [l["id"] for l in self.lists]
        if len(ids) != len(set(ids)):
            raise BuildError("duplicate entity/list ids in input data")
        rule_ids = {r["id"] for r in self.rules_data}
        if len(rule_ids) != len(self.rules_data):
            raise BuildError("duplicate rule ids")
        rule_numbers = [r["number"] for r in self.rules_data]
        if len(rule_numbers) != len(set(rule_numbers)):
            raise BuildError("duplicate rule numbers")
        rows = tsv_row_spans("src-vidyut-sutrapatha")
        for rule in self.rules_data:
            if rule["number"] not in rows:
                raise BuildError(f"rule number missing from sūtrapāṭha: {rule['number']}")
            expected = normalize_for_source(rule["slp1"], "SLP1")
            if rows[rule["number"]][2] != expected:
                raise BuildError(
                    f"rule text does not match sūtrapāṭha row: {rule['number']}"
                )
        term_ids = {t["id"] for t in self.terms_data}
        if len(term_ids) != len(self.terms_data):
            raise BuildError("duplicate term ids")
        rules_by_id = {r["id"]: r for r in self.rules_data}
        text_ids = {t["id"] for t in self.texts_data}
        for text in self.texts_data:
            for sid in text["witness_source_ids"]:
                if sid not in self.sources:
                    raise BuildError(f"unknown witness source {sid} for {text['id']}")
        for rule in self.rules_data:
            for tid in rule.get("relevant_terms", []):
                if tid not in term_ids:
                    raise BuildError(f"unknown term {tid} in {rule['id']}")
        for term in self.terms_data:
            if term["claim"]["target"] not in rule_ids:
                raise BuildError(f"unknown rule target in {term['id']}")
            if term["claim"]["source_id"] not in self.sources:
                raise BuildError(f"unknown source in {term['id']}")
            target_number = rules_by_id[term["claim"]["target"]]["number"]
            anchor = term["claim"].get("anchor_slp1")
            if anchor is not None:
                if normalize_for_source(anchor, "SLP1") != rows[target_number][2]:
                    raise BuildError(
                        f"term anchor does not match its rule row: {term['id']}"
                    )
        for entity in self.entities:
            for claim in entity.get("claims", []):
                if claim["source_id"] not in self.sources:
                    raise BuildError(f"unknown source in {entity['id']}")
                if claim.get("target") not in {x["id"] for x in self.lists}:
                    # Terms and rules use direct targets, not this path.
                    raise BuildError(f"unknown list target in {entity['id']}: {claim.get('target')}")
        for lst in self.lists:
            if lst["kind"] == "CanonicalList":
                count = int(lst["member_count"])
                if "members" in lst:
                    if len(lst["members"]) != count:
                        raise BuildError(f"member count mismatch in {lst['id']}")
                if "components" in lst:
                    total = sum(int(c["count"]) for c in lst["components"])
                    if total != count:
                        raise BuildError(f"component count mismatch in {lst['id']}: {total} != {count}")
                if lst["count_claim"]["source_id"] not in self.sources:
                    raise BuildError(f"unknown count source in {lst['id']}")
        if len(self.selection["roots"]) != int(self.selection["target_count"]):
            raise BuildError("dhātu selection count mismatch")
        if len({r["baseindex"] for r in self.selection["roots"]}) != len(self.selection["roots"]):
            raise BuildError("duplicate dhātu baseindex")
        del text_ids  # validated above; keep the variable explicit for readability

    # ------------------------------------------------------------------
    # Node construction
    # ------------------------------------------------------------------
    def add_sources(self) -> None:
        for source in self.sources.values():
            node = _node(source.id)
            self.g.add((node, RDF.type, IKS.Source))
            self.g.add((node, DCTERMS.title, _lit(source.title, "en")))
            self.g.add((node, IKS.sourceType, _lit(source.source_type)))
            self.g.add((node, IKS.url, Literal(source.url, datatype=XSD.anyURI)))
            self.g.add((node, IKS.localPath, _lit(source.local_path)))
            self.g.add((node, IKS.sha256, _lit(source.sha256)))
            self.g.add((node, IKS.license, _lit(source.license)))
            self.g.add((node, IKS.retrievedAt, Literal(source.retrieved_at, datatype=XSD.date)))
            self.g.add((node, IKS.quality, _lit(source.quality)))
            self.g.add((node, IKS.extraction, _lit(source.extraction)))
            if source.author:
                self.g.add((node, IKS.author, _lit(source.author)))
            if source.edition:
                self.g.add((node, DCTERMS.description, _lit(source.edition)))
            if source.notes:
                self.g.add((node, IKS.note, _lit(source.notes)))

    def add_texts(self) -> None:
        for text in self.texts_data:
            node = _node(text["id"])
            self.g.add((node, RDF.type, IKS.Text))
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            sa = text.get("title_sa") or to_devanagari(text["title_iast"], "IAST")
            self.g.add((node, SKOS.prefLabel, _lit(sa, "sa")))
            self.g.add((node, SKOS.prefLabel, _lit(text["title_iast"], "sa-Latn")))
            self.g.add((node, SKOS.prefLabel, _lit(text["title_en"], "en")))
            self.g.add((node, IKS.titleSa, _lit(sa)))
            self.g.add((node, IKS.titleIast, _lit(text["title_iast"])))
            self.g.add((node, IKS.titleEn, _lit(text["title_en"])))
            self.g.add((node, IKS.author, _lit(text.get("author", ""))))
            self.g.add((node, IKS.note, _lit(text.get("notes", ""))))
            self.labels[text["id"]] = text["title_iast"]

    def add_entities(self) -> None:
        for entity in self.entities:
            node = _node(entity["id"])
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            kind = entity.get("kind", "KnowledgeSystem")
            if kind not in KIND_CLASS:
                raise BuildError(f"unknown entity kind {kind!r} for {entity['id']}")
            self.g.add((node, RDF.type, KIND_CLASS[kind]))
            iast = entity["iast"]
            sa = entity.get("sa") or to_devanagari(iast, "IAST")
            self.g.add((node, SKOS.prefLabel, _lit(sa, "sa")))
            self.g.add((node, SKOS.prefLabel, _lit(iast, "sa-Latn")))
            self.g.add((node, SKOS.prefLabel, _lit(entity["en"], "en")))
            self.g.add((node, SKOS.altLabel, _lit(entity["en"], "en")))
            if "ordinal" in entity:
                self.g.add((node, IKS.ordinal, _int(int(entity["ordinal"]))))
            if entity.get("gloss_status"):
                self.g.add((node, IKS.glossStatus, _lit(entity["gloss_status"])))
            if entity.get("known_issue"):
                self.g.add((node, IKS.note, _lit(entity["known_issue"])))
            self.labels[entity["id"]] = iast

    def add_lists(self) -> None:
        for lst in self.lists:
            node = _node(lst["id"])
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            self.g.add((node, RDF.type, IKS[lst["kind"]]))
            iast = lst["iast"]
            sa = lst.get("sa") or to_devanagari(iast, "IAST")
            self.g.add((node, SKOS.prefLabel, _lit(sa, "sa")))
            self.g.add((node, SKOS.prefLabel, _lit(iast, "sa-Latn")))
            self.g.add((node, SKOS.prefLabel, _lit(lst["en"], "en")))
            if lst.get("list_basis"):
                self.g.add((node, IKS.listBasis, _lit(lst["list_basis"])))
            if "member_count" in lst:
                self.g.add((node, IKS.memberCount, _int(int(lst["member_count"]))))
            if lst.get("scope_note"):
                self.g.add((node, IKS.scopeNote, _lit(lst["scope_note"])))
            if lst.get("selection_basis"):
                self.g.add((node, IKS.selectionBasis, _lit(lst["selection_basis"])))
            for ref in lst.get("members", []):
                if ref not in self.labels:
                    raise BuildError(f"unknown member {ref} in {lst['id']}")
                self.g.add((node, IKS.hasMember, _node(ref)))
            for comp in lst.get("components", []):
                ref = comp["ref"]
                if ref not in self.labels:
                    raise BuildError(f"unknown component {ref} in {lst['id']}")
                comp_id = f"component-{lst['id']}-{ref}"
                cnode = _node(comp_id)
                self.g.add((cnode, RDF.type, IKS.ListComponent))
                self.g.add((cnode, IKS.componentOf, node))
                self.g.add((cnode, IKS.componentRef, _node(ref)))
                self.g.add((cnode, IKS.componentCount, _int(int(comp["count"]))))
                self.g.add((node, IKS.component, cnode))
                self.g.add((node, IKS.hasMember, _node(ref)))
            if lst.get("related_list"):
                target = lst["related_list"]
                if target not in {x["id"] for x in self.lists}:
                    raise BuildError(f"unknown related list {target} in {lst['id']}")
                self.g.add((node, IKS.relatedList, _node(target)))
                target_count = next(
                    (int(x["member_count"]) for x in self.lists if x["id"] == target and "member_count" in x),
                    None,
                )
                if target_count is not None and target_count == int(lst["member_count"]):
                    self.g.add((node, IKS.sameCountAs, _node(target)))
                self.g.add((node, IKS.correspondsTo, _node(target)))
            if lst.get("correspondence_note"):
                self.g.add((node, IKS.note, _lit(lst["correspondence_note"])))
            self.labels[lst["id"]] = iast

    def add_rules(self) -> None:
        for rule in self.rules_data:
            node = _node(rule["id"])
            self.g.add((node, RDF.type, IKS.Rule))
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            label = f"A {rule['number']}"
            self.g.add((node, SKOS.prefLabel, _lit(label, "en")))
            self.g.add((node, IKS.ruleNumber, _lit(rule["number"])))
            self.g.add((node, IKS.ruleTextSlp1, _lit(rule["slp1"])))
            self.g.add((node, IKS.ruleTextIast, _lit(to_iast(rule["slp1"], "SLP1"))))
            self.g.add((node, IKS.ruleTextSa, _lit(to_devanagari(rule["slp1"], "SLP1"))))
            self.g.add((node, IKS.definedIn, _node("text-ashtadhyayi")))
            if rule.get("topic"):
                self.g.add((node, IKS.note, _lit(rule["topic"])))
            self.labels[rule["id"]] = label

    def add_terms(self) -> None:
        for term in self.terms_data:
            node = _node(term["id"])
            self.g.add((node, RDF.type, IKS.VyakaranaTerm))
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            sa = to_devanagari(term["iast"], "IAST")
            self.g.add((node, SKOS.prefLabel, _lit(sa, "sa")))
            self.g.add((node, SKOS.prefLabel, _lit(term["iast"], "sa-Latn")))
            self.g.add((node, SKOS.prefLabel, _lit(term["en"], "en")))
            self.g.add((node, IKS.termSa, _lit(sa)))
            self.g.add((node, IKS.termIast, _lit(term["iast"])))
            self.g.add((node, IKS.termEn, _lit(term["en"])))
            self.g.add((node, IKS.definition, _lit(term["definition_note"])))
            self.g.add((node, IKS.glossStatus, _lit(term["gloss_status"])))
            target = term["claim"]["target"]
            if target not in self.labels:
                raise BuildError(f"unknown rule target {target} in {term['id']}")
            self.g.add((node, IKS.definedBy, _node(target)))
            self.labels[term["id"]] = term["iast"]

    def _dhatu_records(self) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[str, str]]]:
        payload = json.loads(
            (SOURCE_DIR / "dhatu-ashtadhyayi.json").read_text(encoding="utf-8")
        )
        records = {r["baseindex"]: r for r in payload["data"]}
        vidyut: dict[str, tuple[str, str]] = {}
        for line in (SOURCE_DIR / "dhatupatha-vidyut.tsv").read_text(encoding="utf-8").splitlines()[1:]:
            code, root, artha = line.split("\t")
            vidyut[code] = (root, artha)
        return records, vidyut

    def add_dhatus(self) -> None:
        records, vidyut = self._dhatu_records()
        for item in self.selection["roots"]:
            code = item["baseindex"]
            record = records.get(code)
            if record is None:
                raise BuildError(f"selected dhātu {code} missing from primary dataset")
            tags = record.get("tags", "").split(",")
            if "ganasutra" in tags:
                raise BuildError(f"selected dhātu {code} is a gaṇasūtra record")
            if not record.get("artha_english", "").strip():
                raise BuildError(f"selected dhātu {code} has no English gloss")
            if code not in vidyut:
                raise BuildError(f"selected dhātu {code} missing from Vidyut crosscheck")
            vroot, vartha = vidyut[code]
            primary_meaning = normalize_iast(to_iast(record["artha"], "Devanagari"))
            vidyut_meaning = normalize_iast(to_iast(vartha, "SLP1"))
            variant = self.selection.get("crosscheck_variants", {}).get(code)
            mismatch = primary_meaning != vidyut_meaning
            if mismatch:
                if variant is None:
                    raise BuildError(
                        f"dhātu meaning mismatch for {code}: {primary_meaning!r} != {vidyut_meaning!r}"
                    )
                declared_vidyut = normalize_iast(
                    to_iast(variant["vidyut_artha"], "SLP1")
                )
                if declared_vidyut != vidyut_meaning:
                    raise BuildError(
                        f"stale crosscheck variant for {code}: {declared_vidyut!r} != {vidyut_meaning!r}"
                    )
            node = _node(f"dhatu-{code.replace('.', '-')}")
            self.g.add((node, RDF.type, IKS.Dhatu))
            self.g.add((node, RDF.type, IKS.LexicalEntry))
            self.g.add((node, RDF.type, IKS.KnowledgeEntity))
            root_sa = record["dhatu"]
            root_iast = to_iast(root_sa, "Devanagari")
            root_slp1 = to_slp1(root_sa, "Devanagari")
            meaning_sa = record["artha"]
            meaning_iast = to_iast(meaning_sa, "Devanagari")
            self.g.add((node, SKOS.prefLabel, _lit(root_sa, "sa")))
            self.g.add((node, SKOS.prefLabel, _lit(root_iast, "sa-Latn")))
            self.g.add((node, SKOS.prefLabel, _lit(f"{root_iast} ({code})", "en")))
            self.g.add((node, IKS.rootSlp1, _lit(root_slp1)))
            self.g.add((node, IKS.rootSa, _lit(root_sa)))
            self.g.add((node, IKS.rootIast, _lit(root_iast)))
            self.g.add((node, IKS.gana, _int(int(record["gana"]))))
            self.g.add((node, IKS.pada, _lit(record["pada"])))
            self.g.add((node, IKS.meaningSa, _lit(meaning_sa)))
            self.g.add((node, IKS.meaningIast, _lit(meaning_iast)))
            self.g.add((node, IKS.meaningEn, _lit(record["artha_english"])))
            self.g.add((node, IKS.dhatupathaCode, _lit(code)))
            self.g.add((node, IKS.crosscheckSource, _node(self.selection["crosscheck_source_id"])))
            self.g.add((node, IKS.crosscheckCode, _lit(code)))
            self.g.add((node, IKS.sourceRecord, _lit(code)))
            node_id = f"dhatu-{code.replace('.', '-')}"
            self.labels[node_id] = root_iast
            self._dhatu_aux[code] = {
                "node": node_id,
                "record_hash": canonical_hash(record),
                "cross_hash": canonical_hash({"code": code, "dhatu": vroot, "artha": vartha}),
                "meaning_en": record["artha_english"],
                "root_iast": root_iast,
                "tier": item["tier"],
                "crosscheck_status": (
                    "flagged_uncertain" if mismatch else "verified_secondary"
                ),
                "crosscheck_claim_text": (
                    f"The Vidyut record for {root_iast} carries the meaning "
                    f"{variant['vidyut_iast']}, while the primary record reads "
                    f"{variant['primary_iast']}; the primary meaning is retained."
                    if mismatch
                    else None
                ),
                "crosscheck_rationale": (
                    "The code and root correspond, but the meaning strings differ "
                    "by a documented reading variant; the crosscheck is flagged "
                    "rather than treated as an agreement."
                    if mismatch
                    else None
                ),
                "crosscheck_known_issue": variant["note"] if mismatch else None,
            }

    # ------------------------------------------------------------------
    # Claims and citations
    # ------------------------------------------------------------------
    def _claim_id(self, subject: str, relation: str, target: str) -> str:
        self._claim_seq += 1
        safe_target = "".join(c if c.isalnum() or c in "-_" else "-" for c in target)
        return f"claim-{subject}-{relation.split(':')[-1]}-{safe_target}-{self._claim_seq:04d}"

    def add_claim(
        self,
        subject_id: str,
        relation: URIRef,
        obj: URIRef | Literal,
        *,
        source_id: str,
        locator: str,
        anchor: str | None = None,
        anchor_script: str = "IAST",
        anchor_after: str | None = None,
        anchor_after_script: str = "IAST",
        anchor_row: str | None = None,
        record_hash: str | None = None,
        assertion_type: str,
        status: str = "verified_primary",
        method: str = "normalized_string_match",
        rationale: str | None = None,
        claim_text: str | None = None,
        known_issue: str | None = None,
    ) -> str:
        if source_id not in self.sources:
            raise BuildError(f"unknown citation source: {source_id}")
        if status == "unverified_hypothesis":
            raise BuildError("unverified_hypothesis claims are not exportable")
        source = self.sources[source_id]
        target_id = str(obj).rsplit(":", 1)[-1] if isinstance(obj, URIRef) else ""
        claim_id = self._claim_id(subject_id, relation, target_id or "literal")
        claim = _node(claim_id)
        citation = _node(f"citation-{claim_id}")
        self.g.add((claim, RDF.type, IKS.Claim))
        claim_type = CLAIM_TYPES.get(assertion_type)
        if claim_type is not None:
            self.g.add((claim, RDF.type, claim_type))
        self.g.add((claim, IKS.subject, _node(subject_id)))
        self.g.add((claim, IKS.relation, relation))
        self.g.add((claim, IKS.object, obj))
        self.g.add((claim, IKS.assertionType, _lit(assertion_type)))
        self.g.add((claim, IKS.verificationStatus, _lit(status)))
        self.g.add((claim, IKS.method, _lit(method)))
        if claim_text is None:
            if relation == IKS.memberCount:
                claim_text = f"{self.labels.get(subject_id, subject_id)} has {obj} members."
            elif relation == IKS.hasWitness:
                claim_text = f"{self.labels.get(subject_id, subject_id)} is witnessed by {self.labels.get(target_id, target_id)}."
            elif relation == IKS.meaningEn:
                claim_text = f"The Dhātupāṭha record for {self.labels.get(subject_id, subject_id)} gives the meaning: {obj}."
            elif relation == IKS.crosscheckSource:
                claim_text = f"The Vidyut record for {self.labels.get(subject_id, subject_id)} agrees with the primary record."
            elif relation == IKS.memberOf:
                claim_text = f"{self.labels.get(subject_id, subject_id)} is a member of {self.labels.get(target_id, target_id)}."
            elif relation == IKS.definedBy:
                claim_text = f"{self.labels.get(subject_id, subject_id)} is defined by {self.labels.get(target_id, target_id)}."
            else:
                claim_text = f"{self.labels.get(subject_id, subject_id)} is connected to {self.labels.get(target_id, target_id)} by {relation.split(':')[-1]}."
        self.g.add((claim, IKS.claimText, _lit(claim_text)))
        if rationale is None:
            if relation == IKS.memberCount:
                rationale = "The cited passage states the count; the count claim is reified separately from list membership."
            elif relation == IKS.hasWitness:
                rationale = "The source manifest identifies this snapshot as a witness for the text."
            elif relation == IKS.meaningEn:
                rationale = "The primary lexical record and the independent Vidyut record agree after transliteration and normalization."
            elif relation == IKS.crosscheckSource:
                rationale = "The independent Vidyut record matches the primary record after transliteration and normalization."
            elif relation == IKS.definedBy:
                rationale = "The selected rule is present in the sūtrapāṭha record; the term is defined by or attested in that rule."
            else:
                rationale = "The exact source anchor is present in the normalized witness text."
        self.g.add((claim, IKS.rationale, _lit(rationale)))
        if known_issue:
            self.g.add((claim, IKS.knownIssue, _lit(known_issue)))
        self.g.add((claim, IKS.citation, citation))
        self.g.add((_node(subject_id), IKS.hasClaim, claim))

        self.g.add((citation, RDF.type, IKS.Citation))
        self.g.add((citation, IKS.source, _node(source_id)))
        self.g.add((citation, IKS.locator, _lit(locator)))
        self.g.add((citation, IKS.sourceSha256, _lit(source.sha256)))
        self.g.add((citation, IKS.retrievedAt, Literal(source.retrieved_at, datatype=XSD.date)))
        if anchor_row is not None:
            if anchor is not None:
                raise BuildError(f"claim {claim_id} has both anchor and anchor_row")
            start, end, quote = find_tsv_row_span(source_id, anchor_row)
            self.g.add((citation, IKS.evidenceQuote, _lit(quote)))
            self.g.add((citation, IKS.spanStart, _int(start)))
            self.g.add((citation, IKS.spanEnd, _int(end)))
            self.g.add((citation, IKS.spanBasis, _lit("normalized-source-text-v1")))
        elif anchor is not None:
            start, end, quote = find_span(
                source_id, anchor, anchor_script, anchor_after, anchor_after_script
            )
            self.g.add((citation, IKS.evidenceQuote, _lit(quote)))
            self.g.add((citation, IKS.spanStart, _int(start)))
            self.g.add((citation, IKS.spanEnd, _int(end)))
            self.g.add((citation, IKS.spanBasis, _lit("normalized-source-text-v1")))
        elif record_hash is not None:
            self.g.add((citation, IKS.recordHash, _lit(record_hash)))
            self.g.add((citation, IKS.evidenceQuote, _lit(f"record:{record_hash[:16]}")))
        else:
            raise BuildError(f"claim {claim_id} has no evidence anchor or record hash")

        if relation == IKS.memberOf and isinstance(obj, URIRef):
            self.g.add((obj, IKS.memberOf, _node(subject_id)))
            self.g.add((obj, IKS.hasMember, _node(subject_id)))
        elif relation == IKS.memberCount:
            self.g.add((_node(subject_id), IKS.hasCountClaim, claim))
        elif isinstance(obj, URIRef):
            self.g.add((_node(subject_id), relation, obj))
        return claim_id

    def add_claims(self) -> None:
        for entity in self.entities:
            for claim in entity.get("claims", []):
                relation = URIRef(claim.get("relation", str(IKS.memberOf)))
                self.add_claim(
                    entity["id"],
                    relation,
                    _node(claim["target"]),
                    source_id=claim["source_id"],
                    locator=claim["locator"],
                    anchor=claim.get("anchor"),
                    anchor_script=claim.get("anchor_script", "IAST"),
                    anchor_after=claim.get("anchor_after"),
                    anchor_after_script=claim.get("anchor_after_script", "IAST"),
                    anchor_row=claim.get("anchor_row"),
                    record_hash=claim.get("record_hash"),
                    assertion_type=claim.get("assertion_type", "textual_listing"),
                    status=claim.get("status", "verified_primary"),
                    method=claim.get("method", "normalized_string_match"),
                    rationale=claim.get("rationale"),
                    claim_text=claim.get("claim_text"),
                    known_issue=claim.get("known_issue"),
                )
        for lst in self.lists:
            if lst["kind"] != "CanonicalList":
                continue
            count_claim = lst["count_claim"]
            self.add_claim(
                lst["id"],
                IKS.memberCount,
                _int(int(lst["member_count"])),
                source_id=count_claim["source_id"],
                locator=count_claim["locator"],
                anchor=count_claim.get("anchor"),
                anchor_script=count_claim.get("anchor_script", "IAST"),
                anchor_after=count_claim.get("anchor_after"),
                anchor_after_script=count_claim.get("anchor_after_script", "IAST"),
                anchor_row=count_claim.get("anchor_row"),
                record_hash=count_claim.get("record_hash"),
                assertion_type="textual_count",
                status=count_claim.get("status", "verified_primary"),
                method=count_claim.get("method", "normalized_string_match"),
                rationale=count_claim.get("rationale"),
                known_issue=count_claim.get("known_issue"),
            )
            count_crosscheck = lst.get("count_crosscheck")
            if count_crosscheck:
                self.add_claim(
                    lst["id"],
                    IKS.memberCount,
                    _int(int(lst["member_count"])),
                    source_id=count_crosscheck["source_id"],
                    locator=count_crosscheck["locator"],
                    anchor=count_crosscheck.get("anchor"),
                    anchor_script=count_crosscheck.get("anchor_script", "IAST"),
                    anchor_after=count_crosscheck.get("anchor_after"),
                    anchor_after_script=count_crosscheck.get("anchor_after_script", "IAST"),
                    anchor_row=count_crosscheck.get("anchor_row"),
                    record_hash=count_crosscheck.get("record_hash"),
                    assertion_type=count_crosscheck.get("assertion_type", "textual_count"),
                    status=count_crosscheck.get("status", "verified_secondary"),
                    method=count_crosscheck.get("method", "cross_witness_match"),
                    rationale=count_crosscheck.get("rationale"),
                    known_issue=count_crosscheck.get("known_issue"),
                )
        for text in self.texts_data:
            for sid in text["witness_source_ids"]:
                source = self.sources[sid]
                self.add_claim(
                    text["id"],
                    IKS.hasWitness,
                    _node(sid),
                    source_id=sid,
                    locator=f"Source witness: {source.title}",
                    record_hash=source.sha256,
                    assertion_type="dataset_attestation",
                    status="verified_secondary",
                    method="dataset_record_join",
                    rationale="The source manifest identifies this snapshot as a witness for the text.",
                )
        for rule in self.rules_data:
            self.add_claim(
                rule["id"],
                IKS.definedIn,
                _node("text-ashtadhyayi"),
                source_id="src-vidyut-sutrapatha",
                locator=f"Aṣṭādhyāyī {rule['number']}",
                anchor_row=rule["number"],
                assertion_type="textual_attestation",
                status="verified_primary",
                method="normalized_string_match",
                rationale="The rule row is present in the Vidyut sūtrapāṭha and cross-checked against the audited rule records.",
            )
        rules_by_id = {r["id"]: r for r in self.rules_data}
        for term in self.terms_data:
            c = term["claim"]
            self.add_claim(
                term["id"],
                IKS.definedBy,
                _node(c["target"]),
                source_id=c["source_id"],
                locator=c["locator"],
                anchor_row=rules_by_id[c["target"]]["number"],
                record_hash=c.get("record_hash"),
                assertion_type=c.get("assertion_type", "textual_definition"),
                status=c.get("status", "verified_primary"),
                method=c.get("method", "normalized_string_match"),
                rationale=c.get("rationale"),
                known_issue=c.get("known_issue"),
            )
        for code, aux in self._dhatu_aux.items():
            self.add_claim(
                aux["node"],
                IKS.meaningEn,
                _lit(aux["meaning_en"]),
                source_id=self.selection["primary_source_id"],
                locator=f"Dhātupāṭha {code}",
                record_hash=aux["record_hash"],
                assertion_type="lexical_attestation",
                status="verified_primary",
                method="dataset_record_join",
                rationale="The primary dataset record supplies the code, root, gaṇa, pada, and meaning.",
            )
            self.add_claim(
                aux["node"],
                IKS.crosscheckSource,
                _node(self.selection["crosscheck_source_id"]),
                source_id=self.selection["crosscheck_source_id"],
                locator=f"Vidyut dhātupāṭha {code}",
                record_hash=aux["cross_hash"],
                assertion_type="dataset_crosscheck",
                status=aux["crosscheck_status"],
                method="dataset_crosscheck",
                rationale=aux["crosscheck_rationale"]
                or "The Vidyut record code and meaning match the primary record after transliteration and normalization.",
                claim_text=aux["crosscheck_claim_text"],
                known_issue=aux["crosscheck_known_issue"],
            )

    # ------------------------------------------------------------------
    # Auditing and output
    # ------------------------------------------------------------------
    def audit_evidence(self) -> dict[str, Any]:
        problems: list[str] = []
        citations = list(self.g.subjects(RDF.type, IKS.Citation))
        spans = 0
        records = 0
        for citation in citations:
            source = self.g.value(citation, IKS.source)
            source_sha = self.g.value(citation, IKS.sourceSha256)
            if source is None or source_sha is None:
                problems.append(f"citation without source metadata: {citation}")
                continue
            source_id = str(source).rsplit(":", 1)[-1]
            manifest = self.sources.get(source_id)
            if manifest is None:
                problems.append(f"citation source not in manifest: {source}")
            elif str(source_sha) != manifest.sha256:
                problems.append(f"citation source hash mismatch: {citation}")
            start = self.g.value(citation, IKS.spanStart)
            end = self.g.value(citation, IKS.spanEnd)
            quote = self.g.value(citation, IKS.evidenceQuote)
            if start is not None and end is not None:
                spans += 1
                text = witness_text(source_id)
                actual = text[int(start) : int(end)]
                if quote is None or str(quote) != actual:
                    problems.append(f"span/quote mismatch: {citation}")
            elif self.g.value(citation, IKS.recordHash) is not None:
                records += 1
            else:
                problems.append(f"citation has neither span nor record hash: {citation}")
        claims = list(self.g.subjects(RDF.type, IKS.Claim))
        bad_status = [
            str(c)
            for c in claims
            if str(self.g.value(c, IKS.verificationStatus)) not in {
                "verified_primary",
                "verified_secondary",
                "flagged_uncertain",
                "editorial",
            }
        ]
        return {
            "citations": len(citations),
            "span_citations": spans,
            "record_hash_citations": records,
            "claims": len(claims),
            "bad_status_claims": bad_status,
            "problems": problems,
        }

    def stats(self) -> dict[str, Any]:
        claims = list(self.g.subjects(RDF.type, IKS.Claim))
        status_counts = Counter(str(self.g.value(c, IKS.verificationStatus)) for c in claims)
        assertion_counts = Counter(str(self.g.value(c, IKS.assertionType)) for c in claims)
        citation_count = len(list(self.g.subjects(RDF.type, IKS.Citation)))
        audit = self.audit_evidence()
        dhatus = list(self.g.subjects(RDF.type, IKS.Dhatu))
        gana_counts = Counter(int(self.g.value(d, IKS.gana)) for d in dhatus)
        knowledge_entities = set(self.g.subjects(RDF.type, IKS.KnowledgeEntity))
        return {
            "triples": len(self.g),
            "sources": len(self.sources),
            "texts": len(self.texts_data),
            "entities": len(self.entities),
            "knowledge_entities": len(knowledge_entities),
            "lists": len(self.lists),
            "canonical_lists": sum(1 for x in self.lists if x["kind"] == "CanonicalList"),
            "taxonomy_groups": sum(1 for x in self.lists if x["kind"] == "TaxonomyGroup"),
            "rules": len(self.rules_data),
            "terms": len(self.terms_data),
            "dhatus": len(dhatus),
            "claims": len(claims),
            "citations": citation_count,
            "status_counts": dict(sorted(status_counts.items())),
            "assertion_counts": dict(sorted(assertion_counts.items())),
            "dhatu_gana_counts": {str(k): v for k, v in sorted(gana_counts.items())},
            "audit": audit,
        }

    def coverage(self) -> dict[str, Any]:
        def count_type(t: URIRef) -> int:
            return len(list(self.g.subjects(RDF.type, t)))

        return {
            "vidyas": int(self.g.value(_node("list-18-vidya"), IKS.memberCount) or 0),
            "vedas": count_type(IKS.Veda),
            "vedangas": count_type(IKS.Vedanga),
            "upavedas": count_type(IKS.Upaveda),
            "darsanas": count_type(IKS.Darsana),
            "puranas": count_type(IKS.Purana),
            "kalas": count_type(IKS.Kala),
            "lists": count_type(IKS.CanonicalList) + count_type(IKS.TaxonomyGroup),
            "canonical_lists": count_type(IKS.CanonicalList),
            "taxonomy_groups": count_type(IKS.TaxonomyGroup),
            "dhatus": count_type(IKS.Dhatu),
            "rules": count_type(IKS.Rule),
            "terms": count_type(IKS.VyakaranaTerm),
            "texts": count_type(IKS.Text),
            "sources": count_type(IKS.Source),
            "claims": count_type(IKS.Claim),
            "citation_count": count_type(IKS.Citation),
            "knowledge_entities": count_type(IKS.KnowledgeEntity),
            "dhatu_selection_total": len(self.selection["roots"]),
            "dhatu_tiers": dict(
                sorted(Counter(r["tier"] for r in self.selection["roots"]).items())
            ),
        }


def build() -> tuple[Graph, dict[str, Any], dict[str, Any], dict[str, Any]]:
    builder = Builder()
    builder.add_sources()
    builder.add_texts()
    builder.add_entities()
    builder.add_lists()
    builder.add_rules()
    builder.add_terms()
    builder.add_dhatus()
    builder.add_claims()
    stats = builder.stats()
    coverage = builder.coverage()
    audit = builder.audit_evidence()
    if audit["problems"]:
        raise BuildError("evidence audit failed: " + "; ".join(audit["problems"][:5]))
    if audit["bad_status_claims"]:
        raise BuildError("claims with invalid verification status")
    return builder.g, stats, coverage, audit


def load_shapes() -> Graph:
    shapes = Graph()
    shapes.parse(SCHEMA_DIR / "iks-kg.shacl.ttl", format="turtle")
    return shapes


def validate(graph: Graph) -> tuple[bool, str]:
    from pyshacl import validate as shacl_validate

    conforms, _, results_text = shacl_validate(
        graph,
        shacl_graph=load_shapes(),
        inference=None,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )
    return bool(conforms), str(results_text)


def write_outputs(
    graph: Graph,
    stats: dict[str, Any],
    coverage: dict[str, Any],
    audit: dict[str, Any],
    validation: dict[str, Any],
) -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=DIST_DIR / "iks-kg.ttl", format="turtle", encoding="utf-8")
    nt = graph.serialize(format="nt")
    (DIST_DIR / "iks-kg.nt").write_text(
        "\n".join(sorted(line for line in nt.splitlines() if line.strip())) + "\n",
        encoding="utf-8",
    )
    context = json.loads((SCHEMA_DIR / "context.jsonld").read_text(encoding="utf-8"))
    jsonld = json.loads(
        graph.serialize(
            format="json-ld",
            context=context.get("@context", context),
        )
    )
    if isinstance(jsonld.get("@graph"), list):
        jsonld["@graph"].sort(
            key=lambda node: str(node.get("id") or node.get("@id") or "")
        )
    (DIST_DIR / "iks-kg.jsonld").write_text(
        json.dumps(jsonld, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(SCHEMA_DIR / "context.jsonld", DIST_DIR / "context.jsonld")
    shutil.copy2(SCHEMA_DIR / "iks-kg.shacl.ttl", DIST_DIR / "shacl.ttl")
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (REPORT_DIR / "coverage.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tiers = coverage.get("dhatu_tiers", {})
    tier_text = ", ".join(
        f"{tiers.get(k, 0)} {k}"
        for k in ("core", "additional", "extended", "outside_common")
    )
    summary = (
        "# IKS Knowledge Graph\n\n"
        f"- Triples: {stats['triples']}\n"
        f"- Taxonomy entities: {stats['entities']}\n"
        f"- Knowledge entities: {stats['knowledge_entities']}\n"
        f"- Dhātus: {stats['dhatus']} ({tier_text})\n"
        f"- Rules: {stats['rules']}\n"
        f"- Terms: {stats['terms']}\n"
        f"- Claims: {stats['claims']}\n"
        f"- Citations: {stats['citations']}\n"
        f"- SHACL conforms: {validation.get('conforms')}\n\n"
        "All exported claims carry a source citation and verification status. "
        "See `coverage.json` and `validation.json` for details.\n"
    )
    (REPORT_DIR / "summary.md").write_text(summary, encoding="utf-8")
