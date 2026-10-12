"""Phase 2E/3 — Anumana: 5-member Nyaya vs 2-member Buddhist + hetvabhasa detector."""
from __future__ import annotations
from dataclasses import dataclass, field

HETVABHASA = ["Savyabhicara", "Viruddha", "Satpratipaksa", "Asiddha", "Badhita"]


@dataclass
class Anumana:
    school: str
    form: str  # "Nyaya-5" | "Buddhist-2" | "Jaina-Trairupya"
    paksa: str
    sadhya: str
    hetu: str
    drstanta: str = ""
    vyapti: str = ""
    hetvabhasa: str = "none"
    members: dict = field(default_factory=dict)

    def construct_nyaya5(self) -> dict:
        a, s, h = self.paksa, self.sadhya, self.hetu
        return {
            "pratijna": f"{a} {s}-man ({a} has {s})",
            "hetu": f"{h}-at ({h}-possession, ablative: {h}at)",
            "udaharana": f"yo {h}-van sa {s}-man yatha {self.drstanta or 'mahanasa'}",
            "upanaya": f"tatha ca ayam {h}-van (so too this {a} is {h}-possessed)",
            "nigamana": f"tasmat {a} {s}-man",
        }

    def construct_buddhist2(self) -> dict:
        return {
            "paksadharmata": f"{self.hetu}({self.paksa})",
            "vyapti": self.vyapti or f"yatra {self.hetu} tatra {self.sadhya} (sapaksa) / vipakse asattvam",
        }

    def trairupya(self, pakse: bool, sapakse: bool, vipakse_absent: bool) -> bool:
        return bool(pakse and sapakse and vipakse_absent)

    def validate(self) -> tuple[bool, str]:
        """Returns (valid, hetvabhasa-or-none). Material grounding: drstanta required for Nyaya-5."""
        if self.hetvabhasa != "none":
            return False, self.hetvabhasa
        if self.form == "Nyaya-5" and not self.drstanta:
            return False, "Asiddha"  # udaharana missing: vyapti ungrounded
        return True, "none"


def detect_hetvabhasa(pakse: bool, sapakse: bool, vipakse_present: bool,
                      contradicts_sadhya: bool, defeated: bool) -> str:
    if not pakse:
        return "Asiddha"
    if contradicts_sadhya:
        return "Viruddha"
    if defeated:
        return "Badhita"
    if sapakse and vipakse_present:
        return "Savyabhicara"
    if False:  # placeholder for counter-reason symmetry
        return "Satpratipaksa"
    return "none"
