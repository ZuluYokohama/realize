/-
  Cross-check for the `term_series.guarded_integer_sequence` domain (VCOS §8.3).

  Lean agrees or disagrees with the finite facts the Python kernel reports, and with
  the verdict it reports for each spec that ships in this domain.

  It does not certify the Python kernel, and it cannot mint a verdict: working out
  what a verdict has to be is not issuing one.

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

/-! ## What the checker has to report

    Everything above is a quantity found *inside* the search. These are the effect:
    the verdict `realize.checker.check_search` must emit for a spec file that ships
    in this repository. `scripts/vv.py` runs the real entry point on the real file
    and compares the two.

    The branch order below is the checker's, transcribed. The numbers fed to it are
    computed here. `_search_series` also refuses a negative target; `Nat` cannot
    name one, so that branch is not modelled and not claimed. -/

/-- What `_search_series` reports, given the guard, the class size and what it finds. -/
def searchVerdict (budget cap target card nValid : Nat) : String :=
  if budget == 0 then "UNKNOWN/unresolved/zero_budget"
  else if target > cap then "UNSAT/proved/target_outside_invariant"
  else if card > budget then "UNKNOWN/unresolved/incomplete_coverage"
  else if nValid == 0 then "UNSAT/proved/no_valid_sequence"
  else "UNKNOWN/proved/realizations_exist_supply_a_candidate"

/-- `vv/specs/series_seven.spec.json`. -/
def seven : String :=
  searchVerdict 10000 8 7 (upTo repertoire 4).length (valid repertoire 8 7 4).length

/-- `vv/specs/series_even_repertoire.spec.json`: 7 is odd and the steps are not. -/
def evenRepertoireSpec : String :=
  searchVerdict 10000 8 7 (upTo evenRepertoire 4).length (valid evenRepertoire 8 7 4).length

/-- `vv/specs/series_target_nine.spec.json`: R asks for a state the invariant forbids. -/
def targetNine : String :=
  searchVerdict 10000 8 9 (upTo repertoire 4).length (valid repertoire 8 9 4).length

/-- `vv/specs/series_zero_budget.spec.json`. -/
def zeroBudget : String := searchVerdict 0 8 7 0 0

theorem seven_verdict :
    seven = "UNKNOWN/proved/realizations_exist_supply_a_candidate" := by decide
theorem even_repertoire_verdict :
    evenRepertoireSpec = "UNSAT/proved/no_valid_sequence" := by decide
theorem target_nine_verdict :
    targetNine = "UNSAT/proved/target_outside_invariant" := by decide
theorem zero_budget_verdict : zeroBudget = "UNKNOWN/unresolved/zero_budget" := by decide

#eval IO.println s!"fact verdict.series_seven={seven}"
#eval IO.println s!"fact verdict.series_seven.n_valid={(valid repertoire 8 7 4).length}"
#eval IO.println s!"fact verdict.series_seven.min_len={((valid repertoire 8 7 4).map List.length).min?.getD 0}"
#eval IO.println s!"fact verdict.series_even_repertoire={evenRepertoireSpec}"
#eval IO.println s!"fact verdict.series_even_repertoire.n_valid={(valid evenRepertoire 8 7 4).length}"
#eval IO.println s!"fact verdict.series_target_nine={targetNine}"
#eval IO.println s!"fact verdict.series_zero_budget={zeroBudget}"

end Realize.Series
