# HowToStart — introduction

This is the very first demo in the curriculum. It has **two** tiny scripts that together teach
the two foundational skills of Maya Python: (1) running Python at all, and (2) driving Maya with
`maya.cmds`. Neither file defines functions or classes — each is a **top-to-bottom script** you
execute in full (the classic "hello world" + "make a cube" pattern).

## Files in this demo

| File | Target | Role |
|------|--------|------|
| `helloWorld.py` | Maya 2017/2018, **Python 2.7** | The teaching original. One line: `print "Hello, World!"` |
| `helloWorld_2027.py` | Maya 2027, **Python 3** | The one you actually run. `print("Hello, World!")` |
| `helloCube.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Builds a cube + NURBS circle control rig. |
| `helloCube_2027.py` | Maya 2027, **Python 3** | The one you actually run. Same rig, Py3 `print`. |

> **`_2027` convention:** files ending in `_2027` target Maya 2027 / Python 3 and are the ones to
> paste into the Script Editor. The bare `.py` files are the heavily-commented Py2 teaching copies.
> See the repo root `AGENTS.md` for the full convention.

## Prerequisites

- Maya 2027 (Python 3). If you are on Maya 2017/2018, use the Py2 `.py` files instead.
- No plugins, no special units, no project setup needed.

## What the code actually does

- `helloWorld` → prints the string `"Hello, World!"`. Nothing else. It exists to confirm your
  Python environment works.
- `helloCube` → `cmds.polyCube()` makes a polygon cube (returns a 2-item list), `cmds.circle()`
  makes a NURBS circle, the cube is **parented under** the circle, the cube's `translate`/`rotate`/
  `scale` channels are **locked**, and the circle is **selected**. Net result: a ready-to-animate
  prop — a cube you drive indirectly through a circle "controller."

---

## How to Create the Test Maya Scene

You do **not** need to build anything by hand — both scripts create their own objects. The only
"scene setup" is to start clean so object names are predictable:

1. Open Maya and start a **New Empty Scene** (`File ▸ New Scene`, or run `cmds.file(new=True, f=True)`
   in the Script Editor).
2. Make sure the viewport panel is visible and the **Outliner** (`Window ▸ Outliner`) is open so you
   can see the hierarchy the script builds.
3. That's it — an empty scene is the test scene for this demo.

> ⚠️ **Cannot be verified without Maya running.** The "expected result" descriptions below describe
> what the code does according to the `cmds` API — they are predictions read from the source, not
> screenshots captured from a live Maya session. The `commandLine` demo, by contrast, was executed
> and verified directly (see its HowToStart).

---

## How to Run the Functions

There are no functions to call here — each file is a flat script. "Running" means executing the
whole file. Do it from the **Script Editor** (`Windows ▸ General Editors ▸ Script Editor`), in the
**Python** tab (not MEL).

### 1. `helloWorld_2027.py` — confirm Python works

Paste the single line (or the whole file) into the Python tab and press **Ctrl+Enter**:

```python
print("Hello, World!")
```

- **Expected result:** the text `Hello, World!` appears in the Script Editor's history / command
  feedback line. Nothing is created in the viewport.
- **If you see a syntax error** like `SyntaxError: invalid syntax` on the word `print`, you are on
  Python 2 and pasted `print("...")` — that actually still works in Py2, but the real tell is the
  *reverse*: if `print "Hello, World!"` (no parentheses, the Py2 file) errors, you are on Python 3.
  Use the file that matches your Maya's Python.

### 2. `helloCube_2027.py` — build a cube + controller rig

Paste the full contents of `helloCube_2027.py` into the Python tab and press **Ctrl+Enter**.
(First make sure the demo folder is importable is *not* required here — there are no `import`
statements beyond `from maya import cmds`, which Maya provides automatically.)

Equivalently, load the file from disk:

```python
import os, runpy
demo_dir = r'/abs/path/to/PythonForMayaSamplesLearn/introduction'
runpy.run_path(os.path.join(demo_dir, 'helloCube_2027.py'))
```

**Expected result, step by step (match these against the code):**

| Code line | What you should see |
|-----------|---------------------|
| `cube = cmds.polyCube()` | A new polygon cube appears at the origin. |
| `print(cube)` | History prints a 2-item list, e.g. `['pCube1', 'polyCube1']`. |
| `print(type(cube))` | History prints `<class 'list'>` (Py3) / `<type 'list'>` (Py2). |
| `circle = cmds.circle()` | A NURBS circle appears at the origin (overlapping the cube). |
| `cmds.parent(transform, circle)` | In the **Outliner**, `pCube1` becomes a child of the circle (`nurbsCircle1`). |
| `cmds.setAttr(transform+'.translate', lock=True)` (×3) | The cube's Translate / Rotate / Scale channels in the Channel Box turn **grey/locked**. |
| `cmds.select(circle)` | The circle (`nurbsCircle1`) becomes the active selection. |

Move the circle with the Move tool and the cube follows — that's the rig working. Try to move the
cube directly: you can't, because its channels are locked.

---

## Question and Answer

**Q1. Why does `helloWorld_2027.py` use `print("Hello, World!")` with parentheses, but
`helloWorld.py` uses `print "Hello, World!"` without them?**
Because they target different Python versions. In Python 2 `print` is a *statement* (no parens
needed); in Python 3 `print` is a *function*, so the argument must be in parentheses. Maya 2027
runs Python 3, so you use the `_2027` file. This single change is the most common Py2→Py3 delta
in the whole repo (see `py3notes.md`).

**Q2. `cube = cmds.polyCube()` — why is `cube` a *list*, and why do we then take `cube[0]`?**
`cmds.polyCube()` returns a list of **two node names**: the **transform** (`pCube1`) at index `0`
and the **history/creator node** (`polyCube1`) at index `1`. We want the transform (the thing that
has translate/rotate/scale and that you can parent and select), so we take `cube[0]`. Index `1` is
the construction-history node that *made* the cube — useful for editing subdivisions later, but not
for parenting.

**Q3. Why parent the cube *under* the circle instead of just animating the cube directly?**
This is the basic **control-rig** pattern: the circle is a "controller" the animator grabs; the
cube is the visible geometry. By parenting cube → circle and then *locking the cube's own channels*,
you force the animator to move only the circle. The cube inherits the circle's transform, so it
follows. This tiny script is the seed of every rig in the later demos.

**Q4. What do the three `cmds.setAttr(..., lock=True)` lines actually accomplish?**
They **lock** the cube's Translate, Rotate, and Scale compound attributes. Locked channels display
greyed-out in the Channel Box and cannot be keyed or edited — which is what makes the cube
"non-touchable" and funnels all animation through the circle control. Without locking, an animator
could accidentally move the cube and break the rig.

**Q5. I ran `helloCube_2027.py` twice and the second time the names were `pCube2`/`nurbsCircle2`,
not `pCube1`. Why?**
Maya **auto-increments** node names so every node name is unique. The first cube is `pCube1`; the
second run finds `pCube1` already taken and uses `pCube2`. The script still works because it stores
the returned names in variables (`cube`, `circle`) rather than assuming `pCube1`. This is exactly
why you should never hard-code `'pCube1'` in your own scripts — always use the name Maya hands back.

**Q6. What is the difference between `cmds.polyCube()` and `cmds.circle()`? Why does one start with
"poly" and the other returns a `nurbsCircle`?**
They create different geometry *types*. `polyCube` makes **polygon** geometry; `circle` makes a
**NURBS curve** (a 1-D curve, not a surface). A NURBS circle has no "inside" to render — it is used
purely as a selectable handle, which is perfect for a controller. That's why controllers throughout
this repo are curves, not meshes.

**Q7. The script ends with `cmds.select(circle)`. What would happen if I then pressed Delete?**
Deleting the selected circle would delete the circle's transform. Because the cube is its child,
Maya deletes the cube too (deleting a parent removes its descendants by default). You'd be back to
an empty scene. If you wanted to delete *only* the control but keep the cube, you'd first reparent
the cube to the world (`cmds.parent('pCube1', world=True)`) before deleting.

**Q8. Do I need `from maya import cmds` at the top every time?**
Yes — `cmds` is not a Python builtin; it's a module provided by Maya. The `from maya import cmds`
line (or `import maya.cmds as cmds`) makes those commands available. In the Script Editor it's
needed once per execution that uses `cmds`. Later demos put this import at the top of every file.

---

## Advanced Directions

These scripts are deliberately minimal. Here are concrete ways to evolve them — each lists the new
function/class it would need.

1. **Wrap the rig into a reusable function.** Right now the logic is a flat script, so you can't
   make *two* controlled cubes without copy-pasting. Refactor into
   `def create_controlled_primitive(shape='cube', name='ctrl', size=1.0):` that returns the
   controller name. New code: a small `rig.py` module with that function and a `__main__` demo.
2. **Add a naming/side system for rigs.** Extend the function to accept a `side` and `description`
   and build names like `L_arm_ctrl` / `R_arm_ctrl` (matching the conventions the later
   `objectRenamer` demo enforces). New code: a `name_parts(side, description, type)` helper.
3. **Color the controller.** Controllers are easier to grab if they're colored. Add override-color
   calls: `cmds.setAttr(ctrl + '.overrideEnabled', 1)`, `cmds.setAttr(ctrl + '.overrideRGBColors', 1)`
   and set `.overrideColorRGB`. New code: a `set_control_color(node, color)` helper.
4. **Add undo support.** Running the script is currently many undo steps. Wrap it in an undo chunk
   with `cmds.undoInfo(openChunk=True)` … `cmds.undoInfo(closeChunk=True)` (and a `try/finally`) so
   one Ctrl+Z removes the whole rig. New code: a small context manager `undo_chunk()`.
5. **Generalize to "controlled primitive of any shape."** Branch on the `shape` argument to call
   `cmds.polyCube/sphere/cylinder/...` or `cmds.circle`, then always do the parent + lock + select
   steps. This is the bridge from "hello cube" to the procedural builders in `gearCreator`.
6. **Make it a shelf button.** Turn the refactor into a one-click shelf tool: a small script that
   imports `rig` and calls `create_controlled_primitive()`, saved to a Maya shelf so a click builds
   a rig. New code: a `shelf_install.py` that uses `cmds.shelfButton`.
