# HowToStart — lightManager

This is the **Hour 7 / capstone** demo: the most concept-dense tool in the
curriculum. It is a real-world-style **lighting manager** — a dockable Maya
window that lists every light in the scene as an editable row (visibility,
intensity, color, solo, delete), plus JSON **save / import** of a whole light
rig as a shareable preset.

It is the "pull it all together" demo. On top of `controllerLibrary`'s Qt
signals/slots and `tweener`'s class hierarchy, it adds four new ideas:

1. **PyMel** (`pymel.core as pm`) instead of `maya.cmds` — object-oriented
   attribute access (`light.intensity.set(2.0)`).
2. **Custom Qt signals** — `LightWidget` defines its own `onSolo = Signal(bool)`
   so the manager can react when any row is soloed.
3. **Dockable UI** via `workspaceControl` + the OpenMayaUI↔Qt bridge
   (`MQtUtil_findControl` + `wrapInstance`) — the standard recipe for parenting
   a Qt widget inside a Maya-owned dock.
4. **Three Maya Python APIs at once** — `pymel.core`, `maya.cmds`-style calls
   through PyMel, and `maya.api.OpenMayaUI`. Real production tools mix freely.

> ⚠️ **Honesty note up front:** the bundled `README.md` is **aspirational in
> several places** and does not match the source. The most important one: there
> is **no `showUI()` function**. You launch the tool by constructing
> `LightingManager(dock=True)` directly. See "How to Run" below. Every
> code-level claim in this guide was verified against `lightManager_2027.py`.

---

## Files in this demo

| File                            | What it is                                                          | Run it how                                   |
|---------------------------------|---------------------------------------------------------------------|----------------------------------------------|
| `lightManager_2027.py`          | Modern Python-3 / PySide6 version (the one to run)                  | `import` then `LightingManager(dock=True)`   |
| `lightManager.py`               | Original teaching file; identical body except imports use the `Qt.py` shim and `basestring`/`long()` (Python 2) | reference / pre-2022 Maya |
| `lightManager2016Below_2027.py` | **Legacy variant** for Maya ≤2016: uses `dockControl` instead of `workspaceControl`. Skip unless supporting old Maya. | reference only |
| `lightManager2016Below.py`      | Python-2 original of the legacy variant                             | reference only                               |

> **`_2027` convention:** throughout this repo, `foo_2027.py` is the verified
> Python-3 copy that runs in Maya 2022+; `foo.py` is the heavily-commented
> teaching original. This guide targets `lightManager_2027.py`. `lightManager.py`
> differs from it **only in the import block** (`from Qt import …` shim vs
> `from PySide6 import …`, plus `basestring`→`str` and `long()`→`int()`) — all
> behaviour below applies to both.

## Prerequisites

- Maya 2022+ (PySide6 + shiboken6 ship inside Maya — nothing extra to install).
  On older Maya use `lightManager.py` + the `Qt.py` shim, or switch the import
  to `from PySide2 import …`.
- The `lightManager/` folder added to `sys.path` (shown below).
- ⚠️ **No Maya = no run.** This demo imports `pymel.core`, `maya.OpenMayaUI`,
  **and** `PySide6`/`shiboken6` at module top, so it can only be executed inside
  Maya's Script Editor (or `mayapy` with the GUI available). Nothing here was
  testable outside Maya; `py_compile` was used only to confirm valid syntax.

---

## What the code actually does

Two classes plus three module-level helpers. **Running / importing the file
does nothing visible** — there is no `if __name__ == '__main__'` guard and (pace
the README) **no `showUI()`**. You must construct `LightingManager(...)` (or a
standalone `LightWidget(...)`) yourself.

### `LightWidget(QWidget)` — one editable row per light

Constructor: `LightWidget(light)`. `light` may be a **name string**, a **PyMel
shape node**, or a **PyMel transform** — `__init__` normalizes all three to the
light **shape** (it calls `light.getShape()` if handed a transform) and stores
it as `self.light`. A **class-level custom signal** is declared:

