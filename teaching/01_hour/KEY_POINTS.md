# Hour 1 — Key Points: Why Python in Maya + Setup + First Scripts

> **Goal of hour 1:** Every student leaves with a working setup (VS Code ↔ Maya)
> and the experience of having run two scripts inside Maya. Zero prior coding
> assumed.

**Time budget:** 60 minutes total. Three blocks:

```
┌──────────────────┬──────────────────┬──────────────────┐
│  Block A: 15 min │  Block B: 20 min │  Block C: 25 min │
│  "Why?"           │  Setup            │  First scripts   │
│  Real scenarios   │  VS Code + Maya   │  helloWorld +    │
│                   │                   │  helloCube       │
└──────────────────┴──────────────────┴──────────────────┘
```

---

## BLOCK A — Why Python in Maya? (15 min)

### A1. Open with a finished tool, not a slide (3 min)

**Before saying anything about Python**, demo a tool that saves real time.
Pick one of these from the repo:

- **`objectRenamer`** — select 50 controls, click one button, all renamed with a numbered prefix. (8 seconds vs 5 minutes by hand.)
- **`controllerLibrary`** — click to save a controller shape, drag-drop to re-use it later. (Shows UI + icon gallery — feels like a "real" app.)
- **`gearCreator`** — type "teeth = 24" in a window, get a finished gear. (Shows geometry generation.)

> **Teaching point to make out loud:** *"I built all three of these with the
> exact same Python you're going to learn today. None of it is special
> wizardry — it's just the commands you already click in Maya, written down
> as text."*

### A2. What Python in Maya actually is (4 min)

Make these three distinctions explicitly — students get confused without them:

| Thing                | What it is                                              | When you reach for it                         |
|----------------------|---------------------------------------------------------|-----------------------------------------------|
| **MEL**              | Maya's original scripting language                      | Don't — use Python instead                    |
| **Python `cmds`**    | Python calling the same commands MEL does               | 90% of your day-to-day tools                  |
| **PyMel**            | A more Pythonic wrapper over the same things            | When `cmds` feels clunky (mostly rigging)     |
| **OpenMaya (API)**   | Low-level C++ API exposed to Python                     | Performance, callbacks, custom nodes, meshes  |

> **The "aha" line:** *"Everything you can do by clicking in Maya is a
> command. Python lets you chain those commands together and run them a
> thousand times without your mouse."*

### A3. Real-life scenarios (8 min)

Walk through 5 concrete things Python does in real studios. **For each, name
the pain it removes first**, then the Python solution:

1. **Repetitive renaming.** Animator has 200 controls named `nurbsCircle1`,
   `nurbsCircle2`… Pain: hand-renaming takes an hour, mistakes creep in.
   Python: `objectRenamer` does it in 1 second, perfectly.

2. **Procedural geometry.** Modeler needs gears with 12, 16, 24, 32 teeth.
   Pain: build each by hand. Python: `gearCreator` takes one argument and
   builds any gear.

3. **Rigging helpers.** Rigger wants a library of saved control shapes
   (foot, hand, fk arc) they can drop into any rig. Pain: re-draw every time.
   Python: `controllerLibrary` saves them to disk with previews.

4. **Batch file ops.** Compositor has 500 frames named `render.0001.exr`
   but the pipeline expects `shot_24_beauty_v01.0001.exr`. Pain: rename by
   hand or fight with Windows. Python: a 30-line script renames them all.
   (`commandLine/renamer`.)

5. **Animation tweener.** Animator wants a quick ease-in/out between two
   keys without opening the Graph Editor. Pain: 5 clicks per channel.
   Python: `tweener` puts a slider in a window — one drag.

> **Close block A with this:** *"Every one of those is in this repo. By hour
> 7 today you'll understand how all of them work."*

---

## BLOCK B — Environment Setup: VS Code + Maya (20 min)

> **This is the highest-dropout moment of any coding course.** If setup
> doesn't work for someone, they leave. Budget the full 20 minutes and
> circulate the room.

### B1. Why VS Code (not Maya's Script Editor) (2 min)

- Script Editor is fine for **one-liners** and quick tests.
- VS Code gives you: real file editing, autocomplete, git, multi-file
  projects, debugging. Anything longer than 10 lines belongs in VS Code.
- The original course used PyCharm — VS Code is the modern free default.
  Either works; we'll standardize on VS Code so everyone's on the same page.

### B2. Install checklist — walk through together (8 min)

Have students follow along. **Circulate.** Stop when everyone has each
checkbox.

- [ ] **Maya installed** (2020+ works; 2027 ideal — Python 3).
      Check: open Maya, type `print("hi")` in the Script Editor (Python tab),
      Ctrl+Enter. You should see `hi`.
- [ ] **VS Code installed** — <https://code.visualstudio.com/>
- [ ] **Python extension** in VS Code — open Extensions panel, search
      "Python" by Microsoft, install.
