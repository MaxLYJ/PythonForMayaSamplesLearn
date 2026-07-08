# How To Start: `objectRenamer`

This demo is the **Maya-scene counterpart to `commandLine/`**. Where `commandLine/renamer.py` renamed
*files* on disk from the OS shell, `objectRenamer/` renames **DAG nodes inside a Maya scene** — adding
a type-based suffix (`cube` → `cube_geo`, `arm` → `arm_jnt`) so a rig's Outliner reads cleanly. It is
also the natural sequel to `gearCreator/`: where that demo was a definitions-only library you
import-and-call, this one walks you through the **script → function** evolution explicitly.

It contains **two pedagogical stages**, plus a bonus variant:

1. **`renamer1`** — a flat, top-to-bottom *script* (like `introduction/`). You paste the whole file;
   it runs immediately on whatever you have selected. Uses an `if/elif/else` chain for the type lookup.
2. **`renamer2`** — a **definitions-only library** (like `gearCreator/`). It *only* `def`s the
   `rename()` function; running the file does nothing visible until you call it. It replaces the
   `if/elif/else` chain with a **dictionary + `.get()` lookup**, adds a `RuntimeError` for misuse, an
   idempotency guard, and a **return value**.
3. **`renamer_numbered`** — a flat-script variant of `renamer1` that adds a zero-padded numbered
   *prefix* (`ctrl_01_ctrl`, `ctrl_02_ctrl`, …) and a new `nurbsCurve → ctrl` type case.

The payoff of the whole demo: the "script vs. function" lesson in miniature, plus a genuinely useful
naming-convention tool you'll reach for on every rig.

**Files in this demo**

| File | Target | Role |
|------|--------|------|
| `renamer1.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Flat script: type-suffix renamer with `if/elif/else`. |
| `renamer1_2027.py` | Maya 2027, **Python 3** | The one you actually run. Identical logic; only `print` became a function (`print(...)`). |
| `renamer2.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Definitions-only: the `rename(selection=False)` function with dict lookup. |
| `renamer2_2027.py` | Maya 2027, **Python 3** | The one you actually run. Verified identical to the original (no Py3 changes needed). |
| `renamer_numbered.py` | Maya 2027, **Python 3** | A flat-script bonus variant: numbered-prefix names + a `nurbsCurve → ctrl` case. |

> **`_2027` convention:** files ending in `_2027` target Maya 2027 / Python 3 and are the ones to
> paste into the Script Editor. The bare `.py` files are the heavily-commented Py2 teaching copies.
> See the repo root `AGENTS.md` for the full convention.

**Prerequisites**

- Maya 2027 (Python 3). If you are on Maya 2017/2018, use the Py2 `.py` files instead.
- No plugins, units, or project setup required. The only thing the scripts need is **DAG objects of
  the right node types** to rename.

**What the code actually does**

- `renamer1` (flat script) → grabs the selection as full paths (`cmds.ls(selection=True, long=True)`),
  or — if nothing is selected — **every DAG node in the scene** (`cmds.ls(long=True, dag=True)`).
  Sorts **longest full-path first** so children rename before their parents. For each object it finds
  the *real* type by peeking at the single child shape (transforms report `"transform"`, not `"mesh"`),
  then maps `mesh→geo`, `joint→jnt`, `camera→skip`, anything-else→`grp` via `if/elif/else`, and calls
  `cmds.rename(obj, newName)` with the **full path**.
- `renamer2.rename(selection=False)` (function) → same idea, but: the type map is a `SUFFIXES` dict
  (`{"mesh":"geo","joint":"jnt","camera":None}`, default `"grp"`); lookup is `SUFFIXES.get(objType, DEFAULT)`;
  `camera: None` + `if not suffix: continue` implements the skip as **data**; an `endswith('_'+suffix)`
  guard makes re-running **idempotent** (no `cube_geo_geo`); it raises `RuntimeError` if you pass
  `selection=True` with nothing picked; and it **returns** the list of renamed full paths. It also
  **always passes `dag=True`** to `cmds.ls` (see Q6) and renames by **bare short name** rather than
  full path (see Q7).
- `renamer_numbered` (flat script) → same selection/fallback/sort as `renamer1`, but `enumerate()`
  gives each object a 1-based index, zero-padded with `%02d`, so names become `ctrl_01_ctrl`,
  `ctrl_02_ctrl`, …. Adds a `nurbsCurve → ctrl` case the other two files lack.