```python
onSolo = Signal(bool)   # emitted by the Solo button; manager connects isolate() to it
```

`buildUI()` lays out a 2×3 grid:

| Widget (verified)                      | Grid pos    | Signal → slot                                                    |
|----------------------------------------|-------------|------------------------------------------------------------------|
| `QCheckBox` = light's transform name   | row 0, col 0 | `toggled` → `lambda val: self.light.visibility.set(val)`        |
| `QPushButton('Solo')` (checkable)      | row 0, col 1 | `toggled` → `lambda val: self.onSolo.emit(val)`                |
| `QPushButton('X')` (delete)            | row 0, col 2 | `clicked`  → `self.deleteLight`                                |
| `QSlider(Horizontal)`, min 1 / max 1000 | row 1, col 0–1 | `valueChanged` → `lambda val: self.light.intensity.set(val)` |
| `QPushButton` color swatch (20×20)     | row 1, col 2 | `clicked`  → `self.setColor`                                   |

Other methods:

| Method | What it does |
|--------|--------------|
| `disableLight(val)` | `self.name.setChecked(not bool(val))` — un-checks the visibility box. Toggling the box fires the `toggled` lambda, which sets `visibility`, so this **indirectly turns the light off/on**. Used by the manager's `isolate`. |
| `deleteLight()` | Removes the widget from its parent, hides it, `deleteLater()`, **then** `pm.delete(self.light.getTransform())` — deletes the transform (so history/shape go too). Scene is touched only after the widget is safely torn down. |
| `setColor()` | Opens `pm.colorEditor(rgbValue=current)`, parses the returned `"r g b a"` string, sets `light.color` and the swatch. **Alpha is read then discarded** — only r,g,b are applied. |
| `setButtonColor(color=None)` | Reads `light.color` if none given; asserts `len==3`; scales 0–1 floats ×255 into a Qt stylesheet `background-color: rgba(r,g,b,1.0)`. |

### `LightingManager(QWidget)` — the dockable window

Constructor: `LightingManager(dock=False)`.
- `dock=True` → parents itself to `getDock()` (a Maya `workspaceControl` wrapped
  as a `QWidget`).
- `dock=False` → `deleteDock()`, deletes any old `'lightingManager'` UI, then
  parents itself to a fresh `QDialog` whose parent is the Maya main window, and
  `show()`s it.

In both cases it then calls `buildUI()`, `populate()`, and adds itself to the
parent's layout.

**`lightTypes`** — a class attribute mapping UI labels to PyMel callables. Note
the use of `functof.partial` for the two lights that have no one-word PyMel
constructor:

| UI label (sorted)       | Callable                                              |
|-------------------------|-------------------------------------------------------|
| `Area Light`            | `partial(pm.shadingNode, 'areaLight', asLight=True)`  |
| `Directional Light`     | `pm.directionalLight`                                 |
| `Point Light`           | `pm.pointLight`                                       |
| `Spot Light`            | `pm.spotLight`                                        |
| `Volume Light`          | `partial(pm.shadingNode, 'volumeLight', asLight=True)`|

> ⚠️ **No `ambientLight`** is in this dict, and `populate()` does not list it
> either. An ambient light created from Maya's menu will **not** appear in the
> manager. (See Q&A.)

Methods:

