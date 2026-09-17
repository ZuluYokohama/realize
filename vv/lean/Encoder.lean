/-
  Cross-check for the `encoder.finite_case_table` domain (VCMS Example 4.3).

  Lean agrees or disagrees with the finite facts the Python kernel reports, and with
  the verdict it reports for each spec that ships in this domain.

  It does not certify the Python kernel, and it cannot mint a verdict: working out
  what a verdict has to be is not issuing one.
-/

namespace Realize.Encoder

set_option maxRecDepth 4000

/-- The acceptable set A(x) for each input. Empty outside the declared domain. -/
def A : Nat → List Nat
  | 0 => [0, 1]
  | 1 => [1, 2]
  | 2 => [0, 2]
  | _ => []

def dom : List Nat := [0, 1, 2]

def inter (a b : List Nat) : List Nat := a.filter (fun x => b.contains x)

def interAll : List (List Nat) → List Nat
  | [] => []
  | [s] => s
  | s :: rest => inter s (interAll rest)

/-- Every input lands on one code: the encoder of the `three_state` demo. -/
def collapseAll (_ : Nat) : Nat := 0

/-- Every input keeps its own code. -/
def separateAll (x : Nat) : Nat := x

def fibre (e : Nat → Nat) (code : Nat) : List Nat := dom.filter (fun x => e x == code)

def codes (e : Nat → Nat) : List Nat := (dom.map e).eraseDups

/-- Adequate: no fibre asks for two things at once. -/
def adequate (e : Nat → Nat) : Bool :=
  (codes e).all (fun c => !(interAll ((fibre e c).map A)).isEmpty)

/-! ## The UNSAT the checker reports for `three_state` -/

theorem collapse_one_fibre : fibre collapseAll 0 = [0, 1, 2] := by decide
theorem collapse_obstructed : interAll ((fibre collapseAll 0).map A) = [] := by decide
theorem collapse_inadequate : adequate collapseAll = false := by decide

/-! ## The obstruction is three-wise, not pairwise — this is why it is interesting -/

theorem pair_01 : inter (A 0) (A 1) = [1] := by decide
theorem pair_12 : inter (A 1) (A 2) = [2] := by decide
theorem pair_02 : inter (A 0) (A 2) = [0] := by decide

/-! ## The PASS the checker reports for the separating encoder -/

theorem separate_adequate : adequate separateAll = true := by decide

/-- The decoder table in `vv/candidates/encoder_separating.pass.json`. -/
def decoder : Nat → Nat
  | 0 => 0
  | 1 => 1
  | 2 => 0
  | _ => 0

theorem decoder_sound :
    dom.all (fun x => (A x).contains (decoder (separateAll x))) = true := by decide

/-- The COUNTEREXAMPLE table: row `a` emits 2, which A(0) does not accept. -/
def badDecoder : Nat → Nat
  | 0 => 2
  | 1 => 1
  | 2 => 0
  | _ => 0

theorem bad_decoder_violates :
    dom.all (fun x => (A x).contains (badDecoder (separateAll x))) = false := by decide

/-! ## Facts reported back to `scripts/vv.py`, which compares them against the Python kernel. -/

def showList (l : List Nat) : String := String.intercalate "," (l.map toString)

#eval IO.println s!"fact encoder.collapse_adequate={adequate collapseAll}"
#eval IO.println s!"fact encoder.separate_adequate={adequate separateAll}"
#eval IO.println s!"fact encoder.collapse_fibre={showList (fibre collapseAll 0)}"
#eval IO.println s!"fact encoder.obstruction={showList (interAll ((fibre collapseAll 0).map A))}"
#eval IO.println s!"fact encoder.pair_01={showList (inter (A 0) (A 1))}"
#eval IO.println s!"fact encoder.pair_12={showList (inter (A 1) (A 2))}"
#eval IO.println s!"fact encoder.pair_02={showList (inter (A 0) (A 2))}"

/-! ## What the checker has to report

    Everything above is a quantity found *inside* the search. These are the effect:
    the verdict `realize.checker.check_search` must emit for a spec file that ships
    in this repository. `scripts/vv.py` runs the real entry point on the real file
    and compares the two.

    The branch order below is the checker's, transcribed. The numbers fed to it are
    computed here. -/

def subsetsOf : List Nat → List (List Nat)
  | [] => [[]]
  | x :: rest => (subsetsOf rest).flatMap (fun s => [s, x :: s])

/-- Subsets shortest first, matching the order the Python side walks them in. -/
def bySize (l : List Nat) : List (List Nat) :=
  (List.range (l.length + 1)).flatMap (fun k => (subsetsOf l).filter (fun s => s.length == k))

def covers (a b : List Nat) : Bool := a.all (fun x => b.contains x)

/-- Inclusion-minimal B ⊆ dom whose acceptable sets have nothing in common.
    This is the content of the UNSAT, not just its name. -/
def obstructions : List (List Nat) :=
  (bySize dom).foldl
    (fun acc b =>
      if b.isEmpty || acc.any (fun p => covers p b) then acc
      else if (interAll (b.map A)).isEmpty then acc ++ [b] else acc)
    []

/-- The encoders `demos/three_state/spec.json` and `vv/specs/encoder_separating.spec.json`
    put in the library, in file order. -/
def library : List (String × (Nat → Nat)) :=
  [("collapse_all", collapseAll), ("separate_all", separateAll)]

def adequateIds (lib : List (String × (Nat → Nat))) : List String :=
  (lib.filter (fun e => adequate e.2)).map (·.1)

/-- What `_search_encoder` reports, given how many encoders it may read and how many hold. -/
def searchVerdict (budget nEncoders nAdequate : Nat) : String :=
  if budget == 0 then "UNKNOWN/unresolved/zero_budget"
  else if nEncoders > budget then "UNKNOWN/unresolved/incomplete_coverage"
  else if nAdequate == 0 then "UNSAT/proved/no_adequate_encoder"
  else "UNKNOWN/proved/realizations_exist_supply_a_candidate"

/-- `demos/three_state/spec.json`: one encoder is offered, and it collapses. -/
def threeState : String :=
  searchVerdict 100 1 (adequateIds [("collapse_all", collapseAll)]).length

/-- `vv/specs/encoder_separating.spec.json`: the same R, with a separating encoder offered. -/
def separating : String := searchVerdict 100 library.length (adequateIds library).length

/-- `vv/specs/encoder_zero_budget.spec.json`: nothing may be read, so nothing is settled. -/
def zeroBudget : String := searchVerdict 0 1 0

theorem three_state_verdict : threeState = "UNSAT/proved/no_adequate_encoder" := by decide
theorem separating_verdict :
    separating = "UNKNOWN/proved/realizations_exist_supply_a_candidate" := by decide
theorem zero_budget_verdict : zeroBudget = "UNKNOWN/unresolved/zero_budget" := by decide
theorem obstruction_is_the_triple : obstructions = [[0, 1, 2]] := by decide

def showSets (l : List (List Nat)) : String := String.intercalate ";" (l.map showList)

#eval IO.println s!"fact verdict.three_state={threeState}"
#eval IO.println s!"fact verdict.three_state.obstructions={showSets obstructions}"
#eval IO.println s!"fact verdict.encoder_separating={separating}"
#eval IO.println s!"fact verdict.encoder_separating.adequate_encoders={String.intercalate ";" (adequateIds library)}"
#eval IO.println s!"fact verdict.encoder_zero_budget={zeroBudget}"

end Realize.Encoder
