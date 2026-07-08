# HowToStart — fileDialog

This is the curriculum's first **disk / OS-interaction** demo, and it is
unusual: the only `.py` file (`script.py`) is **literally one line** —
`print("Hello world!")`. That is not a mistake and not a stub to "finish later";
it is the *complete, verbatim* official Autodesk example. The real lesson lives
in the **`fileDialog2` workflow you write *around* the file**, not in the file
itself.

So think of this demo as two things:

1. **`script.py`** — a harmless *fixture*: a safe file on disk for the file
   dialog to point at.
2. **The workflow** (which you type into the Script Editor) — pop a native OS
   file picker with `cmds.fileDialog2`, get the chosen path back, then *do
   something* with it (read it, run it, import it, save to it). That
   **"pick → get path → act"** pattern is the backbone of every file-driven
   Maya tool — importers, exporters, library loaders, batch processors.

This is **pure `maya.cmds`** — no OpenMaya API and no Qt required.

---

## Files in this demo

| File        | What it is                                                                       | Run it how                                       |
|-------------|----------------------------------------------------------------------------------|--------------------------------------------------|
| `script.py` | The demo — **one line: `print("Hello world!")`.** A safe pick-target fixture.    | Paste the line in the Script Editor, or `exec()` the picked path. |
| `README.md` | The workflow lesson: the `fileDialog2` wrapper code (not stored as a `.py`).      | Read for context; re-type the wrapper in the Script Editor. |

> **`_2027` convention — not needed here.** In the other demos `foo_2027.py` is
> the verified Python-3 copy. `fileDialog` has **no `_2027` sibling**: `script.py`
> *is* the verbatim modern Autodesk original, and because it is a single
> version-neutral `print`, it runs unchanged in any Maya and any Python. There is
> nothing to modernize, so this guide targets `script.py` directly.

## Prerequisites

- `maya.cmds` basics — see `introduction/helloCube.py`.
- Comfortable with Python strings and filesystem paths.
- ⚠️ **You do need Maya open** to run the `fileDialog2` wrapper (the dialog is a
  Maya command), but you do **not** need any particular scene — `fileDialog2`
  does not look at or change the scene. `script.py` itself can even be run in a
  plain Python REPL, since it is just `print`.

---

## What the code actually does

### `script.py` — a flat one-liner (the "introduction" archetype)

```python
print("Hello world!")
```

That is the entire file: one expression statement, **no** `import`, **no**
`def`, **no** class, **no** `if __name__ == '__main__'` guard. Running it prints
exactly one line. It is the same "flat top-to-bottom script" archetype as the
`introduction/` files — *not* the definitions-only-library archetype of
`objectRenamer`/`gearCreator`. Its only job is to be a **safe, harmless file**
the file dialog can pick and then `exec` without side effects.

### The real demo: the `fileDialog2` wrapper (you write this)

The actual lesson is not *in* `script.py` — it is the wrapper you type in the
Script Editor. The one command that matters:

```python
cmds.fileDialog2(fileMode=1, caption=..., fileFilter=...)
```

| Flag         | Verified meaning                                                                  |
|--------------|-----------------------------------------------------------------------------------|
| `fileMode`   | What the dialog lets the user do — see the cheat sheet below. **Most important flag.** |
| `caption`    | The window title bar text.                                                        |
| `fileFilter` | The dropdown filter, e.g. `"Python Files (*.py)"`. Multiple filters separated by `;;`. |
| *(return)*   | A **list of path strings** (even for a single pick). On **Cancel** it returns an **empty list `[]`** (see Q&A — this is where the README and the docs disagree). |

The command is flagged in the Autodesk reference as **"NOT queryable, NOT
editable"** — you cannot pass `-query`/`-edit` to it. It only ever *opens a
dialog and returns paths*; it never opens, saves, or imports the file for you.
**The file action is always a separate `cmds.file(...)` call you make with the
returned path.**

### The `fileMode` cheat sheet (verified against the Autodesk reference)

