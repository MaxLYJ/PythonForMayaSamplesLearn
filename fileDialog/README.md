# fileDialog/script.py — Selecting a File with Maya's File Dialog

This demo comes from the official Maya Python API documentation.

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/file_dialog_2script_8py-example.html>

> ⚠️ **Important: read this first.** The `script.py` file in this folder is
> literally **one line**: `print("Hello world!")`. That is not a typo and not
> a mistake — it's the *entire* official Autodesk example. The real lesson is
> the **`fileDialog` workflow around the file**, not the file itself.

---

## What is this example actually about?

Autodesk ships this tiny `script.py` so you have a harmless "do-nothing" file
to **pick with the file dialog**. The value here is learning the workflow:

> *"How do I let a user choose a file on disk, then do something with the path
> they chose?"*

That workflow uses the `fileDialog` / `fileDialog2` **command** — not the API.
This `script.py` is just the *target* the user picks. Knowing that upfront
saves you scratching your head looking for hidden meaning in one print line.

---

## What you will learn

1. **`maya.cmds.fileDialog2`** — the modern Maya command that pops a native
   OS file picker and returns the chosen path(s). (Older `fileDialog` is
   deprecated; always prefer `fileDialog2`.)
2. **The "pick → get path → act" pattern** that every file-driven Maya tool
   follows (importers, exporters, library loaders, batch processors…).
3. **File dialog flags** — `fileMode`, `caption`, `fileFilter`, and how they
   shape the dialog the user sees.
4. **Why `script.py` is the way it is**: the world's smallest placeholder
   file, used purely as something safe to point the dialog at.

---

## Prerequisites

| Concept                | Where to learn it                                          |
|------------------------|------------------------------------------------------------|
| `maya.cmds` basics     | `introduction/helloCube.py`                                |
| Python strings / paths | standard Python tutorial                                   |
| Maya's command syntax  | Maya docs → *Python Commands*                              |

You do **not** need the OpenMaya API for this demo — it is pure `cmds`.

---

## Files

```
fileDialog/
├── README.md            ← this file
└── script.py            ← the demo (one line: print("Hello world!"))
```

The official `script.py` content is:

```python
print("Hello world!")
```

That's the whole thing. The point of *this* README is to make that useful.

---

## The actual workflow this example exists to teach

Here's how you would use `fileDialog2` to pick `script.py` (or any file) and
do something with it:

```python
import maya.cmds as cmds

# 1. Pop the native file dialog and let the user pick a .py file
path = cmds.fileDialog2(
    fileMode=1,                                   # 1 = "select existing file"
    caption="Pick a Python script",               # window title
    fileFilter="Python Files (*.py)",             # filter shown in the dropdown
)

# 2. fileDialog2 always returns a LIST (even for a single pick), or None
if path:
    path = path[0]
    print("You picked:", path)

    # 3. Do something with the chosen path.
    #    Here we just exec the script the user picked (this is what makes
    #    script.py print "Hello world!" when selected).
    with open(path) as f:
        code = f.read()
    exec(code)
else:
    print("User cancelled.")
```

Run this in the Maya Script Editor, then pick `script.py` from this folder.
The Script Editor will print:

```
You picked: D:/2026MayaPython/fileDialog/script.py
Hello world!
```

The `Hello world!` is `script.py` running — that's the whole demo.

---

## The `fileMode` cheat sheet

`fileMode` is the most important flag — it controls what the dialog lets the
user do. Memorize these four:

| `fileMode` | Meaning                                            |
|-----------:|----------------------------------------------------|
| `0`        | Save file (asks for a name, may overwrite)         |
| `1`        | Open existing file (single select)                 |
| `2`        | Open existing file (multi-select, returns a list)  |
| `3`        | Select a directory                                 |

`fileMode=4` also exists (multi-dir select) but is rarely used.

---

## `fileDialog` vs `fileDialog2`

You'll see both names floating around. Use `fileDialog2`.

|                     | `fileDialog` (deprecated) | `fileDialog2` (recommended)            |
|---------------------|---------------------------|----------------------------------------|
| Return type         | a single string           | a **list** of strings, or `None`       |
| Multi-select        | not supported             | supported                              |
| Status              | kept for old scripts      | actively maintained, new features      |

Always wrap the result of `fileDialog2` with a length check:

```python
result = cmds.fileDialog2(fileMode=1, ...) or []
```

The `or []` saves you from `NoneType has no len()` crashes when the user cancels.

---

## Things to try next (exercises)

1. **Make it print a real list of files.** Switch to `fileMode=2` and loop
   over every picked path, printing each one. Confirm you now get a list with
   more than one item.
2. **Add a real filter.** Try
   `fileFilter="Maya Files (*.ma *.mb);;All Files (*.*)"` and confirm the
   dropdown lets you switch between filters.
3. **Build a tiny "run script" tool.** Wrap the workflow above in a function
   `run_picked_script()` and add a shelf button for it. Now you have a
   one-click "load and run any .py" tool.
4. **Pick a directory, not a file.** Use `fileMode=3`, then list the folder
   contents with `os.listdir(path)` and print every `.py` file inside.
5. **Save a file.** Use `fileMode=0`, write the current scene name to the
   chosen path with `open(...).write(...)`, and read it back. You've just
   built the skeleton of a config-file save/load tool.
6. **Pair it with a UI.** Combine with `cmds.window` / `cmds.button` to make
   a small panel with a "Browse…" button that fills a text field with the
   picked path. This is the standard look of every Maya export tool.

---

## Common pitfalls

* **`fileDialog2` returns a list, not a string.** Even for a single file. If
  you do `cmds.fileDialog2(...).endswith(...)` you'll crash. Always `path[0]`.
* **Always handle cancellation.** If the user clicks Cancel, you get `None`.
  Guard with `if path:` or `or []` before indexing.
* **Use forward slashes.** Maya accepts `/` on all platforms; mixed `\` paths
  on Windows can break string formatting. `path.replace('\\', '/')` is a
  cheap safety net.
* **`fileDialog` (no 2) is deprecated.** Don't start new code with it. It
  returns a bare string and can't multi-select.
* **Don't `exec` untrusted code.** The demo above runs whatever the user
  picks — fine for a personal tool, dangerous if shipped to others. For
  shared tools, prefer `importlib` over `exec` so the source is at least
  traceable.

---

## Why is the official example so tiny?

Because Autodesk's point isn't to teach `fileDialog2` itself (that belongs in
the `fileDialog2` command docs). This example exists in the API reference so
that **other** examples that say "select a script file" have something to
point at. Treat `script.py` as a fixture, not a lesson — the lesson is the
dialog workflow you write *around* it.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — fileDialog/script.py*, Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/file_dialog_2script_8py-example.html>
