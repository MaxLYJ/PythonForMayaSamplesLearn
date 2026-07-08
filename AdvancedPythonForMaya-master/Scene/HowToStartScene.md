# HowToStartScene.md — Custom Scene Objects (`Scene/`)

> **Position in the curriculum.** This is the Advanced section's **scene-object plugin** demo — the companion to `Nodes/`. Where `Nodes/` showed nodes that live in the dependency graph and *compute values or deform geometry*, this folder shows nodes that **live in the DAG (outliner) as things you can see, select, and transform**: a **custom Transform** and a **custom Locator shape drawn to the viewport**. These are the building blocks of a real rig — a named root node that carries rig metadata, and bespoke control shapes that don't exist in Maya's stock locator set.

This guide covers **two** files that are deliberately paired to teach one contrast: **API 1.0 vs API 2.0** again — but here the split is driven by a *different* API-2.0 limitation than the one in `Nodes/`.

| File | Archetype | Maya scene needed? | Verified runnable? |
|---|---|---|---|
| `characterRoot.py` / `characterRoot_2027.py` | `MPxTransform` (**API 1.0** — not available in API 2.0) carrying `version`/`author` metadata + an Attribute-Editor MEL template | ✅ An empty scene to drop the node into | ⚠️ Logic source-verified; needs Maya to load |
| `customLocator.py` / `customLocator_2027.py` | `MPxLocatorNode` (**API 2.0**) + `MPxDrawOverride` that draws a square/triangle to Viewport 2 | ✅ An empty scene to drop the node into | ⚠️ Logic source-verified; needs Maya to load |

> You met `MPxNode`/`MPxDeformerNode` in `Nodes/`. A **transform** and a **locator** are *DAG* nodes (they have a place in the outliner and a world position), not pure DG nodes. A **locator** additionally needs a **draw override** so Viewport 2 knows how to paint it — the largest piece of code in this folder.

## The `_2027` convention

Every teaching file has a `<name>_2027.py` sibling: a Python-3 / Maya-2027-verified copy. For this folder the diff is **identical in both files** and fixes one **load-blocking bug** in the originals:

- **`characterRoot.py` → `characterRoot_2027.py`**: adds `import inspect`; replaces the hardcoded Windows path `dirName = 'E:\Projects\AdvancedPythonForMaya\Scene'` with `dirName = os.path.dirname(inspect.getfile(initializePlugin))`; and changes `os.getenv('MAYA_SCRIPT_PATH')` → `os.getenv('MAYA_SCRIPT_PATH', '')`. Everything else byte-identical.
- **`customLocator.py` → `customLocator_2027.py`**: the exact same three-line path-derivation fix (plus an `import os`/`import inspect` reorder). The two class bodies are byte-identical.

> **⚠️ Why you must use the `_2027` files.** The original `initializePlugin` does `MAYA_SCRIPT_PATH = os.getenv('MAYA_SCRIPT_PATH')` and then `if dirName not in MAYA_SCRIPT_PATH:`. When `MAYA_SCRIPT_PATH` is **unset** (true in a fresh `mayapy`, and possible in some Script-Editor contexts) `os.getenv` returns `None`, so `'...' not in None` raises **`TypeError: argument of type 'NoneType' is not a container or iterable`** — i.e. the plugin **crashes while loading**. (Confirmed by pure-Python reproduction.) In an interactive GUI session Maya usually pre-populates `MAYA_SCRIPT_PATH`, so the original *may* load there — but it is fragile. The hardcoded `'E:\Projects\...'` path also triggers a Python-3 **`SyntaxWarning: "\P" is an invalid escape sequence`** (and will eventually become a `SyntaxError`). The `_2027` files fix both. (Confirmed: both `_2027` files pass `py_compile`; both are definitions-only — no `if __name__ == '__main__'` guard.)

## Prerequisites

