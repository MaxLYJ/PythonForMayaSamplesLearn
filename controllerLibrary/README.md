# controllerLibrary — A Qt-Based Rigging Control Library

A real-world style tool: save controller shapes (NURBS curves) to a
JSON-indexed library with screenshots, then drag-drop them back into any
scene. The kind of thing every rigging department has.

This is the first **PySide/Qt** demo in the course. It looks like a polished
app because Qt is what real Maya tools are built with.

> ⚠️ **The catch:** this file only defines the `ControllerLibrary` and
> `ControllerLibraryUI` classes plus a `showUI()` helper. **Running the file
> does nothing** — you have to call `showUI()`.

---

## Quick start

1. Open Maya's Script Editor (Python tab).
2. Paste and run:

   ```python
   import sys
   sys.path.insert(0, r'D:\2026MayaPython\controllerLibrary')

   import controllerLibrary_2027 as clib

   # Show the window. Keep a reference so Python doesn't garbage-collect it.
   ui = clib.showUI()
   ```

A Qt window appears with an empty list widget, a name field, and
Save / Delete / Close buttons.

---

## Why doesn't the file do anything when I run it?

The file ends with this convenience function but never calls it:

```python
def showUI():
    ui = ControllerLibraryUI()
    ui.show()
    return ui
```

No `showUI()` call at module level, so importing does nothing visible.
That's the standard "library module" pattern — define everything, let the
caller decide when to launch. See [`gearCreator/README.md`](../gearCreator/README.md)
for the longer version of this pattern.

---

## How to actually use the tool

### Save a controller

1. In Maya, create a NURBS curve you want to save (e.g. `cmds.circle(name='foot_ctrl')`).
2. **Select the curve's transform.**
3. In the controllerLibrary window, type a name in the text field
   (e.g. `foot`).
4. Click **Save**.

The tool:
- Exports the curve to disk (`.ma` file in the library directory).
- Takes a screenshot via `playblast`.
- Records an entry in a `library.json` index file.
- Adds an item with the screenshot icon to the list.

### Re-use a controller

