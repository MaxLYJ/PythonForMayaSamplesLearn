# lightManager — The Capstone (PyMel + Qt + Dockable UI + Signals)

The most advanced demo in the repo. A dockable Maya window for managing
lights — add, delete, modify, batch-edit intensity/color, save and load
presets. It pulls together everything from the previous demos and adds
PyMel, custom Qt signals, and dockable UI integration.

> ⚠️ **The catch:** like the other teaching demos, this file only **defines**
> classes and helpers. **Running the file does nothing visible** — you have
> to call `showUI()`.

---

## Quick start

1. Open Maya's Script Editor (Python tab).
2. Paste and run:

   ```python
   import sys
   sys.path.insert(0, r'D:\2026MayaPython\lightManager')

   import lightManager_2027 as lm

   # Show the dockable window. Keep a reference to avoid GC.
   ui = lm.showUI()
   ```

The Lighting Manager docks to the right side of the Maya window. If you
don't see it, check the UI menu → workspaces, or look for "Lighting Manager"
in the right-side panel area.

---

## Why doesn't the file do anything when I run it?

The file defines a `LightingManagerUI(QWidget)` class and helpers
(`showUI`, `getDock`, `deleteDock`), but never calls any of them at module
level. You supply the call. See [`gearCreator/README.md`](../gearCreator/README.md)
for the longer explanation of this pattern.

---

## How to use the tool

### Add lights

1. Click **Add Light** (or use whatever the add button is labeled in your
   version — the exact label varies).
2. Pick a light type (point, directional, spot, area).
3. The light is created in the scene and appears in the manager's list.

### Modify lights

Each light shows up as a row in the UI with controls for:
- **Intensity** (slider or spinbox)
- **Color** (color picker)
- **Exclusive** / other attributes (checkboxes)
- **Delete** button

Changes apply live. This is **custom Qt signals** in action — each widget
emits a signal when changed, and the UI's slot calls PyMel to set the
attribute.

### Save / load presets

The preset feature lets you save the current set of lights to JSON and
reload them later. Useful for matching lighting across shots or sharing
looks between artists.

---

## What this demo teaches (Hour 7 of the schedule)

This is the "pull it all together" demo. New concepts beyond
`controllerLibrary`:

### 1. PyMel instead of `cmds`

`lightManager` uses `pymel.core as pm` for cleaner, object-oriented
attribute access:

```python
# cmds style (what we used all course)
cmds.setAttr('pointLight1.intensity', 2.0)

# pymel style (this demo)
light = pm.PyNode('pointLight1')
light.intensity.set(2.0)
```

PyMel wraps every node as an object with attribute accessors. More
Pythonic, easier to read, slightly slower. The right choice for UI tools
where ergonomics matter more than speed.

### 2. Custom Qt signals

The file defines custom signal classes (subclasses of `QtCore.QSignal`
or `Signal()`). When a widget changes, the signal fires, and the
connected slot runs.

```python
# Pseudocode from the demo
intensityChanged = Signal(float)

def on_intensity_change(value):
    self.light.intensity.set(value)
    intensityChanged.emit(value)
```

This is how real Qt apps propagate state changes — far cleaner than
`cmds.button(command=...)`.

### 3. Dockable UI via `workspaceControl`

The non-obvious part is `getDock()` (around line 380 in the file):

```python
def getDock(name='LightingManagerDock'):
    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1),
                               label="Lighting Manager")
    qtCtrl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(int(qtCtrl), QtWidgets.QWidget)
    return ptr
```

This:
1. Creates a Maya `workspaceControl` (a dockable panel).
2. Gets its raw Qt pointer via `OpenMayaUI.MQtUtil`.
3. Wraps that pointer as a `QWidget` so the Qt UI can live inside it.

**Why it matters:** Qt widgets don't dock into Maya by default. You have
to parent them to a Maya-owned workspace control. This pattern is the
standard recipe — memorize it if you build dockable tools.

### 4. Mix of PyMel + cmds + OpenMaya

The capstone uses **all three** Python-Maya interfaces:
- `pymel.core` for ergonomics
- `maya.cmds` for fallback / older features
- `maya.api.OpenMayaUI` for the Qt ↔ Maya bridge