- **Maya 2027 (Python 3)** running interactively (GUI). Both files `import maya.*`, so they only parse/run inside Maya's interpreter (Script Editor → Python tab). `customLocator` additionally needs **Viewport 2.0** (the default renderer) to draw.
- The absolute path to this folder, referred to below as `/abs/path/Scene/`. Because the load snippet does `from Scene import characterRoot`, the folder above (`/abs/path/`) must be on `sys.path` — see Run steps.
- **⚠️ API-version split (same contrast as `Nodes/`, different reason).**
  - `characterRoot_2027.py` uses **API 1.0** (`from maya import OpenMaya` + `from maya import OpenMayaMPx`) and has **no `maya_useNewAPI()`**. Reason: **`MPxTransform` has no API-2.0 Python binding** — so a custom transform is one of the (few) remaining legitimate API-1.0 use cases. (This mirrors `Nodes/pushDeformer`, which is API 1.0 because API 2.0 can't author deformers.)
  - `customLocator_2027.py` uses **API 2.0** (`import maya.api.OpenMaya*`) and declares `maya_useNewAPI()`. Comment at the top: *"At long last we can go back to using the API v2.0."* — i.e. only the transform file is forced back to 1.0.
- **⚠️ Node-ID ownership.** Three reserved-range `MTypeId`s are used: `characterRoot` node = `0x01013`, its transformation matrix = `0x01014`, `customLocator` = `0x01015`. Fine for local/teaching use; never ship an ID in this dev range publicly without a reserved block from Autodesk (two plugins claiming the same ID corrupt each other's scenes).
- **⚠️ Attribute-Editor templates need the folder on `MAYA_SCRIPT_PATH`.** Both plugins append their own directory to `MAYA_SCRIPT_PATH` inside `initializePlugin` so Maya can discover the shipping `AEcharacterRootTemplate.mel` / `AEcustomLocatorTemplate.mel`. This is *why* the path-handling code exists at all.

## What the code actually does

### 1. `characterRoot.py` — a custom `MPxTransform` (API 1.0)

A normal transform (`cmds.spaceLocator`/group) has only translate/rotate/scale. A **custom transform** subclasses `MPxTransform` so you can add your **own attributes** (here: rig `version` and `author`) directly on the transform node, and ship a custom Attribute-Editor layout for them. Anatomy:

| Piece | In `characterRoot.py` | Purpose |
|---|---|---|
| `class CharacterRoot(ompx.MPxTransform)` | the node class | Subclass `MPxTransform` (DAG node with a transformation matrix). API 1.0. |
| `kNodeName = 'characterRoot'`, `kNodeID = om.MTypeId(0x01013)` | class attributes | The node-type name + persistent ID. |
| `kMatrix = ompx.MPxTransformationMatrix`, `kMatrixID = om.MTypeId(0x01014)` | class attributes | A custom transform can use a *custom transformation matrix*. Here it just reuses the base class — but **the matrix still needs its own ID**, so both are passed to `registerTransform`. |
| `version = om.MObject()`, `author = om.MObject()` | class placeholders | API 1.0 needs `om.MObject()` (not `None`) for unfilled attribute slots. |
| `creator()` (classmethod) | `return ompx.asMPxPtr(cls())` | Factory. `asMPxPtr` transfers ownership of the Python instance to Maya (API-1.0-only; the API-2.0 `customLocator` just returns `cls()`). |
| `initialize()` (staticmethod) | builds 2 attributes | Declares `version` (int) and `author` (string). |
| `initializePlugin(plugin)` | `registerTransform(name, id, creator, initialize, matrix, matrixID)` — **6 args** | The transform-specific register call. (Plain `MPxNode` uses 4-arg `registerNode`.) |

**`initialize()` flow (verified):** build an `MFnNumericAttribute` → create `version` as `kInt`, default `0`, `.storable=True` (persists in the saved scene) → build an `MFnTypedAttribute` → for a string attribute the **default value must itself be built** from `MFnStringData().create('Dhruv Govil')` → create `author` as `kString` with that default → `addAttribute` both. Neither attribute is set `.keyable`, so they appear in the **Node Editor / AE**, not the Channel Box.

**The AE template (`AEcharacterRootTemplate.mel`).** Maya auto-loads a file named `AE<NodeName>Template.mel` from `MAYA_SCRIPT_PATH` when you select a node of that type. It groups `version`/`author` under a "Character Attributes" layout. (The MEL is boilerplate: `editorTemplate -beginLayout … -addControl … -endLayout`, then `AEdependNodeTemplate` + `addExtraControls`.) This is the only demo in the curriculum that ships a **custom Attribute-Editor UI**.

### 2. `customLocator.py` — a `MPxLocatorNode` + `MPxDrawOverride` (API 2.0)

A locator is a DAG node with **no real geometry** — what you see is drawn procedurally. To draw a custom shape in Viewport 2 you need **three** cooperating pieces:

| Piece | In `customLocator.py` | Purpose |
|---|---|---|
| `class CustomLocator(omui.MPxLocatorNode)` | the node class | Subclass `MPxLocatorNode` (API 2.0). Holds the `shape` (enum) and `color` attributes. |
| `drawDbClassification = "drawdb/geometry/customLocator"` | class attribute | The **draw-database classification string** — Viewport 2 uses it to look up which draw override handles this node. Passed to `registerNode` as the `classification` arg. |
| `drawRegistrantId = "customLocatorPlugin"` | class attribute | A name under which the override is registered. Must match between `registerDrawOverrideCreator` and `deregisterDrawOverrideCreator`. |
| `class CustomLocatorDrawOverride(omr.MPxDrawOverride)` | the draw override | **Controls how VP2 renders the node.** Two callbacks: `prepareForDraw` (fetch/cache data) + `addUIDrawables` (issue draw calls). |
| `class LocatorData(om.MUserData)` | per-instance draw cache | Stores the resolved color + the line/triangle point lists, reused across draws. |
| `maya_useNewAPI()` | sentinel | API-2.0 marker (absent from `characterRoot`). |

**`initialize()` flow (verified):** build an `MFnEnumAttribute` → create `shape` with short name `'s'` → loop `for i, shape in enumerate(shapeNames)` calling `addField(shape, i)` (so `square`=0, `triangle`=1, because `shapeNames = sorted(shapes.keys())`) → `.storable=True` → build an `MFnNumericAttribute` → create `color` via `createColor('color','col')`, default `(0.5, 0.1, 0.1)`, `.storable=True` → `addAttribute` both.

**The draw pipeline (the heart of the file):**

1. **`prepareForDraw(objPath, cameraPath, frameContext, oldData)`** — Maya calls this when the node is dirty. **All attribute reads and geometry building happen here, NOT in the draw callback** (the comment warns: doing it in draw can crash Maya). It reuses the cached `LocatorData` if its `shape` index is unchanged; otherwise it rebuilds the line/triangle lists from the `shapes` dict.
2. **`addUIDrawables(objPath, drawManager, frameContext, data)`** — issues the actual draw calls through `drawManager`: `beginDrawable()` → `setColor(data.color)` → optionally `mesh(kTriangles, triangleList)` when the viewport is shaded → `mesh(kLines, lineList)` → `endDrawable()`.
3. **`LocatorData(om.MUserData)`** — `super().__init__(False)` means **do not delete after draw** (keep the cache so `prepareForDraw` can reuse it). Stores `shape`, `color`, `lineList` (`om.MPointArray`), `triangleList`.

> **The `isAlwaysDirty=False` + caching pair is the key performance teaching point.** The override is constructed with `isAlwaysDirty=False`, so Maya only calls `prepareForDraw` when the node is marked dirty. Inside, `if shape == data.shape: return data` skips the geometry rebuild when only the color changed. Color, by contrast, is re-fetched every draw (it can animate/change frequently). This is the canonical "cache the expensive shape data, refresh the cheap color" pattern.

### Verified source bugs (the best Q&A material)

Three bugs in `customLocator`'s draw math + one wrong comment, all confirmed by reading the code and reimplementing the geometry in pure Python:

1. **Shapes draw as OPEN outlines (missing closing edge).** The line loop is `for i in range(currentShapePointCount - 1)`, which produces `pointCount - 1` segments — an open chain from vertex 0 to the last vertex, with **no edge back from the last vertex to vertex 0**. Verified: the **square** draws only 3 of its 4 edges (right, bottom, left — the top edge is missing → looks like `[`/`C`); the **triangle** draws only 2 of its 3 edges. A closed polygon needs `pointCount` segments, i.e. `range(pointCount)` with the wrap-around `point[(i+1) % pointCount]`.
2. **The first triangle is degenerate.** The fan is `tri(point[0], point[i], point[i+1])` with `i` starting at 0, so the first iteration is `tri(0, 0, 1)` — two identical vertices → zero-area triangle that renders nothing. Harmless (wasted only) but a proper fan starts at `i=1`.
3. **The triangle *fill* is correct, the *outline* is not.** Worth separating: the `mesh(kTriangles, triangleList)` fan genuinely covers the whole convex shape (square = two valid triangles), so in **shaded** mode the shape looks filled and correct; the open-outline bug is only visible in **wireframe**. This nuance is why the bug is easy to miss.
4. **Wrong comment on the bitwise-AND.** The code reads `if state & omr.MGeometryUtilities.kDormant:` and the comment says *"The ampersand operator checks if the two bit values are equal."* That is **false** — `&` is bitwise AND (tests set-bit **intersection**, nonzero if *any* bit is shared), not equality. Equality would be `==` (or `^ == 0`). `displayStatus` returns a **bitmask**, so you *must* test with `&` (a status can be a combination like `kActive | kLead`); the comment's "equal" wording would mislead a learner into using `==`, which silently fails for combined states.

> **Minor depth-priority inconsistency (not asserted as a bug, hedged):** `addUIDrawables` picks the high wire-depth-priority using `state & omr.MGeometryUtilities.kActiveComponent`, but `kActiveComponent` is the status for selected **components** (vertices/faces), whereas the dormant-vs-not branch above uses `kDormant`. Selecting the **whole locator object** yields `kActive`, not `kActiveComponent`, so the high-priority branch may not fire for object-level selection on every Maya version. Treat the exact depth behavior as "confirm on your Maya version."

## How to Create the Test Maya Scene

Both nodes create **their own scene objects** — there is nothing to pre-build. The minimum scene is simply **an empty scene** (so the nodes you create are the only things in the outliner). The one real precondition is that **Viewport 2** is the active renderer (Window → Rendering Editors → Render Setup is irrelevant; it's the viewport's renderer, set in the panel menu → Renderer → Viewport 2.0, the default).

| Entry point | Scene / state it expects |
|---|---|
| `characterRoot` node | Empty scene; you will `createNode('characterRoot')`. Select the resulting node to see the custom AE. |
| `customLocator` node | Empty scene; you will `createNode('customLocator')`. Then change the `shape` enum / `color` to see the draw override react. |

> **⚠️ Reload safety.** Reloading either plugin while an instance of its node still exists in the scene will fail or warn (the node type is in use). The load snippets below therefore `delete` existing instances + `unloadPlugin(..., force=True)` before re-`loadPlugin` — the same `force=True` discipline as `Commands/distributeCmd`.

## How to Run the Functions

Both files are **definitions-only plugins** (no `__main__`): you do **not** "run" them by executing the file. You `loadPlugin` them, then exercise the registered node type via `cmds`. Always load the `_2027` versions (see Prerequisites).

### Run A — `characterRoot` (the custom transform + AE template)

In the Script Editor (Python tab):

```python
import sys
sys.path.insert(0, '/abs/path')          # parent of Scene/, so `from Scene import ...` works
from Scene import characterRoot_2027 as characterRoot   # use the fixed _2027 copy
import maya.cmds as cmds

# Clean any prior instance + plugin, then load the _2027 file.
try:
    cmds.delete(cmds.ls(type='characterRoot'))
    cmds.unloadPlugin('characterRoot', force=True)   # force: node type may still be registered
finally:
    loaded = cmds.loadPlugin(characterRoot.__file__) # robust: capture whatever stem Maya registers
    print('loaded:', loaded)

node = cmds.createNode('characterRoot', name='hero_rig')   # a transform node in the outliner
```

**Expected:** a transform node `hero_rig` appears in the Outliner. Because it is a transform you can parent the rig under it, move it, etc. Now **select** `hero_rig` and open the Attribute Editor (Ctrl+A): you should see a **"Character Attributes"** section (from `AEcharacterRootTemplate.mel`) containing `version` (int, default 0) and `author` (string, default `Dhruv Govil`). Set them:

```python
cmds.setAttr('hero_rig.version', 3)
cmds.setAttr('hero_rig.author', type='string', "Max Liu")
print(cmds.getAttr('hero_rig.author'))   # -> 'Max Liu'
```

> **If the "Character Attributes" section is missing**, the AE template was not found — i.e. the `_2027` path-derivation did not add this folder to `MAYA_SCRIPT_PATH` correctly, or you loaded the **original** (whose hardcoded `'E:\…'` path never resolves on Linux/Mac). The `version`/`author` attributes still exist on the node (visible under the "Extra Attributes" rollout) — only the custom *layout* is lost.

### Run B — `customLocator` (the drawn shape)

```python
import sys
sys.path.insert(0, '/abs/path')
from Scene import customLocator_2027 as customLocator   # the fixed _2027 copy
import maya.cmds as cmds

cmds.file(new=True, force=True)                       # clean scene (destructive — see warning)
try:
    cmds.unloadPlugin('customLocator', force=True)
finally:
    loaded = cmds.loadPlugin(customLocator.__file__)
    print('loaded:', loaded)

loc = cmds.createNode('customLocator')                # transform + locatorShape, drawn at the origin
```

**Expected:** a custom locator appears at the origin. With `shape` at its default (enum 0 = **square**) you will see the square outline — **but it is missing its top edge** (verified source bug #1). Now drive the attributes:

```python
cmds.setAttr(loc + '.shape', 1)        # 1 = triangle  (0 = square). Watch the outline redraw.
cmds.setAttr(loc + '.color', 0.2, 0.8, 0.2, type='double3')   # RGB — dormant color turns green
```

**Expected:** the shape switches to the triangle enum and (when **not** selected) is drawn in your green color. **Select** the locator — `prepareForDraw` switches the color to Maya's wireframe-selection color (`MGeometryUtilities.wireframeColor`). Toggle the viewport between **Wireframe** and **Shaded** (press `4`/`5`): in shaded mode the triangle-fan `mesh(kTriangles,…)` fills the shape; in wireframe you see only the (open) line outline. Switch to the **square** enum to see its missing top edge most clearly.

### Run C — one-shot paste for both, with robust unload

```python
import sys; sys.path.insert(0, '/abs/path')
import maya.cmds as cmds
from Scene import characterRoot_2027 as cr, customLocator_2027 as cl

def reload_plugin(mod, old_name, node_type):
    try:
        cmds.delete(cmds.ls(type=node_type))
        cmds.unloadPlugin(old_name, force=True)
    except Exception:
        pass
    return cmds.loadPlugin(mod.__file__)

print('characterRoot ->', reload_plugin(cr, 'characterRoot', 'characterRoot'))
print('customLocator ->', reload_plugin(cl, 'customLocator', 'customLocator'))

rig = cmds.createNode('characterRoot', name='rig_root')
loc = cmds.createNode('customLocator')
cmds.parent(loc, rig)                       # locator now a child of the custom transform
cmds.setAttr(loc + '.shape', 1)             # triangle
```

> **Cannot verify without Maya running:** the exact on-screen square/triangle outline (including the missing-edge bug), the AE layout rendering, the depth-priority behavior on selection, and whether Maya registers the plugin under the unsuffixed stem (`characterRoot`) or the suffixed one (`characterRoot_2027`) — the load snippets above capture `loadPlugin`'s return rather than hard-coding a name, so they work either way.

## Question and Answer

**Q1. Why is `characterRoot` API 1.0 when the rest of the Advanced section moved to API 2.0?**

Because `MPxTransform` has **no Python binding in API 2.0** — you literally cannot subclass it there. So a custom transform is forced back to API 1.0 (`from maya import OpenMaya`/`OpenMayaMPx`, `ompx.asMPxPtr(cls())`, no `maya_useNewAPI()`). `customLocator` can use API 2.0 because `MPxLocatorNode` *is* bound there. The top comment *"At long last we can go back to using the API v2.0"* celebrates exactly this — only the transform file is stuck on 1.0.

**Q2. What is `registerTransform`'s extra `matrix`/`matrixID` pair, and can I drop it?**

A custom transform can plug in a **custom transformation matrix** (e.g. a transform that constrains rotation, or rotates around a custom pivot). `characterRoot` doesn't need one, so it reuses the base `ompx.MPxTransformationMatrix` — but `registerTransform` **still requires** a matrix class and its own `MTypeId` (`0x01014`). You cannot drop them; if you don't need a custom matrix, pass the base class and a fresh dev-range ID, exactly as shown. (A plain `MPxNode` avoids this entirely with 4-arg `registerNode`.)

**Q3. Why does loading the ORIGINAL `.py` crash with `TypeError: NoneType is not iterable`?**

The original `initializePlugin` does `MAYA_SCRIPT_PATH = os.getenv('MAYA_SCRIPT_PATH')` then `if dirName not in MAYA_SCRIPT_PATH:`. When the env var is **unset**, `os.getenv` returns `None`, and `'…' not in None` raises that `TypeError` **while the plugin loads**. The `_2027` fix is `os.getenv('MAYA_SCRIPT_PATH', '')` — the empty-string default turns `None` into `''` so the `in` check is always safe. (Confirmed by reproduction.) It usually doesn't bite in an interactive GUI session because Maya pre-sets `MAYA_SCRIPT_PATH`, but it is a latent landmine.

**Q4. Why is the square missing its top edge / the triangle missing a side?**

Verified source bug: the line loop runs `range(pointCount - 1)`, drawing `pointCount - 1` segments — an **open** chain that never closes back to vertex 0. A closed polygon needs `pointCount` segments with a wrap-around index `(i+1) % pointCount`. The **fill** still looks correct in shaded mode because the triangle *fan* covers the whole convex shape; the open outline only shows in wireframe, which is why the bug is easy to overlook.

**Q5. Why does the first triangle do nothing?**

The fan is `tri(point[0], point[i], point[i+1])` with `i` starting at `0`, so iteration 0 is `tri(0, 0, 1)` — two identical vertices → a **degenerate** zero-area triangle that renders nothing. It's harmless (just wasted work). A clean fan starts at `i = 1`.

**Q6. What does `state & kDormant` actually test, and why does the comment mislead?**

`displayStatus` returns a **bitmask**, not a single enum. `&` is bitwise AND — it returns nonzero if `state` and `kDormant` **share any set bit** (intersection), **not** if they are "equal." The inline comment ("checks if the two bit values are equal") is **wrong**. The reason you *must* use `&` rather than `==` is that a status can be a combination (e.g. `kActive | kLead`); `== kDormant` would wrongly reject those combined states.

**Q7. Why is data fetched in `prepareForDraw` instead of `addUIDrawables`?**

`prepareForDraw` runs on Maya's update thread when the node is dirty; `addUIDrawables` runs inside the render loop. Reading plugs / building point arrays inside the render callback can **stall or crash** Maya (the source comment says so explicitly). The split also enables caching: `LocatorData` survives across draws (`MUserData(False)` ⇒ don't delete), so `prepareForDraw` rebuilds geometry only when the `shape` enum actually changes.

**Q8. What is `drawDbClassification` / `drawRegistrantId` and why are both needed?**

`drawDbClassification = "drawdb/geometry/customLocator"` is the **string key** Viewport 2 uses to find a draw override for a node type — it's passed to `registerNode` as the `classification` arg AND to `registerDrawOverrideCreator` as the first arg, so the two registrations **must match exactly**. `drawRegistrantId` ("customLocatorPlugin") names *who* registered the override; it must match between `registerDrawOverrideCreator` and `deregisterDrawOverrideCreator` or you leak the override on unload. A node with a `drawDbClassification` but no registered override draws nothing.

**Q9. Why `asMPxPtr` in `characterRoot.creator()` but plain `return cls()` in `customLocator.creator()`?**

It's the API-1.0-vs-2.0 ownership split from `Nodes/`. API 1.0 hands Maya a raw C++ pointer via `ompx.asMPxPtr(cls())`, transferring ownership *away* from Python. API 2.0 manages lifetime itself, so `customLocator.creator()` simply `return cls()`. This is the same contrast as `minMaxNode` (2.0) vs `pushDeformer` (1.0).

**Q10. What happens if I reload the plugin without deleting the node instances first?**

The node *type* is still in use, so `unloadPlugin` refuses with a "node type is registered/in use" error. The fix (used in the load snippets) is `cmds.delete(cmds.ls(type=…))` then `unloadPlugin(name, force=True)` — `force` because the type may linger registered even after the instances are gone. This is the same `force=True` reload discipline as the undoable commands in `Commands/`.

**Q11. How do I add a third shape (e.g. a circle/star)?**

Two places, both in `customLocator_2027.py`. (a) Add an entry to the module-level `shapes` dict — the `shape` enum is rebuilt from `sorted(shapes.keys())` in `initialize` (and re-sorted in `initializePlugin`'s `global shapeNames`), so the new shape appears automatically as the next enum index. (b) Mind the **draw bugs**: a circle needs many points and will reveal the open-outline bug badly, so fix the closing edge first. Adding attributes/templates for the new shape needs no AE-template change (the `shape` enum control already covers it).

## Advanced Directions

1. **Fix the draw pipeline (closing edge + clean fan + correctness).** Add a closed-outline helper: loop `range(pointCount)` with `point[(i+1) % pointCount]` for lines, and start the triangle fan at `i=1` to drop the degenerate. New: `CustomLocatorDrawOverride._buildLineLoop(points) -> MPointArray` and `_buildTriangleFan(points) -> MPointArray`, called from `prepareForDraw`. Bonus: support **non-convex** shapes via `MUIDrawManager.kPolygon`/a tessellator (the current fan only works for convex polygons).

2. **Parameterized, N-shape control library.** Move `shapes` from a hardcoded dict into a **JSON/TOML library** loaded at plugin init, and add a `size`/`scale` float attribute + a `lineWidth` int attribute consumed in `addUIDrawables` (`drawManager.setLineWidth`). New: a `ShapeLibrary` class (`load(path)`, `register(name, points)`), a `size` attribute wired through `prepareForDraw` (scale each `MPoint`), and a per-shape UI picker. This turns the demo into a real animation-control-shape tool.

3. **Rig-metadata transform → full rig-stamping system.** Extend `characterRoot` into a rig manifest node: add `rigName`/`createdDate`/`mayaVersion`/`dependencies` (string-array) attributes, an `onRigLoaded` callback that validates the rig against the stored Maya version, and a `MSceneMessage.kAfterOpen` hook that auto-stamps every root on file open. New: `CharacterRoot.initialize` extra attrs, a `validate_rig(root)` helper, and a `RigStamper` singleton registered in `initializePlugin`. Pair with the `callbackManager` demo for the lifecycle hooks.

4. **Custom transformation matrix (the feature `registerTransform` exists for).** Subclass `ompx.MPxTransformationMatrix` to implement a real constraint — e.g. a transform that **cannot rotate past ±X degrees**, or one that **auto-aligns to a surface normal**. Register it with its own `MTypeId` (currently `0x01014` points at the base class) and pass it as `CharacterRoot.kMatrix`. New: `class ConstrainedMatrix(ompx.MPxTransformationMatrix)` overriding `rotateBy`/`translateTo`, plus the `kMatrix`/`kMatrixID` wiring. This is the door `characterRoot` deliberately leaves closed.

5. **Editable shape via an in-viewport manipulator.** Add a `MPxManipContainer` so the user can drag the locator's points directly in the viewport and have them written back to a new `points` attribute (a `kMayaarray`/mesh-data attribute), bypassing the static `shapes` dict. New: `CustomLocatorManipContainer`, `connectToDependNode`, a `points` attribute + `attributeAffects(points)` plumbing, and a "Edit Shape" context command. This bridges to the `Utilities/` MPxContext demos.

6. **Installable rig-toolkit package + shelf launcher.** Package both plugins as a versioned Maya module (`rigToolkit.mod`) with `versioned`/`pinned` `MTypeId`s (request a real block from Autodesk for shipping), a one-click shelf button that `loadPlugin`s both, `createNode`s a `characterRoot` + a `customLocator` child, opens the AE, and wraps creation in an `undoInfo(openChunk)`/`(closeChunk)` pair. New: a `packaging/` layout, a `make_rig_root()` MPxCommand (so creation is undoable, à la `Commands/distributeCmd`), and the shelf-button bootstrap.