---

## How to Create the Test Maya Scene

Unlike `introduction/` or `gearCreator/` (which build their own geometry), this demo **renames
existing objects**, so the test scene is the whole point. You need a handful of objects of **mixed
node types** so every branch of the type lookup fires. The state each entry point expects:

| Entry point | Scene state it expects |
|-------------|------------------------|
| `renamer1` (paste whole file) | A **selection** of mixed-type DAG objects (mesh, joint, locator, camera, curve). If your selection is empty, it silently falls back to **every DAG node in the scene**. |
| `renamer2.rename(selection=True)` | A selection of mixed-type objects. With nothing selected it **raises `RuntimeError`** (does not fall back). |
| `renamer2.rename()` (no args) | Ignores the selection and processes **every DAG node in the scene** (`selection` defaults to `False`). |
| `renamer_numbered` (paste whole file) | A selection, ideally of **NURBS curves** (controls) to exercise the `nurbsCurve → ctrl` case. |

Build the mixed-type scene (do this in a **Python** tab of the Script Editor):

1. Start a clean scene and open the **Outliner** (`Window ▸ Outliner`) so you can watch names change.

   ```python
   from maya import cmds
   cmds.file(new=True, f=True)
   ```

2. Create one object of each type the renamers care about:

   ```python
   cmds.polyCube(name='cube')         # mesh           -> _geo
   cmds.joint(name='arm')             # joint          -> _jnt
   cmds.spaceLocator(name='marker')   # transform only -> _grp (no shape -> falls to else/DEFAULT)
   cmds.camera(name='cam')            # camera         -> SKIPPED
   cmds.circle(name='control')        # nurbsCurve     -> _grp in renamer1/2, _ctrl in renamer_numbered
   cmds.select(all=True)
   ```

3. With everything selected, you are ready to run `renamer1` or `renamer2.rename(selection=True)`.
   For `renamer_numbered`, swap step 2 for a batch of curves:

   ```python
   from maya import cmds
   cmds.file(new=True, f=True)
   for _ in range(5):
       cmds.circle()                  # nurbsCircle1 .. nurbsCircle5
   cmds.select('nurbsCircle*')
   ```

> ⚠️ I cannot run Maya in this environment, so the "expected result" tables below describe what the
> code does according to the `cmds` API and are not screenshots I captured. The behavior was verified
> by reading `renamer1_2027.py`, `renamer2_2027.py`, and `renamer_numbered.py` line-by-line (syntax
> confirmed with `py_compile`; `renamer2_2027` confirmed to have no `__main__` guard and no call site).

---

## How to Run the Functions

There are two run modes depending on the file: **flat scripts** (`renamer1`, `renamer_numbered`) you
execute whole; the **function library** (`renamer2`) you import and call. Remember: for `renamer2`,
**define ≠ call** — importing the module only loads the recipe.

### A. `renamer1` — the flat script (type suffix)

Set up the mixed-type scene from step 2 above, then **paste the entire contents of
`renamer1_2027.py`** into a Python tab and run it (it has no `__main__` guard — it *is* the body).

- **Expected Outliner result** (for the 5 objects above, all selected):

  | Before | After | Why |
  |--------|-------|-----|
  | `cube` | `cube_geo` | child mesh shape → `mesh` → `geo` |
  | `arm` | `arm_jnt` | `joint` → `jnt` |
  | `marker` | `marker_grp` | locator has no shape child → `else` → `grp` |
  | `cam` | `cam` (unchanged) | `camera` → `print "Skipping camera"` + `continue` |
  | `control` | `control_grp` | nurbsCurve shape → not mesh/joint/camera → `else` → `grp` |

- **Expected Script Editor output:** five `Before rename:` / `After rename:` print pairs, plus one
  `Skipping camera` line.

> **Pitfall — run it twice and you get double suffixes.** `renamer1` has **no** idempotency check, so
> running it again renames `cube_geo` → `cube_geo_geo`. `renamer2` fixes this; see Q8.

### B. `renamer2` — the definitions-only function library

