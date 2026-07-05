# Student Q&A — Maya Python Workshop

Anticipated questions for students across the 7-hour workshop, organized by
when they typically come up. Each answer is written to be **read aloud in
class** or handed out as a reference.

> **Companion to:** [`SCHEDULE.md`](./SCHEDULE.md) and
> [`01_hour/KEY_POINTS.md`](./01_hour/KEY_POINTS.md)

---

## Part 1 — Setup & "Why Python?" (Hour 1)

### Q1. Python 2 or Python 3?

**Use Python 3.** Maya 2022 and newer ship Python 3. The original demo files
in this repo are Python 2 (heavily commented for teaching), and the `_2027.py`
versions are Python 3.

The only difference you'll see in hour 1 is `print`:

```python
print "Hello!"      # Python 2 (the original helloWorld.py)
print("Hello!")     # Python 3 (helloWorld_2027.py) — note the parens
```

If you're on Maya 2020 or earlier, you're stuck on Python 2. Everything in
this course still works — just lose the parens on `print`.

### Q2. Do I need to install Python separately?

**No.** Maya ships its own Python interpreter called `mayapy`. It lives
inside the Maya install folder. VS Code just needs to be told where it is —
that's the "Select Interpreter" step in Block B of hour 1.

Installing standalone Python (from python.org or Anaconda) is fine for
learning general Python, but it **cannot import `maya.cmds`** — only
`mayapy` can.

### Q3. `cmds` vs `pymel` vs `OpenMaya` — which one do I use?

| Library      | Use it for                                              | Difficulty |
|--------------|---------------------------------------------------------|------------|
| `maya.cmds`  | 90% of everyday tools — selecting, creating, renaming   | ★☆☆☆☆ Easy |
| `pymel.core` | When `cmds` feels clunky; more object-oriented style     | ★★★☆☆ Medium |
| `maya.api.OpenMaya` | Performance, callbacks, custom nodes, mesh generation | ★★★★★ Hard |

**Start with `cmds`.** Everything in hours 1–6 uses it. We meet `pymel` in
the capstone (`lightManager`), and `OpenMaya` only in the final "look ahead"
demos (`cameraMessageCmd`, `py1AnimCubeNode`).

### Q4. Why does `cmds.polyCube()` return a list `['pCube1', 'polyCube1']`
###       instead of just the cube name?

Because most Maya commands can create **multiple** things at once —
`cmds.polyCube(n=5)` makes 5 cubes. Returning a list always, even for one
object, is consistent behavior. It's a small annoyance but you get used to
it: grab the transform with `cube[0]`.

### Q5. How do I find the Python command for something I know how to click?

**The Script Editor trick — your most important discovery tool.** Maya
prints the command for almost every action you take in the UI:

1. Open **Windows → General Editors → Script Editor**.
2. Clear the top output panel.
3. Do the action in Maya (create a cube, set an attribute, etc.).
4. Look at the top panel — the command appears, usually as `polyCube;` or
   `setAttr "pCube1.tx" 5;` (MEL syntax).
5. Translate to Python: lowercase first letter, add parens, quote strings.
   `polyCube;` → `cmds.polyCube()`.

This single trick will answer ~60% of "how do I do X?" questions for the
rest of your career.

### Q6. My `cmds.setAttr` line threw an error.

You probably passed a string when Maya wanted a different type:

```python
cmds.setAttr(cube+'.translate', lock="True")   # WRONG — "True" is a string
cmds.setAttr(cube+'.translate', lock=True)      # RIGHT  — True is a boolean
```

`"True"` (with quotes) is the four-letter string. `True` (no quotes) is
Python's boolean. They look similar but are completely different to Maya.

The same trap exists for numbers: `5` (int) vs `"5"` (string).

---

## Part 2 — Working with files & the command line (Hour 2)

### Q7. Why are we running Python from a terminal now? I thought we're in Maya.

Because some Python tools have nothing to do with the Maya UI — they just
process files on disk. The `commandLine/renamer` tool renames a folder of
image sequence files; that's pure OS work, no Maya scene needed.

