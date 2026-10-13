"""Canon round 2: Prasthanatrayi selections, PV/AKB/TS/TA indices, Natya, Alankara,
Ganita classics (BSS/SSiro), Astadhyayi 32-pada map + famous samasa/taddhita,
+4 texts, +7 vada nodes/edges. All tiers honest; verify-notes point to editions.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
V, F, T = "verbatim", "famous-gist", "topic-digest"

NEWTEXTS = [
 {"id": "AKB", "titleSanskrit": "Abhidharmakośabhāṣya", "titleEnglish": "Treasury of Abhidharma (Vasubandhu; Vaibhasika compendium)",
  "authorIds": ["vasubandhu"], "layer": "sangraha", "darsana": "Bauddha-Sautrantika",
  "corpusRefs": {"gretil": "Abhidharmakosa"}},
 {"id": "Natya", "titleSanskrit": "Nāṭyaśāstra", "titleEnglish": "Treatise on Theatre (Bharata)",
  "authorIds": ["bharata"], "layer": "prakarana", "darsana": "Sahitya", "corpusRefs": {}},
 {"id": "BSS", "titleSanskrit": "Brāhmasphuṭasiddhānta", "titleEnglish": "Corrected Brahma Doctrine (Brahmagupta, 628 CE)",
  "authorIds": ["brahmagupta"], "layer": "prakarana", "darsana": "Ganitashastra", "corpusRefs": {}},
 {"id": "SSiro", "titleSanskrit": "Siddhāntaśiromaṇi", "titleEnglish": "Crest of Doctrines (Bhaskara II: Lilavati/Bijaganita/Gola)",
  "authorIds": ["bhaskara2"], "layer": "prakarana", "darsana": "Ganitashastra", "corpusRefs": {}},
]

# (id, textId, notation, tier, sanskrit, translation, pada, pram, logic)
R = [
 # ---- Upanisads (under BS prasthana pattern) ----
 ("UP-ISA", "BS", "Īśa 1", V, "isavasyamidam sarvam yatkinca jagatyam jagat",
  "All this is enveloped by the Lord; enjoy through renunciation", ["Artha"], ["Sabda"], ""),
 ("UP-KENA", "BS", "Kena · presita", T, "kenesitam patati presitam manah",
  "By whom willed does mind speed? — the ear of the ear, mind of mind", ["Artha"], ["Sabda"], ""),
 ("UP-KATHA", "BS", "Kaṭha 1.3.14", V, "uttisthata jagrata prapya varan nibodhata",
  "Arise, awake, approach the excellent and learn (Yama to Naciketas)", ["Artha"], ["Sabda"], ""),
 ("UP-MUND", "BS", "Muṇḍaka 3.1.6", V, "satyameva jayate nanrtam",
  "Truth alone triumphs, not falsehood", ["Artha"], ["Sabda"], ""),
 ("UP-MAND7", "BS", "Māṇḍūkya 7 · caturtha", F, "nantahprajnam ... santam sivam advaitam",
  "The fourth: unseen, calm, auspicious, nondual — the Self", ["Artha"], [], ""),
 ("UP-MAND12", "BS", "Māṇḍūkya 12 · omkara", F, "amatrascaturtho vyavaharyah ...",
  "The measureless fourth beyond oṃ's morae", ["Artha"], [], ""),
 ("UP-TAIT", "BS", "Taittirīya 2.1", F, "satyam jnanam anantam brahma",
  "Brahman is truth, knowledge, infinite", ["Artha"], ["Sabda"], ""),
 ("UP-AIT", "BS", "Aitareya 3.1.3", V, "prajnanam brahma", "Consciousness is brahman", ["Artha"], ["Sabda"], ""),
 ("UP-CHAND314", "BS", "Chāndogya 3.14.1", V, "sarvam khalvidam brahma", "All this is brahman (Śāṇḍilya-vidyā)", ["Artha"], ["Sabda"], ""),
 ("UP-BRH245", "BS", "Bṛhad 2.4.5", F, "atmanastu kamaya sarvam priyam",
  "For the Self's sake all is dear (Maitreyī)", ["Artha"], ["Sabda"], ""),
 ("UP-SVET", "BS", "Śvetāśvatara 6.23", T, "yasya deve para bhaktih",
  "Supreme devotion to God and teacher reveals the truths", ["Artha"], ["Sabda"], ""),
 ("UP-ISA-KARMA", "BS", "Īśa 2 · karma", F, "kurvanneveha karmani ...",
  "Doing works here alone: desire a hundred-year life (karma-jñāna tension)", ["Artha"], ["Sabda"], ""),
 # ---- Gita ----
 ("GITA-247", "BS", "Gītā 2.47", V, "karmanyevadhikaraste ma phalesu kadacana",
  "Right to action alone, never to its fruits", ["Artha"], ["Sabda"], ""),
 ("GITA-216", "BS", "Gītā 2.16", F, "nasato vidyate bhavo nabhavo vidyate satah",
  "No being of non-being; no non-being of being (satkārya-adjacent)", ["Artha"], ["Sabda"], "y ⊆_sakti Prakrti"),
 ("GITA-47", "BS", "Gītā 4.7", V, "yada yada hi dharmasya glanirbhavati",
  "Whenever dharma declines, I manifest myself", ["Artha"], ["Sabda"], ""),
 ("GITA-48", "BS", "Gītā 4.8", F, "paritranaya sadhunam vinasaya ca duskrtam",
  "To protect the good and destroy evil, for dharma's establishment", ["Artha"], ["Sabda"], ""),
 ("GITA-1866", "BS", "Gītā 18.66", V, "sarvadharman parityajya mamekam saranam vraja",
  "Abandoning all dharmas, take refuge in Me alone", ["Artha"], ["Sabda"], ""),
 ("GITA-319", "BS", "Gītā 3.19", F, "tasmadasaktah satatam ...",
  "Ever unattached, do the deed; the unattached attains the supreme", ["Artha"], ["Sabda"], ""),
 ("GITA-1321", "BS", "Gītā 13.21 · puruṣa-prakṛti", T, "purusah prakrtisthah ...",
  "Puruṣa in prakṛti enjoys guṇas; attachment causes high/low births", ["Tattva"], ["Sabda"], ""),
 # ---- Brahmasutra 4 adhyayas ----
 ("BS-ADH1", "BS", "BS adhyāya 1 · samanvaya", F, "samanvaya (1.1-1.4)",
  "Harmony: Vedānta texts teach brahman (janmādi, śāstrayoni, samanvaya)", ["Artha"], ["Sabda"], ""),
 ("BS-ADH2", "BS", "BS adhyāya 2 · avirodha", T, "avirodha (2.1-2.4)",
  "Non-contradiction: Sāṅkhya/atomist/Buddhist/Jaina objections answered", ["Artha"], ["Anumana"], ""),
 ("BS-ADH3", "BS", "BS adhyāya 3 · sādhana", T, "sadhana (3.1-3.4)",
  "Means: transmigration arc, disciplines, meditation", ["Artha"], [], ""),
 ("BS-ADH4", "BS", "BS adhyāya 4 · phala", T, "phala (4.1-4.4)",
  "Fruit: the released soul's powers; non-return", ["Artha"], [], ""),
 # ---- Pramanavarttika ----
 ("PV-SVA", "PV", "PV 1 · svārthānumāna", T, "trairupya-hetu (paksadharmata/anvaya/vyatireka)",
  "Inference for oneself on the triple mark", ["Pramana"], ["Anumana"], ""),
 ("PV-SIDDHI", "PV", "PV 2 · pramāṇasiddhi", T, "pramanabhuta-bhagavan",
  "The Fortunate One as pramāṇa-embodied; compassion as means", ["Pramana"], [], ""),
 ("PV-PRAT", "PV", "PV 3 · pratyakṣa", T, "kalpanapodha-pratyaksa",
  "Perception free of construction; svalakṣaṇa as object", ["Pramana"], ["Pratyaksa"], ""),
 ("PV-PARA", "PV", "PV 4 · parārthānumāna", T, "parartha-vakya",
  "Inference for others: statement form (cf. Nyāya avayavas)", ["Pramana"], ["Anumana"], ""),
 ("PV-APOHA", "PV", "PV · apoha", F, "anyavyavrtti-sabda",
  "Words denote by excluding others; no universals needed", ["Sabda"], ["Anumana"], ""),
 # ---- Abhidharmakosa 8 sthanas ----
 ("AKB-1", "AKB", "Kośa 1 · dhātu", T, "dhatu-nirdesa", "Elements: 18 dhātus (6 senses × objects × cognitions)", ["Tattva"], []),
 ("AKB-2", "AKB", "Kośa 2 · indriya", T, "indriya-nirdesa", "22 faculties; jīvita, vedanā structures", ["Tattva"], []),
 ("AKB-3", "AKB", "Kośa 3 · loka", T, "loka-nirdesa", "Cosmology: Meru, continents, kalpas, sattva-cycles", ["Tattva"], []),
 ("AKB-4", "AKB", "Kośa 4 · karma", T, "karma-nirdesa", "Action: cetanā, three doors, avijñapti against Sautrāntika", ["Tattva"], []),
 ("AKB-5", "AKB", "Kośa 5 · anuśaya", T, "anusaya-nirdesa", "Latent defilements; 98 proclivities taxonomy", ["Tattva"], []),
 ("AKB-6", "AKB", "Kośa 6 · mārga-satya", T, "marga-satya", "Path: 4 truths, 37 aids, darśana/bhāvanā-mārga", ["Tattva"], []),
 ("AKB-7", "AKB", "Kośa 7 · jñāna", T, "jnana-nirdesa", "Ten knowledges; kṣaya/anutpāda at arhattva", ["Tattva"], []),
 ("AKB-8", "AKB", "Kośa 8 · samādhi", T, "samadhi-dhyana-arupya", "Absorptions: 4 dhyānas, 4 formless, nirodha", ["Tattva"], []),
 # ---- Tattvasangraha clusters ----
 ("TS-NYAYA", "TS", "TS · nyāya-vaiśeṣika-parīkṣā", T, "dravya-guna-atman-khandana",
  "Critique of substance/quality/self categories", ["Abhava"], ["Anumana"], ""),
 ("TS-SAMKHYA", "TS", "TS · puruṣa-prakṛti-parīkṣā", T, "purusa-prakrti-khandana",
  "Critique of eternal self and primordial matter", ["Abhava"], ["Anumana"], ""),
 ("TS-MIM", "TS", "TS · śabda-ātman-parīkṣā", T, "apauruseya-atman-khandana",
  "Against eternal word and Mīmāṃsā self", ["Sabda"], ["Anumana"], ""),
 ("TS-JAINA", "TS", "TS · anekānta-parīkṣā", T, "anekanta-khandana",
  "Against many-sided ontology (Śāntarakṣita vs Jaina)", ["Abhava"], ["Anumana"], ""),
 ("TS-ISVARA", "TS", "TS · īśvara-parīkṣā", T, "isvara-khandana",
  "Against Nyāya creator-arguments (karyatva etc.)", ["Abhava"], ["Anumana"], ""),
 # ---- Tattvartha adhyayas ----
 ("TA-ADH2", "TArthaS", "TĀ 2 · jīva", T, "jiva-bheda (samsarin/mukta)",
  "Souls: transmigrating and released; five knowledges", ["Tattva"], []),
 ("TA-ADH5", "TArthaS", "TĀ 5 · ajīva", T, "dharma-adharma-akasa-kala-pudgala",
  "Non-souls: motion/rest/space/time/matter", ["Tattva"], []),
 ("TA-ADH6", "TArthaS", "TĀ 6 · āsrava", T, "yoga-asrava (manas/vacana/kaya)",
  "Influx channels: mind, speech, body activities", ["Tattva"], []),
 ("TA-ADH7", "TArthaS", "TĀ 7 · vrata", T, "anuvrata-sila (5+7)",
  "Five lesser vows + seven disciplinary vows", ["Tattva"], []),
 ("TA-ADH8", "TArthaS", "TĀ 8 · bandha", T, "bandha-caturvidha",
  "Bondage fourfold: nature, duration, intensity, quantity", ["Tattva"], []),
 ("TA-ADH9B", "TArthaS", "TĀ 9 · nirjarā", T, "dvadasa-tapas",
  "Shedding via twelve austerities (6 outer + 6 inner)", ["Tattva"], []),
 # ---- Natyasastra ----
 ("NAT-RASA", "Natya", "NŚ 6 · rasa-sūtra", V, "vibhavanubhavavyabhicarisamyogad rasanispattih",
  "Rasa arises from union of determinants, consequents, transients", ["Rasa"], [], "R=Φ⊙S₀"),
 ("NAT-STHAYI", "Natya", "NŚ 6-7 · sthāyibhāva", F, "asta-sthayin (rati ... sama)",
  "Eight/nine durable emotions seeding the rasas", ["Rasa"], [], ""),
 ("NAT-VYABH", "Natya", "NŚ 7 · vyabhicārin", F, "trayastrimsad vyabhicarinah",
  "Thirty-three transient emotions (nirveda, glāni, ...)", ["Rasa"], [], ""),
 ("NAT-ABHI", "Natya", "NŚ 8-13 · abhinaya", T, "caturvidha-abhinaya",
  "Four enactments: bodily, vocal, costumed, sattvic", ["Rasa"], [], ""),
 ("NAT-DHARMI", "Natya", "NŚ 13 · dharmī", T, "lokadharmi-natyadharmi",
  "Realistic vs theatrical convention", ["Rasa"], [], ""),
 ("NAT-VRTTI", "Natya", "NŚ 20 · vṛtti", T, "catasro vrttayah",
  "Four styles: Bhāratī, Sāttvatī, Kaiśikī, Ārabhaṭī", ["Rasa"], [], ""),
 # ---- Alankara ----
 ("KP-KAVYA", "KavyaP", "KP 1 · kāvya-lakṣaṇa", V, "tadadosau sabdarthau sagunav analankrti punah kvapi",
  "Poetry: faultless word-meaning with qualities, sometimes unadorned", ["Dhvani"], [], ""),
 ("KP-UPAMA", "KavyaP", "KP 10 · upamā", F, "upamana-upameya-sadrsya",
  "Simile: stated likeness of vehicle and topic", ["Dhvani"], [], ""),
 ("KP-RUPAKA", "KavyaP", "KP 10 · rūpaka", F, "aropyamana-aropa",
  "Metaphor: superimposition without likeness-marker", ["Dhvani"], [], ""),
 ("KP-UTPREKSA", "KavyaP", "KP 10 · utprekṣā", F, "sambhavana-utpreksa",
  "Poetic fancy: imagined as-if", ["Dhvani"], [], ""),
 ("KP-ATISAYA", "KavyaP", "KP 10 · atiśayokti", F, "lokati kranta-vacana",
  "Hyperbole: transcending-world description", ["Dhvani"], [], ""),
 # ---- Aryabhatiya padas ----
 ("ARY-GITI", "Arya", "Āryabhaṭīya · Gitikapada", T, "dasagitika-paribhasa",
  "10 gītis + paribhāṣā: notation, yugas, sine-seeds", ["Other"], []),
 ("ARY-GANITA", "Arya", "Āryabhaṭīya · Gaṇitapāda (33)", T, "kuttaka-sredhi-ksetra",
  "Pulverizer, series, π, geometry, shadows", ["Other"], []),
 ("ARY-KALA", "Arya", "Āryabhaṭīya · Kālakriyā (25)", T, "yuga-graha-gati",
  "Time-divisions, planetary revolutions, calendrics", ["Other"], []),
 ("ARY-GOLA", "Arya", "Āryabhaṭīya · Gola (50)", T, "bhugola-graha-grahana",
  "Sphere, day-night, eclipses by shadow-geometry", ["Other"], []),
 ("ARY-KUTTAKA", "Arya", "Āryabhaṭīya · kuṭṭaka", F, "kuttakara-ganita",
  "Pulverizer algorithm for indeterminates (continued-fraction logic)", ["Other"], []),
 # ---- Brahmagupta ----
 ("BSS-ZERO", "BSS", "BSS 18.30-35 · śūnya", F, "sunya-yoga-vyavakalana (18.30-35)",
  "Zero arithmetic: a±0=a; 0²=0; √0=0; debts/fortunes rules", ["Other"], []),
 ("BSS-NEG", "BSS", "BSS 18.31-33 · dhana-ṛṇa", F, "dhana-rna-sunya-vidhi",
  "Positive/negative/zero operations (first full sign rules)", ["Other"], []),
 ("BSS-KUTTAKA", "BSS", "BSS 18 · kuṭṭaka", T, "kutaka-bhavana",
  "Refined pulverizer; second-order indeterminate groundwork", ["Other"], []),
 # ---- Bhaskara II ----
 ("SS-LIL", "SSiro", "Siddhāntaśiromaṇi · Līlāvatī", T, "lilavati-pati",
  "Arithmetic/geometric classic: series, combinatorics, kuṭṭaka", ["Other"], []),
 ("SS-BIJA", "SSiro", "Siddhāntaśiromaṇi · Bījagaṇita", F, "cakravala-vargaprakrti",
  "Cyclic method solving x²−Ny²=1 (Pell) centuries before Europe", ["Other"], []),
 ("SS-GOLA", "SSiro", "Siddhāntaśiromaṇi · Golādhyāya", T, "grahaganita-gola",
  "Planetary computation + sphere; instantaneous motion (tātkālika gati)", ["Other"], []),
 # ---- Astadhyayi 32-pada map ----
 ("A-PADA-11", "Astadh", "A 1.1 · saṃjñā-paribhāṣā", T, "pada-map 1.1", "Terms (vṛddhi/guṇa), substitution logic, pada", ["Sabda"], []),
 ("A-PADA-12", "Astadh", "A 1.2 · pratyaya-doṣa", T, "pada-map 1.2", "Affix markers, accent classes, stem rules", ["Sabda"], []),
 ("A-PADA-13", "Astadh", "A 1.3 · iṭ-pada", T, "pada-map 1.3", "it-markers, elision, voice (ātmanepada) assignment", ["Sabda"], []),
 ("A-PADA-14", "Astadh", "A 1.4 · kāraka-saṅkhyā", T, "pada-map 1.4", "Kāraka roles, number, indeclinables", ["Sabda"], []),
 ("A-PADA-21", "Astadh", "A 2.1 · samāsa I", T, "pada-map 2.1", "Compounds I: avyayībhāva, tatpuruṣa frames", ["Sabda"], []),
 ("A-PADA-22", "Astadh", "A 2.2 · samāsa II", T, "pada-map 2.2", "Compounds II: bahuvrīhi, dvandva, remainder rules", ["Sabda"], []),
 ("A-PADA-23", "Astadh", "A 2.3 · vibhakti", T, "pada-map 2.3", "Case-endings from kāraka meaning", ["Sabda"], []),
 ("A-PADA-24", "Astadh", "A 2.4 · luk-ekaśeṣa", T, "pada-map 2.4", "Elision (luk), one-remainder, repetition", ["Sabda"], []),
 ("A-PADA-31", "Astadh", "A 3.1 · pratyaya-sāmānya", T, "pada-map 3.1", "General affixation (śap, vikaraṇas)", ["Sabda"], []),
 ("A-PADA-32", "Astadh", "A 3.2 · lakāra", T, "pada-map 3.2", "Tense-moods (laṭ, loṭ, liṭ...) and participles", ["Sabda"], []),
 ("A-PADA-33", "Astadh", "A 3.3 · kṛdanta", T, "pada-map 3.3", "Primary nominal derivatives", ["Sabda"], []),
 ("A-PADA-34", "Astadh", "A 3.4 · dhātvadhikāra", T, "pada-map 3.4", "Root-domain rules, tiṅ affix details", ["Sabda"], []),
 ("A-PADA-41", "Astadh", "A 4.1 · strī-pratyaya", T, "pada-map 4.1", "Nominal stems, feminine affixes, patronymic start", ["Sabda"], []),
 ("A-PADA-42", "Astadh", "A 4.2 · taddhita I", T, "pada-map 4.2", "Secondary suffixes I (descendant, place...)", ["Sabda"], []),
 ("A-PADA-43", "Astadh", "A 4.3 · taddhita II", T, "pada-map 4.3", "Secondary suffixes II", ["Sabda"], []),
 ("A-PADA-44", "Astadh", "A 4.4 · taddhita III", T, "pada-map 4.4", "Secondary suffixes III", ["Sabda"], []),
 ("A-PADA-51", "Astadh", "A 5.1 · taddhita IV", T, "pada-map 5.1", "Secondary suffixes IV (rates, measures...)", ["Sabda"], []),
 ("A-PADA-52", "Astadh", "A 5.2 · taddhita V", T, "pada-map 5.2", "Secondary suffixes V", ["Sabda"], []),
 ("A-PADA-53", "Astadh", "A 5.3 · taddhita VI", T, "pada-map 5.3", "Secondary suffixes VI", ["Sabda"], []),
 ("A-PADA-54", "Astadh", "A 5.4 · taddhita VII", T, "pada-map 5.4", "Secondary suffixes VII (abstracts etc.)", ["Sabda"], []),
 ("A-PADA-61", "Astadh", "A 6.1 · sandhi-dvitva", T, "pada-map 6.1", "Vowel sandhi, reduplication, guṇa/vṛddhi ops", ["Sabda"], []),
 ("A-PADA-62", "Astadh", "A 6.2 · samāsa-svara", T, "pada-map 6.2", "Compound accent", ["Sabda"], []),
 ("A-PADA-63", "Astadh", "A 6.3 · samāsa-phonetics", T, "pada-map 6.3", "Aluk, hrasva, and compound-internal changes", ["Sabda"], []),
 ("A-PADA-64", "Astadh", "A 6.4 · aṅga-ādeśa", T, "pada-map 6.4", "Stem changes; asiddhavat suspension", ["Sabda"], []),
 ("A-PADA-71", "Astadh", "A 7.1 · sup-tiṅ-ādeśa", T, "pada-map 7.1", "Case/verb-ending substitutes", ["Sabda"], []),
 ("A-PADA-72", "Astadh", "A 7.2 · iṭ-āgama", T, "pada-map 7.2", "Augments (iṬ) in ārdhadhātuka domain", ["Sabda"], []),
 ("A-PADA-73", "Astadh", "A 7.3 · guṇa-vṛddhi", T, "pada-map 7.3", "Guṇa/vṛddhi operations (sārvadhātuka...)", ["Sabda"], []),
 ("A-PADA-74", "Astadh", "A 7.4 · dvirvacana", T, "pada-map 7.4", "Reduplication phonetics", ["Sabda"], []),
 ("A-PADA-81", "Astadh", "A 8.1 · pada-svara", T, "pada-map 8.1", "Word-boundary rules and accent", ["Sabda"], []),
 ("A-PADA-82", "Astadh", "A 8.2 · padānta", T, "pada-map 8.2", "Final-position changes (jaśtva etc.)", ["Sabda"], []),
 ("A-PADA-83", "Astadh", "A 8.3 · visarga-sandhi", T, "pada-map 8.3", "Visarga and sibilant sandhi", ["Sabda"], []),
 ("A-PADA-84", "Astadh", "A 8.4 · dvitva-anunāsika", T, "pada-map 8.4", "Doubling, nasal substitution (tripādī asiddha zone)", ["Sabda"], []),
 # ---- famous samasa/taddhita ----
 ("A-4182", "Astadh", "A 4.1.82", V, "samarthanam prathamadv a",
  "Taddhita follows semantically-connected first bases", ""),
 ("A-4192", "Astadh", "A 4.1.92", V, "tasyapatyam", "Descendant-meaning suffixes (apatya)", ""),
 ("A-2122", "Astadh", "A 2.1.22", F, "tatpurusah samanakaranah ...",
  "Tatpuruṣa compounds (case-relation determinatives)", ""),
 ("A-2114", "Astadh", "A 2.1.4", F, "saha supa (avyayibhava)",
  "Indeclinable compounds with nominal bases", ""),
]

VNODES = [
 ("arg-pv-pramana", "PV", [], "Pramāṇasiddhi: the Fortunate One as pramāṇa-embodied (vs Mīmāṃsā apauruṣeya)", "Vada", "Pratitantra"),
 ("arg-akb-anatman", "AKB", [], "No-self analysis: skandha/āyatana/dhātu reduction (vs ātman)", "Vada", "Pratitantra"),
 ("arg-bs-samanvaya", "BS", [], "Samanvaya: all Vedānta passages teach brahman (sūtra 1.1.4)", "Vada", "Sarvatantra"),
 ("arg-ns-sabda", "NS", [], "Śabda-parīkṣā: sound non-eternal, convention-fixed (vs Mīmāṃsā)", "Vada", "Pratitantra"),
 ("arg-ta-ubhaya", "TArthaS", [], "Substance-mode both: nitya-anitya reply to kṣaṇikavāda", "Vada", "Pratitantra"),
 ("arg-mmk-sunya", "MMK", [], "Svabhāva-parīkṣā: emptiness of own-being (vs ātman/dravya)", "Vitanda", "Pratitantra"),
 ("arg-ts-isvara", "TS", [], "Īśvara-parīkṣā: creator-argument refutation (vs Nyāya)", "Vitanda", "Pratitantra"),
]
VEDGES = [
 ("e17", "arg-ta-ubhaya", "arg-ts-ksanika", "khandana", "Viruddha", "TArthaS", "dravyaparyaya-vada", 0.6),
 ("e18", "arg-mmk-sunya", "arg-sv-atman", "khandana", "Viruddha", "MMK", "svabhava-pariksa", 0.6),
 ("e19", "arg-pv-pramana", "arg-sv-abhava", "purvapaksa", "Asiddha", "PV", "pramanasiddhi", 0.55),
 ("e20", "arg-akb-anatman", "arg-sv-atman", "khandana", "Savyabhicara", "AKB", "pudgala-pariksa", 0.5),
 ("e21", "arg-ns-sabda", "arg-sv-abhava", "khandana", "Satpratipaksa", "NS", "sabda-pariksa (Bk 2)", 0.65),
 ("e22", "arg-bs-samanvaya", "arg-advsiddhi-mithyatva", "samanvaya", "none", "BS", "samanvaya-adhikarana", 0.5),
 ("e23", "arg-ts-isvara", "arg-nm-isvara", "khandana", "Viruddha", "TS", "isvara-pariksa", 0.6),
]


def main():
    texts = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
    tids = {t["id"] for t in texts}
    for t in NEWTEXTS:
        if t["id"] not in tids:
            texts.append(t)
    write_json(ROOT / "data" / "texts.json", texts)
    mirror_to_docs(ROOT, "texts.json", texts)

    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    added = 0
    for rec in R:
        rec = list(rec) + ["", "", ""]  # pad: sanskrit..logic defaults
        rid, text, not_, tier, san, tr = rec[0], rec[1], rec[2], rec[3], rec[4], rec[5]
        pada = rec[6] if isinstance(rec[6], list) else []
        pram = rec[7] if isinstance(rec[7], list) else []
        logic = rec[8] if isinstance(rec[8], str) else ""
        if rid not in by_id:
            p = provenance(tier, f"{not_} (canon-2)")
            by_id[rid] = {"id": rid, "textId": text, "adhyaNotation": not_,
                          "sanskrit": normalize_iast(san), "translation": tr,
                          "padarthasMentioned": list(pada), "pramanasInvoked": list(pram),
                          **({"logicalForm": logic} if logic else {}),
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "Upanisad/Gita/BS/PV/AKB/TS/TA/Natya/Ganita/Panini eds."}
            added += 1
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)

    nodes = json.loads((ROOT / "data" / "vada_nodes.json").read_text(encoding="utf-8"))
    nids = {n["id"] for n in nodes}
    for nid, text, refs, sidd, katha, kind in VNODES:
        if nid not in nids:
            nodes.append({"id": nid, "textId": text, "sutraRefs": refs, "siddhanta": sidd,
                          "katha": katha, "siddhantaKind": kind})
    edges = json.loads((ROOT / "data" / "vada_edges.json").read_text(encoding="utf-8"))
    eids = {e["id"] for e in edges}
    for eid, fr, to, kind, fal, ref, loc, w in VEDGES:
        if eid not in eids:
            edges.append({"id": eid, "from": fr, "to": to, "kind": kind,
                          "fallacyCharged": fal, "refutationTextId": ref, "locus": loc, "weight": w})
    write_json(ROOT / "data" / "vada_nodes.json", nodes)
    write_json(ROOT / "data" / "vada_edges.json", edges)
    mirror_to_docs(ROOT, "vada_nodes.json", nodes)
    mirror_to_docs(ROOT, "vada_edges.json", edges)
    print(f"texts {len(texts)}; sutras {len(old)} -> {len(out)} (+{added}); "
          f"nodes {len(nodes)}; edges {len(edges)}")


if __name__ == "__main__":
    main()
