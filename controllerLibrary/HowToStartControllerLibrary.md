# HowToStart — controllerLibrary

This is the **Hour 6** demo: the first **PySide/Qt** tool in the curriculum,
and the most concept-dense so far. It is a real-world-style *controller
library* — save NURBS-curve rig controls to a disk library with thumbnail
previews, then import them back into any scene. Every rigging department has a
tool like this.

It also introduces two big ideas the earlier demos didn't have: **Qt signals &
slots** (the professional Maya UI model) and **model/view separation** (the
data class `ControllerLibrary` knows nothing about the window, so you can drive
it from a script with no UI at all).

---

## Files in this demo

| File                    | What it is                                             | Run it how                              |
|-------------------------|--------------------------------------------------------|-----------------------------------------|
| `controllerLibrary_2027.py` | Modern Python-3 / PySide6 version (the one to run) | `import` then call `showUI()`           |
| `controllerLibrary.py`      | Original Python-2-style file, identical body except the import line uses the `Qt.py` shim instead of `PySide6` | reference / pre-2022 Maya |

> **`_2027` convention:** throughout this repo, `foo_2027.py` is the verified
> Python-3 copy that runs in Maya 2022+; `foo.py` is the heavily-commented
> teaching original. This guide targets `_2027`. The two files here are
> **byte-identical except line 4/8** — `from PySide6 import …` (2027) vs
> `from Qt import …` (shim). All behaviour below applies to both.

## Prerequisites

- Maya 2022+ (PySide6 ships inside Maya — nothing extra to install). On older
  Maya use `controllerLibrary.py` + the `Qt.py` shim, or change the import to
  `from PySide2 import …`.
- The `controllerLibrary/` folder added to `sys.path` (shown below).
- ⚠️ **No Maya = no run.** This demo imports `maya.cmds` *and* `PySide6` at
  module top, so it can only be executed inside Maya's Script Editor (or
  `mayapy` with the GUI available). Nothing here was testable outside Maya.

---

## What the code actually does

Two classes plus one helper. **Running the file does nothing visible** — there
is no `if __name__ == '__main__'` guard and no module-level `showUI()` call, so
importing is silent. You must call `showUI()` (or build the classes yourself).

### `ControllerLibrary(dict)` — the data model (no UI)
A subclass of the built-in `dict`, so a library instance *is* the
`{name: info}` mapping and gets all dict methods for free.

| Method | Signature (verified) | What it does |
|--------|----------------------|--------------|
| `createDir` | `createDir(self, directory=DIRECTORY)` | `os.mkdir(directory)` if it doesn't exist. |
| `save` | `save(self, name, screenshot=True, directory=DIRECTORY, **info)` | Builds a record, **exports selection if any, else saves the whole file** as `<name>.ma`, optionally screenshots via `playblast`, writes `<name>.json`, stores `self[name]=info`. |
| `find` | `find(self, directory=DIRECTORY)` | Scans the directory, and for **every `.ma` file** reads its matching `.json` and stores `self[name]=data`. (Scans the *whole directory*, not one name.) |
| `load` | `load(self, name)` | `cmds.file(self[name]['path'], i=True, usingNamespaces=False)` — plain import, no parenting. |
| `saveScreenshot` | `saveScreenshot(self, name, directory=DIRECTORY)` | `viewFit`, set render format to jpeg (`imageFormat=8`), `playblast` a 200×200 jpg; returns the path. |

`DIRECTORY` is defined at module scope as
`os.path.join(cmds.internalVar(userAppDir=True), 'controllerLibrary')` — i.e.
`<your Maya user app dir>/controllerLibrary/`
(e.g. `~/maya/2027/controllerLibrary/` on Linux,
`C:/Users/<you>/Documents/maya/2027/controllerLibrary/` on Windows).

### `ControllerLibraryUI(QDialog)` — the Qt window (the view)
Builds a vertical layout with: a **name `QLineEdit` + `Save` button**, an
**icon-mode `QListWidget`** (64px icons, 76×76 grid), and a row of three
buttons **`Import!` / `Refresh` / `Close`**. Signals are wired as:

