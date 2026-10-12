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

    def construct_jaina(self, standpoint: str = "syad") -> dict:
        """Jaina trairupya: vyapti standpoint-qualified; joint assertion goes via avaktavya."""
        return {
            "paksadharmata": f"{self.hetu}({self.paksa}) [{standpoint}]",
            "vyapti": (self.vyapti or f"yatra {self.hetu} tatra {self.sadhya}") + f" [{standpoint}]",
            "avaktavya_rule": "saha-arpana (simultaneous asti+nasti) -> avaktavya member",
        }

    @staticmethod
    def vyapti_pancaka() -> list[str]:
        """Gangesa's five vyapti definitions ladder: avyapti/ativyapti/asambhava
        filters culminating in siddhanta-laksana."""
        return [
            "1. sadhya-vad-bhinnatva (non-deviation, crude)",
            "2. hetu-samanadhikarana-atyantabhava-apratiyogitva (refined)",
            "3. sadhya-sambandha (relational tightening)",
            "4. pratiyogitavacchedaka-sambandha (limiter-aware)",
            "5. siddhanta-laksana: hetutavacchedaka-sambandhena sadhya-sambandhitva",
        ]

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
                      contradicts_sadhya: bool, defeated: bool,
                      counter_reason: bool = False) -> str:
    """Five hetvabhasas. counter_reason=True + sapakse support on both sides
    yields Satpratipaksa (matched counter-inference, e.g. sabda nitya vs anitya)."""
    if not pakse:
        return "Asiddha"
    if contradicts_sadhya:
        return "Viruddha"
    if defeated:
        return "Badhita"
    if counter_reason and sapakse:
        return "Satpratipaksa"
    if sapakse and vipakse_present:
        return "Savyabhicara"
    return "none"