| `fileMode` | Meaning                                            | Typical use        |
|-----------:|----------------------------------------------------|--------------------|
| `0`        | Any file, existing or not (single) — used for **Save** | "Save As…" path    |
| `1`        | Single **existing** file                           | "Open…" one file   |
| `2`        | Any existing file, **multi-select** (returns a list) | Batch-open many    |
| `3`        | A single **directory**                             | "Pick a folder…"   |
| `4`        | Multiple directories (rarely used)                 | Batch folders      |

---

## How to Create the Test Maya Scene

> ⚠️ **No Maya scene is required for this demo.** Neither `script.py` nor the
> `fileDialog2` wrapper reads or changes the scene graph — `fileDialog2` only
> returns a filesystem path string. Keep this section's heading for consistency
> with the rest of the curriculum, but the honest setup is just: **open Maya**
> (any scene, or none). No objects to create, name, or select.

The only "fixture" you need is the demo file **on disk** — and it is already
there:

1. Open Maya. (Any scene is fine; an empty scene is fine too.)
2. Note the absolute path to this folder, e.g.
   `/abs/path/PythonForMayaSamplesLearn/fileDialog/script.py`. You will navigate
   the file dialog to this file in **Run B** below.

That is the entire setup.

---

## How to Run the Functions

Because `script.py` has no functions, there are **three** things worth running,
in increasing usefulness. Run all of them in the **Maya Script Editor**
(Python tab).

### Run A — just run the one-line file (the minimum)

Paste this in the Script Editor and run:

```python
print("Hello world!")
```

**Expected result (Script Editor output):**

```
Hello world!
```

That is the *entire* official example. Nothing else happens in the viewport or
outliner.

### Run B — the actual workflow: pick `script.py` and run it via the dialog

Paste this block and run it:

```python
import maya.cmds as cmds

# 1. Pop the native file dialog; let the user pick a .py file
path = cmds.fileDialog2(
    fileMode=1,                          # 1 = "select one existing file"
    caption="Pick a Python script",      # window title
    fileFilter="Python Files (*.py)",    # dropdown filter
)

# 2. fileDialog2 returns a LIST (even for one pick); empty list [] on Cancel
if path:
    path = path[0]                       # take the single chosen path
    print("You picked:", path)

    # 3. Act on the chosen path — here: read it and exec it.
    #    Picking script.py is what makes it print "Hello world!".
    with open(path) as f:
        code = f.read()
    exec(code)
else:
    print("User cancelled.")
```

**Steps:** a native OS file dialog opens titled *"Pick a Python script"*. Browse
to this folder and select `script.py`, then click **Open**.

**Expected result (Script Editor output):**

```
You picked: /abs/path/PythonForMayaSamplesLearn/fileDialog/script.py
Hello world!
```

The second line (`Hello world!`) is `script.py` itself executing — that is the
whole payoff of the demo: **the path the user picked got read off disk and run**.

If instead you click **Cancel**, the only output is:

```
User cancelled.
```

…because `path` is an empty list (falsy) and the `else` branch runs.

### Run C — variants worth trying

**Multi-select (fileMode=2)** — pick several files and loop:

```python
import maya.cmds as cmds
paths = cmds.fileDialog2(fileMode=2, caption="Pick several", fileFilter="Python Files (*.py)")
if paths:
    for p in paths:
        print("-", p)
```

Pick two or more `.py` files; each chosen path prints on its own line. This is
what confirms `fileDialog2` returns a **list**, not a single string.

**Pick a directory (fileMode=3)** and list its `.py` files:

```python
import maya.cmds as cmds, os
folders = cmds.fileDialog2(fileMode=3, caption="Pick a folder")
if folders:
    folder = folders[0]
    for name in sorted(os.listdir(folder)):
        if name.endswith(".py"):
            print(os.path.join(folder, name))
```

Pick this demo folder; it prints the absolute path to `script.py`. This is the
seed of a batch processor (see Advanced Directions).

---

## Question and Answer

**Q1. Why is `script.py` literally just `print("Hello world!")`? Isn't that a
stub someone forgot to finish?**
No — it is the *complete* official Autodesk example, kept tiny on purpose.
Autodesk's point is not to teach `fileDialog2` inside the file; it is to give
**other examples that say "select a script file" a safe file to point at**.
Treat `script.py` as a *fixture* (a do-nothing target), not a lesson. The lesson
is the dialog wrapper you type around it.

