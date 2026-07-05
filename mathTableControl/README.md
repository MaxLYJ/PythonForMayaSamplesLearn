# mathTableControl — A Custom Maya UI Table Control (Plugin, API 1.0)

This demo comes from the official Maya Python API documentation.

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2math_table_control_8py-example.html>

This is a **plug-in** — not a script. It registers a new Maya command,
`spMathTableControl`, that builds and manages a custom table widget driven by
Python callbacks. It's the canonical reference for the
**`MPxControlCommand` + `MPxUITableControl`** pattern: the only way (in Python)
to author a fully custom Maya UI control that behaves like a native widget.

> ⚠️ This is an **advanced** example. It is *not* a beginner script — it
> assumes you understand command plugins, MPx classes, and Maya UI basics.
> If those are new, start with `cameraMessageTest` and come back here.

---

## What you will learn

1. **`MPxControlCommand`** — the base class for commands that *create and
   manage* a custom UI control. You register it once and then a new Maya
   command appears that builds your widget.
2. **`MPxUITableControl`** — the base class for the control itself. You
   subclass it and override `cellString(...)` / `labelString(...)` to provide
   cell/label data on demand (lazy evaluation, just like `scriptTable`).
3. **The control command ↔ control lifecycle** — how `makeControl()` builds
   the widget, `doEditFlags` reacts to flag changes at runtime, and the
   command and control stay linked via a Python pointer table.
4. **The `kPythonPtrTable` pattern** — a workaround for the fact that
   `MPxUITableControl` instances get handed to Maya as raw pointers, so you
   need a side-table keyed by `asHashable(self)` to get back the Python
   object. This is an essential idiom for Python MPx UI code.
5. **Lazy cell evaluation** — cells are computed on demand via your
   `cellString` callback, not pre-stored. This scales to huge tables.

---

## Prerequisites