This is realistic — production tools mix freely. Pick the right tool for
each job; don't be a purist.

---

## The `lightManager2016Below` variant

There's a second file: `lightManager2016Below.py`. It's the **same tool**
using the older `dockControl` API for Maya 2016 and earlier.

**Skip it unless you're supporting old Maya.** The main
`lightManager.py` uses `workspaceControl`, which is the modern (Maya 2017+)
dockable UI API. The 2016Below file exists only because some studios still
run older Maya.

---

## Common pitfalls

| Symptom                                                       | Cause                                                                                       | Fix                                                                                                    |
|---------------------------------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'lightManager_2027'`    | Folder not on sys.path                                                                      | Add `sys.path.insert(0, r'.../lightManager')`                                                          |
| Window doesn't dock / appears as a floating window            | Maya's workspace state is confused                                                          | `deleteDock()` should clean this up. If not, manually close any leftover "LightingManagerDock" panels. |
| `ImportError: cannot import name 'wrapInstance'`              | Wrong OpenMayaUI import path for your Maya version                                          | Check the imports at the top of the file; `from sphinxify import wrapInstance` vs `from qtpython...` paths vary |
| Slider moves but light doesn't change                         | Signal not connected, or PyMel node went stale                                              | Re-add the light through the manager (don't delete it manually mid-session)                            |
| `pm.workspaceControl ... doesn't exist`                       | Very old Maya (pre-2017)                                                                    | Use `lightManager2016Below.py` instead                                                                 |
| Window appears then disappears                                | GC — you didn't keep the `ui =` reference                                                   | `ui = lm.showUI()`, not just `lm.showUI()`                                                             |
| Errors about `Signal` not defined                             | Wrong Qt binding (PySide6 uses `Signal`, PyQt5 uses `pyqtSignal`)                           | The `Qt.py` shim should paper over this; if not, check your Qt.py version                              |

---

## How this connects to the rest of the course

| Concept                            | Where you learned it                                  | Where it's used here                    |
|------------------------------------|-------------------------------------------------------|-----------------------------------------|
| Qt basics, signals/slots           | [`controllerLibrary/`](../controllerLibrary/README.md) | light intensity/color widgets           |
| Class inheritance                  | [`tweener/reusableUI`](../tweener/README.md)          | UI class hierarchy                      |
| Functions returning values         | [`objectRenamer/renamer2`](../objectRenamer/renamer2_README.md) | preset save/load                  |
| JSON persistence                   | [`controllerLibrary`](../controllerLibrary/README.md) | preset save/load                        |
| PyMel                              | (new in this demo)                                    | entire file uses `pm` instead of `cmds` |
| OpenMayaUI + wrapInstance          | (new in this demo)                                    | dockable window bridge                  |

If you've worked through demos 1–10, you have all the ingredients to read
this file end-to-end. It's long (~400 lines), but every section should
feel familiar.

---

## Exercises

1. **Add a "Solo" button per light.** Clicking it temporarily mutes all
   other lights (set intensity to 0). Click again to restore.
2. **Add light groups.** Let users tag lights into groups (key, fill, rim).
   Add a dropdown to filter the list by group.
3. **Add a render preview thumbnail.** Use `cmds.render` on a small region
   and display the result in the UI. Updates on any intensity/color change.
4. **Add batch intensity scaling.** A slider that scales every light's
   intensity by a multiplier — useful for exposure tuning.
5. **Add A/B preset compare.** Save two presets and toggle between them
   with a single click. Compare lighting setups without losing either.
6. **Port a widget to OpenMaya callback.** When a light is deleted from
   the Outliner, the UI should auto-remove its row. Use
   `MNodeMessage.addNodePreRemovalCallback` (see
   [`cameraMessageCmd/cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md)).
7. **Add Arnold-specific attributes.** If MtoA is loaded, expose
   `aiExposure`, `aiSamples`, etc. Detect with `cmds.pluginInfo(query=True, listPlugins=True)`.

---

## Source

This is a teaching demo from the original [PythonForMayaSamples](https://github.com/dgovil/PythonForMayaSamples)
repo. The `_2027.py` version is a verified Python-3-compatible copy for
Maya 2022+ / PySide6.