| Widget signal            | Connected slot        |
|--------------------------|-----------------------|
| `Save` `.clicked`        | `self.save`           |
| `Import!` `.clicked`     | `self.load`           |
| `Refresh` `.clicked`     | `self.populate`       |
| `Close` `.clicked`       | `self.close`          |

`populate()` clears the list, calls `self.library.find()`, then for each
`(name, info)` adds a `QListWidgetItem` whose tooltip is `pprint.pformat(info)`
and whose icon — **if** `info.get('screenshot')` is truthy — is
`QtGui.QIcon(screenshot_path)`.

### `showUI()` — the launcher
`ui = ControllerLibraryUI(); ui.show(); return ui`. It **returns** the instance
on purpose — see the GC pitfall below.

> ⚠️ **The repo's `README.md` describes a *different, aspirational* version of
> this tool** (a `delete()` method, a single `library.json` index, a `Delete`
> button, `load()` parenting under the current selection, a
> `save(name, directory, screenshot=path)` signature). **None of those exist in
> the actual `.py` files.** Trust the source, not the README. The divergences
> are called out individually in the Q&A.

---

## 1. How to Create the Test Maya Scene

The library writes to and reads from `DIRECTORY`, so the "scene" is really two
things: a Maya scene containing a controller to save, and a clean library
folder to write into.

### A) Build a controller worth saving
1. Open a **fresh** scene (`File ▸ New Scene`).
2. Create a NURBS circle to act as a rig control, e.g. in the Script Editor:
   ```python
   import maya.cmds as cmds
   cmds.circle(name='foot_ctrl')
   ```
3. (Optional, for a cleaner thumbnail) frame it with `f`, center it at the
   origin, freeze transforms (`Modify ▸ Freeze Transformations`). The
   screenshot is whatever the active viewport shows after `viewFit`.
4. **Select the circle's transform** (`foot_ctrl` in the Outliner). This is the
   key piece of scene state — see the table below.

### B) (First run only) confirm/clear the library directory
The tool creates `<userAppDir>/controllerLibrary/` on first save, so normally
you do nothing. To start clean for the exercise, delete that folder:

```python
import maya.cmds as cmds, shutil, os
d = os.path.join(cmds.internalVar(userAppDir=True), 'controllerLibrary')
if os.path.exists(d):
    shutil.rmtree(d)   # wipes saved controllers — only do this to reset
```

### Scene-state expectations per entry point

| You want to…        | Required scene state                                                                                  |
|---------------------|-------------------------------------------------------------------------------------------------------|
| `save(name)` a **single** controller | **Select the curve transform first.** With a selection the code runs `exportSelected`; without one it **saves the entire open file** as `<name>.ma`. |
| `save(name)` the whole scene         | Select **nothing** — the whole scene is written.                                                      |
| `load(name)` / `Import!`             | Nothing needs selecting. It just imports the `.ma` into the current scene.                            |
| launch `showUI()`                     | An open Maya session. The list populates from whatever is already on disk.                            |

---

## 2. How to Run the Functions

Put the demo folder on the path, import, and launch the UI:

```python
import sys
sys.path.insert(0, r'/abs/path/to/controllerLibrary')

import controllerLibrary_2027 as clib

ui = clib.showUI()   # KEEP this reference — see GC pitfall
```

**Expected result:** a Qt dialog titled *Controller Library UI* appears with an
empty name field, an empty icon gallery (or icons of previously-saved
controllers), and `Import! / Refresh / Close` buttons. The terminal/Script
Editor prints nothing on success.

### Save a controller (UI)
1. With `foot_ctrl` selected in Maya, type `foot` in the name field.
2. Click **Save**.

**Expected result:** the name field clears, a new icon appears in the gallery,
and on disk the folder `<userAppDir>/controllerLibrary/` now contains
`foot.ma`, `foot.json`, and `foot.jpg` (the 200×200 playblast thumbnail).
Hovering the icon shows the pretty-printed `info` dict as a tooltip.

