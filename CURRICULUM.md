# Maya Python — Hands-On Curriculum

A learner-facing index of the **`HowToStart<Demo>.md`** guides in this repo.
Each guide turns a demo folder into a repeatable hands-on lesson: the minimum
Maya scene to build, the exact Script-Editor commands to run, grounded Q&A a
learner would ask after trying it, and concrete ways the demo could evolve.

> **What a `HowToStart` guide always contains** (same 4-section shape in every one):
> 1. **How to Create the Test Maya Scene** — concrete, named objects/node types/selection.
> 2. **How to Run the Functions** — exact import path + Script-Editor commands + expected viewport/outliner result.
> 3. **Question and Answer** — 8–11 pairs grounded in *that demo's* actual code (not generic).
> 4. **Advanced Directions** — 5–6 scoped extension ideas, each with the new functions/classes it would require.
>
> Where a demo needs no Maya scene (pure-Python or pure-math demos), the
> "Create the Test Scene" section honestly says so instead of inventing steps.

---

## How to use this curriculum

- **Read the original `.py` for theory** — it is the heavily-commented teaching reference.
- **Run the `_2027.py` companion** — it is the version that actually runs on Maya 2027 (Python 3 + PySide6 + OpenMaya API 2.0). See `AGENTS.md` and `py3notes.md` for the full `_2027` convention. A handful of originals are hard `SyntaxError`s on Python 3 (Py2 print statements); only their `_2027` copies run.
- **Follow the demo's `HowToStart<Demo>.md`** for the scene + run steps. Most demos are *definitions-only libraries* (no `__main__`, no test calls) — the guide tells you the import-and-call workflow the file itself never shows.
- **Verify claims by reading the code, not the comments.** Every guide flags the source bugs, stale docstrings, and README-vs-source divergences it found — those are the richest learning material in the curriculum.
- **Run inside Maya.** These are Script-Editor scripts (or `loadPlugin` plugins), not shell scripts. The single runnable driver outside Maya is `commandLine/renamer`; everything else needs Maya's interpreter. Demos that could not be fully verified without Maya running are marked ⚠️ in their guides.

---

## The 19 demos in learning order

### Phase 1 — Talking to Maya (Python fundamentals)

| # | Demo | Difficulty | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 1 | `introduction` — `helloWorld`, `helloCube` | ★☆☆☆☆ | `print`, `from maya import cmds`, creating nodes, lists, `setAttr`/`parent`. The "is Python even working?" flat scripts. | [HowToStartIntroduction.md](introduction/HowToStartIntroduction.md) |

### Phase 2 — Real scripts & functions

| # | Demo | Difficulty | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 2 | `commandLine` — `renamer` | ★★☆☆☆ | `argparse`, `os`/`shutil` file I/O, `def main()`, the `__main__` guard. The repo's only **zero-Maya-dependency** demo — verified outside Maya. | [HowToStartCommandLine.md](commandLine/HowToStartCommandLine.md) |
| 3 | `objectRenamer` — `renamer1`, `renamer2` | ★★→★★★ | `cmds.ls`/`listRelatives`/`objectType`, loops, type-detection; then functions-with-defaults, dicts + `.get()`, docstrings, `raise`. The flat-script → function-library evolution. | [HowToStartObjectRenamer.md](objectRenamer/HowToStartObjectRenamer.md) |

### Phase 3 — Object-oriented programming

| # | Demo | Difficulty | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 4 | `gearCreator` — `gears1`, `gears2` | ★★★☆☆ | Multi-arg functions + tuples + poly-modeling cmds (`gears1`); then the same tool as a **class** with `__init__`/`self`/methods (gears2). The curriculum's first true definitions-only library. | [HowToStartGearCreator.md](gearCreator/HowToStartGearCreator.md) |

### Phase 4 — Animation & Maya's built-in UI

| # | Demo | Difficulty | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 5 | `tweener` — `tweener`, `reusableUI` | ★★★★☆ | The animation API (`keyframe`/`setKeyframe`/`currentTime`), keyframe interpolation math, and your **first Maya-built UI** (sliders/buttons). `reusableUI` adds class inheritance (`BaseWindow`) — and a cross-demo dependency on `gearCreator`. | [HowToStartTweener.md](tweener/HowToStartTweener.md) |

