/-
  Cross-check for the `term_series.typed_grid` domain (IGVF-CTS §7.1).

  Lean agrees or disagrees with the finite facts the Python kernel reports.
  It does not certify the Python kernel, and it cannot mint a verdict.
-/

namespace Realize.Grid

set_option maxRecDepth 4000

abbrev Grid := List (List Nat)

/-- The grid in `demos/grid_recolor/spec.json`. -/
def X : Grid := [[0, 3, 0], [4, 4, 0], [0, 0, 5]]

/-- `Extract : Grid → Mask`. -/
def extract (g : Grid) : Grid := g.map (fun r => r.map (fun v => if v == 0 then 0 else 1))

/-- `Render2 : Mask → Grid`. -/
def render2 (g : Grid) : Grid := g.map (fun r => r.map (fun v => if v == 0 then 0 else 2))

/-- What R asks for: every non-background cell becomes colour 2, background stays put. -/
def goal (g : Grid) : Grid := g.map (fun r => r.map (fun v => if v == 0 then 0 else 2))

def cells (g : Grid) : List Nat := g.flatMap id

def palette : List Nat := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def histogram (g : Grid) : List (Nat × Nat) :=
  palette.map (fun v => (v, ((cells g).filter (fun c => c == v)).length))

/-! ## The PASS the checker reports for `Extract, Render2` -/

theorem recolor_meets_R : render2 (extract X) = goal X := by decide

/-! ## The COUNTEREXAMPLE the checker reports for the empty series -/

theorem empty_series_fails : X ≠ goal X := by decide

/-! ## The UNSAT: K asks the colour counts to be kept, R asks them to change -/

theorem histogram_contradicts_R : histogram X ≠ histogram (goal X) := by decide

/-- Concretely: three cells change colour, so no series can satisfy both clauses. -/
theorem histogram_witness :
    histogram X = [(0, 5), (1, 0), (2, 0), (3, 1), (4, 2), (5, 1),
                   (6, 0), (7, 0), (8, 0), (9, 0)] := by decide

theorem goal_histogram_witness :
    histogram (goal X) = [(0, 5), (1, 0), (2, 4), (3, 0), (4, 0), (5, 0),
                          (6, 0), (7, 0), (8, 0), (9, 0)] := by decide

/-! ## Facts reported back to `scripts/vv.py`, which compares them against the Python kernel. -/

def showHist (g : Grid) : String :=
  String.intercalate "," ((histogram g).map fun p => toString p.2)

#eval IO.println s!"fact grid.recolor_meets_R={render2 (extract X) == goal X}"
#eval IO.println s!"fact grid.empty_series_meets_R={X == goal X}"
#eval IO.println s!"fact grid.hist_input={showHist X}"
#eval IO.println s!"fact grid.hist_goal={showHist (goal X)}"

end Realize.Grid