1. Open the library window in any scene.
2. Click an item in the list (you'll see its screenshot).
3. The controller is imported and parented under your current selection
   (or to the world root if nothing is selected).

### Delete a controller

1. Select an item in the list.
2. Click **Delete**.

Removes the entry from `library.json` and deletes the saved files.

---

## The two classes — what each does

Read the file with this map in mind:

### `ControllerLibrary` (the data model)

A `dict` subclass that handles persistence:

| Method                 | What it does                                            |
|------------------------|---------------------------------------------------------|
| `__init__()`           | Loads `library.json` from disk if it exists             |
| `save(name, directory, screenshot)` | Builds a record, exports the `.ma`, writes JSON |
| `find(name)`           | Returns the record for `name` (or None)                 |
| `load(name)`           | Imports the saved `.ma` file into the scene             |
| `delete(name)`         | Removes the entry and its files                         |

It does **no UI work** — just data. This separation matters: you could
script against `ControllerLibrary` directly without ever opening the window.

### `ControllerLibraryUI(QWidget)` (the view)

The Qt window. Connects buttons to library methods:

| UI element              | Triggers                                                  |
|-------------------------|-----------------------------------------------------------|
| Save button             | `self.library.save(name, dir, screenshot)`                |
| List item click         | `self.library.load(name)`                                 |
| Delete button           | `self.library.delete(name)`                               |

The pattern: **UI collects input → calls library methods → library does
the work → UI refreshes.** Every well-built tool follows this.

---

## What this demo teaches (Hour 6 of the schedule)

This is the most concept-dense demo so far. Key takeaways:

1. **Qt (`PySide2` / `PySide6`) is the professional Maya UI library.** It
   replaces `cmds.window` for anything beyond a few widgets. Looks native,
   has 50+ widget types, supports drag-and-drop.
2. **`Qt.py` shim** — the import block at the top auto-detects whichever Qt
   version Maya ships, so your code runs on any Maya version.
3. **Signals and slots** — Qt's event model. `button.clicked.connect(self.on_save)`
   means "when clicked fires, run on_save."
4. **JSON for persistence** — `json.dump(library_dict, f)` writes the index;
   `json.load(f)` reads it back. Standard Python, no Maya-specific code.
5. **`playblast` for screenshots** — the trick for capturing a controller
   preview without third-party tools.
6. **Model/view separation** — `ControllerLibrary` knows nothing about UI.
   This is why you can reuse it from a shelf button, a CLI script, or
   another tool.

---

## Common pitfalls

| Symptom                                                      | Cause                                                                                  | Fix                                                                                                |
|--------------------------------------------------------------|----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'controllerLibrary_2027'` | Folder not on sys.path                                                            | Add `sys.path.insert(0, r'.../controllerLibrary')`                                                 |
| Window flashes and disappears                                | You didn't keep the `ui =` reference — Python garbage-collected it                     | Always do `ui = clib.showUI()`, not just `clib.showUI()`                                           |
| `ImportError: No module named PySide2` / `PySide6`           | Very old Maya (pre-2017) or you're running outside Maya                                | Use Maya 2017+. Inside Maya, PySide2/6 is already installed                                        |
| Save does nothing                                            | You didn't select a NURBS curve transform first                                         | Select the curve, then click Save                                                                  |
| Screenshots are blank                                        | The viewport wasn't in a good view, or playblast timing                                | Frame the controller nicely before saving. Check the screenshot path exists                        |
| Loaded controller has wrong scale/rotation                   | The saved `.ma` includes the transform's parent hierarchy                             | Save the curve at world origin with frozen transforms for cleanest results                         |
| JSON file corrupted                                          | Manual edit broke the syntax, or Maya crashed mid-write                                | Delete `library.json` to start fresh (you'll lose the index, not the `.ma` files)                  |
| `Qt.py` warnings about binding                               | `Qt.py` shim is missing or your Qt version is unusual                                  | Download [Qt.py](https://github.com/mottosso/Qt.py) into the folder, or use Maya's bundled copy    |

---

## How to call the library without the UI (scripting use case)

Because `ControllerLibrary` is separate from the UI, you can use it from
any script:

```python
import controllerLibrary_2027 as clib

lib = clib.ControllerLibrary()

# What's in the library?
print(list(lib.library.keys()))

# Load a controller by name, no UI
lib.load('foot')

# Save the current selection as a new entry
lib.save('hand', directory=r'C:\my_library', screenshot=r'C:\my_library\hand.png')

# Delete one
lib.delete('unused_ctrl')
```

This is the payoff of model/view separation — one library, many interfaces.

---

## Exercises

1. **Add a "Rename" button.** When clicked, prompt for a new name and
   update the JSON record (re-saving the `.ma` under the new name).
2. **Categories.** Add a `category` field to each record. Add a dropdown
   that filters the list by category.
3. **Search box.** Add a `QLineEdit` that filters the list as you type.
4. **Multi-select import.** Let users Ctrl-click multiple items and import
   them all at once.
5. **Custom thumbnails.** Let the user pick a PNG instead of always using
   playblast.
6. **Tags.** Allow multiple tags per controller (`['foot', 'ik', 'left']`)
   and search by tag.
7. **Mirroring.** Add a button that imports a mirrored version of the
   curve (negate the X coordinates).

---

## Source

This is a teaching demo from the original [PythonForMayaSamples](https://github.com/dgovil/PythonForMayaSamples)
repo. The `_2027.py` version is a verified Python-3-compatible copy for
Maya 2022+ / PySide6.

Real-world counterparts: [StudioLibrary](https://github.com/AntonyCarpenter/studiolibrary)
(inspiration for this demo), [aLib](https://github.com/Alexander-Hjelm/alib).
