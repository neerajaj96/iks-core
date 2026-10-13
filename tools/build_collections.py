"""Build terms/inferences/cognitions + expand vada nodes/edges (+ docs mirrors).

Existing vada records preserved by id. All new records carry provenance tiers.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]

TERMS = [
 ("pratyaksa", "प्रत्यक्ष", "pratyakṣa", ["Nyaya", "Vaisesika", "Samkhya", "Purva-Mimamsa", "Advaita"], ["NS-1.1.4"], "Pramana", "V_Pr", ""),
 ("anumana", "अनुमान", "anumāna", ["Nyaya", "Vaisesika", "Samkhya", "Bauddha-Yogacara", "Jaina-Svetambara"], ["NS-1.1.5"], "Pramana", "V_An", ""),
 ("sabda", "शब्द", "śabda", ["Nyaya", "Samkhya", "Purva-Mimamsa", "Advaita"], ["NS-1.1.7"], "Pramana", "V_Sa", ""),
 ("upamana", "उपमान", "upamāna", ["Nyaya", "Purva-Mimamsa", "Advaita"], ["NS-1.1.6"], "Pramana", "V_Up", ""),
 ("arthapatti", "अर्थापत्ति", "arthāpatti", ["Purva-Mimamsa", "Advaita"], ["NS-1.1-VADA"], "Pramana", "V_Ar", ""),
 ("anupalabdhi", "अनुपलब्धि", "anupalabdhi", ["Purva-Mimamsa", "Advaita"], ["SV-ABH"], "Pramana", "V_Anu", ""),
 ("dravya", "द्रव्य", "dravya", ["Vaisesika", "Nyaya"], ["VS-1.1.5", "VS-DRAV-LAK"], "Dravya", "D", ""),
 ("guna", "गुण", "guṇa", ["Vaisesika", "Nyaya"], ["VS-GUNA-LAK"], "Guna", "G", ""),
 ("karma", "कर्मन्", "karman", ["Vaisesika", "Nyaya"], ["VS-1.1.7", "VS-KARMA-LAK"], "Karma", "K", ""),
 ("samanya", "सामान्य", "sāmānya", ["Vaisesika", "Nyaya"], ["VS-SAM-LAK"], "Samanya", "Sa", ""),
 ("visesa", "विशेष", "viśeṣa", ["Vaisesika"], ["VS-VIS-LAK"], "Visesa", "Vi", ""),
 ("samavaya", "समवाय", "samavāya", ["Vaisesika", "Nyaya"], ["VS-SAMAV"], "Samavaya", "Inh", ""),
 ("pragabhava", "प्रागभाव", "prāgabhāva", ["Vaisesika", "Nyaya"], ["VS-ABHAVA"], "Abhava", "¬_p", ""),
 ("dhvamsabhava", "ध्वंसाभाव", "dhvaṃsābhāva", ["Vaisesika", "Nyaya"], ["VS-ABHAVA"], "Abhava", "¬_d", ""),
 ("atyantabhava", "अत्यन्ताभाव", "atyantābhāva", ["Vaisesika", "Nyaya"], ["VS-ABHAVA"], "Abhava", "¬_a", ""),
 ("anyonyabhava", "अन्योन्याभाव", "anyonyābhāva", ["Vaisesika", "Nyaya"], ["VS-ABHAVA"], "Abhava", "≠_id", ""),
 ("purusa", "पुरुष", "puruṣa", ["Samkhya", "Yoga"], ["SK-17", "SK-19"], "Tattva", "Puruṣa", "kevala/draṣṭā — non-formalizable anubhava residue"),
 ("prakrti", "प्रकृति", "prakṛti", ["Samkhya", "Yoga"], ["SK-3"], "Tattva", "Prakṛti", ""),
 ("buddhi", "बुद्धि", "buddhi", ["Samkhya"], ["SK-22"], "Tattva", "mahat", ""),
 ("ahankara", "अहङ्कार", "ahaṅkāra", ["Samkhya"], ["SK-22"], "Tattva", "aham", ""),
 ("vyapti", "व्याप्ति", "vyāpti", ["Nyaya", "Bauddha-Yogacara", "Jaina-Svetambara"], ["NS-1.1.32", "SK-4"], "Other", "⇉", ""),
 ("hetu", "हेतु", "hetu", ["Nyaya", "Bauddha-Yogacara"], ["NS-1.1.32"], "Other", "H", ""),
 ("paksa", "पक्ष", "pakṣa", ["Nyaya"], ["NS-1.1.32"], "Other", "a", ""),
 ("sadhya", "साध्य", "sādhya", ["Nyaya"], ["NS-1.1.32"], "Other", "S", ""),
 ("drstanta", "दृष्टान्त", "dṛṣṭānta", ["Nyaya"], ["NS-1.1.32"], "Other", "∃-ground", ""),
 ("avacchedaka", "अवच्छेदक", "avacchedaka", ["Nyaya"], ["NS-1.1.32"], "Other", "A_φ", ""),
 ("pratiyogin", "प्रतियोगिन्", "pratiyogin", ["Nyaya"], ["VS-ABHAVA"], "Other", "PR", ""),
 ("anuyogin", "अनुयोगिन्", "anuyogin", ["Nyaya"], ["VS-ABHAVA"], "Other", "AN", ""),
 ("sphota", "स्फोट", "sphoṭa", ["Vyakarana"], ["VP-SPH"], "Sabda", "S", "pratibhā flash — opaque axiom, abstain-with-residue"),
 ("dhvani", "ध्वनि", "dhvani", ["Vyakarana", "Sahitya"], ["VP-SPH", "DHA-DHV"], "Dhvani", "(Sv,Sl,Svya)", ""),
 ("rasa", "रस", "rasa", ["Sahitya"], ["KP-RASA"], "Rasa", "R=Φ⊙S₀", "camatkāra — non-formalizable"),
 ("anekanta", "अनेकान्त", "anekānta", ["Jaina-Svetambara"], ["TA-SYAD"], "Other", "◇_n", ""),
 ("syat", "स्यात्", "syāt", ["Jaina-Svetambara"], ["TA-SYAD"], "Other", "◇_n", ""),
 # --- v2.4: Navya-Nyaya technical vocabulary ---
 ("prakarata", "प्रकारता", "prakāratā", ["Nyaya"], ["TC-SABDA"], "Other", "Pr_r", ""),
 ("visesyata", "विशेष्यता", "viśeṣyatā", ["Nyaya"], ["TC-SABDA"], "Other", "Vs", ""),
 ("samsargata", "संसर्गता", "saṃsargatā", ["Nyaya"], ["TC-SABDA"], "Other", "S_R", ""),
 ("nirupaka", "निरूपक", "nirūpaka", ["Nyaya"], ["TC-VYAP5"], "Other", "N", ""),
 ("paryapti", "पर्याप्ति", "paryāpti", ["Nyaya"], ["TC-VYAP5"], "Other", "Π", ""),
 ("paramarsa", "परामर्श", "parāmarśa", ["Nyaya"], ["NS-1.1.32"], "Pramana", "Prm", ""),
 ("paksata", "पक्षता", "pakṣatā", ["Nyaya"], ["NS-1.1.32"], "Other", "Pks", ""),
 # --- v2.4: Mimamsa ---
 ("apurva", "अपूर्व", "apūrva", ["Purva-Mimamsa"], ["JS-112"], "Other", "Ap", ""),
 ("bhavana", "भावना", "bhāvanā", ["Purva-Mimamsa"], ["JS-ADH12"], "Other", "Bh", ""),
 ("vidhi", "विधि", "vidhi", ["Purva-Mimamsa", "Nyaya"], ["TC-SABDA"], "Sabda", "Vidh", ""),
 ("codana", "चोदना", "codanā", ["Purva-Mimamsa"], ["JS-112"], "Sabda", "Cod", ""),
 # --- v2.4: Vedanta ---
 ("adhyasa", "अध्यास", "adhyāsa", ["Advaita"], ["BS-111"], "Other", "Adh", ""),
 ("maya", "माया", "māyā", ["Advaita"], ["BS-111"], "Other", "M", ""),
 ("jiva", "जीव", "jīva", ["Advaita", "Jaina-Svetambara"], ["GITA-220"], "Tattva", "J", ""),
 ("isvara", "ईश्वर", "īśvara", ["Nyaya", "Dvaita", "Visistadvaita"], ["NK-4"], "Other", "I", ""),
 ("brahman", "ब्रह्मन्", "brahman", ["Advaita", "Visistadvaita", "Dvaita"], ["BS-112"], "Other", "B", ""),
 ("moksa", "मोक्ष", "mokṣa", ["Advaita", "Jaina-Svetambara", "Nyaya"], ["TA-10.1"], "Artha", "Mok", ""),
 ("vivarta", "विवर्त", "vivarta", ["Advaita"], ["BS-ADH1"], "Other", "Viv", ""),
 # --- v2.4: Buddhist ---
 ("svalaksana", "स्वलक्षण", "svalakṣaṇa", ["Bauddha-Sautrantika", "Bauddha-Yogacara"], ["PV-PRAT"], "Other", "sva-l", ""),
 ("samanyalaksana", "सामान्यलक्षण", "sāmānyalakṣaṇa", ["Bauddha-Yogacara"], ["PV-PRAT"], "Samanya", "sam-l", ""),
 ("ksanikatva", "क्षणिकत्व", "kṣaṇikatva", ["Bauddha-Sautrantika"], ["MMK-15"], "Other", "kṣ", ""),
 ("pratityasamutpada", "प्रतीत्यसमुत्पाद", "pratītyasamutpāda", ["Bauddha-Madhyamaka"], ["MMK-DED"], "Other", "↝", ""),
 ("sunyata", "शून्यता", "śūnyatā", ["Bauddha-Madhyamaka"], ["MMK-24"], "Abhava", "∅", "śūnyatā-anubhava residue"),
 ("apoha-t", "अपोह", "apoha", ["Bauddha-Yogacara"], ["PV-APOHA"], "Sabda", "Apo", ""),
 # --- v2.4: Jaina ---
 ("naya", "नय", "naya", ["Jaina-Svetambara"], ["TA-NAYA"], "Pramana", "Nay", ""),
 ("niksepa", "निक्षेप", "nikṣepa", ["Jaina-Svetambara"], ["TA-1.4"], "Other", "Nik", ""),
 ("kevalajnana", "केवलज्ञान", "kevalajñāna", ["Jaina-Svetambara"], ["TA-ADH2"], "Pramana", "Kev", "kevala experience non-formalizable"),
]

INF = [
 ("inf-hill-valid", "Nyaya", "Nyaya-5", "parvata", "vahni", "dhuma", "mahanasa",
  "yatra dhuma tatra vahni", "none", "Stock valid inference; anvaya + vyatireka (hrada)"),
 ("inf-kitchen", "Nyaya", "Nyaya-5", "mahanasa", "vahni", "dhuma", "mahanasa-kitchen",
  "sapaksa instantiation", "none", "Positive exemplification grounding vyapti"),
 ("inf-lake-vyati", "Nyaya", "Nyaya-5", "hrada", "vahni-abhava", "dhuma-abhava", "hrada-lake",
  "yatra vahni-nasti tatra dhuma-nasti", "none", "Negative exemplification (vyatireka)"),
 ("inf-kevalanvayi", "Nyaya", "Nyaya-5", "ghata", "vacyatva", "prameyatva", "sarva-vastu",
  "kevalanvayi (no vipaksa)", "none", "Nameable because knowable; ¬∃ vipaksa"),
 ("inf-kevalavyat", "Nyaya", "Nyaya-5", "prthivi", "gandhavat", "gandha", "prthivi-itar-bheda",
  "kevalavyatireki", "none", "Earth differs from non-earth by smell"),
 ("inf-savyabhi", "Nyaya", "Nyaya-5", "sarva", "vahni", "dhuma", "",
  "defective vyapti", "Savyabhicara", "Adversarial: hetu found without sadhya (straying)"),
 ("inf-viruddha", "Nyaya", "Nyaya-5", "sabda", "nityatva", "krtakatva", "",
  "hetu proves opposite", "Viruddha", "Adversarial: producedness proves non-eternity, not eternity"),
 ("inf-satprati", "Nyaya", "Nyaya-5", "sabda", "anityatva", "krtakatva", "ghata",
  "vs counter-inference nityatva/sravanatva", "Satpratipaksa", "Adversarial: matched by equal counter-reason"),
 ("inf-asiddha", "Nyaya", "Nyaya-5", "akasa-kamala", "saurabhya", "kamalatva", "",
  "paksasiddhi missing", "Asiddha", "Adversarial: subject itself unestablished (sky-lotus)"),
 ("inf-badhita", "Nyaya", "Nyaya-5", "agni", "saitya", "dravyatva", "",
  "pratyaksa defeats", "Badhita", "Adversarial: fire is cold — perception sublates"),
 ("inf-buddh-fire", "Bauddha-Sautrantika", "Buddhist-2", "parvata", "vahni", "dhuma", "mahanasa",
  "trairupya: pakse/sapakse/vipakse-asattva", "none", "Dignaga form: paksadharmata + vyapti only"),
 ("inf-buddh-moment", "Bauddha-Sautrantika", "Buddhist-2", "bhava", "ksanikatva", "sattva", "pradipa",
  "yatra sattvam tatra ksanikatvam", "none", "Momentariness from existence (Dharmakirti)"),
 ("inf-buddh-apoha", "Bauddha-Yogacara", "Buddhist-2", "go-sabda", "anya-vyavrtti", "sanketa", "",
  "apoha-vyapti", "none", "Word denotes via exclusion of others"),
 ("inf-jaina-clay", "Jaina-Svetambara", "Jaina-Trairupya", "ghata", "asti (mrttikaya)", "upalabdhi", "mrttika",
  "syat-qualified vyapti", "none", "Standpoint-qualified: exists-as-clay"),
 ("inf-jaina-gold", "Jaina-Svetambara", "Jaina-Trairupya", "ghata", "nasti (kanakatvena)", "anupalabdhi", "",
  "syat-qualified vyapti", "none", "Standpoint-qualified: not-exists-as-gold"),
 ("inf-jaina-avak", "Jaina-Svetambara", "Jaina-Trairupya", "ghata", "avaktavya (saha)", "ubhaya", "",
  "saha-arpana", "none", "Simultaneous assertion inexpressible"),
 ("inf-upamana", "Nyaya", "Nyaya-5", "gavaya", "go-sadrsya", "gavaya-darsana", "go",
  "yatha gaus tatha gavayah", "none", "Comparison: wild cow known via cow-likeness"),
 ("inf-sabda", "Purva-Mimamsa", "Nyaya-5", "dharma", "jijnasya", "codana", "veda",
  "apta/apauruseya", "none", "Dharma known via injunction (Jaimini)"),
 ("inf-artha", "Purva-Mimamsa", "Nyaya-5", "devadatta", "ratri-bhojana", "pinatva+diva-abhojana", "",
  "srutartha-anyathanupapatti", "none", "Presumption: fat Devadatta who fasts by day eats at night"),
 ("inf-anupal", "Advaita", "Nyaya-5", "bhutala", "ghata-abhava", "yogyanupalabdhi", "bhutala",
  "abhava-grahika", "none", "Non-apprehension yields absence-cognition"),
 ("inf-isvara", "Nyaya", "Nyaya-5", "ksiti", "sakrtrkatva", "karyatva", "ghata",
  "karya → karta (Nyayakusumanjali)", "none", "Cosmological: earth effected, hence authored"),
 ("inf-mithya-adv", "Advaita", "Nyaya-5", "jagat", "mithyatva", "drsyatva", "sukti-rajata",
  "drsyatva → mithyatva", "none", "Advaita thesis-argument (Nyayamrta target)"),
 ("inf-mithya-dv", "Dvaita", "Nyaya-5", "jagat", "satyatva", "upapatti", "pratyaksa",
  "satpratipaksa counter", "Satpratipaksa", "Dvaita counter-inference (matched opposition)"),
 ("inf-vahni-svartha", "Nyaya", "Buddhist-2", "parvata", "vahni", "dhuma", "mahanasa",
  "svathanumana (self)", "none", "Inference for oneself: parāmarśa only"),
 ("inf-sabda-anitya", "Nyaya", "Nyaya-5", "sabda", "anityatva", "krtakatva", "ghata",
  "krtaka → anitya", "none", "Sound non-eternal because produced (NS 2.1 debate)"),
 ("inf-atman", "Nyaya", "Nyaya-5", "atman", "asti", "icchadi-linga", "atma-vyavahara",
  "linga → lingin", "none", "Self inferred from desire etc. (NS 1.1.10)"),
 ("inf-manas-anu", "Nyaya", "Nyaya-5", "manas", "anutva", "yaugapadya-abhava", "",
  "serial attention", "none", "Mind atomic: cognitions never simultaneous"),
 ("inf-purusa", "Samkhya", "Nyaya-5", "purusa", "asti", "samghatapararthatva", "",
  "composite serves other", "none", "Puruṣa from teleology of composites (SK 17)"),
 ("inf-satkarya", "Samkhya", "Buddhist-2", "vyakta", "satkaryatva", "asadakaranadi", "",
  "5 satkarya reasons", "none", "Effect pre-exists (SK 9)"),
 ("inf-ksanika-jaina", "Jaina-Svetambara", "Jaina-Trairupya", "jiva", "nitya-anitya (ubhaya)", "dravyaparyaya", "",
  "syat ubhaya", "none", "Jaina reply to kṣaṇikavāda: substance-mode both"),
 ("inf-sabda-vidhi", "Purva-Mimamsa", "Nyaya-5", "adhikarin", "pravrtti", "vidhi-vakya", "yajeta",
  "codana -> pravartana", "none", "Injunction moves to act (svargakamo yajeta)"),
 ("inf-artha-bahir", "Purva-Mimamsa", "Nyaya-5", "caitra", "bahirbhava", "grhe-asattva", "",
  "anyathanupapatti", "none", "Caitra not home, alive: must be outside"),
 ("inf-anupal-diva", "Advaita", "Nyaya-5", "bhutala", "ghata-abhava", "diva-yogyanupalabdhi", "bhutala",
  "abhava-grahika", "none", "Daylight non-apprehension yields absence"),
 ("inf-kevalanvayi2", "Nyaya", "Nyaya-5", "sabda", "abhidheyatva", "prameyatva", "sarva-vastu",
  "kevalanvayi", "none", "Sound is nameable because knowable"),
 ("inf-svartha-ksanika", "Bauddha-Sautrantika", "Buddhist-2", "bhava", "ksanikatva", "arthakriyakaritva", "pradipa",
  "sattva -> ksanikatva (svathanumana)", "none", "Self-inference of momentariness"),
 ("inf-parartha-dhuma", "Bauddha-Yogacara", "Buddhist-2", "parvata", "vahni", "dhuma", "mahanasa",
  "parartha-vakya form", "none", "Inference stated for others (PV 4)"),
 ("inf-jaina-naya", "Jaina-Svetambara", "Jaina-Trairupya", "jiva", "asti (dravyarthikat)", "dravya-drsti", "",
  "syat dravyarthika-naya", "none", "Substance-standpoint affirmation"),
 ("inf-mimamsa-bhavana", "Purva-Mimamsa", "Nyaya-5", "yagamana", "svarga", "bhavana", "jyotistoma",
  "bhavana -> phala", "none", "Productive operation yields heaven via apurva"),
 ("inf-nyaya-iccha", "Nyaya", "Nyaya-5", "atman", "nityatva", "jnanadi-guna", "atma-vyavahara",
  "guna -> gunin", "none", "Self permanent as quality-bearer (NS 3.1 line)"),
 ("inf-satkarya-taila", "Samkhya", "Buddhist-2", "taila", "satkaryatva", "tila-upadana", "tila",
  "upadana-niyama", "none", "Oil pre-exists in sesame (material-cause regularity)"),
 ("inf-viruddha2", "Nyaya", "Nyaya-5", "sabda", "nityatva", "sravanatva", "",
  "hetu proves opposite", "Viruddha", "Adversarial: audibility proves producedness, not eternity"),
 ("inf-savyabhicara2", "Nyaya", "Nyaya-5", "ayas", "dhumavattva", "vahnimattva", "",
  "tapta-ayogolaka counterexample", "Savyabhicara", "Adversarial: red-hot iron has fire, no smoke"),
 ("inf-badhita2", "Nyaya", "Nyaya-5", "candana", "usnatva", "gandhavattva", "",
  "sparsa-pratyaksa defeats", "Badhita", "Adversarial: sandal fragrant yet cool to touch"),
]

COG = [
 ("cog-prat-lauk", "sannikarsa cognition: pot seen by eye", "Pratyaksa", "cakṣu-sannikarsa, dosa-absent", 1, "laukika-sannikarsa"),
 ("cog-prat-alauk", "sāmānyalakṣaṇa: all smoke as smoky", "Pratyaksa", "alaukika; jati-mediated", 1, "samanyalaksana-pratyasatti"),
 ("cog-anum-hill", "parvato vahnimān dhūmāt", "Anumana", "paksa=parvata; trairupya holds", 1, "dhumatva→vahnitva vyapti"),
 ("cog-anum-fail", "hrado vahnimān dhūmāt (no smoke seen)", "Anumana", "paksadharmata missing", 0, "asiddha"),
 ("cog-upam", "gavaya known as cow-like", "Upamana", "similarity cognition active", 1, "go-sadrsya"),
 ("cog-sabda", "agnihotra injunction understood", "Sabda", "apta + akanksa/yogyata/sannidhi", 1, "codana-bodha"),
 ("cog-sabda-fail", "unintelligible string", "Sabda", "akanksa absent", 0, "nirarthaka"),
 ("cog-artha", "Devadatta eats at night (presumed)", "Arthapatti", "day-fast + fatness", 1, "anyathanupapatti"),
 ("cog-anupal", "no pot on floor", "Anupalabdhi", "yogya-anupalabdhi", 1, "¬_a[ghatatva]@bhutala"),
 ("cog-syat", "pot exists-as-clay", "Pratyaksa", "svadravya standpoint", 1, "syad-asti (n1)"),
 ("cog-syat-neg", "pot not-exists-as-gold", "Anupalabdhi", "paradravya standpoint", 1, "syan-nasti (n2)"),
 ("cog-bhrama", "shell-silver illusion", "Pratyaksa", "karana-dosa present", 0, "anyathakhyati; V_Pr=0"),
 ("cog-nirvikalpaka", "pot — bare particular, unschematized", "Pratyaksa", "nirvikalpaka stage", 1, "non-qualificative grasp"),
 ("cog-savikalpaka", "blue pot as qualified (nilah ghatah)", "Pratyaksa", "savikalpaka; samavaya link", 1, "Pr_r(nilatva)+Vs(ghata)"),
 ("cog-smrti", "remembered lecture content", "Pratyaksa", "samskara-janya; excluded from prama", 0, "smrti: reproduction, not pramana"),
 ("cog-samsaya", "stump-or-man doubt at dusk", "Pratyaksa", "sadharana-dharma trigger", 0, "samsaya; NS 2.1"),
 ("cog-yogaja", "yogin perceives the remote/past", "Pratyaksa", "alaukika; dhyana-janya", 1, "yogaja-pratyaksa"),
 ("cog-svapna", "dream-elephant", "Pratyaksa", "nidra-dosa; sublated on waking", 0, "svapna; badhita on waking"),
 ("cog-paramarsa", "smoke-fire pervasion recalled on hill", "Anumana", "vyapti-smrti + paksadharmata", 1, "paramarsa -> anumiti"),
 ("cog-kevala", "kevalin knows all substances-modes", "Pratyaksa", "kevala standpoint", 1, "kevala; anubhava residue"),
]

VNODES = [
 ("arg-tc-pratyaksa", "TC", [], "Pratyakṣa-khaṇḍa: nirvikalpaka/savikalpaka analysis; anyathakhyati defense", "Vada", "Pratitantra"),
 ("arg-tc-sabda", "TC", [], "Śabda-khaṇḍa: śābdabodha mechanism; Mimamsa/Buddhist replies", "Vada", "Pratitantra"),
 ("arg-nm-isvara", "NM", [], "Īśvara-sādhana: Nyāyakusumāñjali karyatva argument (Jayanta/Udayana lineage)", "Vada", "Pratitantra"),
 ("arg-sv-atman", "SV", [], "Ātma-vāda vs Buddhist no-self; abhāva-pramāṇa deployment", "Vada", "Sarvatantra"),
 ("arg-ts-ksanika", "TS", [], "Kṣaṇabhaṅga chapter: momentariness vs permanence (anti-Nyaya/Mimamsa)", "Vitanda", "Pratitantra"),
 ("arg-kkk-vyapti", "KKK", [], "Vyāpti-lakṣaṇa khaṇḍana: six definitions refuted (pre-Gaṅgeśa)", "Vitanda", "Pratitantra"),
 ("arg-vp-6pr", "VP", [], "Vedāntaparibhāṣā: six-pramāṇa Advaita epistemology codified", "Vada", "Sarvatantra"),
 ("arg-pp-bheda", "PP", [], "Pramāṇapaddhati: Dvaita pramāṇas; bheda as real and inferable", "Vada", "Pratitantra"),
 ("arg-sds-idx", "SDS", [], "Sarvadarśanasaṅgraha: doxographical ladder Cārvāka→Śaṅkara", "Vada", "Sarvatantra"),
]

VEDGES = [
 ("e7", "arg-tc-pratyaksa", "arg-kkk-vyapti", "uttarapaksa", "Asiddha", "TC", "Pratyaksa-khanda opening", 0.9),
 ("e8", "arg-kkk-vyapti", "arg-tc-pratyaksa", "purvapaksa", "Savyabhicara", "KKK", "vyapti-laksana khandana", 0.8),
 ("e9", "arg-ts-ksanika", "arg-sv-atman", "khandana", "Viruddha", "TS", "ksanabhanga pariccheda", 0.65),
 ("e10", "arg-sv-atman", "arg-ts-ksanika", "uddhara", "Badhita", "SV", "atma-vada reply", 0.7),
 ("e11", "arg-nm-isvara", "arg-ts-ksanika", "mandana", "none", "NM", "isvara-sadhana", 0.6),
 ("e12", "arg-vp-6pr", "arg-nyayamrta-mithyatva", "samanvaya", "none", "VP", "pramana-paribhasa", 0.5),
 ("e13", "arg-pp-bheda", "arg-advsiddhi-mithyatva", "khandana", "Satpratipaksa", "PP", "bheda-vada", 0.8),
 ("e14", "arg-sds-idx", "arg-satadusani", "samanvaya", "none", "SDS", "doxography index", 0.4),
 ("e15", "arg-tc-sabda", "arg-ts-sabda", "uttarapaksa", "none", "TC", "Sabda-khanda", 0.7),
 ("e16", "arg-satadusani", "arg-pp-bheda", "samanvaya", "none", "SataD", "shared anti-Advaita ground", 0.55),
]


def load(name):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def main():
    terms = [{"id": i, "sanskrit": s, "iast": ia, "darsanaScope": sc, "definitionSutras": ds,
              "ontologicalSort": sort, "formalSymbol": sym, "confidence": "famous-gist",
              "sourceNote": f"term {ia}", "verifyAgainst": "Monier-Williams + sastra editions",
              **({"nonFormalizableResidue": res} if res else {})}
             for i, s, ia, sc, ds, sort, sym, res in TERMS]
    infs = [{"id": i, "school": sc, "form": f, "paksa": pa, "sadhya": sa, "hetu": h,
             "drstanta": d, "vyapti": v, "hetvabhasa": hb,
             "members": {}, "note": n, "confidence": "famous-gist",
             "verifyAgainst": "NS/TC/PV/Tattvartha editions"}
            for i, sc, f, pa, sa, h, d, v, hb, n in INF]
    cogs = [{"id": i, "content": c, "pramana": p, "state": st, "valid": v,
             "standpointQualifier": q} for i, c, p, st, v, q in COG]

    nodes = load("vada_nodes.json")
    nids = {n["id"] for n in nodes}
    for nid, text, refs, sidd, katha, kind in VNODES:
        if nid not in nids:
            nodes.append({"id": nid, "textId": text, "sutraRefs": refs, "siddhanta": sidd,
                          "katha": katha, "siddhantaKind": kind})
    edges = load("vada_edges.json")
    eids = {e["id"] for e in edges}
    for eid, fr, to, kind, fal, ref, loc, w in VEDGES:
        if eid not in eids:
            edges.append({"id": eid, "from": fr, "to": to, "kind": kind,
                          "fallacyCharged": fal, "refutationTextId": ref, "locus": loc, "weight": w})

    for name, obj in (("terms.json", terms), ("inferences.json", infs),
                      ("cognitions.json", cogs), ("vada_nodes.json", nodes),
                      ("vada_edges.json", edges)):
        write_json(ROOT / "data" / name, obj)
        mirror_to_docs(ROOT, name, obj)
        print(name, len(obj))
    # mirror texts too for Pages UI
    for name in ("texts.json",):
        obj = load(name)
        mirror_to_docs(ROOT, name, obj)


if __name__ == "__main__":
    main()