### Phase 5 — Professional Qt / PySide UIs

| # | Demo | Difficulty | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 6 | `controllerLibrary` | ★★★★★ | **PySide/Qt UI**, `json` save/load, `playblast` screenshots, `QListWidget` icon gallery, and model/view separation (`ControllerLibrary(dict)` + `ControllerLibraryUI`). | [HowToStartControllerLibrary.md](controllerLibrary/HowToStartControllerLibrary.md) |
| 7 | `lightManager` | ★★★★★ | The basics-course capstone: **PyMel**, custom Qt `Signal`s (the Solo chain), `OpenMayaUI` + `wrapInstance`, and a dockable `workspaceControl` UI. Pulls together everything from Phases 1–5. | [HowToStartLightManager.md](lightManager/HowToStartLightManager.md) |

### Phase 6 — Beyond the basics: standalone API & plugin demos

These eight demos extend past the 7-hour course. They introduce the OpenMaya API,
the message/callback system, and the two plugin archetypes (`loadPlugin` + `createNode`).
Tackle them in the order below — each builds on the previous.

| # | Demo | Archetype | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 8 | `fileDialog` | one-line script + wrapper | `fileDialog2`'s pick→get-path→act pattern; the dialog only returns a path, you do the `cmds.file(...)` action. First disk/OS-interaction demo. | [HowToStartFileDialog.md](fileDialog/HowToStartFileDialog.md) |
| 9 | `manipulatorMath` | pure-math library (no scene) | `MPoint`/`MVector`, ray/plane and ray/line intersection, dot-vs-scale, API 1.0. Zero `cmds` calls — the "scene" is just the input values. | [HowToStartManipulatorMath.md](manipulatorMath/HowToStartManipulatorMath.md) |
| 10 | `mathTableControl` | **plugin** (MPxCommand control) | The first `loadPlugin` demo: `initializePlugin`, the `kPythonPtrTable` + `asHashable` "find yourself again" idiom, edit flags, and driving a custom control via `cmds.spMathTableControl(...)`. | [HowToStartMathTableControl.md](mathTableControl/HowToStartMathTableControl.md) |
| 11 | `py1AnimCubeNode` | **plugin** (MPxNode DG node) | A dependency-graph node: `compute` + `attributeAffects` + `setClean` (the two rules that stop Maya spinning), `createNode` + `connectAttr` wiring, procedural animated mesh. | [HowToStartPy1AnimCubeNode.md](py1AnimCubeNode/HowToStartPy1AnimCubeNode.md) |
| 12 | `profilerDump` | library + driver | `MProfiler` capture sessions, dumping to JSON/CSV, the microsecond unit, and a runnable `test_example.py` driver. First performance-profiling demo. | [HowToStartProfilerDump.md](profilerDump/HowToStartProfilerDump.md) |
| 13 | `cameraMessageCmd` | event-callback library | The message system's register→store-`MCallbackId`→`removeCallback` lifecycle, `MCameraMessage` (interactive-only firing), and the API-1.0-vs-2.0 plumbing diff. | [HowToStartCameraMessageCmd.md](cameraMessageCmd/HowToStartCameraMessageCmd.md) |

### Phase 7 — Advanced Python for Maya (OpenMaya deep-dive)

The `AdvancedPythonForMaya-master/` section is a structured tour of the OpenMaya API,
mirroring Autodesk's official sample set. Each folder pairs an API-1.0 file with an
API-2.0 file as a deliberate contrast, except where API 2.0 cannot do the job
(deformers, transforms) and the demo stays on API 1.0.

