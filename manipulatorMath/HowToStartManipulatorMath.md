# HowToStart — manipulatorMath

This is the curriculum's first **pure-math / OpenMaya-API** demo. There is **no
Maya scene to build** — not a single DAG node is created, queried, or modified.
The whole file is **geometry arithmetic**: planes, lines, and degree↔radian
conversion, implemented with the `maya.OpenMaya` (API 1.0) `MPoint` / `MVector`
types. Think of it as the math foundation that every "click-drag in the viewport
to place something in 3D" tool has to do behind the scenes.

It is unusual in two ways that shape this guide:

1. **It is the verbatim official Autodesk example** (the copyright header is
   Autodesk's). Unlike `introduction` / `gearCreator` / `objectRenamer` / `tweener`
   / `controllerLibrary` / `lightManager`, there is **no `_2027` sibling** —
   `manipulatorMath.py` *is* the modern original. There is nothing to modernize,
   so this guide targets it directly (same situation as `fileDialog`).

2. **It is *not* the pure "definitions-only" common case.** It *does* ship a
   runnable self-test — `testModule()` behind a `if __name__ == "__main__":`
   guard — so "How to Run" has a real first step: just invoke the self-test.
   That said, `testModule()` only exercises **two of the four** pieces
   (`degreeRadianConverter` and `lineMath`); `planeMath` and `maxOfAbsThree` are
   **completely untested**. Driving them by hand is where the real learning (and
   the real bugs) live.

⚠️ **You need Maya's Python** to run this — the very first line of real code is
`import maya.OpenMaya`, which only resolves inside a Maya install. Use the
**Script Editor**, or `mayapy` from the command line. You do **not** need any
particular scene open.

---

## Files in this demo

| File                 | What it is                                                                                  | Run it how                                                       |
|----------------------|---------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| `manipulatorMath.py` | The demo — 3 math classes (`planeMath`, `lineMath`, `degreeRadianConverter`), `maxOfAbsThree`, and `testModule()`. Pure math, API 1.0. | Script Editor: `import manipulatorMath; manipulatorMath.testModule()`, or `mayapy manipulatorMath.py`. |
| `README.md`          | The book's narrative: per-class math walk-through, "why this matters for manipulators", exercises, pitfalls. | Read for context — but verify its claims against the `.py` (see divergences below). |

> **`_2027` convention — not needed here.** In the other demos `foo_2027.py` is
> the verified Python-3 copy. `manipulatorMath` has **no `_2027` sibling**:
> `manipulatorMath.py` is the verbatim Autodesk API 1.0 original. Its only
> Python-2 leftovers are `from __future__ import division` and
> `from builtins import object`, both harmless no-ops on Maya 2027's Python 3.
> There is nothing to modernize, so this guide targets `manipulatorMath.py`
> directly.

## Prerequisites

- Python classes (`class`, `__init__`, `self`) — any Python tutorial.
- Comfortable with basic linear algebra: a dot product, a normalized
  (unit-length) vector, the plane equation `ax + by + cz + d = 0`.
- What `OpenMaya.MPoint` and `OpenMaya.MVector` are (3-component point and
  vector types). The README's prerequisite table points at
  `cameraMessageCmd/cameraMessageTest/README.md` for API 1.0 basics.
- ⚠️ **Maya's Python interpreter** (`mayapy` or the Script Editor) — required
  only because the file imports `maya.OpenMaya`. The *arithmetic itself* is
  plain geometry; the verified expected outputs below were computed by hand and
  with a pure-Python reimplementation, not inside Maya.

---

## What the code actually does

Four independent pieces. Map of the file:

### `planeMath` — an infinite plane + ray-vs-plane intersection

A plane is `ax + by + cz + d = 0`, where `(a, b, c)` is the (unit) **normal**
and `d` is derived from any known point on the plane.

| Member | Signature | What it does |
|--------|-----------|--------------|
| `setPlane(pointOnPlane, normalToPlane)` | mutator | Normalizes the normal, stores `self.a/b/c` from it, computes `self.d = -(a*px + b*py + c*pz)`. |
| `intersect(linePoint, lineDirection)` | → `(bool, MPoint)` | Casts a ray (point + direction) at the plane; returns `(True, hitPoint)` or `(False, MPoint())` if "parallel". |

> ⚠️ **Verified bug in `intersect`.** The parallel test is
> `if denominator < .00001:`. A ray whose direction has a **negative** dot with
> the normal (i.e. pointing against the normal — the most common case: a
> downward view ray hitting the ground plane) has `denominator < 0`, which is
> `< .00001`, so it is **wrongly reported as "no hit"**. The correct test is
> `if abs(denominator) < .00001:`. Verified: a straight-down ray at the ground
> plane gives `denominator = -1.0` and the current code returns `(False, …)`.
> See Q&A and Advanced Directions.
>
> ⚠️ **`__init__` is dead code.** It writes `a = 0; b = 0; c = 0; d = 0` — those
> are **local variables**, not `self.a` etc. The real attributes are the class
> defaults (`None`) until `setPlane` runs. The constructor does nothing useful.

### `lineMath` — an infinite line + closest-point-on-line

| Member | Signature | What it does |
|--------|-----------|--------------|
| `setLine(linePoint, lineDirection)` | mutator | Stores `self.point`, normalizes and stores `self.direction`. |
| `closestPoint(toPoint)` | → `(bool, MPoint)` | Projects `toPoint` onto the line; always returns `(True, closest)`. |

The line `t = self.direction * (toPoint - self.point)` is a **dot product**
(`MVector * MVector` → scalar in API 1.0), and `self.direction * t` is a
**scalar scale** (`MVector * float` → `MVector`). Same `*`, two meanings — read
both sides.

### `degreeRadianConverter` — trivial but indispensable

`degreesToRadians(d) = d * (M_PI/180)` and `radiansToDegrees(r) = r * (180/M_PI)`,
with `M_PI` stored as a class attribute instead of `import math`. Maya's API
stores angles in **radians**; the channel box shows **degrees**.

### `maxOfAbsThree(a, b, c)` — dominant-axis picker (module function, not a class)

Returns whichever input has the largest absolute value, **preserving its sign**
(`-10, 3, 4 → -10`). Used by manipulators to pick a dominant axis.

> ⚠️ **Verified tie bug.** The comparisons are strict (`aa > ab`, `ab > aa`), so
> a tie for largest-abs is unresolved and the function falls through to
> `return c`. Verified: `maxOfAbsThree(-10, 10, 4)` returns **`4`**, not `±10`.

### `testModule()` — the built-in self-test

Exercises `degreeRadianConverter` (both directions) and `lineMath.closestPoint`
with `point=(0,1,0)`, `direction=(1,1,0)`, `toPoint=(3,0,0)`. It does **not**
touch `planeMath` or `maxOfAbsThree` at all.

---

## How to Create the Test Maya Scene

⚠️ **There is no Maya scene for this demo — and that is the point.** Every prior
demo needed you to build objects, select things, or key channels. This one needs
**none of that**: it is pure geometry on `MPoint` / `MVector` values you pass in.
Nothing appears in the viewport or the Outliner, because no nodes are created.

The "scene" is just the **input values** you choose. To follow the run steps
below, you only need to know these API 1.0 constructors:

```python
import maya.OpenMaya as om      # the file uses the long name `OpenMaya`
# A point in space (homogeneous w=1 by default):
P  = om.MPoint(0.0, 1.0, 0.0)
# A direction / offset (w=0):
D  = om.MVector(1.0, 1.0, 0.0)
Q  = om.MPoint(3.0, 0.0, 0.0)
```

No setup commands, no `cmds`, no Outliner selection. Open a fresh empty scene
(or no scene at all) and proceed to "How to Run".

---

## How to Run the Functions

### Run A — the built-in self-test (the minimum)

In the **Script Editor** (Python tab):

```python
import manipulatorMath
manipulatorMath.testModule()
```

Expected Script Editor output (**first two lines verified correct; the third
line is corrected here — the README mis-prints it**, see Run B note):

```
0.7853981633974483   3.141592653589793
45.0
closest point to line: 1 2 0
```

- Line 1: `degreesToRadians(45)` = π/4 ≈ `0.7853981633974483`; times 4 = π ≈ `3.141592653589793`. ✅ matches the README.
- Line 2: `radiansToDegrees(π/4)` = `45.0`. ✅ matches the README.
- Line 3: `closestPoint((3,0,0))` on the line through `(0,1,0)` dir `(1,1,0)` =
  **`(1, 2, 0)`**. ❗ **The README prints `1 1 0`, which is wrong** — see Run B.

> Or from a terminal with Maya's interpreter:
> ```bash
> # macOS (typical)
> /Applications/Autodesk/maya2027/Maya.app/Contents/bin/mayapy manipulatorMath.py
> # Windows
> "C:/Program Files/Autodesk/Maya2027/bin/mayapy.exe" manipulatorMath.py
> ```
> The `__main__` guard calls `testModule()` for you.

### Run B — exercise `lineMath` by hand (and verify the README divergence)

```python
import manipulatorMath as mm
import maya.OpenMaya as om

lm = mm.lineMath()
lm.setLine(om.MPoint(0, 1, 0), om.MVector(1, 1, 0))   # line through (0,1,0), dir NE
ok, closest = lm.closestPoint(om.MPoint(3, 0, 0))     # query point (3,0,0)
print(ok, closest.x, closest.y, closest.z)
```

Expected: `True 1.0 2.0 0.0`.

**The hand math** (and a pure-Python reimplementation) confirms the closest
point is **`(1, 2, 0)`**, *not* the `(1, 1, 0)` the README prints. Working:
direction `(1,1,0)` normalizes to `(1/√2, 1/√2, 0)`; query minus line-point =
`(3,-1,0)`; projection `t = (3-1)/√2 = √2`; closest = `(0,1,0) + √2·(1/√2,1/√2,0)
= (1,2,0)`. The README's first two output lines are right; only this third line
is wrong.

### Run C — exercise `degreeRadianConverter` and `maxOfAbsThree`

```python
import manipulatorMath as mm

drc = mm.degreeRadianConverter()
print(drc.degreesToRadians(90))     # 1.5707963267948966  (== π/2)
print(drc.radiansToDegrees(drc.M_PI))  # 180.0

print(mm.maxOfAbsThree(-10, 3, 4))  # -10   (sign preserved; README docstring example)
print(mm.maxOfAbsThree(-10, 10, 4)) # 4     (TIE → falls through to c; see Q&A)
```

### Run D — exercise `planeMath` (the untested, buggy class)

The XZ ground plane (through the origin, normal `+Y`) is the canonical case
manipulators care about:

```python
import manipulatorMath as mm
import maya.OpenMaya as om

ground = mm.planeMath()
ground.setPlane(om.MPoint(0, 0, 0), om.MVector(0, 1, 0))   # ground plane

# A view ray pointing DOWN at the ground — the everyday case:
ok, hit = ground.intersect(om.MPoint(0, 5, 0), om.MVector(0, -1, 0))
print(ok, hit.x, hit.y, hit.z)
```

**Expected correct answer:** `True 0.0 0.0 0.0` (the ray hits the origin).
**Actual current-code answer:** `False 0.0 0.0 0.0` — because
`denominator = -1.0 < .00001`, so the bug rejects it. Contrast with an
**upward** ray, `om.MVector(0, 1, 0)`, which gives `denominator = +1.0` and is
accepted (`True`, hit computed). That sign asymmetry is the bug. Fix:
`if abs(denominator) < .00001:`.

### Run E — one-shot paste (shortest path to "it loads")

```python
import manipulatorMath as mm
mm.testModule()
print(mm.maxOfAbsThree(-2, 5, -9))   # -9
```

---

## Question and Answer

**Q1. Why is there no "How to build the scene" — doesn't every demo need Maya objects?**
This is the curriculum's first **pure-math** demo. It never calls `maya.cmds`,
creates no nodes, reads no selection. Its only Maya dependency is the
`maya.OpenMaya` types (`MPoint`/`MVector`) — which is why you still need Maya's
interpreter but need no scene. The "scene" is whatever `MPoint`/`MVector`
arguments you pass in.

**Q2. `testModule()` exists — so isn't this runnable, not "definitions-only"?**
Right — it is a **hybrid**: a definitions module *plus* a self-test behind
`__main__`. That makes the minimum run one line (`testModule()`). But note the
self-test covers only `degreeRadianConverter` and `lineMath`; `planeMath` and
`maxOfAbsThree` have zero coverage, so "it passes the self-test" is not proof
they work.

**Q3. My downward ray at the ground plane reports no hit — why?**
The `intersect` parallel test is `if denominator < .00001:`. A downward ray
has `denominator = normal·direction = -1.0`, and `-1.0 < .00001` is true, so the
code wrongly returns `(False, …)`. The check only catches **positive** near-zero.
Use `abs(denominator) < .00001`. (A genuinely parallel ray — direction lying *in*
the plane — has `denominator ≈ 0` from either side.)

**Q4. `maxOfAbsThree(-10, 10, 4)` returns `4`. That can't be right?**
It's a tie bug. The guards are strict: `aa > ab and aa > ac` and
`ab > aa and ab > ac`. When `|-10| == |10|`, neither strict `>` holds, so both
guards fail and the function falls through to `return c`. Any equal-abs tie is
resolved to the third argument regardless of which tied. The docstring example
`(-10, 3, 4) → -10` has no tie, so it works.

**Q5. `MVector * MVector` returns a number, but `MVector * 2` returns a vector — why?**
Same operator, two meanings in API 1.0: `MVector * MVector` is the **dot
product** (a scalar `float`); `MVector * scalar` (or `scalar * MVector`) is
**scaling** (an `MVector`). `lineMath.closestPoint` uses both in two adjacent
lines: `t = self.direction * (toPoint - self.point)` is a dot product, then
`self.direction * t` is a scale. Always check the right-hand type.

**Q6. The `planeMath.__init__` sets `a=b=c=d=0`, so the plane starts at the origin, right?**
No — that's dead code. It writes **local** variables `a, b, c, d`, not
`self.a` etc. Until you call `setPlane`, the instance attributes are the class
defaults (`None`), inherited from the class body. The constructor does nothing
observable.

**Q7. Why `from builtins import object` and `from __future__ import division`?**
Python-2 leftovers from when this was written. On Python 2, `class planeMath:`
made an *old-style* class, so the file imports the new-style `object` base
explicitly, and `from __future__ import division` made `/` true-divide. On
Maya 2027's Python 3 both are no-ops — every class is new-style and `/` is
already true division. Safe to delete in new code.

**Q8. The README says `closestPoint` prints `1 1 0`, but I get `1 2 0`. Who's right?**
The code is right: `(1, 2, 0)`. The README's first two output lines (the
degree/radian conversions) are correct, but its third line is a mis-print.
Verified by hand and by a pure-Python reimplementation of the projection. This
is a good reminder: for a math module, **re-derive the printed numbers** rather
than trust the doc's "expected output".

