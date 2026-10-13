"""v2.7 Phase 5: assign verified-live corpusRefs to all 41 texts.

Every URL below was HEAD-checked live on 2026-10-13 before storing
(see tools/linkcheck.py --audit run + --check self-verification).
YuktiB: no stable e-text found -> noStableEtext.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
A = "https://archive.org/details/"
D = "2026-10-13"

REFS: dict[str, dict] = {
 "NS": {"edition": "https://www.in.yoga/en/nyaya-sutra", "archiveOrg": A + "NyayaSutrasOfGautama"},
 "VS": {"archiveOrg": A + "vaiesikasutrasof0000kana"},
 "SK": {"gretil": "https://raw.githubusercontent.com/sanskrit-texts/gretil-corpus/main/1_sanskr/sa_IzvarakRSNa-sAMkhyakArikA.xml",
        "archiveOrg": "https://ia600801.us.archive.org/15/items/samkhya-karika_202307/Samkhya-Karika_text.pdf"},
 "YS": {"gretil": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_pataJjali-yogasUtra.htm"},
 "MMK": {"archiveOrg": A + "2226454Nagarjuna"},
 "PV": {"archiveOrg": A + "dharmakirtiisenlightenmentpossiblepramanasiddhichapterofdharmakirtispramanavartt_698_K",
        "note": "Pramanasiddhi chapter translation; full PV Sanskrit pending"},
 "TS": {"archiveOrg": A + "in.ernet.dli.2015.210857", "note": "Vol. II; Vol. I: in.ernet.dli.2015.311023"},
 "TArthaS": {"archiveOrg": A + "in.ernet.dli.2015.548689"},
 "SV": {"archiveOrg": A + "SlokavarttikaNyayaratnakara"},
 "BS": {"archiveOrg": A + "brahmasutrasbda00cgoog", "note": "Thibaut translation with Sankara comm."},
 "NM": {"archiveOrg": A + "in.ernet.dli.2015.311116"},
 "KKK": {"archiveOrg": A + "ksu.1697.khandanakhandakh0000pand"},
 "TC": {"archiveOrg": A + "tattvacintamanivyakhyamathuranthaed.kamakhyanathatrakavagishavol2anumitibadhaasiaticsocietycomp_926_A",
        "note": "Mathuranatha comm., Anumana vol."},
 "Nyaymrta": {"archiveOrg": A + "Wkjf_nyayamrita-tarangini-by-vyasa-ramacharya-damaged-beginning-missing-sanskrit-vasi",
              "note": "Tarini comm.; scan damaged at start"},
 "AdvSiddhi": {"archiveOrg": A + "advaitasiddhi"},
 "SataD": {"archiveOrg": A + "in.ernet.dli.2015.405072"},
 "SDS": {"archiveOrg": A + "dli.ernet.242145"},
 "VP": {"archiveOrg": A + "vedantaparibhasha-CGV-PSS-1504-0717"},
 "PP": {"archiveOrg": A + "pramana-paddhati-of-sri-jayatirtha-with-commentaries-of-vijayindra-tirthavedesha"},
 "Astadh": {"edition": "https://ashtadhyayi.com/",
            "wikisource": "https://sa.wikisource.org/wiki/अष्टाध्यायी",
            "sanskritdocs": "https://sanskritdocuments.org/learning_tools/ashtadhyayi"},
 "VPakya": {"archiveOrg": A + "VP2AmbakartriRSarmaReprint1980", "note": "Kanda 2 with Ambakartri"},
 "KavyaP": {"archiveOrg": A + "iExk_mammata-kavyaprakasha-vol-2-ullas-7-10-no.-122-oriental-research-institute-mysore"},
 "DhvA": {"archiveOrg": A + "tqqk_dhvanyaloka-of-anandavardhana-by-sri-badarinatha-sharma-with-the-didhiti-comment"},
 "Arya": {"archiveOrg": A + "TheAryabhatiyaOfAryabhata"},
 "YuktiB": {"noStableEtext": True,
            "note": "Sarma Hindustan Book Agency critical edition is print-only; no stable e-text located"},
 "PS": {"archiveOrg": A + "dignangapramanasamuccayachapter1earnststeinkelner_536_P",
        "note": "Ch.1 translation (Steinkellner); full Sanskrit pending"},
 "NK": {"archiveOrg": A + "GxAi_nyaya-kusumanjali-of-udayanacharya-with-commentary-by-bachcha-jha-kashi-sanskrit"},
 "JS": {"archiveOrg": A + "dli.ernet.170066", "note": "Jha English comm.; Sandal translation alt: mimamsasutra00jaimuoft"},
 "BP": {"archiveOrg": A + "bhasha-pariccheda", "note": "With Muktavali"},
 "VedSara": {"archiveOrg": A + "vedantasara-of-sadananda-dr.-rakesh-shastri_202108"},
 "KAd": {"archiveOrg": A + "gmme_kavyadarsha-commentary-sudarshana-sanskrit-hindi-commentator-dharmendra-kum"},
 "KAS": {"archiveOrg": A + "bOmY_kavyalankara-sutra-vrittih-by-shri-vamana-1892-shri-jeevananda-vidya-sagar-bhattacharya"},
 "AKB": {"archiveOrg": A + "ooch_abhidharmakosha-karika-chos-mngon-pai-mdzod-kyi-tshig-leur-byas-pa-tibetan-",
         "note": "Tibetan materials; Sanskrit Kośa pending"},
 "Natya": {"archiveOrg": A + "osbq-bharata-the-natyashastra-by-kapila-vatsyayan-natya"},
 "BSS": {"archiveOrg": A + "Brahmasphutasiddhanta_Vol_3", "note": "Vol. 3 Sanskrit"},
 "SSiro": {"archiveOrg": A + "SiddhantaShiromani837GhaAlm4Shlf5DevanagariJyotish"},
 "ASang": {"archiveOrg": A + "arthasangraha"},
 "Sribhasya": {"archiveOrg": A + "Sribhashya_of_Ramanuja-VS_Abhyankar_Parts_1_2"},
 "TattvaSank": {"archiveOrg": A + "20240409_20240409_1334"},
 "NBindu": {"archiveOrg": A + "dli.pahar.1785", "note": "Tibetan translation; Sanskrit pending"},
 "SyadManj": {"archiveOrg": A + "in.ernet.dli.2015.485441"},
}

NOSTABLE = {"YuktiB"}


def main():
    texts = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
    assert len(texts) == 41, len(texts)
    for t in texts:
        spec = REFS[t["id"]]
        refs = {k: v for k, v in spec.items() if k not in ("noStableEtext", "note")}
        t["corpusRefs"] = refs
        if spec.get("note"):
            t["refNote"] = spec["note"]
        if t["id"] in NOSTABLE:
            t["noStableEtext"] = True
        t["refsChecked"] = D
    write_json(ROOT / "data" / "texts.json", texts)
    mirror_to_docs(ROOT, "texts.json", texts)
    print(f"texts with refs: {sum(1 for t in texts if t.get('corpusRefs'))}/41; "
          f"noStableEtext: {sorted(NOSTABLE)}")


if __name__ == "__main__":
    main()
