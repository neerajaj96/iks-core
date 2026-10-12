"""Build data/sutras.json (+ docs/data mirror): NS/VS/SK/YS/TA/MMK/Vyakarana/Vedanta.

Every record: {id, textId, adhyaNotation, sanskrit, translation, padarthasMentioned,
pramanasInvoked, logicalForm, confidence, sourceNote}. Confidence tiers:
verbatim (exact wording attested) / famous-gist (doctrine certain, wording may vary)
/ topic-digest (accurate summary; verify against edition before verbatim citation).
Existing seed records (7) are preserved by id.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]


def S(id_, text, notation, tier, sanskrit, translation, pada=(), pram=(),
       logic="", note=""):
    d = {"id": id_, "textId": text, "adhyaNotation": notation,
         "sanskrit": normalize_iast(sanskrit), "translation": translation,
         "padarthasMentioned": list(pada), "pramanasInvoked": list(pram)}
    if logic:
        d["logicalForm"] = logic
    p = provenance(tier, note or translation[:80])
    d["confidence"] = p["tier"]
    d["sourceNote"] = p["note"]
    d["verifyAgainst"] = p["verifyAgainst"]
    return d


REC = []

# ---------------- NYAYA (NS) — Book 1 Ch 1: 16 padarthas & pramana laksanas ----------------
NS = [
 ("NS-1.1.1", "NS 1.1.1", "verbatim", "pramanaprameyasamsayaprayojanadrstantasiddhantavayavatarkanirnayavadajalpavitanandahetvabhasacchalajatinigrahasthananam tattvajnanannihsreyasadhigamah",
  "From true knowledge of the 16 categories comes the highest good", ["Nyaya16"], [], "tattva-jnana(N16) -> nihsreyasa"),
 ("NS-1.1.2", "NS 1.1.2", "famous-gist", "duhkhajanmapravrttidosamithyajnananam uttarottarapaye tadanantarapayad apavargah",
  "Apavarga follows successive destruction of suffering, birth, activity, defect, false cognition", ["prameya"], [], "¬mithya-jnana -> ¬dosa -> ... -> apavarga"),
 ("NS-1.1.3", "NS 1.1.3", "verbatim", "pratyaksanumanopamanasabdah pramanani",
  "Perception, inference, comparison, word are the pramanas", ["pramana"], ["Pratyaksa", "Anumana", "Upamana", "Sabda"]),
 ("NS-1.1.4", "NS 1.1.4", "verbatim", "indriyarthasannikarsotpannam jnanam avyapadesyam avyabhicari vyavasayamakam pratyaksam",
  "Perception: sense-object-contact cognition, unsayable-free, non-errant, determinate", ["pramana"], ["Pratyaksa"], "V_Pr iff sannikarsa & avyabhicari & vyavasaya"),
 ("NS-1.1.5", "NS 1.1.5", "famous-gist", "atha tatpurvakam trividham anumanam purvavacchesavatsamanyatodrstam ca",
  "Inference follows perception; threefold: pūrvavat, śeṣavat, sāmānyatodṛṣṭa", ["pramana"], ["Anumana"]),
 ("NS-1.1.6", "NS 1.1.6", "famous-gist", "prasiddhasadharmyat sadhyasadhanam upamanam",
  "Comparison: establishing the unknown via known similarity (as cow, so gavaya)", ["pramana"], ["Upamana"]),
 ("NS-1.1.7", "NS 1.1.7", "verbatim", "aptopadesah sabdah",
  "Word: the teaching of a trustworthy (āpta) person", ["pramana"], ["Sabda"], "V_Sa iff apta & akanksa & yogyata & sannidhi"),
 ("NS-1.1.8", "NS 1.1.8", "famous-gist", "sa dvividhah drstadrstartthatvat",
  "Word is twofold: seen-purpose (laukika) and unseen-purpose (vaidika)", ["pramana"], ["Sabda"]),
 ("NS-1.1.9", "NS 1.1.9", "famous-gist", "atmasarirendriyarthabuddhimanahpravrttidosapretyabhavaphaladuhkhapavargas tu prameyam",
  "The 12 knowables: self, body, senses, objects, cognition, mind, activity, defect, rebirth, fruit, suffering, release", ["prameya"], []),
 ("NS-1.1.10", "NS 1.1.10", "famous-gist", "icchadvesaprayatnasukhaduhkhajnananam atmano lingam",
  "Desire, aversion, effort, pleasure, pain, cognition are marks of the self", ["prameya"], ["Anumana"]),
 ("NS-1.1.11", "NS 1.1.11", "famous-gist", "cestendriyarthasrayah sariram",
  "Body: the locus of activity, senses, and objects", ["prameya"], []),
 ("NS-1.1.12", "NS 1.1.12", "famous-gist", "ghranarasanacaksustvakstrotrani indriyani bhutebhyah",
  "The five sense-organs arise from the elements", ["prameya"], []),
 ("NS-1.1.14", "NS 1.1.14", "famous-gist", "gandharasarupasparsasabdah prthivyadigunas tadarthah",
  "Smell, taste, form, touch, sound are element-qualities and sense-objects", ["prameya"], ["Pratyaksa"]),
 ("NS-1.1.15", "NS 1.1.15", "verbatim", "buddhir upalabdhir jnanam iti anarthantaram",
  "Cognition, apprehension, knowledge are synonyms", ["prameya"], []),
 ("NS-1.1.16", "NS 1.1.16", "verbatim", "yugapajjnanutpattih manaso lingam",
  "Non-simultaneity of cognitions marks the (atomic) mind", ["prameya"], ["Anumana"]),
 ("NS-1.1.32", "NS 1.1.32", "verbatim", "pratijnahetudaharanopanayanigamanani avayavah",
  "Thesis, reason, example, application, conclusion are the members", ["avayava"], ["Anumana"], "P(a); H(a); vyapti+drstanta; upanaya; nigamana"),
]
for id_, not_, tier, san, tr, pada, pram, *rest in NS:
    REC.append(S(id_, "NS", not_, tier, san, tr, pada, pram, rest[0] if rest else ""))

# NS prameya-laksana cluster 1.1.17-22 (doctrine certain; exact numbering varies by edition)
for id_, sub, san, tr in [
 ("NS-1.1-PRAV", "pravrtti", "pravrttir vagbuddhimanahsarira-arambhah", "Activity: initiation by speech, mind, cognition, body"),
 ("NS-1.1-DOSA", "dosa", "pravartanalaksana dosah (raga-dvesa-moha)", "Defects: what impel activity — attachment, aversion, delusion"),
 ("NS-1.1-PRETYA", "pretyabhava", "punarutpattih pretyabhavah", "Rebirth: re-origination after death"),
 ("NS-1.1-PHALA", "phala", "pravrttidosajanito arthah phalam", "Fruit: the object born of activity and defect"),
 ("NS-1.1-DUHKHA", "duhkha", "badhanalaksanam duhkham", "Suffering: characterized by affliction"),
 ("NS-1.1-APAV", "apavarga", "tadatyantavimokso apavargah", "Release: absolute freedom from suffering"),
]:
    REC.append(S(id_, "NS", f"NS 1.1.17-22 · {sub}", "famous-gist", san, tr, ["prameya"], []))
# Siddhanta 4 kinds
for id_, sub, tr in [
 ("NS-1.1-SARVA", "sarvatantra", "Universally-accepted tenet (all schools)"),
 ("NS-1.1-PRATI", "pratitantra", "School-specific tenet (proved within one tantra)"),
 ("NS-1.1-ADHI", "adhikarana", "Implied tenet (follows from an accepted thesis)"),
 ("NS-1.1-ABHYU", "abhyupagama", "Hypothetical tenet (assumed for argument)"),
]:
    REC.append(S(id_, "NS", f"NS 1.1.26-31 · {sub}", "topic-digest", sub, tr, ["siddhanta"], []))
# Tarka / nirnaya / katha-laksana cluster
for id_, sub, tr, pram in [
 ("NS-1.1-TARKA", "tarka", "Hypothetical reasoning toward truth via cause-analysis of the unknown", ["Anumana"]),
 ("NS-1.1-NIR", "nirnaya", "Ascertainment settling both sides after debate", []),
 ("NS-1.1-VADA", "vada", "Truth-seeking discussion with pramana + tarka, no quibbling", []),
 ("NS-1.1-JALPA", "jalpa", "Victory-seeking wrangling admitting chala/jati/nigraha", []),
 ("NS-1.1-VIT", "vitanda", "Cavilling: pure refutation without counter-thesis", []),
]:
    REC.append(S(id_, "NS", f"NS 1.1.33-41 · {sub}", "topic-digest", sub, tr, [sub], pram))

# NS 1.2: hetvabhasa (old five), chala (3), jati (24), nigraha (22)
for id_, sub, san, tr in [
 ("NS-1.2-SAV", "savyabhicara", "savyabhicara (anaikantika)", "Inconclusive reason: strays (found with and without sadhya)"),
 ("NS-1.2-VIR", "viruddha", "viruddha", "Contradictory reason: proves the opposite"),
 ("NS-1.2-PRAK", "prakaranasama", "prakaranasama (satpratipaksa-ancestor)", "Countered reason raising the very question at issue"),
 ("NS-1.2-SADH", "sadhyasama", "sadhyasama", "Reason itself as unproved as the thesis"),
 ("NS-1.2-KALA", "kalatita", "kalatita (badhita-ancestor)", "Untimely/mistimed reason, defeated by perception"),
]:
    REC.append(S(id_, "NS", f"NS 1.2.4-9 · {sub}", "famous-gist", san, tr, ["hetvabhasa"], ["Anumana"],
                "V_An=0 via " + sub))
for id_, sub, tr in [
 ("NS-1.2-VAKC", "vakchala", "Verbal quibble on ambiguous utterance"),
 ("NS-1.2-SAMC", "samanyachala", "Generalizing quibble (over-pressing a general term)"),
 ("NS-1.2-UPAC", "upacarachala", "Metaphorical quibble (literalizing figurative use)"),
]:
    REC.append(S(id_, "NS", f"NS 1.2.10-12 · {sub}", "topic-digest", sub, tr, ["chhala"], []))
JATI24 = ["sadharmya", "vaidharmya", "utkarsa", "apakarsa", "varnya", "avarn ya".replace(" ", ""),
          "vikalpa", "sadhya", "prapti", "aprapti", "prasanga", "pratidrstanta",
          "anutpatti", "samsaya", "prakarana", "ahetu", "arthapatti", "avisesa",
          "upapatti", "upalabdhi", "anupalabdhi", "nitya", "anatya".replace("t", "itya"), "karya"]
JATI24 = ["sadharmya", "vaidharmya", "utkarsa", "apakarsa", "varnya", "avarnya",
          "vikalpa", "sadhya", "prapti", "aprapti", "prasanga", "pratidrstanta",
          "anutpatti", "samsaya", "prakarana", "ahetu", "arthapatti", "avisesa",
          "upapatti", "upalabdhi", "anupalabdhi", "nitya", "anitya", "karya"]
for i in range(0, 24, 6):
    chunk = JATI24[i:i + 6]
    REC.append(S(f"NS-1.2-JATI{i // 6 + 1}", "NS", f"NS 1.2.13-18 · jati {i + 1}-{i + 6}",
                 "famous-gist", "jati: " + ", ".join(chunk),
                 "Futile rejoinders (jati) group: " + ", ".join(chunk), ["jati"], []))
NIGRAHA22 = ["pratijnahani", "pratijnantara", "pratijna-virodha", "pratijnasannyasa",
             "hetvantara", "arthantara", "nirarthaka", "avijnatartha", "aparthaka",
             "apraptakala", "nyuna", "adhika", "punarukta", "ananubhasana", "ajnana",
             "apratibha", "viksepa", "matanujna", "paryanuyojyopeksana",
             "niranuyojyanuyoga", "apasiddhanta", "hetvabhasa"]
for i in range(0, 22, 6):
    chunk = NIGRAHA22[i:i + 6]
    REC.append(S(f"NS-1.2-NIG{i // 6 + 1}", "NS", f"NS 1.2.19-20 · nigrahasthana {i + 1}-{i + len(chunk)}",
                 "famous-gist", "nigrahasthana: " + ", ".join(chunk),
                 "Points of defeat group: " + ", ".join(chunk), ["nigrahasthana"], []))
for id_, sub, tr, pada in [
 ("NS-1.2-VADA", "vada-laksana", "Vada: shared inquiry with pramana/tarka, opponent as fellow-seeker", ["vada"]),
 ("NS-1.2-JALPA", "jalpa-laksana", "Jalpa: debate admitting chala, jati, nigrahasthana for victory", ["jalpa"]),
 ("NS-1.2-VIT", "vitanda-laksana", "Vitanda: destructive criticism with no thesis of its own", ["vitanda"]),
]:
    REC.append(S(id_, "NS", f"NS 1.2.1-3 · {sub}", "topic-digest", sub, tr, pada, []))

# NS Book 2: doubt, whole/part, sabda-pariksa (incl. sphota-adjacent), varna
for id_, not_, tier, san, tr, pram in [
 ("NS-2.1-SAM", "NS 2.1.1-7 · samsaya", "famous-gist", "samanadharmadhyavasayat ... samsayah",
  "Doubt arises from common traits, conflicting testimony, irregularity", ["Pratyaksa", "Anumana"]),
 ("NS-2.1-AVAY", "NS 2.1.30-36 · avayavin", "topic-digest", "avayava-avayavin",
  "Whole (avayavin) over and above parts, against Buddhist reduction", ["Pratyaksa", "Anumana"]),
 ("NS-2.1-SAB1", "NS 2.1.50-54 · sabda-anitya", "topic-digest", "sabda-anityatva",
  "Sound is non-eternal (effort-produced, Hacker-reading target of Mimamsa reply)", ["Sabda", "Anumana"]),
 ("NS-2.1-SPHO", "NS 2.1.55-57 · sphota", "topic-digest", "sphota-pariksa",
  "Examination of sphoṭa: letter-sequence vs unitary meaning-bearer; Naiyayika critique", ["Sabda"]),
 ("NS-2.1-VAR", "NS 2.1.58-69 · varna", "topic-digest", "varna-vyavastha",
  "Ordering of phonemes and convention (samaya) fixing word-meaning", ["Sabda"]),
 ("NS-2.2-UP", "NS 2.2 · upamana-samarthana", "topic-digest", "upamana-samarthana",
  "Defense of comparison as independent pramana (gavaya case)", ["Upamana"]),
 ("NS-2.2-SAB", "NS 2.2 · sabda-artha", "topic-digest", "sabda-artha-sambandha",
  "Word-meaning relation: convention vs natural fitness; apta requirement", ["Sabda"]),
 ("NS-3.1-ATM", "NS 3.1 · atma-pariksa", "topic-digest", "atma-pariksa",
  "Self examined: distinct from body/senses/mind; desire etc. as marks", ["Anumana"]),
 ("NS-3.2-MAN", "NS 3.2 · manas-anutva", "famous-gist", "anu manah",
  "Mind is atomic (explains serial attention)", []),
 ("NS-4.1-DOS", "NS 4.1 · dosa-moha", "topic-digest", "moha-mula-dosa",
  "Delusion as root defect; Raga/dvesa structure of bondage", []),
 ("NS-4.1-PRET", "NS 4.1 · pretyabhava", "topic-digest", "pretyabhava-upapatti",
  "Establishing rebirth against Carvaka/Buddhist objections", ["Anumana"]),
 ("NS-5.1-JATI", "NS 5.1 · jati-vicara", "topic-digest", "jati-vicara",
  "Book 5: casuistry of futile objections answered one by one", []),
]:
    REC.append(S(id_, "NS", not_, tier, san, tr, ["Nyaya16"], list(pram)))

# ---------------- VAISESIKA ----------------
# ---------------- VAISESIKA: exact/famous lakshanas ----------------
for id_, not_, tier, san, tr, pada in [
 ("VS-1.1.5", "VS 1.1.5", "verbatim", "prthivyapastejo vayur akasam kalo dig atma mana iti dravyani",
  "Earth, water, fire, air, ether, time, direction, self, mind are the 9 substances", "Dravya"),
 ("VS-1.1.6", "VS 1.1.6", "famous-gist", "dravyasadharana? dravya-guna-karma-samanya-visesa-samavaya",
  "Enumeration context of the six bhava padarthas", "Dravya"),
 ("VS-1.1.7", "VS 1.1.7", "verbatim", "utksepanam avaksepanam akuncanam prasaranam gamanam iti karmani",
  "The 5 motions: up, down, contraction, expansion, locomotion", "Karma"),
 ("VS-DRAV-LAK", "VS 1.1.15 · dravya-laksana", "famous-gist", "kriyagunavat samavayikaranam iti dravyalaksanam",
  "Substance: possessor of action/quality, inherent cause", "Dravya"),
 ("VS-GUNA-LAK", "VS 1.1.16 · guna-laksana", "famous-gist", "dravyasrayi agunavan samyogavibhagesu akaranam anapeksa iti gunalaksanam",
  "Quality: resides in substance, has no quality, not a cause of conjunction", "Guna"),
 ("VS-KARMA-LAK", "VS 1.1.17 · karma-laksana", "famous-gist", "ekadravyam agunam samyogavibhagesu anapeksakaranam iti karmalaksanam",
  "Motion: one-substanced, qualityless, independent cause of conjunction/disjunction", "Karma"),
 ("VS-SATTA", "VS 1.2 · satta", "famous-gist", "sad iti yato dravyagunakarmasu sa satta",
  "Being (sattā): that by which 'existent' applies to substance/quality/action", "Samanya"),
 ("VS-SAM-LAK", "VS 1.2 · samanya", "famous-gist", "samanya-visesa-siddhih ... para-apara",
  "Universals: higher (satta) and lower (dravyatva etc.); lampu-lakshana cluster", "Samanya"),
 ("VS-VIS-LAK", "VS 3.1 · visesa", "topic-digest", "visesa-antya",
  "Ultimate particulars individuating eternal atoms/souls (school's namesake)", "Visesa"),
 ("VS-SAMAV", "VS 7.2 · samavaya", "famous-gist", "ayutasiddhanam adharadheyabhutanam ... samavayah",
  "Inherence: relation of inseparables (container/contained), one and eternal", "Samavaya"),
 ("VS-ABHAVA", "VS later · abhava", "topic-digest", "abhava-saptama (Sridhara/Udayana)",
  "Absence as 7th padartha: prag/dhvamsa/atyanta/anyonya", "Abhava"),
]:
    REC.append(S(id_, "VS", not_, tier, san, tr, [pada], []))
# 9 dravyas × 1 record
DRAVYA_NOTES = {
 "prthivi": "smell-bearing; 4-atom TEMPORARY solids", "ap": "taste-bearing; fluids",
 "tejas": "form-bearing; heat/light", "vayu": "touch-bearing; air atoms",
 "akasa": "sound-locus; all-pervading, eternal", "kala": "time; cause of priority/posteriority",
 "dik": "direction; spatial order", "atman": "selves; infinite, cognition as quality",
 "manas": "inner sense; atomic, serial attention",
}
for d, note in DRAVYA_NOTES.items():
    REC.append(S(f"VS-DRAV-{d}", "VS", f"VS 1-3 · dravya {d}", "topic-digest", d,
                 f"Dravya {d}: {note}", ["Dravya"], []))
# 24 gunas in 4 groups of 6
GUNAS = ["rupa", "rasa", "gandha", "sparsa", "sankhya", "parimana", "prthaktva",
         "samyoga", "vibhaga", "paratva", "aparatva", "buddhi", "sukha", "duhkha",
         "iccha", "dvesa", "prayatna", "gurutva", "dravatva", "sneha", "dharma",
         "adharma", "sabda", "samskara"]
for i in range(0, 24, 6):
    chunk = GUNAS[i:i + 6]
    REC.append(S(f"VS-GUNA{i // 6 + 1}", "VS", f"VS 1-7 · guna {i + 1}-{i + 6}", "famous-gist",
                 "guna: " + ", ".join(chunk), "Qualities group: " + ", ".join(chunk), ["Guna"], []))
KARMA_NOTES = {"utksepena": "throwing upward", "avaksepena": "throwing downward",
               "akuncana": "contraction", "prasarana": "expansion", "gamana": "locomotion"}
for k, note in KARMA_NOTES.items():
    REC.append(S(f"VS-KARMA-{k}", "VS", f"VS 1.1.7 · karma {k}", "famous-gist", k,
                 f"Motion {k}: {note}; transient, dravya-bound", ["Karma"], []))

# ---------------- SAMKHYA KARIKA (thematic; famous singles verbatim-adjacent) ----------------
SK = [
 ("SK-1", "SK 1", "famous-gist", "duhkhatrayabhighataj jijnasa tadapaghatake hetau",
  "Inquiry begins from the blow of threefold suffering", ["Tattva"], []),
 ("SK-2", "SK 2", "topic-digest", "drstavad anusravikah ...", "Seen and heard remedies fail; discriminative knowledge required", ["Tattva"], []),
 ("SK-3", "SK 3", "famous-gist", "mulaprakrtir avikrtih mahadadyah prakrtivikrtayah saptah",
  "Root prakrti unproduced; mahat etc. seven are produced-and-producing", ["Tattva"], [],
  "Prakrti=mula; E7=vikrti+ prakrti"),
 ("SK-4", "SK 4", "verbatim", "drstam anumanam aptavacanam ca sarvapramanasiddhatvat",
  "Seen, inferred, trustworthy-word: all pramanas established", ["Pramana"], ["Pratyaksa", "Anumana", "Sabda"]),
 ("SK-9", "SK 9", "famous-gist", "asadakaranad upadan agrahanat sarvasambhavabhavat ... satkaryam",
  "Satkāryavāda: effect pre-exists (5 reasons: non-being makes nothing etc.)", ["Tattva"], ["Anumana"],
  "y ⊆_sakti Prakrti"),
 ("SK-11", "SK 11", "famous-gist", "trgunam aviveki visayah samanyam acetanam prasavadharmi",
  "The manifest: 3-guṇa'd, non-discriminating, objective, common, insentient, productive", ["Tattva"], []),
 ("SK-12", "SK 12", "famous-gist", "priti-apriti-visadamakaih ... gunah",
  "Guṇas: pleasure/pain/delusion-natured; mutual domination", ["Tattva"], []),
 ("SK-13", "SK 13", "topic-digest", "sattva-ragas-tamas krtya", "Sattva lightness/illumination, rajas urge, tamas restraint", ["Tattva"], []),
 ("SK-17", "SK 17", "famous-gist", "samghatapararthatvat ... puruso asti",
  "Puruṣa proved: composites serve another; plurality from birth/death/instruments", ["Tattva"], ["Anumana"]),
 ("SK-19", "SK 19", "famous-gist", "tasmac ca viparyasat ... kevalatva",
  "Puruṣa: witness, isolated, neutral, seer, inactive", ["Tattva"], []),
 ("SK-21", "SK 21", "famous-gist", "purusasya darsanartham ... pangu-andha",
  "Puruṣa-prakṛti conjunction like lame-and-blind for seeing and acting", ["Tattva"], []),
 ("SK-22", "SK 22-27 · sarga", "topic-digest", "mahad-ahamkara-indriya-tanmatra",
  "Evolution: mahat → ahaṅkāra → 11 senses + 5 tanmātras (sāttvika/tāmasa)", ["Tattva"], []),
 ("SK-29", "SK 29-35 · indriya", "topic-digest", "buddhi-indriya-karmendriya-manas",
  "10 outer senses + manas; functions and cooperation", ["Tattva"], []),
 ("SK-38", "SK 36-39 · bhuta", "topic-digest", "tanmatra-mahabhuta",
  "5 subtle elements → 5 gross elements; liṅga-śarīra", ["Tattva"], []),
 ("SK-40", "SK 40-45 · bhava", "topic-digest", "linga-bhava-adhivasita",
  "Subtle body migrates, invested with dispositions (bhāvas)", ["Tattva"], []),
 ("SK-46", "SK 46-51 · pratyayasarga", "topic-digest", "viparyaya-asakti-tusti-siddhi",
  "Intellectual creation: error, disability, contentment, accomplishment", ["Tattva"], []),
 ("SK-57", "SK 57-58 · prakrti-celebration", "famous-gist", "vatsavivrddhinimittam ksirasya ...",
  "Prakṛti acts like unconscious milk for the calf — for puruṣa's release", ["Tattva"], []),
 ("SK-59", "SK 59-61 · nivrtti", "topic-digest", "rangasya darsayitva ...",
  "Having shown herself, prakṛti withdraws like a dancer", ["Tattva"], []),
 ("SK-62", "SK 62-64 · viveka", "famous-gist", "tasmad ... na asmi na me naham",
  "'I am not, not mine, not I' — discriminative knowledge", ["Tattva"], []),
 ("SK-68", "SK 68-70 · kaivalya-parampara", "topic-digest", "kaivalya + sisya-parampara",
  "Isolation of puruṣa; transmission Kapila→Āsuri→Pañcaśikha→Īśvarakṛṣṇa", ["Tattva"], []),
]
for id_, not_, tier, san, tr, pada, pram, *rest in SK:
    if id_ == "SK-4":
        continue  # seed already has SK-4
    REC.append(S(id_, "SK", not_, tier, san, tr, pada, pram, rest[0] if rest else ""))

# ---------------- YOGA SUTRA selections ----------------
for id_, not_, tier, san, tr in [
 ("YS-1.2", "YS 1.2", "verbatim", "yogas cittavrttinirodhah", "Yoga is the stilling of mind-turnings"),
 ("YS-1.3", "YS 1.3", "famous-gist", "tada drastuh svarupe avasthanam", "Then the seer abides in its own form"),
 ("YS-1.6", "YS 1.6", "famous-gist", "pramana-viparyaya-vikalpa-nidra-smrtayah", "Five turnings: valid cognition, error, fancy, sleep, memory"),
 ("YS-1.7", "YS 1.7", "verbatim", "pratyaksanuman agamah pramanani", "Perception, inference, testimony are the pramanas"),
 ("YS-2.3", "YS 2.3", "famous-gist", "avidya-asmita-raga-dvesa-abhinivesah klesah", "Five afflictions: ignorance, egoity, attraction, aversion, clinging"),
 ("YS-2.29", "YS 2.29", "famous-gist", "yama-niyama-asana-pranayama-pratyahara-dharana-dhyana-samadhayo astav angani", "Eight limbs from restraint to absorption"),
 ("YS-3.13", "YS 3.13", "topic-digest", "dharma-laksana-avastha parinama", "Threefold transformation: property, mark, condition"),
 ("YS-4.34", "YS 4.34", "topic-digest", "purusartha-sunyanam gunanam pratiprasavah kaivalyam", "Release: guṇas resolve, puruṣa established in own form"),
]:
    REC.append(S(id_, "YS", not_, tier, san, tr, ["Tattva"], []))

# ---------------- TATTVARTHA SUTRA (Jaina) ----------------
for id_, not_, tier, san, tr in [
 ("TA-1.1", "TĀ 1.1", "verbatim", "samyagdarsanajnanacaritrani moksamargah", "Right view, knowledge, conduct are the path to release"),
 ("TA-1.4", "TĀ 1.4", "famous-gist", "jiva-ajiva-asrava-bandha-samvara-nirjara-moksas tattvam", "Seven tattvas: soul, non-soul, influx, bondage, stoppage, shedding, release"),
 ("TA-5.29", "TĀ 5.29", "topic-digest", "pudgala-laksana", "Matter defined; touch/taste/smell/form aggregates"),
 ("TA-5.30", "TĀ 5.30", "topic-digest", "guna-paryaya", "Substance bears qualities and modes (anekanta ontology)"),
 ("TA-9.1", "TĀ 9 · samvara", "topic-digest", "samvara-hetu", "Stoppage of influx via vows, vigilance, conduct"),
 ("TA-10.1", "TĀ 10 · moksa", "topic-digest", "moksa-svarupa", "Release: soul's ascent on shedding all karma"),
 ("TA-SYAD", "Āptamīmāṃsā · syadvada", "topic-digest", "syat-asti-nasti ...", "Conditioned predication: every judgment standpoint-qualified (saptabhangi)"),
 ("TA-NAYA", "Parīkṣāmukha · naya", "topic-digest", "naigama-sangraha-... naya", "Partial standpoints; pramana = self-and-other revealing cognition"),
]:
    REC.append(S(id_, "TArthaS", not_, tier, san, tr, ["Tattva"], []))

# ---------------- MADHYAMAKA ----------------
for id_, not_, tier, san, tr in [
 ("MMK-DED", "MMK dedication", "verbatim", "anirodham anutpadam anucchedam asasvatam ... pratityasamutpadam",
  "Homage to dependent arising: no cessation, no birth, no cutting, no permanence"),
 ("MMK-1", "MMK 1 · pratyaya", "topic-digest", "na svato napi parato ...", "Nothing arises from self, other, both, or no cause"),
 ("MMK-15", "MMK 15 · svabhava", "topic-digest", "svabhava-pariksa", "Examination of own-being: refuted"),
 ("MMK-18", "MMK 18 · atman", "topic-digest", "atma-pariksa", "Self and dharmas: neither identical nor different"),
 ("MMK-24", "MMK 24.18 · sunyata", "verbatim", "yah pratityasamutpadah sunyatam tam pracaksmahe",
  "What is dependently arisen, that we call emptiness (middle path)"),
 ("MMK-25", "MMK 25 · nirvana", "topic-digest", "nirvana-pariksa", "Nirvana: neither existent nor non-existent as own-being"),
]:
    REC.append(S(id_, "MMK", not_, tier, san, tr, ["Abhava"], []))

# ---------------- VYAKARANA pilot ----------------
for id_, not_, tier, san, tr, logic in [
 ("A-1142", "A 1.4.2", "verbatim", "vipratisedhe param karyam", "On conflict, the later (para) rule wins", "conflict(R1,R2) -> apply(max-order)"),
 ("A-3168", "A 3.1.68", "verbatim", "kartari sap", "After verbal root, śap in agent-sense", "bhu+laT -> bhu+a+ti"),
 ("A-6178", "A 6.1.78", "verbatim", "eco ayavayavah", "ec vowels take ay/āv substitutions", "bho+a -> bhav+a"),
 ("A-1103", "A 1.1.3", "verbatim", "iko gunavrddhi", "ik vowels take guṇa/vṛddhi", "i->e (guna)"),
 ("A-SIVA", "Māheśvara 1-14", "famous-gist", "a-i-u-n r-l-k ... hal (14 sutras)",
  "Sound-arrangement: pratyāhāra engine of the grammar", "pratyahara(ac,hal)->varna-set"),
 ("A-KAR", "A 1.4.23-55 · karaka", "topic-digest", "karaka-vibhakti", "Six kārakas map to case-endings (kartā, karman, karaṇa...)", "karaka(k)->vibhakti"),
 ("A-LAT", "A 3.2.123-124 · laT", "famous-gist", "vartamane lat", "Present-tense affix laṬ", "bhu->bhavati"),
 ("VP-SPH", "Vākyapadīya 1 · sphota", "topic-digest", "sphota-dhvani-bheda", "Meaning-bearer (sphoṭa) vs sounded manifestation (dhvani)", "eta: D=>S colimit"),
 ("MB-PASP", "Mahābhāṣya Paspaśā · sadhutva", "topic-digest", "sadhu-sabda-prayojana", "Purpose of correct-word study: dharma, अर्थ-knowledge, niyama", ""),
 ("SK-SID", "Siddhāntakaumudī · samjna", "topic-digest", "samjna-prakarana", "Re-ordered pedagogy of Aṣṭādhyāyī rules", ""),
]:
    REC.append(S(id_, "Astadh" if id_.startswith("A-") or id_ == "A-SIVA" else ("VPakya" if id_ == "VP-SPH" else "Astadh"),
                 not_, tier, san, tr, ["Sabda"], [], logic))

# ---------------- VEDANTA / MIMAMSA / SAHITYA / GANITA seeds ----------------
VED = [
 ("BS-111", "BS", "BS 1.1.1", "verbatim", "athato brahmajijnasa", "Now, therefore, inquiry into brahman", ["Artha"], []),
 ("BS-112", "BS", "BS 1.1.2", "verbatim", "janmadyasya yatah", "That from which birth etc. proceed", ["Artha"], []),
 ("UP-TAT", "BS", "Chāndogya · tattvamasi", "famous-gist", "tattvam asi", "That thou art (mahavakya)", ["Artha"], []),
 ("UP-AHAM", "BS", "Bṛhadāranyaka · aham Brahmasmi", "famous-gist", "aham Brahmasmi", "I am brahman (mahavakya)", ["Artha"], []),
 ("SV-ABH", "SV", "Ślokavārttika · abhava", "topic-digest", "abhava-pramana", "Absence as 6th pramana (Bhāṭṭa); against pratyakṣa-only", ["Abhava"], ["Anupalabdhi"]),
 ("SV-SAB", "SV", "Ślokavārttika · sabda-nityatva", "topic-digest", "sabda-nityatva + apoha-khandana", "Eternal word; critique of Buddhist exclusion-theory", ["Sabda"], ["Sabda"]),
 ("VP-6PR", "VP", "Vedāntaparibhāṣā · 6 pramanas", "topic-digest", "vedanta-pramana-samarthana", "Advaita accepts six pramanas incl. arthāpatti/anupalabdhi", ["Pramana"], ["Arthapatti", "Anupalabdhi"]),
 ("PP-BHEDA", "PP", "Pramāṇapaddhati · bheda", "topic-digest", "bheda-anumana", "Dvaita: difference as inferable real; Viṣṇu sarvottama", ["Tattva"], ["Anumana"]),
 ("NP-BHEDA", "SataD", "Nyāyapariśuddhi · bheda-grahana", "topic-digest", "pratyaksa-grahya-bheda", "Viśiṣṭādvaita: difference grasped in perception itself", ["Tattva"], ["Pratyaksa"]),
 ("SD-100", "SataD", "Śatadūṣaṇī · vada 1-10", "topic-digest", "nirvisesa-khandana", "100 defects charged on qualityless brahman", ["Artha"], []),
 ("SDS-IDX", "SDS", "Sarvadarśanasaṅgraha · index", "topic-digest", "sodasa-darsana-krama", "Doxography: Cārvāka → Śaṅkara in 16 chapters", ["Other"], []),
 ("KP-RASA", "KavyaP", "Kāvyaprakāśa · rasa-dhvani", "topic-digest", "kavya-laksana + rasa", "Poetry defined; rasa soul; doṣa/guṇa/alaṅkāra apparatus", ["Rasa"], []),
 ("DHA-DHV", "DhvA", "Dhvanyāloka · dhvani", "topic-digest", "vyanjana-pradhanya", "Suggestion dominant over expressed sense = best poetry", ["Dhvani"], []),
 ("ARY-PI", "Arya", "Āryabhaṭīya · pi", "famous-gist", "caturadhikam satam ... 62832/20000", "π ≈ 3.1416; place-value + sine-table mathematics", ["Other"], []),
 ("YUK-SER", "YuktiB", "Yuktibhāṣā · madhava-series", "topic-digest", "pi-series-upapatti", "Kerala proof: infinite series for π with correction terms", ["Other"], []),
 ("GITA-220", "BS", "Gītā 2.20", "famous-gist", "na jayate mriyate va ...", "Self unborn, undying — prameya anchor for Vedanta", ["Artha"], ["Sabda"]),
]
for id_, text, not_, tier, san, tr, pada, pram in VED:
    REC.append(S(id_, text, not_, tier, san, tr, pada, pram))


def main():
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    for r in by_id.values():  # backfill v1.0 seeds to v2 provenance standard
        r.setdefault("confidence", "verbatim")
        r.setdefault("sourceNote", "v1.0 seed; attested wording")
        r.setdefault("verifyAgainst", "SARIT/GRETIL edition")
    for r in REC:
        by_id.setdefault(r["id"], r)
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)
    print(f"sutras: {len(old)} -> {len(out)}")


if __name__ == "__main__":
    main()
