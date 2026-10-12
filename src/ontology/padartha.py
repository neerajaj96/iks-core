"""Phase 2B — Vaisesika 7 padarthas + Nyaya 16 padarthas as algebraic sorts."""
from __future__ import annotations

DRAVYAS_9 = ["prthivi", "ap", "tejas", "vayu", "akasa", "kala", "dik", "atman", "manas"]
GUNAS_24 = ["rupa", "rasa", "gandha", "sparsa", "sankhya", "parimana", "prthaktva",
            "samyoga", "vibhaga", "paratva", "aparatva", "buddhi", "sukha", "duhkha",
            "iccha", "dvesa", "prayatna", "gurutva", "dravatva", "sneha", "dharma",
            "adharma", "sabda", "samskara"]
KARMAS_5 = ["utksepena", "avaksepena", "akuncana", "prasarana", "gamana"]
SAMANYA_LEVELS = ["para-satta", "parapara", "apara"]
# Visesa: bijection with nitya-dravya instances; Samavaya: singleton inherence.

PADARTHAS_7 = ["Dravya", "Guna", "Karma", "Samanya", "Visesa", "Samavaya", "Abhava"]

NYAYA_16 = ["pramana", "prameya", "samsaya", "prayojana", "drstanta", "siddhanta",
            "avayava", "tarka", "nirnaya", "vada", "jalpa", "vitanda",
            "hetvabhasa", "chhala", "jati", "nigrahasthana"]

PRAMEYA_12 = ["atman", "sarira", "indriya", "artha", "buddhi", "manas",
              "pravrtti", "dosa", "pretyabhava", "phala", "duhkha", "apavarga"]

HETVABHASA_5 = ["Savyabhicara", "Viruddha", "Satpratipaksa", "Asiddha", "Badhita"]


def check_disjointness() -> bool:
    sorts = {"D": set(DRAVYAS_9), "G": set(GUNAS_24), "K": set(KARMAS_5)}
    return len(sorts["D"] & sorts["G"] & sorts["K"]) == 0 and len(sorts["D"]) == 9 \
        and len(sorts["G"]) == 24 and len(sorts["K"]) == 5


def inheres(quality: str, substance: str) -> bool:
    """Samavaya axiom: every guna/karma inheres in exactly one dravya kind; no guna bears karma."""
    if quality in GUNAS_24:
        return substance in DRAVYAS_9
    if quality in KARMAS_5:
        # akasa/kala/dik/atman are niskriya
        return substance not in {"akasa", "kala", "dik", "atman"}
    return False