Running from terminal also lets you **schedule** scripts (overnight batch
renders, automated backups) and **chain** them with other pipeline tools.

### Q8. `if __name__ == '__main__':` — what does this actually do?

It means "only run this code if I executed this file directly. If something
imported me, don't run it."

```python
def main():
    print("running")

if __name__ == '__main__':
    main()
```

- Running `python myscript.py` from terminal → `__name__` is `'__main__'`
  → `main()` runs.
- `import myscript` from another file → `__name__` is `'myscript'` →
  `main()` does NOT run. But you can still call `myscript.main()` yourself.

This lets your file be both a runnable script **and** an importable module.

### Q9. Why use `argparse` instead of just `input()`?

`argparse` lets users pass arguments at launch:

```bash
python renamer.py --folder ./images --prefix "shot24_"
```

vs. prompting interactively. Why it matters:
- **Automatable** — scripts can call other scripts with args, no human typing.
- **Repeatable** — same command, same args, same result. Great for pipelines.
- **Self-documenting** — `--help` shows users what flags exist.

---

## Part 3 — The scene graph, loops & functions (Hour 3)

### Q10. `cmds.ls(selection=True)` vs `cmds.ls('pCube1')`?

`cmds.ls` is a query — "give me a list of things."

```python
cmds.ls(selection=True)        # what the user has selected right now
cmds.ls('pCube*')              # everything whose name starts with "pCube"
cmds.ls(type='camera')         # every camera in the scene
cmds.ls(dag=True, ap=True)     # every DAG object in the scene
```

When you don't pass anything, `cmds.ls()` returns *everything*, which is
rarely what you want. Default to `selection=True` for tools that act on
what the user picked.

### Q11. Why does `listRelatives(parent=True)` return a list, not a string?

Same reason as Q4 — Maya commands tend to return lists even for one item,
for consistency. Wrap with `[0]` to grab the first:

```python
parent = cmds.listRelatives(cube, parent=True)[0]
```

### Q12. How do I make my function "remember" things between calls?

Two ways, in order of preference:

**Option A — closure / factory (functions only):**
```python
def make_counter():
    count = 0
    def step():
        count += 1   # actually needs 'nonlocal count' — see hour 4
        return count
    return step
```

**Option B — class (hour 4):**
```python
class Counter:
    def __init__(self):
        self.count = 0
    def step(self):
        self.count += 1
        return self.count
```

For state that's more than one variable, use a class. Hour 4 exists for this.

### Q13. What's the difference between `=` and `==`?

| Symbol | Meaning                              | Example                     |
|--------|--------------------------------------|-----------------------------|
| `=`    | Assignment — "make this equal to"    | `x = 5` (sets x to 5)       |
| `==`   | Comparison — "are these equal?"      | `if x == 5:` (asks)         |

