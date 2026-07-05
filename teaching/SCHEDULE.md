# Maya Python — 7-Hour Teaching Schedule

A one-day intensive workshop built on the `PythonForMayaSamplesLearn` repo.
Designed for **artists with no programming background** who want to leave
the day able to write their own Maya Python tools.

---

## The 7-hour arc at a glance

| Hour | Topic                                                       | Repo demos used                                |
|-----:|-------------------------------------------------------------|------------------------------------------------|
| 1    | Why Python in Maya + Environment setup + first scripts      | `introduction/helloWorld`, `introduction/helloCube` |
| 2    | Real scripts: command-line tools & batch operations         | `commandLine/renamer`                          |
| 3    | Working with the scene graph: loops, conditions, functions  | `objectRenamer/renamer1`, `objectRenamer/renamer2` |
| 4    | Functions that build geometry + intro to classes            | `gearCreator/gears1`, `gearCreator/gears2`     |
| 5    | The animation API + first Maya UI                           | `tweener/tweener`, `tweener/reusableUI`        |
| 6    | Professional Qt/PySide UIs                                  | `controllerLibrary`                            |
| 7    | Capstone + a peek at the Maya API (OpenMaya)                | `lightManager`, `cameraMessageCmd`, `py1AnimCubeNode` |

> **Pacing principle:** every hour ends with the student running something
> visible in Maya. Never two consecutive "theory" segments without a payoff.

---

## Hour-by-hour outline

### Hour 1 — Why Python in Maya + Setup + First Scripts

> **Detailed key points below** in [`01_hour/KEY_POINTS.md`](./01_hour/KEY_POINTS.md)

Real-world scenarios → VS Code + Maya environment → `helloWorld` + `helloCube`.

### Hour 2 — Real Scripts: Command-Line Tools & Batch Operations

| Block | Focus                                          | Demo          |
|-------|------------------------------------------------|---------------|
| 0:00  | Recap: `cmds`, variables, lists (5 min)        | —             |
| 0:05  | `argparse` — Python scripts that take args     | `commandLine` |
| 0:20  | `os`, `shutil`, file I/O                        | `commandLine` |
| 0:35  | `def main()` and `if __name__ == '__main__'`   | `commandLine` |
| 0:50  | **Exercise:** modify the renamer to pad with `_v01` |               |

**Students leave with:** a Python script they can run from a terminal, outside Maya, that renames a folder of files. The "aha" — Python isn't just inside Maya.

### Hour 3 — Scene Graph: Loops, Conditions, Functions

| Block | Focus                                          | Demo            |
|-------|------------------------------------------------|-----------------|
| 0:00  | `cmds.ls`, `listRelatives`, `objectType`        | `renamer1`      |
| 0:15  | `for` loops, `if/elif/else`, string split/concat | `renamer1`     |
| 0:35  | From `renamer1` → `renamer2`: defaults, dicts, `.get()` | `renamer2` |
| 0:50  | **Exercise:** add a "skip if name already has suffix" rule |              |

**Students leave with:** a robust rename utility that handles selections, with docstrings and error handling. They've internalized the "select → loop → modify" pattern that 80% of Maya scripts use.

### Hour 4 — Functions That Build Geometry + Classes

| Block | Focus                                          | Demo        |
|-------|------------------------------------------------|-------------|
| 0:00  | Multi-arg functions, returning tuples           | `gears1`    |
| 0:15  | Poly-modeling cmds (`polyPipe`, `polyExtrude`)  | `gears1`    |
| 0:30  | **The conceptual leap:** `gears1` (functions) → `gears2` (class) | `gears1` → `gears2` |
| 0:45  | `class`, `__init__`, `self`, storing state      | `gears2`    |
| 0:55  | **Exercise:** add a `bevel` method to the class |             |

**Students leave with:** their first class. This is the hardest hour conceptually — give it air.

### Hour 5 — Animation API + First Maya UI

| Block | Focus                                          | Demo            |
|-------|------------------------------------------------|-----------------|
| 0:00  | `keyframe`, `setKeyframe`, `currentTime`        | `tweener`       |
| 0:15  | List comprehensions                             | `tweener`       |
| 0:25  | **First UI:** `cmds.window`, sliders, buttons   | `tweener`       |
| 0:45  | Inheritance: `BaseWindow` → child windows       | `reusableUI`    |
| 0:55  | **Exercise:** reuse `BaseWindow` for the gear tool |              |

**Students leave with:** a windowed UI that does animation work. The moment a tool gets a window, students feel like "real" tool developers.

### Hour 6 — Professional Qt/PySide UIs

| Block | Focus                                          | Demo                  |
|-------|------------------------------------------------|-----------------------|
| 0:00  | Why Qt over `cmds.window`                       | `controllerLibrary`   |
| 0:10  | `Qt.py` shim, `QListWidget`, signals/slots      | `controllerLibrary`   |
| 0:30  | `json` save/load + screenshot via `playblast`   | `controllerLibrary`   |
| 0:50  | **Exercise:** add a "rename" button to the library |                    |

**Students leave with:** a publishable control library tool with icon gallery — the kind of thing a real rigging department uses.

### Hour 7 — Capstone + Peek at OpenMaya API

| Block | Focus                                          | Demo                |
|-------|------------------------------------------------|---------------------|
| 0:00  | Pull it all together: PyMel + Qt + signals      | `lightManager`      |
| 0:15  | `dockControl` / dockable UI                     | `lightManager`      |
| 0:30  | **Beyond `cmds`: the OpenMaya API**             | `cameraMessageCmd`, `py1AnimCubeNode` |
| 0:40  | What callbacks are (event-driven vs polling)    | `cameraMessageTest` |
| 0:50  | Q&A, where to go next, resources                | —                   |

**Students leave with:** a map of the whole ecosystem — `cmds` for 90% of work, `pymel` for ergonomics, `OpenMaya` for performance and low-level access. They know which to reach for when.

---

## Course philosophy

1. **Show the payoff before the mechanics.** Hour 1 opens with finished tools doing real work — *then* we learn how.
2. **Never go 15 minutes without running something.** Long theory blocks lose artists. Every concept has a runnable `.py` in the repo.
3. **Use the 11 original demos as the spine.** They're already ordered by difficulty. The 7 new API demos (camera, fileDialog, manipulatorMath, etc.) are "look ahead" material, not core curriculum.
4. **Learn from the commented files, run the `_2027.py` versions.** The originals are Python 2 (heavily commented for teaching); the `_2027` siblings run in modern Maya.
5. **Every hour ends with an exercise, not a lecture.** Students retain the hour where they *wrote* code, not the one where they watched.

---

## Materials checklist (per student)

- [ ] Maya 2020+ installed (2027 ideal for Python 3)
- [ ] VS Code installed
- [ ] Python extension for VS Code
- [ ] This repo cloned locally
- [ ] `mayapy` on PATH (covered in hour 1)
- [ ] A working folder for exercises