- [ ] **Clone the repo** to a known path, e.g. `D:\2026MayaPython`.
      ```bash
      git clone https://github.com/MaxLYJ/PythonForMayaSamplesLearn.git
      ```
- [ ] **Open the repo folder in VS Code** — `File → Open Folder`.

### B3. The key trick: connecting VS Code's Python to Maya's Python (6 min)

**The single most important concept of setup:** Maya ships its *own* Python
interpreter (`mayapy`). The `maya` module isn't available to system Python.
So we point VS Code at `mayapy`.

**Find mayapy on each OS:**

| OS      | Path                                                                |
|---------|---------------------------------------------------------------------|
| Windows | `C:\Program Files\Autodesk\Maya<YEAR>\bin\mayapy.exe`               |
| macOS   | `/Applications/Autodesk/maya<YEAR>/Maya.app/Contents/bin/mayapy`    |
| Linux   | `/usr/autodesk/maya<YEAR>/bin/mayapy`                               |

**In VS Code:**

1. `Ctrl+Shift+P` → "Python: Select Interpreter" → "Enter interpreter path"
2. Browse to the `mayapy.exe` from the table above.
3. Open a terminal in VS Code (`Ctrl+~`) and verify:
   ```bash
   "C:\Program Files\Autodesk\Maya2027\bin\mayapy.exe" -c "import maya; print('ok')"
   ```
   Should print `ok` (or close to it).

> **Note for the class:** `mayapy` is **headless Maya** — same Python, no UI.
> Great for testing commands. We'll come back to it in hour 2 when we run
> scripts from the command line.

### B4. Three ways to run Python in Maya (4 min)

Set expectations: there are **three** run paths, and you'll use all three today.

1. **Script Editor (inside Maya)** — paste code, Ctrl+Enter. Fastest for
   experiments. **This is how we'll run hour 1's demos.**

2. **VS Code → save `.py` → drag into Maya / `execfile` / shelf button.**
   The "edit in a real editor, run in Maya" loop.

3. **`mayapy` from terminal** — runs Maya Python without the UI. Hour 2's
   command-line renamer uses this.

> **Live demo:** open `introduction/helloWorld.py` in VS Code, copy its
> contents, paste into Maya's Script Editor (Python tab!), Ctrl+Enter.
> Everyone should see `Hello, World!`. **Setup verified.**

---

## BLOCK C — First Scripts: helloWorld and helloCube (25 min)

> Now that setup works, we actually write code. Both demos are in
> `introduction/`. Read the commented `.py` together, **then run it**.

### C1. `helloWorld.py` — Python fundamentals in 12 lines (8 min)

Open `introduction/helloWorld.py`. Read it together.

#### Key points to extract:

- **`print`** — Python's "show me a value" command. The most basic
  debugging tool you'll ever use.
  ```python
  # Python 2 (the original file):
  print "Hello, World!"
  # Python 3 (Maya 2027+ — see helloWorld_2027.py):
  print("Hello, World!")
  ```
  > **Call this out explicitly:** the parens are the only difference. The
  > original files use Python 2 syntax; the `_2027.py` versions use Python 3.
  > Maya 2020 and earlier = Python 2; Maya 2022+ = Python 3.

- **Comments** — anything after `#` is ignored by Python, read by humans.
  Use liberally. The repo's `.py` files are heavily commented *on purpose* —
  they're teaching files.

- **Docstrings** — triple-quoted strings at the top of a file/function.
  ```python
  """
  This is a docstring. It documents the file.
  Python ignores it at runtime but tools display it.
  """
  ```
  Point out that `helloWorld.py` opens with one.

- **Strings** — text in quotes. Single or double, as long as they match.
  ```python
  "Hello, World!"
  'Hello, World!'     # same thing
  ```

#### Run it

Copy the contents → paste into Maya's Script Editor → Ctrl+Enter.
**Everyone should see `Hello, World!` in the output.**

> **Why this matters (say it out loud):** *"This isn't trivial. You just
> proved your Python is wired up. Every script you'll write this whole course
> starts from this exact foundation."*

### C2. `helloCube.py` — Talking to Maya for the first time (15 min)

Open `introduction/helloCube.py`. **This is the most important file in the
whole repo for a beginner.** It introduces ~8 concepts in 75 lines. Read it
in chunks, running as you go.

#### Chunk 1: Importing (lines 1–7)

```python
from maya import cmds
```

- **`import`** — bring in a module (a Python toolbox). `maya` is the package,
  `cmds` is the module inside it.
- **`cmds`** = "commands." This is THE library you'll use 90% of the time.
  Every Maya action — `polyCube`, `circle`, `setAttr`, `select` — lives here.
- **Aliasing alternative:** `import maya.cmds as cmds` does the same thing.
  The repo uses both; pick one and be consistent.