| # | Demo | Archetype | You learn | Guide |
|--:|------|-----------|-----------|-------|
| 14 | `Intro` — `simple`, `standalone` | flat script + hybrid | The gateway to the API section: API-1.0-vs-2.0 imports, `MGlobal.displayInfo` routing, and the `MItDependencyNodes(om.MFn.kAnimCurveTimeToAngular)` typed-iterator vs `cmds.ls(type=...)`. | [HowToStartIntro.md](AdvancedPythonForMaya-master/Intro/HowToStartIntro.md) |
| 15 | `Commands` — `decorators`, `helloWorldCmd`, `distributeCmd` | pure-Python + MPxCommand plugin | A pure-Python decorators lesson, a minimal `MPxCommand`, and an **undoable** command (`isUndoable`/`doIt`→`redoIt`/`undoIt` contract, per-instance undo stack). | [HowToStartCommands.md](AdvancedPythonForMaya-master/Commands/HowToStartCommands.md) |
| 16 | `Nodes` — `minMaxNode`, `pushDeformer` | MPxNode (API 2.0) + MPxDeformerNode (API 1.0) | The full API-1.0-vs-2.0 dependency-node contrast: `compute` (API 2.0) vs `deform` + geometry iterators (API 1.0, because API 2.0 can't author deformers). | [HowToStartNodes.md](AdvancedPythonForMaya-master/Nodes/HowToStartNodes.md) |
| 17 | `Scene` — `characterRoot`, `customLocator` | MPxTransform + MPxLocatorNode/MPxDrawOverride | DAG-node plugins: a custom transform (`registerTransform` + AE template) and a procedurally-drawn locator (the `prepareForDraw`/`addUIDrawables` Viewport-2 pipeline). | [HowToStartScene.md](AdvancedPythonForMaya-master/Scene/HowToStartScene.md) |
| 18 | `Utilities/callbackManager` | architectural singleton | Evolution from Phase-6 raw callbacks to a reusable **signal-multiplexer hub**: dynamic per-signal methods, weak-ref storage, fault-isolated fan-out. | [HowToStartCallbackManager.md](AdvancedPythonForMaya-master/Utilities/HowToStartCallbackManager.md) |
| 19 | `Utilities/contexts` | pure-Python + Maya context | Python `with`-statement context managers (`__enter__`/`__exit__`, `@contextmanager`), then a Maya `MDGMessage.addNodeAddedCallback` node-capture context. | [HowToStartContexts.md](AdvancedPythonForMaya-master/Utilities/HowToStartContexts.md) |

> **Note on the word "context":** it is triple-overloaded in Maya. Demo 19 covers Python
> `with`-statement context managers (PEP 343) — *not* Maya viewport `MPxContext` tools, and
> *not* DG/`MDGContext` evaluation contexts. The guides disambiguate where it matters.

---

## Out of scope for this Python curriculum

- **`AdvancedPythonForMaya-master/Compiling/minMaxPlugin/`** — C++ `.cpp`/`.h` + CMake, no Python. The `minMax` logic is already covered in Python at demo 16 (`Nodes/minMaxNode`).
- **`teaching/`** — instructor meta-material (`SCHEDULE.md`, `SHOWCASE.md`, `KEY_POINTS.md`, `STUDENT_QA.md`). It is the teacher's 7-hour lesson plan and external "wow" demos, not a runnable Python demo.

---

## Cross-cutting reference (memorized facts the guides rely on)

These recurring facts are grounded in the guides and kept as project memory
(`.claude/projects/.../memory/`); they explain several "why does it behave that way?" moments:

- **`cmds.fileDialog2` returns `[]` (empty list) on Cancel**, not `None`. Both are falsy, so `if path:` is correct — but never compare to `None`. (demo 8)
- **Plugin demos use `initializePlugin`/`loadPlugin`, not import-and-call.** The `kPythonPtrTable` + `asHashable` idiom is how a Python MPx UI plugin re-finds itself after handing Maya a raw C++ pointer. (demos 10, 14–17)
- **Message callbacks have a 3-step lifecycle: register → store the `MCallbackId` at module/singleton scope → `removeCallback`.** Skipping storage (e.g. `importlib.reload` mid-session) leaves ghost callbacks that keep firing and can't be removed. (demos 13, 18)
- **The two "Maya freezes" bugs:** forgetting `data.setClean(plug)` in `compute()` (MPxNode) and forgetting `geoIterator.next()` in `deform()` (MPxDeformerNode) — both infinite-loop the DG. (demos 11, 16)
- **The window-reference GC pitfall:** `ui = showUI()` (or `Window().show()`) must keep the instance; bound-method callbacks die with a GC'd window. (demos 5, 6, 7)

For the full per-demo detail, open the guide for each demo above.