| Method | Signature (verified) | What it does |
|--------|----------------------|--------------|
| `buildUI` | `(self)` | Combobox (sorted light types) + `Create` button; a `QScrollArea` holding the rows; and `Save` / `Import` / `Refresh` buttons. |
| `createLight` | `(self, lightType=None, add=True)` | Reads the combobox if `lightType` is `None`, looks up `self.lightTypes[lightType]`, calls it, and (if `add`) calls `addLight`. **Returns the new light PyNode.** |
| `addLight` | `(self, light)` | Builds a `LightWidget`, connects its `onSolo` → `self.isolate`, adds it to the scroll layout. |
| `populate` | `(self)` | `pm.ls(type=[area, spot, point, directional, volume])` → `addLight` each. **Does NOT clear existing rows first.** |
| `refresh` | `(self)` | Clears every child of the scroll layout (`takeAt(0)` until empty, `deleteLater`), then calls `populate`. |
| `isolate` | `(self, val)` | For every `LightWidget` that is **not** `self.sender()`, call `disableLight(val)` — i.e. soloing one light hides the rest. |
| `saveLights` | `(self)` | For each `LightWidget`, record `{translate, rotation, lightType, intensity, color}` keyed by transform name; write `<appDir>/lightManager/lightFile_<MMDD>.json`. |
| `importLights` | `(self)` | `QFileDialog` → load JSON → for each entry, match `lightType` (via a `for/else`), `createLight`, set intensity/color/translate/rotate, then `populate()`. |
| `getDirectory` | `(self)` | `os.path.join(pm.internalVar(userAppDir=True), 'lightManager')`, `os.mkdir` if missing. |

### Module helpers

| Function | What it does |
|----------|--------------|
| `getMayaMainWindow()` | `omui.MQtUtil_mainWindow()` → `wrapInstance(int(win), QMainWindow)`. Returns Maya's main window as a Qt object you can parent to. |
| `getDock(name='LightingManagerDock')` | `deleteDock(name)`, `pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Lighting Manager")`, then `omui.MQtUtil_findControl(ctrl)` → `wrapInstance(int(qtCtrl), QWidget)`. Returns the dock as a Qt widget. |
| `deleteDock(name='LightingManagerDock')` | If `pm.workspaceControl(name, q=True, exists=True)`, `pm.deleteUI(name)`. |

> **The `lightManager2016Below_2027.py` variant** differs only in the docking
> mechanics: it uses the legacy `pm.dockControl(..., content='lightingManager')`
> (parenting by object name, no `wrapInstance` needed) and constructs the dialog
> first, dock last. **It also has a real bug:** its `createLight` is missing the
> `return light` line, so `importLights` (which does `light = self.createLight(...)`
> then `light.intensity.set(...)`) will raise `AttributeError: 'NoneType'`. Use
> the main file for actual work.

---

## How to Create the Test Maya Scene

The manager builds its own lights via the **Create** button, so a totally empty
scene is fine for the basic flow. But to exercise `populate()` (rows for
*existing* lights) and to test the ambient-light gap, build this by hand first.

### Scene A — a few pre-existing lights (to test auto-populate)

In Maya's Script Editor (Python tab):

```python
import pymel.core as pm
pm.pointLight()                 # -> pointLightShape1 under transform pointLight1
pm.spotLight()
pm.directionalLight()
pm.ambientLight()               # intentionally: this one should NOT appear
pm.move(0, 5, 0)                # lift one so the viewport isn't pure black
```

Open the Outliner. You should see the light transforms. Now launch the manager
("How to Run" below) — the point/spot/directional rows appear automatically; the
**ambient light does not**. That gap is the lesson, not a mistake in your scene.

### Scene B — translate/rotate the lights (to test Save/Import round-trip)

`saveLights` records each light's **translate and rotate**. To see a meaningful
round-trip, move/rotate a couple of lights so their transforms are non-zero:

```python
pm.setAttr('pointLight1.translate', 3, 2, 0)
pm.setAttr('spotLight1.rotate', -35, 0, 0)
```

### Scene state each entry point expects

| Entry point | Scene state it expects |
|-------------|------------------------|
| `LightingManager(dock=True/False)` | Any scene (empty is fine). `populate()` adds a row for every supported light already present. |
| `Create` button | Any scene; needs the combobox to hold one of the 5 supported labels. |
| `LightWidget('pointLight1')` (standalone) | A light named `pointLight1` (shape **or** transform) must exist — the name is resolved to a PyNode in `__init__`. |
| `Save` | ≥1 supported light in the scene (writes whatever `LightWidget`s currently exist). |
| `Import` | A previously-saved `lightFile_<MMDD>.json` in `<appDir>/lightManager/`. |