Put the demo folder on `sys.path` and import (once per Script Editor session):

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/objectRenamer')
import renamer2_2027 as renamer2
```

**1. Rename the current selection:**

```python
renamed = renamer2.rename(selection=True)
print("Renamed:", renamed)
```

- **Expected result:** same Outliner changes as `renamer1` (`cube_geo`, `arm_jnt`, `marker_grp`,
  `control_grp`; `cam` skipped), **plus** the function returns the list of renamed full paths, e.g.
  `['|cube_geo', '|arm_jnt', '|marker_grp', '|control_grp']`.

**2. Rename the entire scene (no selection needed):**

```python
cmds.select(clear=True)
renamer2.rename()                 # selection defaults to False -> whole scene (dag=True)
# or, explicit:
renamer2.rename(selection=False)
```

- **Expected result:** every DAG object in the scene gets its suffix, regardless of selection.

**3. Trigger the misuse error:**

```python
cmds.select(clear=True)
renamer2.rename(selection=True)   # raises RuntimeError: You don't have anything selected
```

- **Expected result:** a `RuntimeError` with the message `"You don't have anything selected"`. This
  is intentional — the function refuses to silently no-op when you asked it to use the selection.

**4. Idempotency check — run it twice on the same selection:**

```python
cmds.select(all=True)
renamer2.rename(selection=True)   # cube -> cube_geo
renamer2.rename(selection=True)   # NO double-suffix: the endswith() guard skips already-renamed objects
```

- **Expected result:** the second call renames **nothing new** — objects whose name already ends in
  `_geo`/`_jnt`/`_grp` are skipped. Contrast with `renamer1` (Q8).

### C. `renamer_numbered` — the flat-script numbered-prefix variant

Build the batch-of-curves scene from step 3 above, then **paste the entire contents of
`renamer_numbered.py`** into a Python tab and run it.

- **Expected Outliner result** (5 circles selected):

  | Before | After |
  |--------|-------|
  | `nurbsCircle1` | `ctrl_01_ctrl` |
  | `nurbsCircle2` | `ctrl_02_ctrl` |
  | `nurbsCircle3` | `ctrl_03_ctrl` |
  | `nurbsCircle4` | `ctrl_04_ctrl` |
  | `nurbsCircle5` | `ctrl_05_ctrl` |

- **Expected Script Editor output:** five `Renamed: nurbsCircleN -> ctrl_0N_ctrl` lines, then
  `Done. Renamed 5 objects.`

> **Why `_ctrl` and not `_grp`?** This file added a `nurbsCurve → ctrl` case that `renamer1`/`renamer2`
> lack. In those two, a NURBS curve falls through to `else`/`DEFAULT` and wrongly becomes `…_grp`. See
> Q10 for how to give `renamer2` the same fix via its `SUFFIXES` dict.

### D. One-shot paste (shortest path to seeing it work)

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/objectRenamer')
import renamer2_2027 as renamer2
from maya import cmds
cmds.file(new=True, f=True)
cmds.polyCube(name='cube'); cmds.joint(name='arm'); cmds.spaceLocator(name='marker')
cmds.select(all=True)
print("Renamed:", renamer2.rename(selection=True))
```

---

## Question and Answer

**Q1. There are two versions — a flat script (`renamer1`) and a function (`renamer2`). What's the
pedagogical point of having both?**
The "script vs. function" lesson, in miniature. `renamer1` is a **one-off script**: it runs top-to-
bottom, has no return value, and you re-paste it every time. `renamer2` packages the same logic into a
reusable `rename()` with a docstring, a default argument, error handling, an idempotency guard, and a
return value — so you can `import renamer2` from anywhere and call it without side effects at import
time. The meta-lesson (from the demo's own `renamer2_README.md`): whenever you write a 5-case
`if/elif/else` that just maps inputs to outputs, you almost always want a **dict** (and a function)
instead.

**Q2. Why does the code sort the object list `key=len, reverse=True` (longest full-path first) before
renaming?**
To rename **children before parents**. A child's full path includes its parent's name
(`|grp|parent|child`); if you rename the parent first, the child's path string changes, and any later
`cmds.rename(obj, ...)` still holding the *old* path fails to find the node. Sorting longest-path-first
guarantees the deepest descendants are renamed first, so by the time a parent's turn comes, none of its
descendants' paths depend on a name you haven't changed yet.

**Q3. To decide the suffix, the code does `cmds.listRelatives(obj, children=True)` and, if there's
exactly one child, calls `cmds.objectType(child)` on the *child* — not on `obj`. Why not just ask
`objectType(obj)`?**
Because for a transform node, `objectType` returns `"transform"`, which tells you nothing useful about
the *content*. The real type (`mesh`, `joint`, `camera`, `nurbsCurve`) lives on the **shape** below the
transform. So the code peeks at the single child shape to read the true type. The `len(children) == 1`
guard is a simplification: it only trusts the shape when there's exactly one (a typical
transform-with-one-shape setup, e.g. a mesh or curve); with zero or multiple children it falls back to
`objectType(obj)`. Joints and locators are handled correctly by that fallback — a joint reports
`objectType == "joint"` and a locator (no shape) reports `"transform"` → `else` → `grp`, both without
needing the shape peek.

