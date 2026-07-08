# HowToStart — mathTableControl

> A **plug-in** (not a script) that registers a custom Maya command,
> `spMathTableControl`, which builds a 5×3 table widget whose cells are filled
> on demand by Python callbacks. It is the canonical reference for the
> `MPxControlCommand` + `MPxUITableControl` pattern — the only way, in Python,
> to author a fully custom Maya UI control that behaves like a native widget.

This is the curriculum's **first plug-in demo** and the most advanced one in the
basic set. Unlike every demo so far (scripts and definitions-only libraries),
this file is *loaded* by Maya's plug-in manager and exposes a brand-new
command; it is never `import`-ed and called like a normal module.

---

## Files in this demo

| File | Role |
|------|------|
| `mathTableControl.py` | The plugin source. Defines two `MPx` classes, four command flags, three cell-computing lambdas, the `kPythonPtrTable` pointer bridge, and the `initializePlugin` / `uninitializePlugin` lifecycle hooks. |

> **`_2027` convention note:** there is **no `_2027` sibling** for this demo.
> `mathTableControl.py` is the verbatim, version-neutral Autodesk API 1.0
> original (its only dependency is `maya.OpenMaya[MPx][UI]`, unchanged across
> modern Maya versions). The guide targets `mathTableControl.py` directly.

## Prerequisites

Before this demo you should already be comfortable with:

- Maya **command plugins** — the `MPxCommand` + `initializePlugin` /
  `uninitializePlugin` lifecycle, and the Plug-in Manager / `loadPlugin` /
  `unloadPlugin` workflow. (Maya docs → *Writing Commands*, *Loading Plug-ins*.)
- The `MPx` **proxy-class** idea — Python subclasses of C++ base classes that
  Maya instantiates and calls back into. (Maya docs → *Proxy Classes Overview*.)
- Basic `cmds` UI (`cmds.window`, `cmds.columnLayout`, `cmds.showWindow`) — see
  `introduction/helloCube.py`.
- **API 1.0** basics (`maya.OpenMaya`, `MScriptUtil`) — see
  `../cameraMessageCmd/` and `../manipulatorMath/`.

> ⚠️ If command plugins or `MPx` classes are new, do `cameraMessageCmd` and
> `manipulatorMath` first and come back. This example is genuinely advanced.

## What the code actually does

The file has three logical parts and the standard plugin entry points.

### Part 1 — the command: `MathTableControlCmd(MPxControlCommand)`

Registered as the `spMathTableControl` Maya command.

| Member | What it does |
|--------|--------------|
| `makeControl()` | Called when the command **creates** the widget. Builds a `MathTableControl`, sets the default operation to `kNop`, sets **5 rows × 3 columns** (`setNumberOfRows(5)`, `setNumberOfColumns(3)`), and returns it wrapped in `asMPxPtr(control)` so Maya owns it as a C++ pointer. |
| `doEditFlags()` | Called when the command is run in **edit** mode with flags. Reads the parser, looks the control back up from `kPythonPtrTable`, then — in an `if/elif` chain — honors exactly **one** flag: `-nop` → `kNop`, `-mul` → `kMult`, `-add` → `kAdd`, `-rd` → `redrawCells()` + `redrawLabels()`. Unmatched flags delegate to the parent. |
| `doQueryFlags()` | Delegates straight to the parent. **There are no queryable flags** — this plugin is edit-only. |
| `appendSyntax()` | Declares the four flags (`-nop/-noOperation`, `-mul/-multiplyVals`, `-add/-addVals`, `-rd/-redraw`) so Maya's command parser knows they exist. |

### Part 2 — the widget: `MathTableControl(MPxUITableControl)`

The actual table. Maya calls back into it lazily.

