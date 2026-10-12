"""Expand Vyakarana: famous Astadhyayi rules (verbatim short sutras / gist long ones),
Mahabhasya + Kaumudi + Vakyapadiya index records. Plus FIXUPS for v1/v2 notations.

Tier rule: verbatim = short wording + number both certain; famous-gist otherwise.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
V = "verbatim"
F = "famous-gist"
T = "topic-digest"

# (id, notation, tier, sanskrit, translation, logicalForm)
R = [
 # -- 1.1 samjna/paribhasa --
 ("A-1111", "A 1.1.1", V, "vrddhir adaic", "vṛddhi = ā, ai, au", ""),
 ("A-1112", "A 1.1.2", V, "aden guna", "guṇa = a, e, o", ""),
 ("A-1113", "A 1.1.3", V, "iko gunavrddhi", "ik vowels take guṇa/vṛddhi substitutes", "i->e (guna)"),
 ("A-1114", "A 1.1.4", F, "na dhatulopa ardhadhatuke", "No guṇa/vṛddhi before affixes causing root-vowel loss", ""),
 ("A-1115", "A 1.1.5", F, "kniti ca", "No guṇa/vṛddhi before kit/ṅit affixes", ""),
 ("A-1118", "A 1.1.8", F, "mukhanasikavacano nunasikah", "Sound uttered nose-and-mouth = anunāsika", ""),
 ("A-1119", "A 1.1.9", F, "tulyasyaprayatnam savarnam", "Same articulation place+effort = homorganic (savarṇa)", ""),
 ("A-11111", "A 1.1.11", F, "idud ed dvivacanam pragrhyam", "Dual ī/ū/e endings are pragrhya (no sandhi)", ""),
 ("A-11127", "A 1.1.27", F, "sarvadini sarvanamani", "sarva etc. are pronouns", ""),
 ("A-11149", "A 1.1.49", V, "sasthi sthaneyoga", "Genitive denotes 'in place of'", "Xgen = substitute-for(X)"),
 ("A-11150", "A 1.1.50", V, "sthane ntaratamah", "Take the nearest (most similar) substitute", "argmin distance"),
 ("A-11151", "A 1.1.51", V, "uran raparah", "ṛ-vowel substitutes take appended r", ""),
 ("A-11152", "A 1.1.52", V, "alo ntyat purva upadha", "Penultimate letter before final = upadhā", ""),
 ("A-11156", "A 1.1.56", V, "sthanivad adeso nalvidhau", "Substitute behaves as the original (except for letter-conditioned rules)", ""),
 ("A-11157", "A 1.1.57", V, "aco ntyadi ti", "Final vowel-onward = ṭi", ""),
 ("A-11162", "A 1.1.62", V, "pratyayah", "An affix (is denoted by what follows the prakṛti)", ""),
 # -- 1.2 --
 ("A-12127", "A 1.2.27", F, "ukalo jhrasvadirghaplutah", "u-kālas: short/long/prolated mora timing", ""),
 ("A-12129", "A 1.2.29", V, "uccair udattah", "High pitch = udātta", ""),
 ("A-12130", "A 1.2.30", V, "nicair anudattah", "Low pitch = anudātta", ""),
 ("A-12131", "A 1.2.31", V, "samaharah svaritah", "Combined tone = svarita", ""),
 ("A-12141", "A 1.2.41", V, "aprkta ekal pratyayah", "One-phoneme affix = aprkta", ""),
 ("A-12145", "A 1.2.45", V, "arthavadadhaturapratyayah pratipadikam", "Meaningful non-root non-affix = stem (prātipadika)", ""),
 ("A-12146", "A 1.2.46", V, "krttaddhitasamasasca", "kṛt/taddhita/compound forms are stems too", ""),
 # -- 1.3 it-markers, atmanepada --
 ("A-1311", "A 1.3.1", V, "bhuvadayo dhatavah", "bhū etc. are roots (dhātupāṭha)", ""),
 ("A-1312", "A 1.3.2", V, "upadese janunasika it", "Nasals in teaching-text are it-markers", "it-strip"),
 ("A-1313", "A 1.3.3", V, "halantyam", "Final consonant is it-marker", "it-strip"),
 ("A-1314", "A 1.3.4", V, "na vibhaktau tusmah", "...except t/s/m of inflection", ""),
 ("A-1315", "A 1.3.5", V, "adirnit udavah", "Initial ñi/ṭu/ḍu are it-markers", ""),
 ("A-1316", "A 1.3.6", V, "sah pratyayasya", "Initial ṣ of an affix is it", ""),
 ("A-1317", "A 1.3.7", V, "cutu", "Initial c/ṭu are it-markers", ""),
 ("A-1318", "A 1.3.8", V, "lasakvataddhite", "l/ś/k of non-taddhita affixes are it", ""),
 ("A-1319", "A 1.3.9", V, "tasya lopah", "The it-marker is elided", ""),
 ("A-13110", "A 1.3.10", V, "yathasankhyam anudesa samanam", "Serial mapping of equals in order", "zip-map"),
 ("A-13111", "A 1.3.11", V, "svaritenadhikarah", "High-pitched vowel marks the governing domain (adhikāra)", ""),
 ("A-13112", "A 1.3.12", V, "anudattanit atmanepadam", "anudātta/ṅit roots take ātmanepada", ""),
 ("A-13113", "A 1.3.13", V, "bhavakarmanoh", "...also for impersonal/passive", ""),
 ("A-13172", "A 1.3.72", F, "svaritanitah kartr abhipraye kriyaphale", "svarita/ñit roots: ātmanepada when fruit accrues to agent", ""),
 ("A-13178", "A 1.3.78", V, "sesat kartari parasmaipadam", "Elsewhere active voice takes parasmaipada", ""),
 # -- 1.4 karaka + 2.3 vibhakti --
 ("A-1411", "A 1.4.1", F, "a kadarad eka samjna", "Up to kaḍāra: one technical term per rule-domain", ""),
 ("A-1413", "A 1.4.3", V, "yu stryakhyau nadi", "Long ī/ū feminine stems = nadī", ""),
 ("A-14113", "A 1.4.13", V, "yasmat pratyayavidhis tadadi pratyaye ngam",
  "That from which an affix is enjoined = aṅga base", "anga(base, affix)"),
 ("A-14114", "A 1.4.14", V, "suptingantam padam", "Inflected word (sup/tiṅ-ending) = pada", ""),
 ("A-14121", "A 1.4.21", F, "bahusu bahuvacanam", "Plural number for many", ""),
 ("A-14122", "A 1.4.22", V, "dvyekayor dvivacanaikavacane", "Dual for two, singular for one", ""),
 ("A-14123", "A 1.4.23", V, "karake", "Domain: kāraka roles begin", "karaka(k)->vibhakti"),
 ("A-14124", "A 1.4.24", V, "dhruvamapaye padanam", "Fixed point of departure = apādāna", ""),
 ("A-14132", "A 1.4.32", V, "karmana yamabhipraiti sa sampradanam", "Whom one aims at with the act = recipient", ""),
 ("A-14142", "A 1.4.42", V, "sadhakatamam karanam", "Most effective means = instrument", ""),
 ("A-14149", "A 1.4.49", V, "karturipsitatamam karma", "Agent's most desired = direct object", ""),
 ("A-14151", "A 1.4.51", V, "akathitam ca", "Unmentioned (secondary) object = karma too", ""),
 ("A-14152", "A 1.4.52", V, "gatibuddhipratyavasanartha ...",
  "Motion/cognition verbs: lower agents count as objects", ""),
 ("A-14154", "A 1.4.54", V, "svatantrah karta", "Independent one = agent", ""),
 ("A-231", "A 2.3.1", V, "anabhihite", "Case-endings when meaning not already expressed", ""),
 ("A-232", "A 2.3.2", V, "karmani dvitiya", "Accusative for the object", "karma->2nd"),
 ("A-2318", "A 2.3.18", V, "kartrkaranyos trtiya", "Instrumental for agent/instrument (passive)", ""),
 ("A-2346", "A 2.3.46", F, "pratipadikarthalingaparimanavacanam atre prathama",
  "Nominative for mere stem-meaning/gender/measure", ""),
 ("A-2350", "A 2.3.50", V, "sasthi sese", "Genitive for residual relations", ""),
 # -- 3.1-3.2 affixation/lakaras --
 ("A-311", "A 3.1.1", V, "pratyayah", "An affix is enjoined (domain start)", ""),
 ("A-312", "A 3.1.2", V, "parasca", "...and it follows (the base)", ""),
 ("A-317", "A 3.1.7", V, "dhatoh", "Affixes enjoined after roots", ""),
 ("A-32123", "A 3.2.123", V, "vartamane lat", "Present tense = laṬ", "bhu->bhavati"),
 # -- 4.1 nominal stems --
 ("A-411", "A 4.1.1", V, "nyapah pratipadikat", "After ṅī/āp/feminine stems and stems: nominal affixes", ""),
 ("A-412", "A 4.1.2", V, "svaujasamaut ...", "The sup triplet series (s, au, jas...)", ""),
 # -- 6.1 sandhi --
 ("A-611", "A 6.1.1", V, "ekaco dve prathamasya", "Double the first syllable (reduplication)", ""),
 ("A-6177", "A 6.1.77", V, "iko yanaci", "ik → yaṇ before vowels", "i+a->ya"),
 ("A-6187", "A 6.1.87", V, "adgunah", "a + i/u → guṇa single (e/o)", "a+i->e"),
 ("A-6188", "A 6.1.88", V, "vrddhireci", "a + e/o/ai/au → vṛddhi (ai/au)", "a+e->ai"),
 ("A-61101", "A 6.1.101", V, "akah savarne dirghah", "Homorganic vowels coalesce long", "a+a->aa"),
 ("A-6422", "A 6.4.22", V, "asiddhavadatra bhat", "bha-section treated as suspended (asiddha)", "tripadi-asiddha"),
 # -- 7.3 guna rules --
 ("A-7384", "A 7.3.84", V, "sarvadhatukardhadhatukayoh", "guṇa before sārvadhātuka/ārdhadhātuka", "bhu->bho"),
 ("A-7386", "A 7.3.86", F, "pugantalaghupadhasya ca", "guṇa for pu-final/light-penultimate roots", ""),
 # -- 8.2-8.4 finals --
 ("A-8239", "A 8.2.39", V, "jhalam jaso nte", "Final jhal → jaś (voicing)", ""),
 ("A-8315", "A 8.3.15", V, "kharavasanayorvisarjaniyah", "Final r/s before khar/pause → visarga", ""),
 ("A-8453", "A 8.4.53", V, "jhalam jas jhasi", "jhal → jaś before jhaś", ""),
 ("A-8458", "A 8.4.58", F, "anaci ca", "Doubling rules before non-vowels (dvitva)", ""),
 ("A-8468", "A 8.4.68", V, "anudit savarnasya capratyayah", "Homorganic nasal substitute (non-affix)", ""),
 # -- Mahabhasya / Kaumudi / Vakyapadiya index --
 ("MB-RAKSA", "Mahābhāṣya Paspaśā · rakṣā", F, "raksartha ...",
  "Grammar for preserving the Veda (rakṣā), with ūha, āgama, laghu, asaṃdeha", ""),
 ("MB-SADHU", "Mahābhāṣya Paspaśā · sādhu", T, "sadhu-asadhu-viveka",
  "Correct vs corrupt words: dharma from correct usage; niyama of the cultured", ""),
 ("SKK-SAMJNA", "Siddhāntakaumudī · saṃjñā", T, "samjna-prakarana",
  "Bhaṭṭoji's reordering: technical terms first (pedagogical view of A.)", ""),
 ("SKK-KARAKA", "Siddhāntakaumudī · kāraka", T, "karaka-prakarana",
  "Kāraka-vibhakti mapping reorganized for learners", ""),
 ("SKK-SAMASA", "Siddhāntakaumudī · samāsa", T, "samasa-prakarana",
  "Compounds: avyayībhāva/tatpuruṣa/bahuvrīhi/dvandva system", ""),
 ("SKK-TADDH", "Siddhāntakaumudī · taddhita", T, "taddhita-prakarana",
  "Secondary suffixes (4.1-5.4) pedagogically condensed", ""),
 ("VP-BRAHMA", "Vākyapadīya 1.1 · brahman", F, "anadinidhanam brahma sabdatattvam ...",
  "Beginningless-endless brahman as word-principle; grammar as liberation path", "eta: D=>S colimit"),
 ("VP-JATI", "Vākyapadīya 3 · jāti-samuddeśa", T, "jati-vyakti-vicara",
  "Universal vs individual in word-meaning; sphoṭa across three levels", ""),
]

# Fixups for earlier records (id -> field updates)
FIXUPS = {
    "A-LAT": {"adhyaNotation": "A 3.2.123", "sanskrit": "vartamane lat",
              "sourceNote": "corrected 3.2.124->3.2.123 (v2.1 fixup)"},
}


def main():
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    for rid, patch in FIXUPS.items():
        if rid in by_id:
            by_id[rid].update(patch)
    added = 0
    for rid, not_, tier, san, tr, logic in R:
        if rid not in by_id:
            p = provenance(tier, f"Astadhyayi-family rule; {not_}")
            by_id[rid] = {"id": rid,
                          "textId": "VPakya" if rid.startswith("VP-") else "Astadh",
                          "adhyaNotation": not_, "sanskrit": normalize_iast(san),
                          "translation": tr, "padarthasMentioned": ["Sabda"],
                          "pramanasInvoked": [], **({"logicalForm": logic} if logic else {}),
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "Astadhyayi (Sharma/Katre eds.); Kaumudi; VP eds."}
            added += 1
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)
    print(f"sutras: {len(old)} -> {len(out)} (+{added} panini-family)")


if __name__ == "__main__":
    main()