**Q4. `renamer1` skips cameras with a hard-coded `elif objType == 'camera': continue`, but `renamer2`
stores `"camera": None` in the `SUFFIXES` dict. Why?**
Same behavior, better mechanism. In `renamer2`, `None` is a **sentinel value**: `SUFFIXES.get("camera")`
returns `None`, and the next line — `if not suffix: continue` — treats falsy values (`None`, `""`) as
"skip this type." So "skip cameras" becomes **data in the dict** instead of **code in a branch**. The
practical win: to make cameras get a `_cam` suffix instead of being skipped, you change one dict entry
(`None` → `"cam"`) and touch no logic — which is exactly the "edit data, not code" benefit the dict buys
you.

**Q5. `renamer1` uses the current selection and only falls back to the whole scene if the selection is
empty. `renamer2.rename()` *defaults* to the whole scene and raises if you ask for the selection with
nothing picked. Why flip the default?**
Explicit over implicit. `renamer1`'s silent fallback is convenient but **dangerous**: an empty
selection quietly renames *everything*, which on a 10,000-node rig is a catastrophe you can't easily
undo. `renamer2` makes the choice a required, named argument (`selection=False` means "yes, the whole
scene, on purpose"), and refuses to guess when you pass `selection=True` with nothing selected — it
raises `RuntimeError` instead. The function forces you to say what you mean.

**Q6. `renamer2` always passes `dag=True` to `cmds.ls` (line 52), but `renamer1` only uses `dag=True` in
its empty-selection fallback (its primary `ls` on line 12 has no `dag=True`). What changes?**
`dag=True` tells `ls` to **descend the DAG**. So `renamer2.rename(selection=True)` processes the
selected objects **plus all their DAG descendants** (child shapes, child transforms, etc.), whereas
`renamer1` with a selection processes **exactly** the selected objects and no more. In practice this
means `renamer2` can rename a shape node directly (it's a DAG descendant of the selected transform),
while `renamer1` with a selection never reaches the shape. With `selection=False`, both enumerate the
whole DAG — `renamer2` via the always-on `dag=True`, `renamer1` via the fallback's `dag=True`.

**Q7. `renamer1` calls `cmds.rename(obj, newName)` with the **full path**, but `renamer2` calls
`cmds.rename(shortName, newName)` with the **bare leaf name**. Which is safer?**
The full path (`renamer1`) is **unambiguous**: `|grp|parent|child` names exactly one node. The bare
short name (`renamer2`) is **ambiguous** if two objects share the same leaf name (e.g. two `pCube1`
under different parents) — `cmds.rename("pCube1", ...)` may rename the wrong one or raise. `renamer2`
mitigates this with its `dag=True` enumeration and longest-first sort, and rewrites its internal list
after each rename (`objects[index] = obj.replace(shortName, newName)`) to keep paths fresh, but it does
not fully eliminate the ambiguity. A hardened version would rename by full path throughout (see
Advanced Directions).

**Q8. `renamer2` has `if shortName.endswith('_'+suffix): continue` before renaming. What is it for, and
does `renamer1` have the same protection?**
**Idempotency:** if an object is already correctly named (`cube_geo`), skip it so you don't get
`cube_geo_geo` on a second run. `renamer2` **has** this guard; `renamer1` **does not** — so running
`renamer1` twice on the same scene appends a second suffix every time. This alone is a strong reason to
prefer `renamer2` for real work. (The guard is also case-sensitive: `_GEO` would slip through. The
demo's README suggests `shortName.lower().endswith('_'+suffix)` to fix that.)

**Q9. `renamer_numbered` uses `enumerate(selection, start=1)` and skips cameras with `continue`. If a
camera is in the middle of the selection, what happens to the `ctrl_01`, `ctrl_02`, … numbering?**
The index **still increments** on the skipped camera, leaving a **gap**. `enumerate` counts every item
it visits, whether or not the loop body `continue`s past it. So a selection of `[curve, camera, curve]`
produces `ctrl_01_ctrl` and `ctrl_03_ctrl` — `02` is "used up" by the skipped camera and never appears.
This is usually fine (you wanted to skip the camera), but if you need gap-free numbering you'd have to
increment a separate counter only inside the non-skipped branch.

**Q10. `renamer_numbered` has a `nurbsCurve → ctrl` case. What happens to a NURBS-circle control in
`renamer1` or `renamer2`, and how would you fix it?**
In `renamer1`/`renamer2` a NURBS curve is **not** mesh/joint/camera, so it falls through to `else` /
`DEFAULT` and becomes `control_grp` — misleading, since it's a control, not a group. `renamer_numbered`
shows the fix pattern: add a `nurbsCurve` case. For `renamer2` specifically, you add **one line to the
dict** — `SUFFIXES = {"mesh":"geo", "joint":"jnt", "camera":None, "nurbsCurve":"ctrl"}` — and the
`.get()` lookup does the rest, no other code changes. That's the dict-as-config payoff: extending the
type table is a data edit, not a code edit.

---

## Advanced Directions

These files teach the fundamentals but stop short of production use. Here are concrete ways to evolve
the demo — each lists the new functions/classes it would require.

1. **Make the suffix table a user-editable config, plus prefix and side tokens.** The `SUFFIXES` dict is
   hard-coded in the module; a real naming convention also wants prefixes (`char1_`) and side tokens
   (`_L`/`_R`/`_C`). Move the rules into a `RENAMER_CONFIG.json` and extend the signature to
   `rename(selection=False, prefix='', side='', config=None)`. New code: `load_config(path)`, a
   `NameParts` dataclass (`{prefix, base, side, suffix}`), and a `build_name(parts)` builder that
   assembles the final string. This turns "rename by type" into "rename to a full convention."

2. **Add undo-chunk, dry-run, and a structured return.** Right now each `cmds.rename` is its own undo
   step (removing a batch = dozens of Ctrl+Z), and the function returns only a list of strings. Wrap
   the loop in an `undo_chunk()` context manager so the whole batch is one undo; add a `dry_run=True`
   mode that prints the planned `(old → new)` pairs without renaming; and return a list of
   `RenameRecord(old, new, type, suffix)` dataclasses instead of bare strings. New code: a
   `@contextmanager undo_chunk()` (wrapping `undoInfo(openChunk=True)` / `closeChunk=True` in a
   `try/finally`), the `RenameRecord` dataclass, and a `build_undo_log(records)` helper for one-click
   reversal.

3. **Harden the rename itself: full-path, namespace-aware, and reference-safe.** Replace the bare
   `cmds.rename(shortName, ...)` with a `safe_rename(full_path, new_name)` that resolves the node
   unambiguously, strips/honors namespaces, and detects **referenced or locked** nodes (which
   `cmds.rename` will refuse or silently skip) — warning instead of failing mid-batch. New code:
   `safe_rename()`, a `LockedNodeWarning` exception, and a `resolve_namespace(obj)` helper. This
   addresses the ambiguity bug from Q7 and makes the tool safe on referenced rigs.

4. **Wrap it as an installable package + shelf tool with a PySide2/6 UI.** Today users must
   `sys.path.insert` and `import` by hand. Turn the demo into a package (`objectrenamer/` with
   `__init__.py`, `renamer.py`, `config.json`, `ui.py`) installable with `pip install -e .` against
   Maya's interpreter, then add a shelf button calling `import objectrenamer; objectrenamer.show_ui()`.
   The UI shows a table of every type→suffix mapping (editable, saved back to `config.json`), a
   prefix/side field, a dry-run toggle, and a live preview list of `(old → new)` before you hit Apply.
   New code: `pyproject.toml`, the `RenamerUI(QWidget)` view (model/view split mirroring
   `controllerLibrary/`), and a `showUI()` that retains the window reference per the repo's UI-launch
   convention.

5. **Extend to a full scene naming-convention auditor.** Instead of only renaming, scan the **whole
   scene** and *report* violations: objects missing a suffix, wrong type for their suffix, wrong
   prefix, non-conforming names, duplicate names — then offer a one-click batch fix. New code: a
   `NamingConvention` rules engine (`check(node) -> list[Violation]`), an `audit_report()` that walks
   `cmds.ls(long=True, dag=True)` and collects violations, and a `batch_fix(violations, dry_run=...)`
   that applies the fixes through the hardened `safe_rename()`. This is the bridge from "rename tool"
   to "rig-QA tool."