**Q2. `fileDialog2` returns a list even when I pick one file. Why `path[0]`?**
By design the command always returns a **string array** so the same return
shape works for single- and multi-select (`fileMode=1` vs `2`). For a single
pick the list has one element, so you take `path[0]`. If you write
`path.endswith(".py")` directly you will hit
`AttributeError: 'list' object has no attribute 'endswith'` — a classic trap the
README's pitfalls list calls out.

**Q3. The README says "if the user clicks Cancel, you get `None`." Is that
right?**
**No — for modern Maya it returns an *empty list* `[]`, not `None`.** This is
verified against the Autodesk command reference and matches the underlying Qt
`QFileDialog` ("if the user user presses Cancel, it returns an empty list").
The README's *example code* (`if path:`) is still correct because **both `[]`
and `None` are falsy**, so the branch behaves identically. The README's
`or []` idiom is therefore slightly redundant for the cancel case (cancel
already returns `[]`), but it is a harmless belt-and-braces guard that also
covers any old version that *did* return `None`. Bottom line: guard with `if
path:` / `if not paths:` and you are safe on every version.

**Q4. What is the difference between `fileMode=0` and `fileMode=1`?**
`0` = "**any** file, existing or not" (the user can type a brand-new name) —
this is the mode for **Save / Save As**, where the file does not exist yet.
`1` = "**existing** file only" — this is the mode for **Open**, where the dialog
should refuse a non-existent path. Picking the wrong one is the usual reason a
"save" dialog lets you open a missing file or an "open" dialog refuses your
typed name.

**Q5. The reference says `fileDialog2` is "NOT queryable, NOT editable." What
does that mean in practice?**
Unlike many `cmds` commands you cannot pass `-query` or `-edit` to it — there is
no node it edits, and nothing to query later. The command does exactly one
thing: **open a dialog and return the chosen path(s)**. It does **not** open,
import, or save the file — that is always a *separate* `cmds.file(path, i=True)`
(open/import) or `cmds.file(path, s=True)` (save) call you make with the
returned path. Beginners expect the dialog to "do the thing"; it never does.

**Q6. `fileDialog` vs `fileDialog2` — why the `2`?**
`fileDialog` (no `2`) is the **deprecated** older command: it returns a **bare
string**, cannot multi-select, and is kept only for old scripts. `fileDialog2`
is the maintained command: it returns a **list**, supports multi-select, and
gets new flags (`returnFilter`, `optionsUICommit`, …). Start every new tool with
`fileDialog2`.

**Q7. The example uses `exec(code)` to run the picked script. Is that safe?**
Only for a **personal** tool. `exec` runs *whatever* the file contains, with no
sandbox, so a malicious or buggy picked file runs with full Maya permissions.
For shared/shipped tools, prefer `importlib` (`spec_from_file_location` +
`exec_module`) so the source is at least a *traceable import* you can audit, or
— better — never execute picked files at all; only read data from them. The
demo's `exec` is fine precisely because `script.py` is a known-good fixture.

**Q8. How do I show multiple filters in the dropdown (e.g. "Maya Files" *and*
"All Files")?**
Separate filters with a double-semicolon `;;` — the Qt convention that
`fileDialog2` passes through:
`fileFilter="Maya Files (*.ma *.mb);;All Files (*.*)"`.
The dropdown then lets the user switch between the two. If you also pass
`returnFilter=True`, the command tells you *which* filter the user actually
picked — useful when one button should accept several formats but behave
differently per format.