| Concept                            | Where to learn it                                                                 |
|------------------------------------|-----------------------------------------------------------------------------------|
| Maya command plugins (`MPxCommand`) | Maya docs → *Writing Commands*                                                    |
| `MPx` proxy classes                | Maya docs → *Proxy Classes Overview*                                              |
| Maya UI basics (`cmds.window`, …)  | `introduction/helloCube.py` for `cmds`; Maya docs → *UI Elements*                 |
| OpenMaya API 1.0                   | [`../cameraMessageCmd/cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md) |
| Plug-in load/unload workflow       | Maya docs → *Loading Plug-ins* (Plug-in Manager, `loadPlugin`, `unloadPlugin`)   |

You should already be comfortable writing a basic `MPxCommand` plugin before
tackling this — `MPxControlCommand` builds directly on top of it.

---

## Files

```
mathTableControl/
├── README.md                ← this file
└── mathTableControl.py      ← the plugin source
```

The `.py` is bundled here directly (it's a public Autodesk docs listing).

---

## Architecture: the three pieces

The plugin has three logical parts. Read the file in this order:

### 1. `MathTableControlCmd(OpenMayaMPx.MPxControlCommand)` — the command

This is what gets registered as the `spMathTableControl` command. It does
three things:

- **`makeControl()`** — called when the user runs the command. Builds a
  `MathTableControl`, sets a default operation and the initial row/column
  count (5 rows, 3 columns), and hands it back to Maya as an MPx pointer.
- **`doEditFlags()`** — reacts to flags the user passes at runtime
  (`-nop`, `-mul`, `-add`, `-rd`). Each flag swaps the operation lambda or
  forces a redraw.
- **`appendSyntax()`** — declares those four flags so Maya's command parser
  knows they exist.

### 2. `MathTableControl(OpenMayaMPx.MPxUITableControl)` — the widget

This is the actual table. It overrides two callbacks:

- **`cellString(row, column, isValidCell)`** — Maya calls this *lazily* for
  each visible cell. It invokes the current operation lambda
  (`kNop` / `kMult` / `kAdd`) and writes whether the result is a valid cell
  via `MScriptUtil.setBool`.
- **`labelString(labelType, index)`** — provides row/column header labels
  (`[Row N]` / `[Col N]`).

The `__myOperation` attribute holds whichever lambda was last set, and
`setOperation(...)` swaps it and triggers a redraw.

### 3. `kPythonPtrTable` — the pointer-to-Python bridge

```python
kPythonPtrTable = {}
# ...
kPythonPtrTable[OpenMayaMPx.asHashable(self)] = self
```

This is the **most important pattern to internalize**. When you call
`asMPxPtr(control)` in `makeControl`, you hand Maya a raw pointer and lose
direct access to the Python object. To call methods on it later (from
`doEditFlags`, for example), you have to look it back up by hashing the
control pointer:

```python
theControl = kPythonPtrTable.get(OpenMayaMPx.asHashable(self._control()), None)
```

`__del__` removes the entry so the table doesn't leak across control
lifetimes.

> **Why this matters:** In C++ you'd just keep a pointer. In Python, the
> MPx object handed to Maya isn't the same Python object you wrote — you
> need this side-table to "find yourself" again. Memorize this idiom; it
> appears in every Python MPx UI plugin.

---

## The four operations (lambdas)

```python
kNop  = lambda x, y: "cell(%d,%d)" % (x, y)    # default: just label the cell
kMult = lambda x, y: str(x * y)                # multiply row by column
kAdd  = lambda x, y: str(x + y)                # add row and column
```

The "math" in `mathTableControl` is just these three lambdas — they take a
`(row, column)` and return a string. The point isn't the math; the point is
that the **operation is swappable at runtime** by passing different flags.

---

## How to build and run it

### 1. Save the file somewhere Maya can load it

Either place `mathTableControl.py` in Maya's plug-ins directory, or add its
folder to `MAYA_PLUGIN_PATH`. (A simple alternative: use the full path when
loading.)

### 2. Load the plugin

In Maya, either:

- **Plug-in Manager** (`Windows → Settings/Preferences → Plug-in Manager`),
  browse to `mathTableControl.py` and check *Loaded*, **or**

- in the Script Editor:
  ```python
  import maya.mel as mel
  mel.eval('loadPlugin "D:/2026MayaPython/mathTableControl/mathTableControl.py"')
  # or, if it's on MAYA_PLUGIN_PATH:
  import maya.cmds as cmds
  cmds.loadPlugin('mathTableControl.py')
  ```

### 3. Create the control inside a window

```python
import maya.cmds as cmds

win = cmds.window(title="Math Table", widthHeight=(400, 200))
cmds.columnLayout()
cmds.spMathTableControl()      # the command the plugin registered
cmds.showWindow(win)
```

You should see a 5×3 table. The default operation (`-nop`) shows
`cell(row,col)` strings in each cell.

### 4. Switch operations at runtime

While the window is open, run any of:

```python
cmds.spMathTableControl(mul=1)   # cells now show row*column
cmds.spMathTableControl(add=1)   # cells now show row+column
cmds.spMathTableControl(nop=1)   # back to cell(r,c)
cmds.spMathTableControl(rd=1)    # force a redraw
```

The table should recompute every cell on the next paint.

### 5. Unload when done

```python
cmds.unloadPlugin('mathTableControl.py')
```

---

## Key API reference links

- `OpenMayaMPx.MPxControlCommand` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_mpx_control_command.html>
- `OpenMayaMPx.MPxUITableControl` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_mpx_u_i_table_control.html>
- `OpenMayaMPx.asMPxPtr`, `OpenMayaMPx.asHashable` — Python-pointer helpers
- `maya.cmds.scriptTable` — the *non-plugin* alternative for simpler use cases

---

## When should you use this vs `cmds.scriptTable`?

Most of the time you don't need this plugin at all. Use the built-in:

```python
cmds.scriptTable(
    rows=5, columns=3,
    getCellCmd=lambda r, c: str(r * c),   # much simpler
    ...
)
```

Reach for `MPxControlCommand` + `MPxUITableControl` only when:

| You need…                                                      | Use                          |
|----------------------------------------------------------------|------------------------------|
| A quick table with a Python cell callback                      | `cmds.scriptTable`           |
| The table to behave like a native Maya widget in arbitrary UIs | this plugin pattern          |
| Tight integration with custom command flags / undo             | this plugin pattern          |
| To ship a table control that other tools install and reuse     | this plugin pattern          |

For 95% of tooling work, `cmds.scriptTable` is enough. This example is
mostly a reference for the rare cases that need the full MPx treatment.

---

## Things to try next (exercises)

1. **Change the default table size.** In `makeControl`, swap
   `setNumberOfRows(5)` / `setNumberOfColumns(3)` for larger values and
   confirm the table scales. The lazy `cellString` callback means even
   1000×1000 should be fine.
2. **Add a new operation.** Define `kSquare = lambda x, y: str(x*x)`, add a
   `-sq/-square` flag in `appendSyntax`, and wire it up in `doEditFlags`.
   This is the smallest end-to-end plugin edit and a great confidence check.
3. **Read row/column labels from real data.** Replace the `[Row N]` / `[Col N]`
   strings in `labelString` with names pulled from a list — e.g. joint names
   down the rows, attribute names across the columns. You've just built the
   skeleton of a spreadsheet-style attribute editor.
4. **Trace the pointer table.** Add `print(kPythonPtrTable.keys())` inside
   `doEditFlags` and watch entries appear when the control is created and
   disappear when it's destroyed. This is the clearest way to *see* the
   lifecycle the README describes.
5. **Port `cellString` to API 2.0.** Try rewriting just the control class
   using `maya.api.OpenMayaUI.MPxUITableControl`. Note what changes vs.
   API 1.0 — most of the bridge code stays the same.
6. **Make cells editable.** The base class supports a cell-change callback.
   Wire one up that prints the edited value and stores it in a dict. You've
   now turned the read-only demo into a real data-entry widget.

---

## Common pitfalls

* **Forgetting `asMPxPtr`.** Every `makeControl` must *return* an
  `asMPxPtr(control)`, not the raw Python object. If you return the Python
  object directly, Maya won't recognize it and the command will fail to
  build the widget.
* **Losing your Python object.** After `asMPxPtr`, the `self` you wrote is
  no longer reachable through Maya. Always add to `kPythonPtrTable` in
  `__init__` and look it back up via `asHashable(self._control())` when you
  need it. Forgetting this is the #1 cause of "method not found" errors.
* **`__del__` cleanup is not optional.** If you skip the `del
  kPythonPtrTable[...]` line, the table grows forever as users open and
  close windows. Treat it as mandatory.
* **Flags must be declared in `appendSyntax`.** A flag that isn't added to
  `self._syntax()` will be silently ignored — Maya's parser won't know it
  exists. If your `-mul` does nothing, check syntax first.
* **The plugin name is `spMathTableControl`, not `mathTableControl`.** The
  Python filename and the registered command name are different. You load
  the *file* `mathTableControl.py`; you call the *command*
  `cmds.spMathTableControl(...)`. Don't confuse them.
* **Lambdas receive raw row/column ints.** `kMult = lambda x, y: str(x*y)`
  uses zero-based indices. If you want 1-based display values, add 1
  inside the lambda.
* **You need Maya, not `mayapy`, to *see* anything.** The plugin runs under
  `mayapy` for load testing, but the UI only renders in the interactive
  Maya application. Don't expect a window from a headless run.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — python/api1/mathTableControl.py*,
Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2math_table_control_8py-example.html>
