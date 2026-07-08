# HowToStart — gearCreator

This is the **first "definitions-only library" demo** in the curriculum. Unlike `introduction/`
(flat scripts you execute top-to-bottom) or `commandLine/` (a script with a `__main__` guard you
invoke), the `gearCreator` files contain **only `def`s and a `class`** — there is no `if __name__
== '__main__'` block and no example call. Importing the file does **nothing visible**; you must
*call* the functions yourself. This is the "common case" the curriculum keeps returning to, so this
demo is where you learn the import-and-call workflow you'll reuse for almost every later demo.

The payoff: procedural geometry. A configurable gear built from a `polyPipe` whose every-other side
face is extruded into a tooth. The same pattern (a primitive + a component selection + an extrude)
extends to screws, springs, stairs, fences — anything repeating.

## Files in this demo

| File | Target | Role |
|------|--------|------|
| `gears1.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Functional version: `createGear()` + `changeTeeth()`. |
| `gears1_2027.py` | Maya 2027, **Python 3** | The one you actually run. Verified identical to the original (no Py3 changes needed). |
| `gears2.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Object-oriented version: the `Gear` class. |
| `gears2_2027.py` | Maya 2027, **Python 3** | The one you actually run. Verified identical to the original. |

> **`_2027` convention:** files ending in `_2027` target Maya 2027 / Python 3 and are the ones to
> paste into the Script Editor. The bare `.py` files are the heavily-commented Py2 teaching copies.
> See the repo root `AGENTS.md` for the full convention.

## Prerequisites

- Maya 2027 (Python 3). If you are on Maya 2017/2018, use the Py2 `.py` files instead.
- No plugins, no special units, no project setup. The gear's units are the scene's linear units
  (centimeters by default) — `length=0.3` means 0.3 cm of extrusion.

## What the code actually does

- `gears1.createGear(teeth, length)` → builds a polygon **pipe** (`cmds.polyPipe`) with
  `subdivisionsAxis = teeth * 2` spans, selects **every other side face** (the future teeth),
  extrudes them by `length` (`cmds.polyExtrudeFacet(localTranslateZ=length)`), and returns a tuple
  of the three node names you need to edit the gear later: `(transform, constructor, extrude)`.
- `gears1.changeTeeth(constructor, extrude, teeth, length)` → re-points the existing pipe and
  extrude at new values: re-spans the pipe (`polyPipe(edit=True)`), rewrites **which faces** the
  extrude affects (`setAttr(..., type='componentList')`), and re-sets the extrude length. Edits in
  place — it does **not** build a new gear (despite what its docstring says; see Q3).
- `gears2.Gear` → the same logic refactored into a class. The instance **remembers** its own
  `transform`, `constructor`, and `extrude` on `self`, so you call `g.changeTeeth(teeth=12)` without
  passing node names back. It also adds a `changeLength()` method the functional version lacks.

---

## How to Create the Test Maya Scene

The functions **build their own geometry** from nothing, so — like `introduction/` — there is no
hand-built scene. The "test scene" is an **empty scene**, plus the demo folder placed on Python's
import path. The only scene state the functions care about is:

| Function | Scene state it expects |
|----------|------------------------|
| `createGear()` / `Gear().create()` | **Empty scene.** No selection required; it creates the pipe and selects faces internally, then clears the selection. |
| `changeTeeth()` / `Gear().changeTeeth()` | **A gear you just built** (the pipe + extrude nodes must still exist). For `gears1` you must pass back the `constructor` and `extrude` names returned by `createGear()`; for `gears2` the instance already holds them. |
| `Gear().changeLength()` | A gear whose `self.extrude` is set (i.e. `create()` was called first). |

Set up like this:

1. Open Maya and start a **New Empty Scene** (`File ▸ New Scene`, or `cmds.file(new=True, f=True)`).
2. Open the **Script Editor** (`Windows ▸ General Editors ▸ Script Editor`) and switch to the
   **Python** tab (not MEL).
3. Open the **Outliner** (`Window ▸ Outliner`) and the **Channel Box** so you can watch the gear
   appear and see its construction-history nodes.
4. Put the demo folder on `sys.path` so Python can `import` it (do this once per Script Editor
   session):

   ```python
   import sys
   sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/gearCreator')
   ```

   Substitute your clone location. Use a **raw string** (`r'...'`) and forward slashes on
   macOS/Linux.

