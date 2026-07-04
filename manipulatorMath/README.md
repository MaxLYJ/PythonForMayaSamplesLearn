# manipulatorMath — Geometry Utilities for Viewport Manipulators (API 1.0)

This demo comes from the official Maya Python API documentation.

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2manipulator_math_8py-example.html>

It is a small **pure-math utility module** (no Maya commands, no UI) containing
classes for the kind of geometry math you need when building **viewport
manipulators** — planes, lines, and unit conversions.

---

## What you will learn

1. **Plane intersection math** — given an infinite plane and a ray, find the
   point where they meet. This is what every "click-drag in the viewport to
   place something in 3D" tool has to do.
2. **Closest-point-on-line** — given an infinite line and a query point,
   find the line point nearest to the query. Used by axis manipulators.
3. **Degree ↔ radian conversion** — Maya's API works in radians; the UI shows
   degrees. You'll need this conversion constantly.
4. **`MPoint` / `MVector` arithmetic with API 1.0** — how to add, scale, and
   dot-product these types, and when normalization matters.
5. **Writing reusable math classes** — the file is structured as utility
   classes (`planeMath`, `lineMath`, `degreeRadianConverter`) rather than a
   script. This is the right shape for code you'll import from other tools.

---

## Prerequisites

| Concept                       | Where to learn it                                          |
|-------------------------------|------------------------------------------------------------|
| Python classes (`class`, `__init__`) | any Python tutorial                                  |
| `maya.cmds` basics            | `introduction/helloCube.py`                                |
| OpenMaya API 1.0 basics       | [`cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md) |
| What `MPoint` and `MVector` are | Maya docs → `OpenMaya.MPoint`, `OpenMaya.MVector`        |

You do **not** need to know anything about manipulators, dependency graphs,
or plug-ins to read this file. It's just geometry.

---

## Files

```
manipulatorMath/
├── README.md                ← this file
└── manipulatorMath.py       ← the demo
```

The `.py` is bundled here directly (it's a public Autodesk docs listing).

---

## The four pieces of the file

Read the module top to bottom — it's small and well-named. Here's the map:

### 1. `planeMath` — an infinite plane and ray-vs-plane intersection

A plane is defined by the equation `ax + by + cz + d = 0`, where `(a, b, c)`
is the plane's **normal** and `d` is computed from any point known to lie on
the plane.

```python
def setPlane(self, pointOnPlane, normalToPlane):
    _normalToPlane = normalToPlane
    _normalToPlane.normalize()
    self.a = _normalToPlane.x
    self.b = _normalToPlane.y
    self.c = _normalToPlane.z
    self.d = -(self.a*pointOnPlane.x + self.b*pointOnPlane.y + self.c*pointOnPlane.z)
```

The interesting method is **`intersect(linePoint, lineDirection)`** — given a
ray (a point + a direction), find where it hits the plane:

```python
denominator = self.a*lineDirection.x + self.b*lineDirection.y + self.c*lineDirection.z
if denominator < .00001:
    return (False, intersectionPoint)        # ray parallel to plane → no hit
t = -(self.d + self.a*linePoint.x + self.b*linePoint.y + self.c*linePoint.z) / denominator
intersectionPoint = linePoint + lineDirection * t
return (True, intersectionPoint)
```

> **Why this matters:** when you click-drag in the viewport, Maya gives you a
> screen ray. To convert that to a 3D position, you intersect the ray with a
> plane (the ground plane, a plane aligned to the active view, etc.). This
> `intersect` method is the math behind every "drop on grid" / "move on
> plane" manipulator.

### 2. `lineMath` — an infinite line and closest-point-on-line

```python
def closestPoint(self, toPoint):
    t = self.direction * (toPoint - self.point)
    closest = self.point + (self.direction * t)
    return (True, closest)
```

The expression `self.direction * (toPoint - self.point)` is the **dot
product** (it's a scalar `t`), not element-wise multiply. `MVector * MVector`
in API 1.0 is the dot product. Then `self.direction * t` scales the unit
direction back up to the actual offset.

> **Why this matters:** axis manipulators (the X/Y/Z arrows on the Move tool)
> project the mouse onto each axis line; the closest line point to the mouse
> becomes the new dragged position. This is the math behind that.

### 3. `degreeRadianConverter` — trivial but indispensable

```python
def degreesToRadians(self, degrees):
    return degrees * (self.M_PI / 180.0)
def radiansToDegrees(self, radians):
    return radians * (180.0 / self.M_PI)
```

Maya's API stores angles in **radians**; the channel box and UI show **degrees**.
You'll convert between them constantly. Note this class stores `M_PI` as a
class attribute instead of importing `math.pi` — stylistic choice.

### 4. `maxOfAbsThree(a, b, c)` and `testModule()`

`maxOfAbsThree` returns whichever of three inputs has the largest absolute
value, but **preserves the sign** of the winner (`-10, 3, 4 → -10`). This is
used by manipulators to pick a dominant axis.

`testModule()` is a tiny self-test you can run from the command line:

```python
if __name__ == "__main__":
    testModule()
```

It exercises `degreeRadianConverter` and `lineMath.closestPoint` and prints
the results. Run it to confirm the module loads.

---

## How to run it

### Option A: From the command line (no Maya needed for the math)

The file's `__name__ == "__main__"` block runs `testModule()`. But note: it
imports `maya.OpenMaya`, which only exists inside a Maya installation. To run
outside Maya you'd need the `mayapy` interpreter shipped with Maya:

```bash
# Windows (typical Maya install path)
"C:/Program Files/Autodesk/Maya2027/bin/mayapy.exe" manipulatorMath.py
```

Expected output:

```
0.7853981633974483   3.141592653589793
45.0
closest point to line: 1 1 0
```

### Option B: Inside Maya's Script Editor

```python
import manipulatorMath
manipulatorMath.testModule()
```

You should see the same output in the Script Editor.

---

## How this connects to real manipulators

This module on its own doesn't create any manipulators — it's the **math
foundation**. A real manipulator (built with `MPxManipulatorNode` in the C++
API, or via `cmds.manipMove` / custom context in Python) would use these
classes like this:

```python
# When the user drags in the viewport:
raySource = OpenMaya.MPoint(...)        # from Maya's view ray
rayDir    = OpenMaya.MVector(...)       # from Maya's view ray

# Build the ground plane (XZ plane, normal = +Y)
ground = planeMath()
ground.setPlane(OpenMaya.MPoint(0,0,0), OpenMaya.MVector(0,1,0))

# Find where the view ray hits the ground
ok, hit = ground.intersect(raySource, rayDir)
if ok:
    # move the selected object to 'hit'
    ...
```

The Autodesk devkit ships **C++ examples** named `moveManip` / `rotManip` /
`scaleManip` that consume exactly this kind of math. This Python module is
the reference-implementation of that math for Python tool developers.

---

## Things to try next (exercises)

1. **Add a `distanceTo(point)` method to `lineMath`.** It should return the
   Euclidean distance from `toPoint` to the line, not just the closest point.
   Hint: it's `(toPoint - closestPoint).length()`.
2. **Add a `closestPoint` to `planeMath`.** Mirror `lineMath.closestPoint`:
   project `toPoint` onto the plane along its normal.
3. **Make `planeMath.intersect` more robust.** The current code checks
   `if denominator < .00001` — but `denominator` could be **negative** (ray
   pointing away from the normal). Add a comment explaining what the sign
   means, then try `if abs(denominator) < .00001` and compare.
4. **Port `planeMath` to API 2.0.** Rewrite using
   `import maya.api.OpenMaya as om`. The math is identical; only the
   `MPoint`/`MVector` construction differs slightly. Good practice for the
   API 1.0 ↔ 2.0 transition.
5. **Write a `lineLineClosestPoint` function.** Two skew lines in 3D don't
   intersect; find the midpoint of the shortest segment connecting them.
   This is a classic geometry problem and a natural extension of this module.
6. **Use `planeMath.intersect` in a real tool.** Register a
   `dragCommand`-style context that, on viewport drag, casts a ray, hits the
   ground plane, and snaps the selected object to the hit point. You've now
   built the core of a placement/painting tool.

---

## Common pitfalls

* **`MVector * MVector` is dot product, not element-wise.** It returns a
  scalar. If you want element-wise, that's not directly supported — use
  `.x`, `.y`, `.z` explicitly.
* **`MVector * scalar` scales the vector.** Same `*` operator, different
  meaning depending on the right-hand side. Read both sides before assuming.
* **Always normalize direction vectors.** `planeMath.intersect` and
  `lineMath.setLine` both assume unit directions. Forgetting to normalize is
  the most common source of "the math looks right but the numbers are wrong."
* **`denominator < .00001` only catches positive near-zero.** A ray going
  the opposite direction has a negative denominator and is *not* parallel.
  Use `abs(denominator) < .00001` to be safe.
* **The file uses `from __future__ import division` and `from builtins import object`.** These are leftovers from Python 2 support. On Python 3
  (Maya 2027+) they're harmless no-ops, but you can drop them in new code.
* **`planeMath.__init__` assigns to locals, not `self`.** Look at the
  constructor: `a = 0; b = 0; ...` sets local variables, not attributes —
  the real attributes are set in `setPlane`. Don't be fooled into thinking
  the init is doing useful work; it's effectively dead code.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — python/api1/manipulatorMath.py*,
Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2manipulator_math_8py-example.html>
