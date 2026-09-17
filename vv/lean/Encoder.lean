/-
  Cross-check for the `encoder.finite_case_table` domain (VCMS Example 4.3).

  Lean agrees or disagrees with the finite facts the Python kernel reports.
  It does not certify the Python kernel, and it cannot mint a verdict.
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

end Realize.Encoder