> ⚠️ I cannot run Maya in this environment, so the "expected result" descriptions below describe
> what the code does according to the `cmds` API and are not screenshots I captured. The one demo
> verified by direct execution is `commandLine/` (pure Python, no Maya). Everything here is a
> faithful read of `gears1_2027.py` / `gears2_2027.py`.

---

## How to Run the Functions

Remember: **define ≠ call.** Importing the module only loads the recipe. You must invoke the
function/method yourself.

### Run A — `gears1` (the functional version)

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/gearCreator')
import gears1_2027 as gears1
```

**1. Create a gear (default: 10 teeth, 0.3 length):**

```python
transform, constructor, extrude = gears1.createGear()
print(transform, constructor, extrude)
```

- **Expected viewport result:** a polygon **pipe** appears at the origin with **10 teeth** sticking
  out along its local Z axis by 0.3 units. It is named `pPipe1` (Maya auto-numbers: `pPipe2` on the
  next run).
- **Expected history print:** three node names, e.g.
  `pPipe1 polyPipe1 polyExtrudeFace1`.
- **Keep the three names** — `changeTeeth` needs the last two.

**2. Create a custom gear (20 teeth, 0.5 length):**

```python
transform, constructor, extrude = gears1.createGear(teeth=20, length=0.5)
```

- **Expected result:** a second gear (`pPipe2`) with 20 teeth, each 0.5 long.

**3. Modify an existing gear in place (reuse the saved nodes):**

```python
gears1.changeTeeth(constructor, extrude, teeth=12, length=0.2)
```

- **Expected result:** the **same** gear updates — now 12 teeth, each 0.2 long. No new `pPipe`
  appears in the Outliner (the pipe and extrude nodes are edited, not recreated). The
  `inputComponents` attribute on the extrude node is rewritten to point at the new every-other-face
  list.

> **Pitfall — direction of teeth:** on some Maya versions the teeth extrude **inward** (into the
> pipe) because the selected face normals point the other way. If your teeth look sunken, pass a
> negative length: `gears1.createGear(length=-0.3)`.

### Run B — `gears2` (the class version)

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/gearCreator')
import gears2_2027 as gears2
```

**1. Build a gear through an instance:**

```python
g = gears2.Gear()          # runs __init__, sets placeholders to None
g.create(teeth=20, length=0.5)
print(g.transform)         # -> pPipe1
```

- **Expected result:** a 20-tooth gear at the origin. The instance now holds `g.transform`,
  `g.constructor`, `g.extrude`, `g.shape` (see Q5 on what `shape` actually is).

**2. Modify it — no node names to pass back:**

```python
g.changeTeeth(teeth=12, length=0.6)   # instance knows its own constructor/extrude
g.changeLength(length=0.1)            # change just the length, leave teeth at 12
```

- **Expected result:** the same gear updates in place (12 teeth, then length 0.1).

**3. Make a second, independent gear:**

```python
g2 = gears2.Gear()
g2.create(teeth=8, length=0.2)
```

- **Expected result:** a second gear (`pPipe2`). `g` and `g2` hold **different** node names, so
  editing one never touches the other — this is the main advantage of the class version.

### Run C — one-shot paste (shortest path to a gear)