### Import it back (UI)
1. `File ▸ New Scene` (or keep the scene — doesn't matter).
2. Click the **`foot`** icon in the gallery (it becomes the current item).
3. Click **Import!**.

**Expected result:** `foot_ctrl` is imported into the scene. Because `load()`
is a plain `cmds.file(..., i=True, usingNamespaces=False)`, it lands at world
root with its saved transforms — there is **no** "parent under current
selection" behaviour.

### Drive the library headlessly (no UI)
Because the model is decoupled from the view, you can script it directly — this
is the whole point of model/view separation:

```python
import sys, os
sys.path.insert(0, r'/abs/path/to/controllerLibrary')
import controllerLibrary_2027 as clib

lib = clib.ControllerLibrary()   # empty dict; nothing loaded yet
lib.find()                       # populate from DIRECTORY
print(list(lib.keys()))          # -> ['foot', ...] the saved names
print(lib['foot'])               # -> {'name':..., 'path':..., 'screenshot':...}

lib.load('foot')                 # import it into the scene

# Save the current selection under a new name, with no screenshot:
# cmds.select('hand_ctrl')
lib.save('hand', screenshot=False)
```

> The README's headless example uses `lib.library.keys()`,
> `lib.save('hand', directory=..., screenshot=r'...png')`, and
> `lib.delete(...)`. **All three are wrong against the real source:** the
> library *is* the dict (so it's `lib.keys()`), `screenshot` is a **bool not a
> path**, and `delete()` does not exist.

### The screenshot typo — a real bug to observe
`save()` writes the JSON key spelled correctly (`info['screenshot']`), but
`find()` reads it back into a **misspelled** key (`data['screnshot']`, missing
the second *e* — source line 133). To see the consequence:
- After a normal save-then-find, the icon **still shows**, because the JSON
  file's correctly-spelled `screenshot` key survives into `data` and
  `populate()` reads `info.get('screenshot')`.
- **But** if a controller has a `.ma` + `.jpg` yet **no `.json`**, `find()`
  hits the `else: data = {}` branch, adds only the misspelled `data['screnshot']`,
  and `populate()` finds no `screenshot` key → **no icon, even though the jpg
  exists.** Delete a controller's `.json` by hand and Refresh to reproduce.

---

## 3. Question and Answer

**Q1. Running the file does nothing — no window appears. Why?**
Because the file is a *library module*: it defines `ControllerLibrary`,
`ControllerLibraryUI`, and `showUI()` but never calls any of them at module
scope and has no `__main__` guard. You must call `clib.showUI()` yourself. This
"define everything, let the caller launch it" pattern is the same one used in
`gearCreator` and `objectRenamer/renamer2`.

**Q2. Why does `ControllerLibrary` inherit from `dict`?**
So the library instance *is* the `{name: info}` mapping. That gives it `.items()`,
`.keys()`, `[name]`, `name in lib`, etc. for free — `populate()` simply loops
`self.library.items()`. The custom methods (`save`, `find`, `load`) add behaviour
on top of the dict storage.

**Q3. I clicked Save but it wrote my entire scene, not just the control. Why?**
`save()` branches on `cmds.ls(selection=True)`: with a selection it runs
`cmds.file(force=True, exportSelected=True)`; **without** one it runs
`cmds.file(save=True, force=True)` and writes the whole open file. Always
select the curve transform before Save. (It also calls `cmds.file(rename=path)`
first, which renames the current scene's save target — a side effect worth
knowing if you Save with nothing selected.)

**Q4. Why does `find()` store the screenshot under a misspelled `screnshot` key?**
It's a bug in the source (`data['screnshot']` at line 133 vs the correct
`screenshot` written by `save()` and read by `populate()`). It's usually masked
because the JSON file already carries the correctly-spelled key, so `populate()`
still finds an icon. It only bites when a controller has no `.json` — then the
icon silently disappears despite the `.jpg` existing on disk.

**Q5. The README mentions a `Delete` button and a `delete()` method. Where are they?**
They aren't in the code. The actual buttons are **Save / Import! / Refresh /
Close**, and `ControllerLibrary` has no `delete()` method at all. The README
describes an aspirational/enhanced version of the tool. To actually delete a
controller today you'd remove the entry from the dict and `os.remove()` the
`.ma`, `.json`, `.jpg` yourself — which is exactly the "Add a Delete button"
exercise.

**Q6. The README says there's one `library.json` index, but I see one `.json` per controller. Which is right?**
The source: `save()` writes `<name>.json` per controller, and `find()` scans
for each `<name>.json` alongside its `<name>.ma`. There is no single index
file. A single `library.json` would be a reasonable refactor (one read/write
instead of N), but it is not what this code does.

**Q7. Why must I write `ui = clib.showUI()` and keep `ui`? If I just call `clib.showUI()` the window flashes and vanishes.**
`showUI()` creates a local `ControllerLibraryUI()`, calls `.show()`, and
returns it. If you don't bind the return value to a name, the instance has no
live reference, Python garbage-collects it, and Qt destroys the window.
`ui = clib.showUI()` keeps the reference alive for the session. (This is the
same GC pitfall noted in the `tweener` curriculum file.)

**Q8. What is the `**info` parameter on `save()`, and how is it used?**
`**info` collects arbitrary keyword arguments into a dict, so a caller can
stamp metadata: `lib.save('foot', side='L', author='me')` ends up with
`side` and `author` written into `foot.json`. `save()` then adds the reserved
keys `name`, `path`, and (if `screenshot`) `screenshot`. It's the same `**kwargs`
idea as `*args` collects positional args.

**Q9. `Import!` imports to world root. How would I parent it under my current selection instead?**
The current `load()` is just `cmds.file(path, i=True, usingNamespaces=False)`
— no parenting. To parent under the selection you'd capture the returned node
names and `cmds.parent(...)` them under `cmds.ls(selection=True)[0]` after the
import. (The README claims this already happens; it does not.)

**Q10. Why is the data class separate from the UI class at all?**
Model/view separation. `ControllerLibrary` does pure data work (export, json,
playblast, import) and knows nothing about Qt. `ControllerLibraryUI` only
collects input and calls library methods. The payoff: you can drive the same
library from a shelf button, a CLI script, or another tool (see the headless
example) without ever opening the window.

---

## 4. Advanced Directions

1. **Add the missing `delete()` method + `Delete` button.** The most-requested
   gap. New code: `ControllerLibrary.delete(self, name)` that pops the dict
   entry and `os.remove()`s the `.ma`, `.json`, and `.jpg`; a `deleteBtn` in
   `buildUI` wired to a `ControllerLibraryUI.delete` slot that reads
   `self.listWidget.currentItem().text()` and calls the library method. Handle
   the nothing-selected case with a guard like `load()` does.

2. **Collapse to a single `library.json` index.** Replace per-controller JSONs
   with one index dict written by `save()`/`delete()` and read by `find()`.
   Requires a new `ControllerLibrary._index_path` helper and rewriting `find()`
   to do one `json.load` instead of scanning. Benefit: one disk read on
   `populate()`, atomic rewrites, and the `screnshot` typo disappears because
   there's only one write path.

3. **Categories, tags, and a search/filter box.** Extend the record with
   `category` and `tags` (passed via `**info`), add a `QLineEdit` filter + a
   category `QComboBox`, and filter `populate()` to only add matching items.
   Needs a `ControllerLibraryUI._matches(item, query)` helper and signals on
   `textChanged` / `currentIndexChanged`.

4. **Rename-in-place and multi-select import.** Add a `Rename` button
   (`ControllerLibrary.rename(self, old, new)` that re-saves the `.ma` under
   the new name and removes the old files) and switch the list to
   `ExtendedSelection` so `load()` imports every selected item in one
   `cmds.file(..., i=True)` per name.

5. **Custom thumbnails + clean import options.** Let users pick a PNG via
   `QFileDialog` instead of always playblating (a `screenshot=False, image=path`
   path through `save()`), and add import options (parent-under-selection,
   mirror by negating X, namespace prefix). These turn the toy into something
   comparable to real tools like StudioLibrary / aLib.

6. **Wrap as an installable shelf tool with undo chunks.** Package the module
   (a `setup.py`/`pyproject` entry point so `import controllerLibrary` works
   without `sys.path` hacks), add a shelf button calling `showUI()`, and wrap
   every `save`/`load`/`delete` in `cmds.undoInfo(openChunk=True)` …
   `(closeChunk=True)` so the whole operation collapses to one Ctrl-Z —
   currently each `cmds.file` call is its own undo step.
