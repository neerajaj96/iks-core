// IKS-MAM Phase 1 — TypeScript type definitions (mirrors schema/iks-schema.json)
export type Darsana =
  | "Carvaka" | "Bauddha-Sautrantika" | "Bauddha-Yogacara" | "Bauddha-Madhyamaka"
  | "Jaina-Svetambara" | "Jaina-Digambara" | "Samkhya" | "Yoga" | "Nyaya" | "Vaisesika"
  | "Purva-Mimamsa" | "Advaita" | "Visistadvaita" | "Dvaita" | "Vyakarana" | "Sahitya" | "Ganitashastra";

export type PramanaKind = "Pratyaksa" | "Anumana" | "Sabda" | "Upamana" | "Arthapatti" | "Anupalabdhi";
export type AbhavaKind = "Pragabhava" | "Dhvamsabhava" | "Atyantabhava" | "Anyonyabhava";
export type HetvabhasaKind = "Savyabhicara" | "Viruddha" | "Satpratipaksa" | "Asiddha" | "Badhita" | "none";
export type KathaKind = "Vada" | "Jalpa" | "Vitanda";
export type VadaEdgeKind = "khandana" | "mandana" | "purvapaksa" | "uttarapaksa" | "samanvaya" | "uddhara";

export interface Authority { id: string; name: string; datesCE: [number, number] | null; tradition: Darsana; }
export interface Text {
  id: string; titleSanskrit: string; titleEnglish: string;
  authorIds: string[]; rootTextId?: string;
  layer: "sutra"|"bhashya"|"varttika"|"tika"|"khandana"|"mandana"|"sangraha"|"prakarana";
  corpusRefs?: { sarit?: string; gretil?: string; wikisource?: string; archiveOrg?: string };
  darsana: Darsana;
}
export interface SutraNode {
  id: string; textId: string; adhyaNotation: string;
  sanskrit: string; translation: string;
  padarthasMentioned: string[]; pramanasInvoked: PramanaKind[];
  logicalForm?: string;
  confidence?: "verbatim" | "famous-gist" | "topic-digest";
  sourceNote?: string; verifyAgainst?: string;
}
export interface SastricTerm {
  id: string; sanskrit: string; iast: string;
  darsanaScope: Darsana[]; definitionSutras: string[];
  ontologicalSort: "Dravya"|"Guna"|"Karma"|"Samanya"|"Visesa"|"Samavaya"|"Abhava"|"Tattva"|"Pramana"|"Prameya"|"Padartha16"|"Rasa"|"Dhvani"|"Sabda"|"Artha"|"Other";
  formalSymbol: string; nonFormalizableResidue?: string;
}
export interface PramanaDef {
  kind: PramanaKind; acceptedBy: Darsana[]; rejectedBy: Darsana[];
  lakshanaSutraId: string; validationFunction: string;
}
export interface Inference {
  id: string; school: Darsana; form: "Nyaya-5"|"Buddhist-2"|"Jaina-Trairupya";
  paksa: string; sadhya: string; hetu: string; drstanta?: string;
  vyapti: string; hetvabhasa: HetvabhasaKind;
  members: { pratijna?: string; hetu?: string; udaharana?: string; upanaya?: string; nigamana?: string };
}
export interface ArgumentNode {
  id: string; textId: string; sutraRefs: string[];
  siddhanta: string; purvapaksaTargetId?: string;
  katha: KathaKind; siddhantaKind?: "Sarvatantra"|"Pratitantra"|"Adhikarana"|"Abhyupagama";
}
export interface VadaEdge {
  id: string; from: string; to: string; kind: VadaEdgeKind;
  fallacyCharged: HetvabhasaKind | "Chhala" | "Jati" | "Nigrahasthana" | "none";
  refutationTextId: string; locus: string; weight: number;
}
export interface Cognition {
  id: string; content: string; pramana: PramanaKind; state: string;
  valid: 0|1; standpointQualifier: string;
}