| Member | What it does |
|--------|--------------|
| `cellString(row, column, isValidCell)` | Maya calls this **per visible cell, on demand**. Runs the current operation lambda `(row, column)` to get a string, writes a validity bool into `isValidCell` via `MScriptUtil.setBool`, and returns the string. If no operation is set the result is `""` and the cell is marked invalid/empty. |
| `labelString(labelType, index)` | Returns the header text: `"[Row N]"` for a row label, `"[Col N]"` for a column label, `""` otherwise. Indices are 0-based. |
| `setOperation(op)` | Stores the new lambda in the name-mangled `self.__myOperation` and immediately calls `self.redrawCells()` so the table re-fetches every visible cell. |
| `__init__` / `__del__` | Register / deregister `self` in `kPythonPtrTable` keyed by `asHashable(self)`. |

### Part 3 — the bridge: `kPythonPtrTable`

```python
kPythonPtrTable = {}                                   # module-level dict
kPythonPtrTable[asHashable(self)] = self               # in MathTableControl.__init__
theControl = kPythonPtrTable.get(asHashable(self._control()), None)   # in doEditFlags
```

Because `makeControl` returns `asMPxPtr(control)`, the Python object you wrote
is handed to Maya as a raw C++ pointer and is no longer reachable through Maya.
To call methods on it later (from `doEditFlags`), you must look it back up by
hashing the control pointer. **This is the single most important idiom to
internalize for any Python `MPx` UI plugin.**

### The three operations and four flags

```python
kNop  = lambda x, y: "cell(%d,%d)" % (x, y)   # default: label the cell
kMult = lambda x, y: str(x * y)               # row * column
kAdd  = lambda x, y: str(x + y)               # row + column
```

| Flag (short / long) | Effect |
|---------------------|--------|
| `-nop` / `-noOperation` | Cells show `cell(row,col)` strings (the default). |
| `-mul` / `-multiplyVals` | Cells show `row * column`. |
| `-add` / `-addVals` | Cells show `row + column`. |
| `-rd` / `-redraw` | Force a repaint of cells **and** labels without changing the operation. |

### Plugin lifecycle hooks

| Function | What it does |
|----------|--------------|
| `cmdCreator()` | Factory Maya calls to build the command object; returns `asMPxPtr(MathTableControlCmd())`. |
| `initializePlugin(mobject)` | Registers the command under `kPluginCmdName = "spMathTableControl"` via `MFnPlugin.registerControlCommand`. |
| `uninitializePlugin(mobject)` | Deregisters the command. |

> **The `self._parser()`, `self._control()`, `self._syntax()` calls** in
> `MathTableControlCmd` look private (leading underscore) but are the **official
> Python bridge** to C++ `protected` members of `MPxControlCommand`. They are
> meant to be called — the underscore is the standard SWIG convention for
> protected access, not a "don't touch" warning.

---

## How to Create the Test Maya Scene

> ⚠️ **No Maya scene is needed.** This is a UI plugin: it creates no nodes,
> reads no selection, and touches no DAG. The only "scene state" is an **empty,
> interactive Maya session** with the plugin loaded. (Consistent with
> `commandLine` / `fileDialog` / `manipulatorMath`, which also need no scene —
> though each for a different reason.)

What you **do** need to set up:

1. **Start interactive Maya** (the desktop application, *not* `mayapy`). The
   `MPxUITableControl` only renders inside Maya's UI layer; a headless `mayapy`
   run can load the plugin but cannot show a window.
2. **Know the plugin's on-disk path.** For this guide that is
   `/abs/path/PythonForMayaSamplesLearn/mathTableControl/mathTableControl.py`.
   (The README uses a Windows example `D:/2026MayaPython/...`; substitute your
   own absolute path.)