---

## How to Run the Functions

### 1. Launch the dockable manager (the main use case)

Script Editor → Python tab:

```python
import sys
sys.path.insert(0, '/abs/path/to/lightManager')   # use your real path

import lightManager_2027 as lm

ui = lm.LightingManager(dock=True)    # docks to the right of the Maya window
# or, as a floating dialog:
# ui = lm.LightingManager(dock=False)
```

> Keep the `ui =` reference. The widget is parented to a Maya-owned dock/dialog
> so it usually survives garbage collection, but holding the reference is the
> defensive habit carried over from `controllerLibrary`/`tweener` — and the
> README itself lists "window appears then disappears (GC)" as a known pitfall.

**Expected result:** a "Lighting Manager" panel docks on the right (or a
floating dialog). With Scene A above you see three rows (point, spot,
directional). Each row: a name checkbox, a **Solo** button, a red **X**, a
horizontal intensity slider, and a small color swatch.

### 2. Drive the UI row-by-row

| Action | What happens in the viewport / outliner |
|--------|-----------------------------------------|
| Drag a row's **intensity slider** | That light's `intensity` changes live (watch the viewport brighten/darken). Slider range is **1–1000**, integer. |
| Click the **color swatch** | Maya's color editor opens preset to the light's color; choosing a color sets `light.color` and re-tints the swatch. |
| Uncheck the **name checkbox** | `visibility` → 0; the light turns off in the viewport. |
| Click **Solo** on one row | `isolate` runs: every *other* row's checkbox unchecks (those lights go dark); the soloed light stays on. Click Solo again to restore. |
| Click **X** | The row disappears **and** `pm.delete(light.getTransform())` removes the light from the scene/outliner. |

### 3. Create / Save / Import / Refresh

- **Create:** pick a type in the combobox (e.g. `Spot Light`), click **Create**.
  A new light appears in the scene and a new row appears in the manager.
- **Save:** click **Save**. Check the log line `Saving file to .../lightFile_<MMDD>.json`.
  On Linux that's `~/maya/<version>/lightManager/lightFile_0719.json`; on Windows
  `C:/Users/<you>/Documents/maya/<version>/lightManager/...`.
- **Import:** click **Import** → file dialog opens in the lightManager folder →
  pick a JSON. The lights are recreated and re-parented with their saved
  translate/rotate/intensity/color. (⚠️ see Q&A about duplicate rows.)
- **Refresh:** click **Refresh** to clear and re-list all scene lights (use this
  after deleting lights by hand in the Outliner).

### 4. Headless / single-row usage (no full manager)

`LightWidget` is usable on its own — its docstring shows the pattern:

```python
import sys
sys.path.insert(0, '/abs/path/to/lightManager')
import lightManager_2027 as lm
import pymel.core as pm
pm.pointLight()                      # make sure a light exists
w = lm.LightWidget('pointLight1')    # accepts a name, transform, or shape PyNode
w.show()                             # a tiny floating editor for that one light
```

You can also call the three module helpers directly, e.g.
`lm.deleteDock()` to tear down a stuck dock, or `lm.getMayaMainWindow()` to
parent your own Qt windows to Maya.

> ⚠️ Unlike `controllerLibrary`, this demo does **not** separate a headless data
> model from the UI — `saveLights`/`importLights`/`populate` live on the window
> class. There is no clean "drive it with no UI" path for save/import. (See
> Advanced Directions.)

---

## Question and Answer