**Q9. API 1.0 vs API 2.0 — does it matter here?**
For this file, only the import path and minor constructor details differ.
The file uses `import maya.OpenMaya` (API 1.0). An API 2.0 port would be
`import maya.api.OpenMaya as om`; the `MPoint`/`MVector` arithmetic is the same.
API 2.0 is newer, more Pythonic, and preferred for new tools — see Advanced
Directions.

**Q10. Where would I actually *use* `planeMath.intersect` in a real tool?**
Any "drop on grid / move on plane" placement tool. On a viewport drag, Maya
hands you a screen **ray** (source point + direction). Build a `planeMath` for
the ground (or the active view's plane), call `intersect`, and snap the selected
object to the returned hit point. That is the core of every painting/placement/
snapping manipulator — which is exactly the context this module was extracted
from.

---

## Advanced Directions

1. **Fix and harden `planeMath.intersect`.** Replace
   `if denominator < .00001:` with `if abs(denominator) < 1e-6:`. Then add a
   **half-space / ray-segment** option: a flag that rejects hits *behind* the ray
   origin (`t < 0`) so a ray pointing away from the plane correctly reports "no
   forward hit". Add a `signedDistance(point)` helper while you're there.
   *New code:* `intersect(..., ray_only=False)`, `signedDistance(self, point)`.

2. **Add the missing geometry methods.** Give `lineMath` a
   `distanceTo(point)` returning `(closestPoint - point).length()`, and give
   `planeMath` a `closestPoint(toPoint)` that projects along the normal
   (`toPoint - normal * signedDistance(toPoint)`). These mirror each other and
   round the module out. *New code:* `lineMath.distanceTo`, `planeMath.closestPoint`.

3. **Build a real placement tool on top of `planeMath`.** Register a viewport
   context (`cmds.manipMoveContext` / a `dragCommand`) that, on drag, reads the
   view ray, intersects it with a chosen plane, and snaps the selected object to
   the hit — turning this math file into a working "drop on grid" tool. Add an
   **undo chunk** (`cmds.undoInfo(openChunk=True/False)`) so each drag is one
   undoable step. *New code:* `placeOnPlane()` context + `PlaceContext` class.

4. **Port the module to API 2.0.** Rewrite as
   `import maya.api.OpenMaya as om` with the same class bodies. The math is
   identical; `MPoint`/`MVector` behave the same. This is low-risk practice for
   the 1.0→2.0 transition every Maya tool eventually makes, and API 2.0 vectors
   are more Pythonic (better `__repr__`, no SWIG proxies). *New file:*
   `manipulatorMath_2027.py` mirroring the class API.

5. **Replace `testModule()` with a real test suite.** The current self-test is
   ad hoc and skips half the module. Add `pytest`-style cases (runnable under
   `mayapy -m pytest`) covering: the `intersect` sign bug, the `maxOfAbsThree`
   tie case, parallel rays, the closest-point value (asserting `1 2 0`), and
   round-trip degree↔radian. This is also how you *prove* fix #1 didn't regress.
   *New file:* `test_manipulatorMath.py`.

6. **Add `lineLineClosestPoint` for two skew lines.** Two infinite lines in 3D
   generally don't meet; the classic result is the midpoint of the shortest
   segment connecting them (solving a 2×2 linear system from the dot products).
   It's a natural extension of `lineMath` and appears in IK / constraint solvers.
   *New code:* module-level `lineLineClosestPoint(lineA, lineB) -> (MPoint, MPoint, float)`.

---

## Source

- **Source code:** `manipulatorMath.py` is the verbatim official Autodesk Maya
  Python API 1.0 example `python/api1/manipulatorMath.py`, Maya 2027 (ENU) API
  reference:
  <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2manipulator_math_8py-example.html>.
- **Verification:** every printed number was re-derived by hand and by a
  pure-Python reimplementation of the arithmetic (no Maya needed): this caught
  the README's `lineMath.closestPoint` misprint (`1 2 0`, not `1 1 0`) and two
  real bugs — `planeMath.intersect`'s wrong-sign denominator test and
  `maxOfAbsThree`'s strict-`>` tie case. The module's only Maya dependency is the
  `maya.OpenMaya` import (`MPoint`/`MVector`), so running it needs Maya's
  interpreter (`mayapy` / Script Editor) even though it builds no scene; that
  interpreter step is marked as such throughout.