#### Chunk 2: Variables + the `cmds` return value (lines 9–25)

```python
cube = cmds.polyCube()
print(cube)
print(type(cube))
```

- **Variables** — nicknames for values. `cube` is just a label.
- **The big surprise:** `cmds.polyCube()` returns a **list**, not a single
  name. Print it and you'll see something like `['pCube1', 'polyCube1']`.
  - The first item is the **transform** (the thing with translate/rotate).
  - The second is the **shape** (the geometry itself).
- **`type(cube)`** → `<class 'list'>`. Verifies it's a list.

> **Teaching moment — the transform/shape split.** Most beginners don't know
> Maya has two nodes per visible object. Pause here. Show it in the Outliner
> with "Display → Shapes" enabled. *This is a Maya concept, not a Python one
> — but Python forces you to confront it because the return value is a list.*

#### Chunk 3: List indexing (lines 27–37)

```python
transform = cube[0]
creator = cube[1]
```

- **Computers count from 0, not 1.** `cube[0]` is the first item.
- **`[]` notation** — "give me item at this index."
- This is why you write `cube[0]` for the transform, not `cube[1]`.

> **Common mistake to flag:** students type `cube[1]` thinking "first item."
> Have them print `cube[0]` and `cube[1]` side by side and watch which is
> which.

#### Chunk 4: Creating more + reassigning variables (lines 39–52)

```python
circle = cmds.circle()
print(circle)
circle = circle[0]
```

- Same list-return pattern as `polyCube()`.
- **Variables can be reassigned.** `circle` first holds the whole list, then
  we point it at just the transform. Python is fine with this.

#### Chunk 5: Commands with arguments — positional vs keyword (lines 54–70)

```python
cmds.parent(transform, circle)               # positional
cmds.setAttr(transform+'.translate', lock=True)  # keyword
```

This is a critical distinction students will meet forever:

- **Positional arguments** — order matters. `cmds.parent(child, parent)`.
  Swapping them parents it the wrong way.
- **Keyword arguments** — order doesn't matter, name does.
  `lock=True` is a keyword arg. `cmds.setAttr(x, lock=True)` and
  `cmds.setAttr(x, lock=True, ...)` work the same.
- **String concatenation:** `transform + '.translate'` joins two strings into
  `'pCube1.translate'` — Maya's "attribute path" syntax.

#### Chunk 6: Select to verify (lines 72–73)

```python
cmds.select(circle)
```

End on a visible result. The circle should now be selected in the viewport.

#### Run the whole file

Paste into Script Editor → run. Everyone should see:
1. A cube parented under a circle.
2. The cube's translate/rotate/scale channels locked (greyed out).
3. The circle selected.

> **The framing line:** *"You just built a rig control. Animators use
> hundreds of these. You wrote it once."*

### C3. Wrap-up: what they now know (2 min)

End the hour by listing what they've already seen:

- ✅ `print`, comments, docstrings, strings
- ✅ Variables and reassignment
- ✅ Lists and indexing (counting from 0)
- ✅ `from maya import cmds`
- ✅ Creating nodes (`polyCube`, `circle`)
- ✅ `cmds.parent`, `cmds.setAttr`, `cmds.select`
- ✅ Positional vs keyword arguments
- ✅ The transform/shape split
- ✅ Running code in Maya's Script Editor

**Preview hour 2:** *"Next hour we leave the Script Editor behind and write
real `.py` files that run from a terminal — the foundation of every batch
tool."*

---

## Common student questions to anticipate

| Question                                         | Answer to give                                                                                  |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------|
| "Python 2 or 3?"                                 | Maya 2022+ is Python 3. Use the `_2027.py` files. The originals are Python 2 — only the print syntax differs in hour 1. |
| "Do I need to install Python separately?"        | No. Maya ships its own (`mayapy`). VS Code just needs to know where it is.                      |
| "`cmds` vs `pymel`?"                             | `cmds` is built-in and simpler. `pymel` is more Pythonic but adds a dependency. We'll meet `pymel` in hour 7. |
| "Why does `polyCube()` return a list?"           | Because most Maya commands can create multiple things. Returning a list always, even for one, is consistent. |
| "How do I find the command for X?"               | Do X manually in Maya → open Script Editor → the command shows up at the top. This is the #1 trick. |
| "My `setAttr` line errored."                     | You probably typed `lock="True"` (string). It needs the bare `True` (boolean).                   |

---

## Timing safety margin

- Block A: 15 min (tight, but no live coding — pure demo)
- Block B: 20 min (setup is unpredictable — protect this time)
- Block C: 25 min (the actual content)
- **= 60 min exactly.** If Block B overruns (someone's install is broken),
  cut A3 to 5 scenarios instead of 5, don't cut Block C.

> **Rule of thumb:** never cut the hands-on coding block. Cut the lecture.