**Q1. The README says `ui = lm.showUI()`, but I get `AttributeError: module has no attribute 'showUI'`.**
The README is aspirational here. There is **no `showUI()` function** in the
file. Launch directly: `ui = lm.LightingManager(dock=True)`. (`controllerLibrary`
had a `showUI()`; this demo doesn't — a deliberate difference, and a good reason
to trust the source over the README.)

**Q2. I made an ambient light from Maya's Create menu, but it never shows up in the manager. Why?**
`lightTypes` lists only point / spot / area / directional / volume, and
`populate()` calls `pm.ls(type=[...])` with that same five. `ambientLight` is
simply not in either list, so it is invisible to the tool. To support it you'd
add `"Ambient Light": pm.ambientLight` to `lightTypes` and `"ambientLight"` to
the `populate()` type list.

**Q3. The intensity slider won't let me drag to 0 — how do I turn a light fully off?**
`intensity.setMinimum(1)`, so the slider bottoms out at 1, not 0. (It's also
an integer `QSlider`, so fractional intensities round.) To actually disable a
light, **uncheck the name checkbox** — that sets `visibility` to 0. If you want
intensity-0 control, change `setMinimum(0)` (and consider a `QDoubleSpinBox` for
fractional values).

**Q4. I clicked Import on a preset and now every light appears twice.**
Verified-from-source bug: `importLights` ends with `self.populate()`, but
`populate()` only **adds** rows — it never clears. The original lights already
had rows from `__init__`, so re-listing the whole scene produces duplicates. It
should call `self.refresh()` (which clears first). Workaround: click **Refresh**
isn't enough either (it would also duplicate); close and relaunch the manager,
or fix the call site to `self.refresh()`.

**Q5. What exactly does the Solo button do?**
Solo is `setCheckable(True)`. Toggling it emits the custom `onSolo` signal;
the manager wired `widget.onSolo → self.isolate`. `isolate` walks every
`LightWidget` and, for any widget that is **not** `self.sender()` (the soloed
one), calls `disableLight(val)`. `disableLight` unchecks the visibility box,
which fires the box's `toggled` lambda, which sets `visibility` — so the chain
is `Solo → onSolo → isolate → disableLight → checkbox → visibility`. Soloing one
light hides all the others; un-soloing restores them.

**Q6. The legacy `lightManager2016Below_2027.py` Import crashes with `AttributeError: 'NoneType'`. Why?**
That file's `createLight` is missing the `return light` line (confirmed by
diff against the main file). So `light = self.createLight(...)` is `None`, and
the next line `light.intensity.set(...)` blows up. It's a teaching-comparison
file; use `lightManager_2027.py` for real work, or add the missing `return light`.

**Q7. I saved my rig twice in the same day and the first preset is gone.**
`saveLights` names the file `lightFile_%s.json % time.strftime('%m%d')` —
month+day only, no time. Same-day saves **overwrite** the same file. If you need
versioning, add `%H%M` (or a user-supplied name) to the filename.

**Q8. `saveLights` didn't remember which lights I had Solo'd (visibility off).**
Correct — `saveLights` records only `translate, rotation, lightType,
intensity, color`. It does **not** save `visibility` (nor `scale`). Re-importing
always brings lights back visible at intensity-1-ish defaults. Add
`'visibility': light.visibility.get()` to the record and restore it in
`importLights` if you need solo state persisted.

**Q9. Why are Area and Volume lights defined with `partial(...)` while Point/Spot/Directional are plain functions?**
PyMel exposes direct constructors `pm.pointLight`, `pm.spotLight`,
`pm.directionalLight` — call them with no args. But area and volume lights are
created via the generic `pm.shadingNode('areaLight', asLight=True)`. Rather than
write two throwaway `def createAreaLight(self)` methods, the demo freezes those
arguments with `functools.partial`, so the dict's values are uniformly
zero-arg callables. `partial` captures arg values **at definition time**; a
`lambda` would capture them **at call time** — for fixed args like these it
doesn't matter, which is why the comment calls them "identical in most cases."

