"""Phase 2A — Epistemic Accumulation Engine: poset of pramanas + validation functions."""
from __future__ import annotations
from dataclasses import dataclass

PRAMANA_SETS: dict[str, frozenset[str]] = {
    "Carvaka": frozenset({"Pratyaksa"}),
    "Bauddha": frozenset({"Pratyaksa", "Anumana"}),
    "Vaisesika": frozenset({"Pratyaksa", "Anumana"}),
    "Samkhya": frozenset({"Pratyaksa", "Anumana", "Sabda"}),
    "Yoga": frozenset({"Pratyaksa", "Anumana", "Sabda"}),
    "Jaina": frozenset({"Pratyaksa", "Anumana", "Sabda"}),
    "Nyaya": frozenset({"Pratyaksa", "Anumana", "Upamana", "Sabda"}),
    "Purva-Mimamsa": frozenset({"Pratyaksa", "Anumana", "Upamana", "Sabda", "Arthapatti", "Anupalabdhi"}),
    "Advaita": frozenset({"Pratyaksa", "Anumana", "Upamana", "Sabda", "Arthapatti", "Anupalabdhi"}),
}

LAKSANA = {
    "Pratyaksa": "NS 1.1.4 indriyarthasannikarsotpannam jnanam",
    "Anumana": "NS 1.1.5 atha tatpurvakam trividham anumana",
    "Upamana": "NS 1.1.6 prasiddhasadharmyat sadhyasadhanam upamanam",
    "Sabda": "NS 1.1.7 aptopadesah sabdah",
    "Arthapatti": "Srutararthapatti-anyathanupapatti (Mimamsa)",
    "Anupalabdhi": "Abhava-grahika yogyanupalabdhi (Kumarila/Bhatta)",
}


@dataclass(frozen=True)
class CognitiveState:
    locus: str
    kala: str = "present"
    adhikari: str = "apta-adhikari"
    karana_dosa_absent: bool = True
    akanksa: bool = True
    yogyata: bool = True
    sannidhi: bool = True


def V_pratyaksa(sannikarsa: bool, avyabhicari: bool, vyavasaya: bool, state: CognitiveState) -> int:
    return int(bool(sannikarsa and avyabhicari and vyavasaya and state.karana_dosa_absent))


def V_anumana(paksadharmata: bool, vyapti: bool, trairupya: bool, hetvabhasa: str = "none") -> int:
    return int(bool(paksadharmata and vyapti and trairupya and hetvabhasa == "none"))


def V_upamana(similarity_cognition: bool, state: CognitiveState) -> int:
    return int(bool(similarity_cognition and state.karana_dosa_absent))


def V_sabda(apta: bool, state: CognitiveState) -> int:
    return int(bool(apta and state.akanksa and state.yogyata and state.sannidhi))


def V_arthapatti(srutartha: bool, anupapatti_otherwise: bool) -> int:
    return int(bool(srutartha and anupapatti_otherwise))


def V_anupalabdhi(yogya: bool, anupalabdhi: bool) -> int:
    return int(bool(yogya and anupalabdhi))


def shared_ground(school_a: str, school_b: str) -> frozenset[str]:
    """Meet in poset: pramanas both schools accept = debate common ground."""
    return PRAMANA_SETS[school_a] & PRAMANA_SETS[school_b]


def joint_ground(*schools: str) -> frozenset[str]:
    out = PRAMANA_SETS[schools[0]]
    for s in schools[1:]:
        out = out & PRAMANA_SETS[s]
    return out


def is_subset_chain() -> bool:
    order = ["Carvaka", "Bauddha", "Samkhya", "Nyaya", "Advaita"]
    for a, b in zip(order, order[1:]):
        if not PRAMANA_SETS[a] <= PRAMANA_SETS[b]:
            return False
    return True
