/-
  Cross-check for the `term_series.guarded_integer_sequence` domain (VCOS §8.3).

  Lean agrees or disagrees with the finite facts the Python kernel reports.
  It does not certify the Python kernel, and it cannot mint a verdict.

  This is the grammar that shipped no spec before `vv/specs/series_seven.spec.json`.
-/

namespace Realize.Series

set_option maxRecDepth 20000

inductive Op where
  | add1 | add2 | add3 | double
deriving DecidableEq, Repr, BEq

/-- One guarded step. The guard is the invariant `0 ≤ q ≤ cap`; `Nat` carries the lower half. -/
def step (cap q : Nat) : Op → Option Nat
  | .add1   => let r := q + 1; if r ≤ cap then some r else none
  | .add2   => let r := q + 2; if r ≤ cap then some r else none
  | .add3   => let r := q + 3; if r ≤ cap then some r else none
  | .double => let r := 2 * q; if r ≤ cap then some r else none

/-- Walk a series. A blocked step is a dead series, not a clamped one. -/
def run (cap : Nat) : Nat → List Op → Option Nat
  | q, [] => some q
  | q, o :: rest =>
      match step cap q o with
      | none => none
      | some q' => run cap q' rest

def ofLength (ops : List Op) : Nat → List (List Op)
  | 0 => [[]]
  | n + 1 => (ofLength ops n).flatMap (fun s => ops.map (fun o => s ++ [o]))

/-- Every series the grammar can name up to the horizon, shortest first. -/
def upTo (ops : List Op) (horizon : Nat) : List (List Op) :=
  (List.range (horizon + 1)).flatMap (ofLength ops)

def repertoire : List Op := [.add1, .add3, .double]
def evenRepertoire : List Op := [.add2, .double]

def valid (ops : List Op) (cap target horizon : Nat) : List (List Op) :=
  (upTo ops horizon).filter (fun s => run cap 0 s == some target)

/-! ## Counts the Python side freezes in tests/test_counts.py -/

theorem syntactic_121 : (upTo repertoire 4).length = 121 := by decide
theorem syntactic_31 : (upTo evenRepertoire 4).length = 31 := by decide

/-! ## The PASS and the COUNTEREXAMPLE the checker reports for `series_seven` -/

theorem witness_reaches_seven : run 8 0 [.add3, .double, .add1] = some 7 := by decide
theorem counterexample_is_blocked : run 8 0 [.add3, .double, .double] = none := by decide

/-! ## Ten series reach 7, none shorter than three steps -/

theorem seven_has_ten : (valid repertoire 8 7 4).length = 10 := by decide
theorem seven_needs_three :
    (valid repertoire 8 7 4).filter (fun s => s.length < 3) = [] := by decide

/-! ## The two UNSATs: an even repertoire, and a target above the cap -/

theorem even_repertoire_empty : valid evenRepertoire 8 7 4 = [] := by decide
theorem target_nine_empty : valid repertoire 8 9 4 = [] := by decide

/-! ## Facts reported back to `scripts/vv.py`, which compares them against the Python kernel. -/

def showSeq (s : List Op) : String :=
  String.intercalate "," (s.map fun o => match o with
    | .add1 => "add1" | .add2 => "add2" | .add3 => "add3" | .double => "double")

#eval IO.println s!"fact series.syntactic_121={(upTo repertoire 4).length}"
#eval IO.println s!"fact series.syntactic_31={(upTo evenRepertoire 4).length}"
#eval IO.println s!"fact series.seven_valid={(valid repertoire 8 7 4).length}"
#eval IO.println s!"fact series.even_valid={(valid evenRepertoire 8 7 4).length}"
#eval IO.println s!"fact series.nine_valid={(valid repertoire 8 9 4).length}"
#eval IO.println s!"fact series.seven_min_len={((valid repertoire 8 7 4).map List.length).min?.getD 0}"
/-- The shortest valid series, in enumeration order — derived here, not written down. -/
def minValid : List (List Op) :=
  let vs := valid repertoire 8 7 4
  let m := (vs.map List.length).min?.getD 0
  vs.filter (fun s => s.length == m)

#eval IO.println s!"fact series.witness={showSeq (minValid.headD [])}"

end Realize.Series
