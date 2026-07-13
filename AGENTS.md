# AGENTS.md

Guidance for ZCode agents working in this repo.

## What this repo is

Course code samples for **"Python For Maya: Artist Friendly Programming"** (Udemy, by Devanshu Govil).
This is a *learning fork* (`PythonForMayaSamplesLearn`) that adds per-demo `README.md`
files and **`_2027.py`** companions on top of the upstream `PythonForMayaSamples`.

There is **no build system, package manifest, requirements file, linter, or CI**. Code is a set of
standalone scripts meant to be pasted into **Maya's Script Editor** (Python tab) — not run from a
shell. The one "test" (`profilerDump/test_example.py`) is a manual smoke test run *inside Maya*.

## The `_2027` convention (read before editing any .py)

Each demo ships in **two forms** — do not collapse them:

| File               | Target                          | Role                                           |
|--------------------|---------------------------------|------------------------------------------------|
| `foo.py`           | Maya 2017/2018, **Python 2.7**  | Original, heavily commented — the *teaching* reference. Keep intact. |
| `foo_2027.py`      | Maya 2027, **Python 3 + PySide6 / Shiboken6 / OpenMaya API 2.0** | The one users actually *run*. |

- 6 demos needed real Py2→Py3 conversion; 6 were already Py3-compatible and got verified copies with
  a header note ("No code changes were required...").
- When fixing a runtime bug, fix the **`_2027.py`** file. When clarifying a *concept*, edit the
  original commented file. Keep both in sync where it makes sense.
- Qt imports differ: originals use the **`Qt.py`** shim (`import Qt; from Qt import QtWidgets...`);
  `_2027` files import **`PySide6`** directly. Don't port the shim back into `_2027` files.
- See `py3notes.md` for the canonical Py2→Py3 deltas (`basestring`→`str`, `long(win)`→`int(win)`,
  `print` as function, `importlib.reload`).

## Major directories

- Beginner→intermediate demos (in learning order): `introduction/`, `commandLine/`,
  `objectRenamer/`, `gearCreator/`, `tweener/`, `controllerLibrary/`, `lightManager/`.
- Standalone extras: `cameraMessageCmd/`, `fileDialog/`, `manipulatorMath/`,
  `mathTableControl/`, `profilerDump/`, `py1AnimCubeNode/`.
- `AdvancedPythonForMaya-master/` — a **separate sub-course** on the OpenMaya API (plugins, nodes,
  deformers, locators, C++ compiling). Targets Maya 2018; has its own `README.md` and difficulty
  table. Two APIs coexist here: `maya.api.OpenMaya` (2.0, modern) vs `maya.OpenMaya`+`OpenMayaMPx`
  (1.0, still required for deformers and custom transforms). The `maya_useNewAPI()` marker must stay
  in every API 2.0 plugin (it's a no-op but Maya checks for it).
- `teaching/` — a 7-hour workshop schedule (`SCHEDULE.md`) mapping hours to demos. Not code.
- Empty `__init__.py` files only mark packages — they contain no demos; leave them empty.

## Conventions to match

- **Model/view separation** in the Qt tools: a data class (`ControllerLibrary`) does no UI; a
  `...UI(QWidget)` class calls into it. Preserve this boundary when editing.
- **Logging** via the stdlib `logging` module with a named logger
  (`logging.getLogger('LightingManager')`, `logger.setLevel(logging.DEBUG)`) — used in the advanced
  demos instead of `print`. Match it in new code added to those files.
- **UI launch pattern**: files that define a Qt window end with a `showUI()` helper but **do not
  call it at module level** — importing does nothing visible. Don't "fix" this by adding a call.
- **Hardcoded `MTypeId` values** (e.g. `0x01010`) live in the safe dev range `0x00000–0x7FFFF`.
  Don't renumber casually.

## Running / verifying code

You cannot execute these scripts yourself (no Maya here). To tell a user how to run:

```python
import sys
sys.path.insert(0, r'/abs/path/to/<demoFolder>')
import <module>_2027 as m
ui = m.showUI()   # keep the reference or Qt GCs the window
```

Paths like `D:\2026MayaPython\...` in READMEs are **examples**, not real constraints — substitute
the user's clone location.

## Gotchas

- **`lightManager2016Below.py`** is *not* a separate demo — it's the same tool on the legacy
  `dockControl` API for Maya ≤2016. Use `lightManager.py` / `lightManager_2027.py` instead.
- **Controller Library screenshots** need the renderer set to **Maya Software**, not Arnold (the
  default since Maya 2017). Documented in `py3notes.md`.
- **`profilerDump`**: the on/off flag is `cmds.profiler(sampling=True/False)` — **not**
  `action='enable'`. The README originally got this wrong; `GUIDE.md` corrects it. Trust `GUIDE.md`
  + `test_example.py` over the older README text.
- **Qt window disappears instantly** → user didn't keep the `ui =` return value.

## Docs to read before touching sensitive areas

- Top-level `README.md` — demo difficulty table and learning order (the source of truth for which
  demo teaches what).
- `py3notes.md` — Py2→Py3 and Maya-version changes.
- `AdvancedPythonForMaya-master/README.md` — before editing anything under that folder.
- Each demo's own `README.md` / `GUIDE.md` — especially `profilerDump/GUIDE.md`.
- `teaching/SCHEDULE.md` — before reordering or relabeling demos.
