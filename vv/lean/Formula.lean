/-
  Cross-check for the `formula.bounded_coeff_template` domain (VCOS §8.1 / Table 2).

  Lean agrees or disagrees with the finite facts the Python kernel reports.
  It does not certify the Python kernel, and it cannot mint a verdict.

  Every coefficient in D = {-1, -1/2, 0, 1/2, 1} is a whole number of halves, so
  the template is carried here in halves: `h` stands for the value `h/2`. That
  keeps the arithmetic exact in core Lean, with no rational type and no Mathlib.
-/

namespace Realize.Formula

-- the template has 625 members; kernel reduction walks the whole list
set_option maxRecDepth 8000

/-- Twice a coefficient. `D` is {-1, -1/2, 0, 1/2, 1} doubled. -/
abbrev Half := Int

def D : List Half := [-2, -1, 0, 1, 2]

structure Coeffs where
  h0 : Half
  h1 : Half
  h2 : Half
  h3 : Half
deriving DecidableEq, Repr, BEq

/-- The declared finite class: every tuple the bounded template can name. -/
def template : List Coeffs :=
  D.flatMap fun a => D.flatMap fun b => D.flatMap fun c => D.map fun d => ⟨a, b, c, d⟩

inductive Phrase where
  | larger | smaller | midpoint | absdiff
deriving DecidableEq, Repr

/-- `c0 + c1·a + c2·b + c3·|a-b|` restricted to a ≥ b, as an affine form in (1, a, b). -/
def planeA (c : Coeffs) : Half × Half × Half := (c.h0, c.h1 + c.h3, c.h2 - c.h3)

/-- The same form restricted to b ≥ a. -/
def planeB (c : Coeffs) : Half × Half × Half := (c.h0, c.h1 - c.h3, c.h2 + c.h3)

def targetA : Phrase → Half × Half × Half
  | .larger   => (0, 2, 0)
  | .smaller  => (0, 0, 2)
  | .midpoint => (0, 1, 1)
  | .absdiff  => (0, 2, -2)

def targetB : Phrase → Half × Half × Half
  | .larger   => (0, 0, 2)
  | .smaller  => (0, 2, 0)
  | .midpoint => (0, 1, 1)
  | .absdiff  => (0, -2, 2)

def realizes (c : Coeffs) (p : Phrase) : Bool :=
  planeA c == targetA p && planeB c == targetB p

def solutions (p : Phrase) : List Coeffs := template.filter (realizes · p)

/-- The affine sub-template: the |a-b| leg is not available. -/
def affine : List Coeffs := template.filter (fun c => c.h3 == 0)

/-! ## Counts the Python side freezes in tests/test_counts.py -/

theorem template_card : template.length = 625 := by decide
theorem affine_card : affine.length = 125 := by decide

/-! ## Each phrase is realized by exactly one tuple, and it is the reported one -/

theorem larger_unique : solutions .larger = [⟨0, 1, 1, 1⟩] := by decide
theorem smaller_unique : solutions .smaller = [⟨0, 1, 1, -1⟩] := by decide
theorem midpoint_unique : solutions .midpoint = [⟨0, 1, 1, 0⟩] := by decide
theorem absdiff_unique : solutions .absdiff = [⟨0, 0, 0, 2⟩] := by decide

/-! ## The UNSAT the checker reports for the affine-only spec -/

theorem affine_larger_empty : affine.filter (realizes · .larger) = [] := by decide

/-! ## Facts reported back to `scripts/vv.py`, which compares them against the Python kernel.
    A proof nobody compares to anything corroborates nothing. -/

def showHalves (cs : List Coeffs) : String :=
  String.intercalate ";" (cs.map fun c => s!"{c.h0},{c.h1},{c.h2},{c.h3}")

#eval IO.println s!"fact formula.template_card={template.length}"
#eval IO.println s!"fact formula.affine_card={affine.length}"
#eval IO.println s!"fact formula.larger_count={(solutions .larger).length}"
#eval IO.println s!"fact formula.smaller_count={(solutions .smaller).length}"
#eval IO.println s!"fact formula.midpoint_count={(solutions .midpoint).length}"
#eval IO.println s!"fact formula.absdiff_count={(solutions .absdiff).length}"
#eval IO.println s!"fact formula.affine_larger_count={(affine.filter (realizes · .larger)).length}"
#eval IO.println s!"fact formula.larger_solution={showHalves (solutions .larger)}"
#eval IO.println s!"fact formula.smaller_solution={showHalves (solutions .smaller)}"
#eval IO.println s!"fact formula.midpoint_solution={showHalves (solutions .midpoint)}"
#eval IO.println s!"fact formula.absdiff_solution={showHalves (solutions .absdiff)}"

end Realize.Formula