Beginners constantly confuse them. `if x = 5:` is a syntax error in Python
(some languages allow it; Python doesn't, which protects you).

---

## Part 4 — Functions & classes (Hour 4)

### Q14. Why do I need `self` in class methods?

Because Python needs to know **which instance** of the class you're talking
about. Consider:

```python
class Gear:
    def __init__(self, teeth):
        self.teeth = teeth          # this specific gear's teeth count

g1 = Gear(12)
g2 = Gear(24)
g1.report()                         # prints 12
g2.report()                         # prints 24
```

When you call `g1.report()`, Python secretly passes `g1` as the first
argument. So:

```python
def report(self):                   # self IS g1 here
    print(self.teeth)
```

`self` is just the explicit name for "the instance this method was called
on." Some languages hide it; Python doesn't, which can feel clunky but is
honest.

### Q15. What's the difference between `__init__` and a regular method?

`__init__` runs **once, when the object is created**. Regular methods run
**whenever you call them**.

```python
g = Gear(12)        # __init__ runs here, sets self.teeth = 12
g.rotate()          # rotate() runs now (and any time after)
```

`__init__` is the "setup" — use it to set starting values. You never call
it directly; `Gear(12)` does.

### Q16. When do I use a class vs. just a function?

**Use a function** when:
- The operation is a one-shot: take input, return output, done.
- No state needs to persist between calls.

**Use a class** when:
- You have **multiple related pieces of state** that change together
  (a gear's teeth count + radius + bevel setting).
- You want to **reuse the same logic across many objects** (12-tooth gear,
  24-tooth gear, all sharing the `build()` method).
- The thing you're modeling has a **lifecycle** (create → modify → export).

If you find yourself passing 6 arguments to a function, you probably want a
class.

### Q17. What's the difference between a method and a function?

- **Function:** standalone. `def add(a, b): return a+b`. Called as `add(1, 2)`.
- **Method:** defined inside a class. `def report(self):` inside `Gear`.
  Called as `g1.report()`.

Methods always take `self` as the first parameter. Functions don't.

---

## Part 5 — Animation & Maya UI (Hour 5)

### Q18. `cmds.setKeyframe` vs `cmds.setDrivenKeyframe`?

- **`setKeyframe`** — key an attribute at the current time (or a time you
  specify). The classic animation key.
  ```python
  cmds.setKeyframe('pCube1', attribute='translateX', time=12, value=5)
  ```
- **`setDrivenKeyframe`** — key one attribute based on the value of
  another (no time component). E.g. "when hand opens, fingers curl."
  ```python
  cmds.setDrivenKeyframe('finger curl', currentDriver='hand.open')
  ```

The `tweener` demo uses `setKeyframe` to insert keys between existing ones.

### Q19. The `tweener` window appears then disappears immediately.

You forgot `cmds.showWindow(window_name)` at the end. The window is created
invisible; you have to explicitly show it:

```python
window = cmds.window(title="My Tool")
cmds.columnLayout()
cmds.button(label="Click me")
cmds.showWindow(window)         # ← DON'T FORGET THIS
```

### Q20. How do I make my button actually do something?

Pass a function (callable) to the `command=` flag:

```python
def on_click(*args):              # *args absorbs Maya's extra args
    print("clicked!")

cmds.button(label="Go", command=on_click)
```

**Two traps:**
1. **Pass the function, don't call it.** `command=on_click` ✓,
   `command=on_click()` ✗ (calls it immediately at window-build time).
2. **Always use `*args`** in the callback signature. Maya passes extra
   arguments to buttons that will crash your function if it doesn't accept
   them.

### Q21. List comprehension — what's `[_ for _ in _]`?

A compact way to build a list by transforming each item. Equivalent to a
`for` loop:

```python
# Long form
squares = []
for i in range(5):
    squares.append(i ** 2)

# Comprehension
squares = [i ** 2 for i in range(5)]
```

You can also filter:
```python
even_squares = [i**2 for i in range(10) if i % 2 == 0]
```

Once you read them fluently, you'll never go back. The `tweener` demo uses
them to gather keyframe times.

---

## Part 6 — Qt/PySide (Hour 6)

### Q22. Why Qt instead of `cmds.window`?

`cmds.window` is fine for simple tools (5 widgets, a button, done). It falls
apart fast:
- No native look (looks like 2005)
- Limited widget types
- No signals/slots (the cleanest event pattern)
- Hard to make complex layouts

**Qt** (via PySide2/PySide6) is what every professional Maya tool uses —
mGear, AdvancedSkeleton, StudioLibrary, etc. It looks native, has 50+ widget
types, and supports drag-and-drop, custom painting, dockable windows.

We use **`Qt.py`** as a shim — it auto-detects whichever Qt version Maya
ships (PySide, PySide2, PySide6, PyQt4, PyQt5) so your code runs anywhere.

### Q23. What's a "signal" and a "slot"?

The Qt event model:
- **Signal** — "something happened." A button was clicked. A slider moved.
  A value changed.
- **Slot** — a function that responds to a signal.

You connect them:
```python
button.clicked.connect(on_click)        # signal.connect(slot)
slider.valueChanged.connect(on_change)  # signal.connect(slot)
```

When the signal fires, the slot runs. Multiple slots can connect to one
signal (and vice versa).

### Q24. My Qt window doesn't stay on top of Maya / appears behind.

Two fixes:

```python
# Make the window stay on top
window.setWindowFlags(QtCore.Qt.Tool)

# Or — better — parent it to Maya's main window
import maya.OpenMayaUI as omui
from Qt.QtWidgets import QWidget
maya_window = wrapInstance(omui.MQtUtil.mainWindow(), QWidget)
window.setParent(maya_window)
```

The `controllerLibrary` demo shows the full pattern.

---

## Part 7 — Capstone & OpenMaya (Hour 7)

### Q25. When should I use OpenMaya instead of cmds?

`cmds` is fine for most tools. Reach for `OpenMaya` when:

| Need                                                | Why OpenMaya                       |
|-----------------------------------------------------|------------------------------------|
| React to events (selection change, attribute edit)  | `MMessage` callbacks (see `cameraMessageTest`) |
| Build procedural geometry in a custom node          | `MPxNode` + `MFnMesh` (see `py1AnimCubeNode`) |
| Touch thousands of components fast                  | `MFnMesh` iterates faster than `cmds` |
| Read mesh data (vertex positions, normals)          | `MFnMesh` direct access            |
| Custom manipulators                                 | `MPxManipulatorNode`               |

If your tool is "select → loop → setAttr", stick with `cmds`. The
`OpenMaya` demos in this repo are all under the
[API reference examples](../README.md) — they're the next step after this
course.

### Q26. API 1.0 vs API 2.0?

| API 1.0                                  | API 2.0                                         |
|------------------------------------------|--------------------------------------------------|
| `import maya.OpenMaya`                    | `import maya.api.OpenMaya`                       |
| Pre-allocate empty objects, fill them    | Methods return values directly                   |
| Verbose, more boilerplate                | Cleaner, more Pythonic                           |
| Older, more examples online              | Autodesk-recommended for new code                |

The two `cameraMessageTest` demos in this repo are the same example in both
dialects — diff them to see the difference. For new code, use 2.0.

### Q27. The official docs are JavaScript-heavy and I can't get clean source.

You're not alone — the modern Autodesk docs pages are JS-rendered and a pain
to scrape. Workarounds:
1. The 2009–2017 archive at `download.autodesk.com/us/maya/<year>help/API/`
   is static HTML and works fine.
2. The Maya install ships some examples under `devkit/plug-ins/`.
3. The devkit download (separate from Maya) has the full set.
4. Community mirrors on GitHub sometimes have clean copies.

---

## Part 8 — Beyond the course

### Q28. Where do I go next?

In rough order of value:

1. **Read the rest of this repo.** Demos 8–11 (`tweener`, `controllerLibrary`,
   `lightManager`) are real production-style tools.
2. **Study a real open-source tool.** See
   [`SHOWCASE.md`](./SHOWCASE.md) for a curated list — mGear, StudioLibrary,
   Batch Renamer, etc.
3. **Read *Maya Python for Games and Film* (Mechtley et al.).** The classic
   book. Heavy but comprehensive.
4. **Join the [Python Inside Maya](https://groups.google.com/forum/#!forum/python_inside_maya)
   Google Group.** Industry people answer questions here.
5. **Read the [Tech-Artists.org](https://tech-artists.org/) forums.**
6. **Build something.** Pick a tool you actually need at work/studio and
   write it. You'll learn more from one real tool than ten tutorials.

### Q29. How do I make my code "production quality"?

After the course, look up:
- **`flake8` / `black`** — auto-formatting and linting (catches style issues).
- **Unit tests** — `pytest` works with `mayapy`.
- **Type hints** — `def rename(node: str, prefix: str) -> None:`.
- **Logging** instead of `print` for tools you ship to others.
- **Documentation** — `__doc__` strings, `sphinx` for big projects.

None of this is in the course because it's overwhelming on day one. But it's
the difference between "tool I use myself" and "tool the studio uses."

### Q30. Is there a job market for this?

Yes. Titles to search: **Technical Artist (TA)**, **Tools Programmer**,
**Pipeline TD**, **Rigging TD**, **Character TD**. Every studio making games,
animation, or VFX has these roles, and Python-in-Maya is the core skill.

See [`SHOWCASE.md`](./SHOWCASE.md) for the kinds of tools that show up in
portfolios.
