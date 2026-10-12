"""Expand SK to 70 individual karika records (ids SK-K01..SK-K70; existing thematic kept).

Tier honesty: verbatim only for exactly-remembered wording; famous-gist for
doctrine-certain; topic-digest with outline-level theme otherwise (verify: Larson
Classical Samkhya / Whicher Integrity of the Yoga Darsana / SK editions on SARIT).
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

# (karika, tier, sanskrit/key-phrase, translation/theme)
K = [
 (1, F, "duhkhatrayabhighataj jijnasa tadapaghatake hetau",
  "Blow of threefold suffering (adhyatmika/adhibhautika/adhidaivika) starts inquiry"),
 (2, T, "drsta-anusravika-upaya", "Seen (dṛṣṭa) and heard (Vedic) remedies fail to end suffering finally"),
 (3, F, "mulaprakrtir avikrtih mahadadyah prakrtivikrtayah saptah s sodasakas tu vikrtah na prakrtir na vikrtih purusah",
  "Root nature unproduced; 7 produced-and-producing; 16 mere products; puruṣa neither"),
 (4, V, "drstam anumanam aptavacanam ca sarvapramanasiddhatvat",
  "Perception, inference, trustworthy word — all pramāṇas established thereby"),
 (5, F, "prativisayadhyavasayo drstam",
  "Perception: determinate cognition of the presented object"),
 (6, F, "lingalingipurvakam anumanam aptasrutir aptavacanam",
  "Inference via mark-bearer relation; testimony is the apta's word"),
 (7, T, "satah anupalabdhi-hetu", "Why the existent may go unperceived (leads to 8 causes)"),
 (8, F, "atidurat samipyad ... anupalabdhih (8 karana)",
  "Eight causes of non-perception: distance, nearness, defect, inattention, subtlety, etc."),
 (9, F, "asadakaranad upadan agrahanat sarvasambhavabhavat saktasya sakyakaranat karanabhavat ca satkaryam",
  "Satkārya: 5 reasons — nothing from non-being, material cause needed, etc."),
 (10, F, "hetumad anityam avyapi sakriyam anekam asritam lingam ...",
  "Manifest has cause, is impermanent, parted, active, manifold, dependent, a mark"),
 (11, F, "trigunam aviveki visayah samanyam acetanam prasavadharmi vyaktam",
  "Manifest: three-guṇa'd, undiscriminating, objective, common, insentient, productive"),
 (12, F, "prityapritivisadamakaih ... gunah paraspara ...",
  "Guṇas pleasure/pain/delusion-natured; mutually dominating, supporting, producing"),
 (13, T, "sattva-ragas-tamas-vrtti", "Sattva buoyance/illumination, rajas stimulation, tamas restraint"),
 (14, F, "bhedanam parimanat samanvayat ... avyaktasiddhih",
  "Unmanifest proved: finitude of products, homogeneity, evolution, cause-effect split"),
 (15, T, "karana-karya-aikya", "Cause-effect unity argued (effect the unfolded cause)"),
 (16, T, "karana-vyapara", "How the one prakṛti's activity yields manifold effects"),
 (17, F, "samghatapararthatvat trigunadiviparyayad adhisthanat ... puruso asti",
  "Puruṣa proved: composites serve another; guṇa-opposite; superintendence; enjoyment"),
 (18, F, "jananamaranakarananam pratiniyamad ... purusabahutvam",
  "Plurality of puruṣas: birth/death/instruments distributed per individual"),
 (19, F, "tasmac ca viparyasat ... saksi kevalo madhyasthah drasta akarta",
  "Puruṣa as witness: isolated, neutral, seer, non-agent — opposite of guṇas"),
 (20, T, "cetana-samyoga", "Conscious principle's conjunction with the insentient explained"),
 (21, F, "purusasya darsanartham ... pangvandhavad ubhayoh samyogah",
  "Lame-and-blind simile: union for seeing (puruṣa) and acting (prakṛti)"),
 (22, T, "mahadadi-krama", "Order: prakṛti → mahat → ahaṅkāra → gaṇa + tanmātras"),
 (23, F, "adhyavasayo buddhih dharmo jnanam vairagyam aisvaryam ...",
  "Intellect is resolve; its sattvic forms: dharma, knowledge, dispassion, power"),
 (24, F, "abhimano ahankarah",
  "Ego-principle is self-appropriation (ahaṅkāra)"),
 (25, F, "sattvika ekadasakah ... tamasah tanmatrah",
  "Sāttvika creation: 11 senses; tāmasa: 5 subtle elements"),
 (26, T, "buddhindriya-karmendriya", "Five sense-powers and five action-powers enumerated"),
 (27, T, "ubhaya-vrtti", "Senses function on present objects; mind spans all times"),
 (28, T, "svavisyaya-vrtti", "Each outer sense grasps only its own object-range"),
 (29, F, "sv alaks anyam ... manah ubhayamakam",
  "Mind two-sided: like senses outward, like intellect inward"),
 (30, T, "dvara-vrtti", "Outer senses as doors; intellect enjoys the gathered objects"),
 (31, T, "yugapat-pravrtti", "Joint operation of the thirteenfold instrument explained"),
 (32, T, "karana-kala-niyama", "Senses never grasp past/future; intellect's wider scope"),
 (33, T, "antahkarana-bheda", "Three inner instruments: intellect, ego, mind — functions distinguished"),
 (34, T, "visaya-bheda", "Five-fold objects apportioned to the sense-powers"),
 (35, T, "prana-adi-vrtti", "Vital airs as common function of the instrument-totality"),
 (36, T, "karana-asakti", "Why instruments act: superintended by puruṣa, like the chariot"),
 (37, T, "purusartha-pravrtti", "All instrument-activity for puruṣa's enjoyment and release"),
 (38, F, "tanmatrany avisesah ...",
  "Subtle elements unspecific; gross elements specific (peaceful/terrible/dull)"),
 (39, T, "visesa-avisesa-vibhaga", "Specific/unspecific division across elements and senses"),
 (40, F, "purvotpannam asaktam niyatam mahadadi suksmaparyantam samsarati ...",
  "Subtle body: primeval, unconfined, transmigrates, invested with bhāvas"),
 (41, T, "citra-pradipa", "Painting/lamp similes for instrument cooperation"),
 (42, T, "bhogartha-sarga", "Creation serves enjoyment; liṅga persists till release"),
 (43, T, "bhava-samskara", "Dispositions carried across births by the liṅga"),
 (44, T, "dharma-adi-gati", "Dharma leads upward, adharma downward — transmigration logic"),
 (45, T, "vairagya-siddhi", "Dispassion dissolves prakṛti-bond; knowledge liberates"),
 (46, F, "viparyayo asaktis tustih siddhih (pratyayasarga)",
  "Intellectual creation fourfold: error, disability, contentment, accomplishment"),
 (47, F, "astavikalpo ... asaktih (28 bheda)",
  "Disability 28-fold: 11 sense-defects + 17 intellect-defects"),
 (48, F, "navadha tustih ...",
  "Contentment 9-fold: 4 internal + 5 external"),
 (49, F, "astadha siddhih ...",
  "Accomplishment 8-fold: reasoning, word, study, suffering-acceptance, etc."),
 (50, T, "pratyayasarga-laksana", "Why this creation is called intellectual (pratyaya-based)"),
 (51, T, "linga-vrtti-bheda", "Liṅga's modes across the four intellectual creations"),
 (52, T, "daiva-adi-sarga", "Eightfold divine creation within the manifest order"),
 (53, T, "manusya-tiryak-sarga", "Human, animal, vegetal orders and guṇa-mixture"),
 (54, F, "urdhvam sattvavisalah ...",
  "Upward sattva-abundance, below tamas-dominance; middle rajas"),
 (55, T, "jara-marana-duhkha", "Ageing-death-suffering across the orders"),
 (56, T, "prakrti-pravrtti-hetu", "Why prakṛti acts at all: puruṣa's two ends"),
 (57, F, "vatsavivrddhinimittam ksirasya ...",
  "Unconscious milk flows for the calf — prakṛti acts for puruṣa"),
 (58, T, "akartrtva-upapatti", "How the non-agent prakṛti is still the doer (driven by guṇas)"),
 (59, F, "rangasya darsayitva nivartate nartaki ...",
  "Dancer retires after the show — prakṛti withdraws once seen"),
 (60, T, "pararthatva-nirnaya", "Prakṛti's other-directedness settled against rival views"),
 (61, T, "prakrti-vairupya", "Why the one prakṛti appears manifold to many puruṣas"),
 (62, F, "tasmad na asmi na me naham iti ...",
  "'I am not, not mine, not I' — knowledge free of residue"),
 (63, T, "viveka-parinati", "Maturing discrimination; puruṣa as pure witness-vision"),
 (64, F, "evam tattvabhyasat ...",
  "By practice of truth: pure, single, final discriminative knowledge"),
 (65, T, "dharma-megha", "Cloud-of-dharma samādhi as penultimate state (with Yoga)"),
 (66, F, "drsta mayety ...",
  "'Seen by me' — prakṛti's exit-speech; 'I am seen' — puruṣa's indifference"),
 (67, T, "samyagjnana-phala", "Fruition: no further birth compulsion for the knower"),
 (68, F, "dharmadinamittam ... prapte sarirabhede ...",
  "On body's fall: isolation absolute; dharma-structures burnt"),
 (69, T, "sastra-upasamhara", "Treatise summed: whereof liberation, how taught"),
 (70, F, "etat pavitram ... kapilasuraye ... pancasikhaya ... isvarakrsnena",
  "Transmission: Kapila → Āsuri → Pañcaśikha → Īśvarakṛṣṇa; seventy verses"),
]


def main():
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    for n, tier, san, tr in K:
        rid = f"SK-K{n:02d}"
        if rid not in by_id:
            p = provenance(tier, f"SK karika {n}; " +
                           ("exact wording" if tier == "verbatim" else
                            "doctrine per SK editions" if tier == "famous-gist" else
                            "outline-level theme; verify vs Larson/Whicher/SARIT"))
            by_id[rid] = {"id": rid, "textId": "SK", "adhyaNotation": f"SK {n}",
                          "sanskrit": normalize_iast(san), "translation": tr,
                          "padarthasMentioned": ["Tattva"], "pramanasInvoked": [],
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": p["verifyAgainst"]}
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)
    sk = [r for r in out if r["textId"] == "SK"]
    print(f"sutras: {len(old)} -> {len(out)} (SK singles: {len([r for r in sk if r['id'].startswith('SK-K')])})")


if __name__ == "__main__":
    main()
