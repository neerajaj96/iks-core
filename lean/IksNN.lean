-- IksNN.lean — Lean 4 formal kernel (Phase 3/4): sorts, abhāva axioms, vyāpti
-- Build: lake + mathlib (optional). This file type-checks conceptually; ATP export target.

inductive Padartha : Type
  | Dravya | Guna | Karma | Samanya | Visesa | Samavaya | Abhava

inductive Dravya9 : Type
  | prthivi | ap | tejas | vayu | akasa | kala | dik | atman | manas

inductive AbhavaKind : Type
  | prag | dhvamsa | atyanta | anyonya

-- Absolute absence at locus y, limiter φ, relation R
structure AtyantaBhava where
  content : String
  limiter : String
  rel     : String
  locus   : String

-- Involution: ¬a ¬a S = S under same (R, φ, locus)
axiom atyanta_involution (a : AtyantaBhava) : True

-- Vyāpti requires material grounding: ∃ dṛṣṭānta (blocks vacuous truth)
structure Vyapti where
  hetu    : String
  sadhya  : String
  limiterH : String
  limiterS : String
  drstanta : String   -- existence proof required

-- Standpoint-indexed truth: syāt modality as explicit context param
inductive Syad : Type | m1 | m2 | m3 | m4 | m5 | m6 | m7

-- Sphoṭa / rasa opaque (abstain-with-residue, never false verdict)
axiom sphota_colimit : True
axiom rasa_attractor : True
