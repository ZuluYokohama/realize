/-
  Cross-check for the `term_series.typed_grid` domain (IGVF-CTS §7.1).

  Lean agrees or disagrees with the finite facts the Python kernel reports, and with
  the verdict it reports for each spec that ships in this domain.

  It does not certify the Python kernel, and it cannot mint a verdict: working out
  what a verdict has to be is not issuing one.
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

/-! ## What the checker has to report

    Everything above is a quantity found *inside* the search. These are the effect:
    the verdict `realize.checker.check_search` must emit for a spec file that ships
    in this repository. `scripts/vv.py` runs the real entry point on the real file
    and compares the two.

    The branch order below is the checker's, transcribed. The class is enumerated
    here rather than assumed: the checker reports `realizations_exist` only after
    walking every term the grammar can name, so Lean walks them too. -/

inductive Op where
  | extractOp | render2Op
deriving DecidableEq, Repr, BEq

inductive Ty where
  | grid | mask
deriving DecidableEq, Repr, BEq

def ops : List Op := [.extractOp, .render2Op]

def sig : Op → Ty × Ty
  | .extractOp => (.grid, .mask)
  | .render2Op => (.mask, .grid)

def ofLength : Nat → List (List Op)
  | 0 => [[]]
  | n + 1 => (ofLength n).flatMap (fun s => ops.map (fun o => s ++ [o]))

/-- Every term the grammar can name up to `bound.max_term_size` = 4. -/
def terms : List (List Op) := (List.range 5).flatMap ofLength

/-- `compose.type_of_prefix`: a term's type, or none where a step does not fit. -/
def typeOf : List Op → Option (Ty × Ty)
  | [] => some (.grid, .grid)
  | o :: rest =>
      rest.foldl
        (fun acc o' =>
          match acc with
          | none => none
          | some (i, out) =>
              let s := sig o'
              if s.1 == out then some (i, s.2) else none)
        (some (sig o))

def apply : Op → Grid → Grid
  | .extractOp => extract
  | .render2Op => render2

/-- Ill-typed terms and terms that are not `Grid → Grid` produce nothing to judge. -/
def evalTerm (t : List Op) (g : Grid) : Option Grid :=
  match typeOf t with
  | some (.grid, .grid) => some (t.foldl (fun acc o => apply o acc) g)
  | _ => none

/-- R: the output is the recolouring, and it moved no cell on or off. -/
def meetsR (x y : Grid) : Bool := y == goal x && extract y == extract x

def valid (x : Grid) : List (List Op) :=
  terms.filter (fun t => match evalTerm t x with
                         | none => false
                         | some y => meetsR x y)

/-- What `_search_grid` reports. `histogramBlocks` is K's pre-check, which runs first. -/
def searchVerdict (budget card nValid : Nat) (histogramBlocks : Bool) : String :=
  if budget == 0 then "UNKNOWN/unresolved/zero_budget"
  else if histogramBlocks then "UNSAT/proved/histogram_contradicts_R"
  else if card > budget then "UNKNOWN/unresolved/incomplete_coverage"
  else if nValid == 0 then "UNSAT/proved/no_typed_realization"
  else "UNKNOWN/proved/realizations_exist_supply_a_candidate"

/-- `demos/grid_recolor/spec.json`: K is null, so nothing blocks the search. -/
def recolor : String := searchVerdict 100 terms.length (valid X).length false

/-- `vv/specs/grid_preserve_histogram.spec.json`: K asks the colour counts to be kept. -/
def preserveHistogram : String :=
  searchVerdict 100 terms.length (valid X).length (histogram X != histogram (goal X))

/-- `vv/specs/grid_zero_budget.spec.json`. -/
def zeroBudget : String := searchVerdict 0 terms.length 0 false

theorem term_count : terms.length = 31 := by decide
theorem two_terms_realize : (valid X).length = 2 := by decide
theorem recolor_verdict :
    recolor = "UNKNOWN/proved/realizations_exist_supply_a_candidate" := by decide
theorem preserve_histogram_verdict :
    preserveHistogram = "UNSAT/proved/histogram_contradicts_R" := by decide
theorem zero_budget_verdict : zeroBudget = "UNKNOWN/unresolved/zero_budget" := by decide

#eval IO.println s!"fact verdict.grid_recolor={recolor}"
#eval IO.println s!"fact verdict.grid_recolor.n_valid={(valid X).length}"
#eval IO.println s!"fact verdict.grid_preserve_histogram={preserveHistogram}"
#eval IO.println s!"fact verdict.grid_zero_budget={zeroBudget}"

end Realize.Grid