If you just want to see a gear:

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/gearCreator')
import gears1_2027 as gears1
transform, constructor, extrude = gears1.createGear(teeth=20, length=0.5)
print("Created gear:", transform)
```

---

## Question and Answer

**Q1. The file has no `if __name__ == '__main__'`. Why does running it do nothing, and is that a
bug?**
It's intentional, not a bug. The file is a **module** — a library of definitions meant to be
`import`ed by other code. Defining a function is writing a recipe; **calling** it is cooking. With
no call site, importing loads the definitions into memory and stops. You supply the call
(`gears1.createGear()`) in the Script Editor. A `__main__` guard would be the place to put a demo
call that runs only when the file is executed directly — these teaching files deliberately omit it
so importing is side-effect-free.

**Q2. `createGear` does `spans = teeth * 2` and `polyPipe(subdivisionsAxis=spans)`. Why double the
teeth count to get the span count?**
Because a tooth occupies **every other** side face of the pipe. To get `N` teeth you need `2N`
side faces around the pipe so that alternating faces can be extruded (tooth, gap, tooth, gap…). The
selection `range(spans * 2, spans * 3, 2)` then walks the side-face index range **two at a time**,
picking exactly the tooth faces and skipping the gap faces.

**Q3. `gears1.changeTeeth`'s docstring says "This will create a new extrude node." Does it?**
No — the docstring is **misleading**. The code edits the **existing** extrude node in place: it
re-spans the pipe with `polyPipe(constructor, edit=True, ...)`, rewrites the extrude's
`inputComponents` with a `setAttr(..., type='componentList')` call, and re-sets the length with
`polyExtrudeFacet(extrude, edit=True, ltz=length)`. No new node is created. The cheap part (rewriting
the component list) is the whole point — recreating the extrude would be expensive and would break
the node name you saved.

**Q4. `changeTeeth` uses `cmds.setAttr('%s.inputComponents' % extrude, len(faceNames), *faceNames,
type='componentList')`. Why the count, the `*`, and the `type`?**
A `componentList` attribute is a **variable-length list of component specifiers** (like
`f[40]`, `f[42]`, …). Maya's `setAttr` for such attributes needs the items spelled out one-by-one:
`setAttr(node.inputComponents, count, item1, item2, ..., type='componentList')`. The `len(faceNames)`
is the count; `*faceNames` is Python **list-unpacking** — it expands the list `['f[40]','f[42]',...]`
into individual arguments in the call; and `type='componentList'` tells Maya to interpret the
arguments as a component list rather than a plain string array. Drop any of the three and the call
fails or silently sets the wrong type.

**Q5. In `gears2`, `createPipe` stores `self.transform, self.shape = cmds.polyPipe(...)`. What is
`self.shape`, and why is `self.constructor` found separately afterward?**
`cmds.polyPipe()` returns `[transform, polyPipeNode]` — the transform and the **construction-history
(creator) node**, not the mesh shape. So `self.shape` is a **misnomer**: it actually holds the
`polyPipe` creator node. The loop that follows (`for node in cmds.listConnections(transform.inMesh):
if objectType(node)=='polyPipe'`) re-discovers that same creator node via the dependency graph and
stores it as `self.constructor`. The two end up pointing at the **same node**, so `self.shape` is
redundant — it's left over from an earlier design where the author "didn't like having to find the
constructor from the extrude node" (per the inline comment). Reading the code, you can ignore
`self.shape` and treat `self.constructor` as the pipe's creator.

**Q6. In `gears1` I have to pass `constructor` and `extrude` back into `changeTeeth`; in `gears2` I
don't. What did the class actually buy me?**
**Encapsulation of state.** The functional version forces *you* to track the three node names
(`transform, constructor, extrude`) in your script and thread them through every later call — lose
them and you can no longer edit the gear. The class stores them on `self` at `create()` time, so
`g.changeTeeth(teeth=12)` just reads `self.constructor` / `self.extrude` internally. The class also
makes **multiple independent gears** trivial (`g1`, `g2` each hold their own nodes) and adds a
`changeLength()` convenience method. Use functions for one-shot "build and forget"; use the class
when you'll create several gears or edit them over time.

**Q7. What happens if I call `g.changeTeeth()` before `g.create()`?**
You'll get an error. `__init__` sets `self.constructor = None` and `self.extrude = None`; without
`create()`, `changeTeeth` calls `cmds.polyPipe(None, edit=True, ...)` and
`self.modifyExtrude(...)`, both of which will fail because `None` is not a valid node name. The
class has no guard against this — `create()` must run first. (A `if self.transform is None: raise`
check would be a natural hardening improvement; see Advanced Directions.)

**Q8. I ran `createGear()` twice and got `pPipe1` then `pPipe2`. If I kept the first `transform`
variable, does it still point at the first gear?**
Yes — `transform` is just a string captured at creation time (`'pPipe1'`). Running `createGear()`
again creates `pPipe2` and returns a *new* tuple; it does **not** touch your saved `'pPipe1'`
string. The first gear is still in the scene and `transform` still names it. Where people get
tripped up is *reassigning* the variable: `transform, constructor, extrude = createGear()` a second
time overwrites the names, and you lose your handle on the first gear unless you used different
variables or the class version.

**Q9. `gears2.getTeethFaces` builds `'f[%d]' % face` while `gears1` uses `'%s.f[%s]' % (transform,
face)`. Why `%d` in one and `%s` in the other?**
`%d` formats an **integer**; `%s` formats **anything** (via `str()`). `gears2` builds only the face
part (`'f[40]'`) and prepends the transform separately at select time
(`'%s.%s' % (self.transform, face)`), so it can safely use `%d` since `face` is always an int from
`range()`. `gears1` builds the full `pPipe1.f[40]` string in one shot and uses `%s` for both slots.
Functionally interchangeable here; `%d` is slightly stricter (it would raise if you ever passed a
non-number). It's a small style difference between the two files, not a behavior difference.

**Q10. There's no undo chunk. If I call `createGear()`, how many Ctrl+Z steps does it take to
remove the gear?**
Many — every `cmds` call (the `polyPipe`, each `cmds.select`, the `polyExtrudeFacet`) is a separate
undo step, so removing one gear can take a dozen undos. Wrapping the body in
`cmds.undoInfo(openChunk=True)` … `cmds.undoInfo(closeChunk=True)` (with a `try/finally`) would
collapse the whole build into one undo. None of the gear files do this; see Advanced Directions.

---

## Advanced Directions

These files are a solid seed but stay deliberately small. Here are concrete ways to evolve the demo
— each lists the new functions/classes it would require.

1. **Expose the full `polyPipe` parameter set.** `createGear` hard-codes everything but `teeth` and
   `length`; `cmds.polyPipe` also takes `radius`, `height`, `thickness`, `subdivisionsHeight`.
   Extend the signature to `createGear(teeth, length, radius=1, height=1, thickness=0.2, ...)` and
   thread the values into both `polyPipe` and the `changeTeeth` edit path. New code: a
   `PipeParams` dataclass holding the full parameter set, passed to `create`/`changeTeeth`.

2. **Turn it into a procedural gear-train / rig builder.** The README exercise asks for meshed
   gears; make it real. Add a `GearTrain` class that places N gears of given radii along a line so
   pitch circles touch, parents each to a joint, and sets `rotate` offsets so teeth mesh
   (`rotation = 360 / teeth / 2` offset between neighbors, drive ratio = `teeth_b / teeth_a`).
   New code: `GearTrain.add_gear(radius, teeth)`, `GearTrain.align()`, `GearTrain.bind_joints()`,
   plus a joint-creation helper. This is the bridge from "one gear" to a procedural-rig builder.

3. **Add undo-chunk + safe-state hardening.** Wrap every mutator in an `undo_chunk()` context
   manager (`undoInfo(openChunk=True)` … `closeChunk=True` in a `try/finally`) so each build/edit is
   one Ctrl+Z. Add `if self.transform is None: raise RuntimeError('call create() first')` guards to
   `changeTeeth`/`changeLength`, and a `delete()` method (`cmds.delete(self.transform)` then reset
   placeholders to `None`). New code: a `@contextmanager undo_chunk()` and a `_assert_built()`
   helper.

4. **Give it a real UI (the "Hour 5" goal).** The README sketches a `cmds` slider window; upgrade
   it to a **PySide6** `QWidget` with teeth/length/radius sliders, a live preview that calls
   `changeTeeth` on drag, and an "Add Gear" button. Reuse the model/view split used by
   `controllerLibrary`: a `Gear` model class (this file) + a `GearCreatorUI(QWidget)` that only
   calls into it. New code: `GearCreatorUI` with slider signals wired to `Gear.changeTeeth`, and a
   `showUI()` helper that keeps the window reference (per the repo's UI-launch convention).

5. **Generalize to "repeating-feature extruder."** The pattern — primitive → pick every-kth
   component → extrude — is not gear-specific. Refactor a base `RepeatingFeature` class with a
   `select_components()` hook, then subclass: `Gear` (pipe, every-other rim face), `Screw`
   (cylinder, helical edge loop selection + twist), `Stairs` (cube, sequential top faces + step
   translate), `Spring` (curve + periodic offset). New code: an abstract `RepeatingFeature` base
   with `build()` / `rebuild()` template methods and a `select_faces()` abstract method per
   subclass.

6. **Package it as an installable Maya shelf tool.** Right now users must `sys.path.insert` and
   `import` by hand. Turn the demo into a small package (`gearcreator/` with `__init__.py`,
   `gear.py`, `ui.py`) installable via `pip install -e .` against Maya's Python, then add a shelf
   button whose command is `import gearcreator; gearcreator.show_ui()`. New code: a `pyproject.toml`
   / `setup.py`, a package `__init__.py` exposing `show_ui()`, and a `shelf_install.py` that calls
   `cmds.shelfButton` to install the button into the current shelf.