3. **Optional — put it on `MAYA_PLUGIN_PATH`.** If the folder is on that env
   var (or copied into Maya's plug-ins directory), you can load by bare name
   `mathTableControl.py`; otherwise load by full path.

That is the entire "scene". Everything below happens in the Script Editor.

---

## How to Run the Functions

This demo's "functions" are the plugin's lifecycle (load/unload) plus the
registered command and its four edit flags. **None of this can be verified
without Maya running** — every step below is marked as Maya-only.

### Step A — Load the plugin

In the Script Editor (Python tab):

```python
import maya.cmds as cmds
cmds.loadPlugin('/abs/path/PythonForMayaSamplesLearn/mathTableControl/mathTableControl.py')
```

(Equivalent: *Windows → Settings/Preferences → Plug-in Manager → Browse*,
check **Loaded**.) On success the command `spMathTableControl` now exists.
Confirm:

```python
print(cmds.spMathTableControl)   # <function spMathTableControl ...>
```

### Step B — Create the control inside a window

```python
import maya.cmds as cmds

win = cmds.window(title="Math Table", widthHeight=(420, 220))
cmds.columnLayout()
table = cmds.spMathTableControl()   # creates the widget; returns its UI path
cmds.showWindow(win)

print(table)   # e.g. 'Math Table|columnLayout|spMathTableControl1'
```

**Expected visible result:** a window containing a 5-row × 3-column table whose
cells show the default `kNop` output. Header labels read `[Row 0]`…`[Row 4]`
down the side and `[Col 0]` `[Col 1]` `[Col 2]` across the top.

The exact `kNop` cell contents (0-based indices):

| | Col 0 | Col 1 | Col 2 |
|---|---|---|---|
| **Row 0** | `cell(0,0)` | `cell(0,1)` | `cell(0,2)` |
| **Row 1** | `cell(1,0)` | `cell(1,1)` | `cell(1,2)` |
| **Row 2** | `cell(2,0)` | `cell(2,1)` | `cell(2,2)` |
| **Row 3** | `cell(3,0)` | `cell(3,1)` | `cell(3,2)` |
| **Row 4** | `cell(4,0)` | `cell(4,1)` | `cell(4,2)` |

### Step C — Switch operations at runtime (edit mode)

While the window is still open, edit the existing control **by its UI path**:

```python
cmds.spMathTableControl(table, e=True, mul=1)   # row * column
```

**Expected result** — the table repaints with the product of the indices:

| | Col 0 | Col 1 | Col 2 |
|---|---|---|---|
| **Row 0** | 0 | 0 | 0 |
| **Row 1** | 0 | 1 | 2 |
| **Row 2** | 0 | 2 | 4 |
| **Row 3** | 0 | 3 | 6 |
| **Row 4** | 0 | 4 | 8 |

Then the other operations:

```python
cmds.spMathTableControl(table, e=True, add=1)   # row + column
```

| | Col 0 | Col 1 | Col 2 |
|---|---|---|---|
| **Row 0** | 0 | 1 | 2 |
| **Row 1** | 1 | 2 | 3 |
| **Row 2** | 2 | 3 | 4 |
| **Row 3** | 3 | 4 | 5 |
| **Row 4** | 4 | 5 | 6 |

```python
cmds.spMathTableControl(table, e=True, nop=1)   # back to cell(r,c)
cmds.spMathTableControl(table, e=True, rd=1)    # force a repaint of cells + labels
```

> **About edit-mode targeting.** Maya control commands, like the built-in
> `cmds.button(path, e=True, ...)`, edit by UI path — that is why we captured
> `table` in Step B and pass `table, e=True` here. The README shows a simpler
> bare form `cmds.spMathTableControl(mul=1)` which also works when only one
> control of this type exists (the command edits that instance); passing the
> explicit path is the robust pattern when more than one is open. (The exact
> "current-control" resolution is Maya-version-dependent — verify on yours.)

### Step D — Unload the plugin when done

```python
cmds.unloadPlugin('mathTableControl.py')
```

Close the window first if it is still open (unloading while a widget is alive
can error). After unload, `cmds.spMathTableControl` no longer exists.

---

## Question and Answer

**Q1. There's no `if __name__ == "__main__"` and nothing looks "callable" — how
do I even run this?**
You don't `import` it and you don't call functions on it. It is a **plugin**.
The entry point is `initializePlugin(mobject)`, which Maya invokes for you when
you `loadPlugin` the file. That call registers `spMathTableControl` as a new
Maya command; from then on you drive it through `cmds.spMathTableControl(...)`.

**Q2. The file is `mathTableControl.py` but the command is `spMathTableControl`
— why the mismatch?**
`kPluginCmdName = "spMathTableControl"`. The "sp" prefix is the Autodesk sample
convention. The **filename** is what you `loadPlugin`; the **command name** is
what you call. Mixing them up ("`cmds.mathTableControl()`") is the #1 first-hour
pitfall — and the source of the demo's own README callout.

**Q3. What is `kPythonPtrTable` actually for? I can just keep a reference,
right?**
No — not after `makeControl`. It returns `asMPxPtr(control)`, which hands Maya a
raw C++ pointer; the Python `self` you wrote is now unreachable through Maya.
When `doEditFlags` later needs to call `setOperation` on that control, it must
re-find the Python object by hashing the control pointer:
`kPythonPtrTable.get(asHashable(self._control()), None)`. This side-table is THE
idiom for Python `MPx` UI code — memorize it.

**Q4. What happens if I pass `-mul` and `-add` in the same call?**
Only `-mul` is honored. `doEditFlags` is an `if/elif` chain in the order
**nop → mul → add → redraw**, so the first flag that is set, in that order,
wins. `mul` therefore beats `add` beats `nop`; `-rd` (redraw) only fires when
*none* of the three operation flags are present.

**Q5. If `setOperation` already calls `redrawCells()`, why does the `-rd` flag
exist?**
`-rd` is for the case where the **operation did not change** but the underlying
data did (imagine a lambda that reads from a shared list you just edited).
Because the operation lambda is identical, `setOperation` would be a no-op, so
you need an explicit `-rd` to force Maya to re-fetch every visible cell — and
uniquely it also repaints the labels (`redrawCells()` **+** `redrawLabels()`).

**Q6. Why does the whole table recompute when I switch operations?**
`cellString` is **lazy** — Maya invokes it per *visible* cell on each paint,
asking the current operation lambda for that `(row, column)`. `setOperation` +
`redrawCells` simply marks the cached cell data stale, so the next paint
re-queries each visible cell with the new lambda. This is why huge tables stay
cheap: off-screen cells are never computed.

**Q7. What is the `isValidCell` argument, and why would a cell be "invalid"?**
`cellString` must signal, through `MScriptUtil.setBool(isValidCell, ...)`,
whether the returned string is real content. The demo sets it to
`bool(result)`: a non-empty string → valid cell; an empty string (no operation
set, or an operation that returned `""`) → Maya treats the cell as blank. It is
how you tell Maya "this cell has nothing to show."

**Q8. The first row is all zeros for `-mul` — are the indices 1-based or
0-based?**
**0-based.** Maya passes raw 0-based `row`/`column` to both `cellString` and
`labelString`, and `kMult = lambda x, y: str(x*y)` uses them directly, so
`row 0 * anything = 0`. Even the labels say `[Row 0]` and `[Col 0]`. To display
1-based values, add inside the lambda, e.g.
`lambda x, y: str((x + 1) * (y + 1))`.

**Q9. Why does `-q` (query) on any flag return nothing useful?**
`doQueryFlags` is a one-liner that delegates to the parent, and `appendSyntax`
declares no queryable behavior for any flag. This plugin is **edit-only** —
there is no way to ask "what is the current operation?" or "what is in cell
(2,1)?". Adding query support is a natural Advanced Direction.

**Q10. Can I load this under `mayapy` and see the window?**
You can **load** it under `mayapy` (useful as a smoke test that
`initializePlugin` runs and the command registers), but `MPxUITableControl`
only renders inside **interactive Maya**'s UI layer. A headless run loads the
plugin silently and creating the control produces no visible window. To *see*
anything you must be in the desktop application.

**Q11. The redraw long-flag constant is `kRedrawFlagLong` while the others are
`kNopLongFlag`/`kMultLongFlag`/`kAddLongFlag` — is that a bug?**
Cosmetic only. The naming pattern is inconsistent (`FlagLong` vs `LongFlag`)
but the constant is referenced consistently in `appendSyntax` (`kRedrawFlagLong`
on line 59), so it works. It is a tidy-up a learner could make without changing
behavior — a good first "safe edit" to build confidence.

---

## Advanced Directions

Each idea lists the concrete functions/classes it would add.

1. **Add a new operation flag (smallest end-to-end plugin edit).**
   Define `kSquare = lambda x, y: str(x * x)`, add `kSqFlag = "-sq"` /
   `kSqLongFlag = "-square"` and a `theSyntax.addFlag(...)` line in
   `appendSyntax`, and wire an `elif theParser.isFlagSet(kSqFlag)` branch into
   `doEditFlags`. This touches all three overrideable methods in one change and
   is the best confidence check that you understand the flag lifecycle.

2. **Read labels from real data — a spreadsheet-style attribute editor.**
   Replace the hard-coded `"[Row N]"` / `"[Col N]"` in `labelString` with names
   pulled from lists: joint names down the rows, attribute names across the
   columns. New API on `MathTableControl`: `setRowLabels(list)`,
   `setColumnLabels(list)`, and have `cellString` index
   `self.__rowLabels[row]` × `self.__colLabels[column]` to look up a live
   `cmds.getAttr` value. You now have the skeleton of a custom Attribute
   Spread Sheet.

3. **Make cells editable (turn the read-only demo into a data-entry widget).**
   `MPxUITableControl` supports a cell-change callback the demo does not use.
   Override it so an edited value is printed and stored in a backing
   `self.__cells` dict keyed `(row, column)`; have `cellString` prefer the dict
   over the lambda when a cell has been hand-edited; add a `-c/-commit` flag in
   `appendSyntax` + `doEditFlags` that writes the dict back to the scene inside
   an `cmds.undoInfo(openChunk=True)` / `closeChunk()` pair. *(The exact
   cell-change callback name/signature is defined by the base class and not
   exercised in this file — confirm it in the Maya API reference before wiring.)*

4. **Add queryable state.**
   Implement a real `doQueryFlags` plus query-declared flags: `-qop/-queryOperation`
   returns the current operation's name, `-qn/-queryNumCells` returns
   `rows × columns`, and a `-qc/-queryCell` flag with two integer arguments
   returns one cell's string. This requires `appendSyntax` to mark the flags
   queryable and `doQueryFlags` to `setResult(...)` — filling the gap called
   out in Q9.

5. **Drive it from a live selection (an attribute-matrix editor).**
   Rows = currently selected nodes, columns = their keyable attributes, cells =
   live values. New methods on the control: `refreshFromSelection()` (populate
   the label lists from `cmds.ls(sl=True)` + `listAttr(keyable=True)`), and make
   `cellString` call `cmds.getAttr` and the cell-change callback call
   `cmds.setAttr` (wrapped in an undo chunk). Add a `-ref/-refresh` edit flag so
   a shelf button can rebuild the table when the selection changes.

6. **Port to OpenMaya API 2.0.**
   Rewrite the control/command against `maya.api.OpenMayaUI.MPxUITableControl`
   / `maya.api.OpenMayaMPx.MPxControlCommand` instead of the API 1.0 classes.
   The `kPythonPtrTable` + `asMPxPtr` / `asHashable` bridge and the lazy
   `cellString` / `labelString` overrides stay conceptually identical; the main
   changes are the imports and (in API 2.0) the cleaner
   `MScriptUtil`-free argument handling. Note for the curriculum: this demo is
   the API 1.0 reference; `manipulatorMath` and the Advanced set cover API 2.0.

---

## Source

- **Source code:** `mathTableControl.py` is the verbatim official Autodesk Maya
  Python API 1.0 example `python/api1/mathTableControl.py`, Maya 2027 (ENU) API
  reference:
  <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2math_table_control_8py-example.html>.
- **Verification:** the kNop/kMult/kAdd cell grids and the `[Row N]`/`[Col N]`
  labels were hand-derived by tracing `cellString`/`labelString` against the row
  and column indices, and the single-flag-per-call priority (mul>add>nop>rd) was
  read from the `doEditFlags` if/elif chain. The plugin load, `createNode`, and
  control evaluation require a running Maya to execute and are marked as such.