**Q9. Do I need to worry about Windows backslashes in the returned path?**
A little. Maya accepts forward slashes `/` on every platform, and the returned
path on Windows will usually contain `\`, which can break f-strings and regex.
A cheap normaliser is `path.replace('\\', '/')`. For real path work prefer
`os.path` / `pathlib` rather than slicing raw strings.

**Q10. There is no `script_2027.py` here — every other demo has one. Why?**
The `_2027` files elsewhere are Python-3 modernisations of Python-2-style
originals. `fileDialog`'s official example is a single version-neutral `print`,
so there is **nothing to modernise** — `script.py` already runs in any Python.
This is the one demo where the "modern copy" and the "teaching original" are the
same file.

---

## Advanced Directions

These extend the bare "pick a path" idea into real tools. Each names the new
functions/classes it would need.

1. **A one-click "run picked script" shelf tool.** Wrap the Run B workflow in
   `def run_picked_script(file_filter="Python Files (*.py)")` that returns the
   exec'd module, and register it as a shelf button (`cmds.shelfButton`). Add an
   `cmds.undoInfo(openChunk=True/…)` pair around `exec` so a misbehaving script
   can be rolled back. This turns the demo into the "load-and-run any `.py`"
   tool the README's exercise #3 asks for.

2. **The standard "Browse…" export panel (UI + text field).** Combine
   `fileDialog2` with `cmds.window`/`cmds.rowLayout`/`cmds.textField`: a
   `browse()` callback pops the dialog and writes the returned path into the
   text field; a `do_export()` callback reads it back and calls
   `cmds.file(path, exportSelected=True, type='mayaAscii', ...)`. This is the
   look of essentially every Maya export tool and the natural home for a
   `fileMode=0` (Save) dialog.

3. **A directory-driven batch processor.** Use `fileMode=3` to pick a folder,
   then `os.walk`/`os.listdir` to find every `.ma`/`.mb` (or `.py`) file and
   loop: `for f in matches: process(f)`. New pieces: a `BatchProcessor`
   class with `collect(dir, exts)` and `run(on_each)`, plus an `importlib`-based
   `load_module_safely(path)` (instead of `exec`) so each processed file is a
   traceable import. Add a dry-run flag that prints the plan before touching
   anything.

4. **A config save/load utility.** `fileMode=0` to pick where to *write* a JSON
   config, serialise a dict of tool settings with `json.dump`, then `fileMode=1`
   + `json.load` to read it back. New pieces: `save_config(data, path=None)` and
   `load_config(path=None)` where a `None` path triggers the dialog. This is the
   skeleton the README's exercise #5 describes and the foundation of any
   preference-persisting tool.

5. **A multi-format import manager with `returnFilter`.** One dialog, several
   filters (`Alembic (*.abc);;FBX (*.fbx);;Maya (*.ma *.mb)`), and
   `returnFilter=True` so you learn *which* format the user picked and dispatch
   to the right importer (`cmds.file(path, i=True, type='Alembic', …)` etc.).
   New pieces: an `importers = {filter: handler}` registry and a
   `smart_import()` that pops the dialog, looks up the handler for the chosen
   filter, and calls it with `usingNamespaces=False` and an undo chunk.

6. **Undo- and error-safe wrapper around the whole pattern.** A
   `pick_and_act(file_mode, action, **dialog_kwargs)` helper that opens the
   dialog, returns early on cancel, normalises the path (`replace('\\','/')`),
   wraps `action(path)` in `try/except` + `cmds.undoInfo` chunk, and reports
   failures via `cmds.warning`. Every tool above then calls this one helper, so
   the cancel/normalise/undo/error handling lives in exactly one place.

---

## Source

- **Source code:** `script.py` is the verbatim official Autodesk Maya Python API
  1.0 example `python/api1/script.py` (a single `print` line), Maya 2027 (ENU)
  API reference:
  <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/file_dialog_2script_8py-example.html>.
  The actual lesson — the `cmds.fileDialog2` pick→get-path→act wrapper — is not
  stored as a `.py` at all; it lives only in `fileDialog/README.md`, so this guide
  re-types it in the Script Editor (see *How to Run the Functions*).
- **Verification:** `fileDialog2`'s Cancel return value (`[]`, not `None`) and its
  "not queryable, not editable" semantics were confirmed against the Autodesk
  command reference and the underlying Qt `QFileDialog` behavior, and the
  `if path:` / `or []` truthiness logic was checked in pure Python. Opening the
  native dialog and acting on the returned path require a running Maya and are
  marked as such.