**Q10. How does a pure-Qt widget actually dock into Maya?**
`getDock()` is the recipe: (1) `pm.workspaceControl(name, dockToMainWindow=('right',1))`
creates a Maya-owned dockable panel and returns its **name**; (2)
`omui.MQtUtil_findControl(ctrl)` fetches the underlying Qt pointer for that
name; (3) `wrapInstance(int(qtCtrl), QWidget)` wraps the raw C++ pointer as a
Python `QWidget` you can parent to. The widget then "lives" inside Maya's dock.
Memorize this three-step bridge if you build any dockable Qt tool.

**Q11. Why PyMel here when every earlier demo used `cmds`?**
Ergonomics. `light.intensity.set(2.0)` and `light.getTransform()` read better
than `cmds.setAttr(name+'.intensity', 2.0)` plus a separate `cmds.listRelatives`
call, especially inside a UI class that touches the same node many times. The
tradeoff (noted in the file's own comments) is speed and some edge-case quirks;
for an interactive UI tool, clarity wins.

---

## Advanced Directions

1. **Separate a headless data model from the UI** (the biggest architectural
   gap vs `controllerLibrary`). Today `saveLights`/`importLights`/`populate`
   live on the window class, so nothing is scriptable without a GUI. Extract a
   `LightingState` class: `list_lights() -> [PyNode]`, `serialize() -> dict`,
   `save(path)`, `load(path) -> dict`, `apply(dict)` (create lights + set
   attrs). `LightingManager` then becomes a thin view over `LightingState`, and
   you can save/import lighting rigs from a render-farm script with no UI.

2. **Fix the real bugs as a hardening pass.** (a) `importLights` should call
   `self.refresh()` not `self.populate()`; (b) make `populate()` idempotent —
   skip lights that already have a `LightWidget` (track `self._lights` by node);
   (c) restore the missing `return light` in the 2016Below file; (d) widen the
   intensity slider to `setMinimum(0)` and switch to a `QDoubleSpinBox` for
   fractional values; (e) wrap every slot in `try/except` + `logger.exception`
   so one bad light doesn't kill the panel.

3. **Support ambient + renderer-specific lights (Arnold/Redshift).** Extend
   `lightTypes` with `"Ambient Light": pm.ambientLight`; detect the renderer with
   `cmds.pluginInfo(q=True, listPlugins=True)` (look for `mtoa`/`redshift4maya`)
   and, when present, expose `aiExposure` / `aiSamples` / `aiDecayType` as extra
   row widgets. This turns the manager into a renderer-aware tool.

4. **Per-light preset library (not just whole-rig MMDD).** Replace the single
   `lightFile_<MMDD>.json` dump with a `LightLibrary` that saves **named**
   individual light presets (`key_warm.json`, `rim_cool.json`) with optional
   viewport thumbnails (reuse `controllerLibrary`'s `playblast` screenshot
   trick). Add a library browser panel and an "import preset at cursor" action.

5. **Undo chunks + safe batch operations.** Today dragging the intensity slider
   fires one `setAttr` per tick with no undo grouping, and Solo fans out many
   visibility changes — both create undo spam. Wrap slot bodies in
   `with pymel.core.UndoChunk():` (or `cmds.undoInfo(openChunk=True/False)`).
   Add the README's "batch intensity scaling" slider (multiplies every light's
   intensity) and an A/B preset-compare toggle, both as single undoable chunks.

6. **OpenMaya callbacks for live sync + shot-based lighting.** Today the manager
   only learns about scene changes when you click Refresh. Add an
   `MNodeMessage.addNodePreRemovalCallback` (see
   `cameraMessageCmd/cameraMessageTest/`) so deleting a light in the Outliner
   auto-removes its row, and a `MSceneMessage` callback to re-populate on
   file open. Then tie presets to shots/cameras — `save_for_shot(shot_name)`
   and `load_for_shot(shot_name)` — for a basic shot-based lighting system.
