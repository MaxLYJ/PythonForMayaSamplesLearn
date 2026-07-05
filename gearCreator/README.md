# gearCreator — Building Geometry with Functions and Classes

This demo shows how to generate procedural geometry in Maya using Python —
specifically, a configurable gear. The same idea extends to screws, springs,
stairs, fences, anything repeating.

**The catch:** these files only contain `def`s (function definitions) and a
`class`. Running the file does **nothing visible** — you have to *call* the
functions. This README shows you exactly how.

---

## Files

| File              | What it is                                            | Difficulty |
|-------------------|-------------------------------------------------------|------------|
| `gears1.py`       | Functional version: `createGear()` + `changeTeeth()`  | ★★★☆☆      |
| `gears2.py`       | Object-oriented version: the `Gear` class             | ★★★☆☆      |
| `gears1_2027.py`  | Same as `gears1.py`, verified for Maya 2027 (Py3)     | ★★★☆☆      |
| `gears2_2027.py`  | Same as `gears2.py`, verified for Maya 2027 (Py3)     | ★★★☆☆      |

> Use the `_2027` versions if you're on Maya 2022 or newer. The originals
> are Python 2 (Maya 2020 and earlier).

---

## Quick start (the shortest path to a gear in your viewport)

1. **Open Maya's Script Editor** (`Windows → General Editors → Script Editor`).
2. **Python tab** — make sure you're not on the MEL tab.
3. **Paste this entire block** and press `Ctrl+Enter`:

```python
# 1. Import the gears module from this folder
import sys
sys.path.insert(0, r'D:\2026MayaPython\gearCreator')

# 2. Import the function (gears1) or the class (gears2)
import gears1_2027 as gears1
# import gears2_2027 as gears2   # uncomment to use the class version

# 3. CALL the function — this is the part the file doesn't do for you
transform, constructor, extrude = gears1.createGear(teeth=20, length=0.5)

print("Created gear:", transform)
```

You should see a gear with 20 teeth in your viewport. 🎉

> 💡 **Change the path** in line 2 to wherever you cloned the repo. On macOS
> or Linux, use forward slashes: `'/Users/you/2026MayaPython/gearCreator'`.

---

## Why doesn't the file do anything when I run it?

Because `gears1_2027.py` only **defines** functions:

```python
def createGear(teeth=10, length=0.3):
    ...
    return transform, constructor, extrude

def changeTeeth(constructor, extrude, teeth=10, length=0.3):
    ...
```

Defining a function is like writing a recipe. **Calling** it is cooking the
meal. The file gives you the recipe — you decide when and how to cook.

This is on purpose: defining-only files are **modules**. Other scripts can
`import` them and use the functions, without anything happening at import
time. (See Q8 in [`teaching/STUDENT_QA.md`](../teaching/STUDENT_QA.md) for
more on this pattern.)

The missing piece is `if __name__ == '__main__':` — a block that says
"only run this if I executed the file directly." None of the gear files
have one. You supply the call yourself, in the Script Editor.

---

## Usage — `gears1` (the functional version)

### Step 1: Import

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\gearCreator')
import gears1_2027 as gears1
```

### Step 2: Create a gear

```python
# Default: 10 teeth, 0.3 length
transform, constructor, extrude = gears1.createGear()

# Custom: 24 teeth, longer teeth
transform, constructor, extrude = gears1.createGear(teeth=24, length=0.8)
```

`createGear` returns a **tuple of three node names**:

| Return value   | What it is                                                  |
|----------------|-------------------------------------------------------------|
| `transform`    | The gear itself (`pPipe1`, `pPipe2`, ...)                   |
| `constructor`  | The `polyPipe` node that builds the underlying pipe         |
| `extrude`      | The `polyExtrudeFacet` node that pushes the teeth out       |

**Keep these three names!** You'll need them to change the gear later.

### Step 3: Modify it

```python
# Change to 12 teeth with shorter length.
# Pass back the constructor and extrude nodes you got from createGear.
gears1.changeTeeth(constructor, extrude, teeth=12, length=0.2)
```

The gear updates in-place. No new node is created (mostly — the extrude's
component list is rewritten, which is the cheap operation).

---

## Usage — `gears2` (the class version)

The class version is nicer once you have it loaded — **the instance
remembers** its own `transform`, `constructor`, and `extrude`, so you don't
have to pass them around.

### Step 1: Import

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\gearCreator')
import gears2_2027 as gears2
```

### Step 2: Make a Gear instance, then call its methods

```python
# Create an instance — this runs __init__, which sets placeholders
my_gear = gears2.Gear()

# Build the geometry (10 teeth, 0.3 length by default)
my_gear.create()

# Modify it — no need to pass back node names!
my_gear.changeTeeth(teeth=24, length=0.6)

# Change just the length, leave teeth alone
my_gear.changeLength(length=0.1)

# Make a second, totally independent gear
other_gear = gears2.Gear()
other_gear.create(teeth=8, length=0.2)
```

Notice the difference: `my_gear.changeTeeth(...)` takes only the
parameters you want to change. The gear knows its own nodes.

---

## Side-by-side: gears1 vs gears2

Same result, different style:

| Task                       | gears1 (functions)                                  | gears2 (class)                       |
|----------------------------|-----------------------------------------------------|--------------------------------------|
| Create                     | `t,c,e = createGear(teeth=20)`                      | `g = Gear(); g.create(teeth=20)`     |
| Change teeth later         | `changeTeeth(c, e, teeth=12)` (must pass c and e)   | `g.changeTeeth(teeth=12)`            |
| Change length later        | Not provided — call `cmds.polyExtrudeFacet(e, ...)` | `g.changeLength(length=0.1)`         |
| State (the node names)     | **You** track `t, c, e` in your script              | **The instance** tracks them on `self` |

**Use the class version** when you'll create multiple gears or modify them
over time. **Use the function version** for one-shot "build it and forget
it" scripts.

---

## Make a gear with a UI (bonus)

This is what **Hour 5** of the teaching schedule covers. A minimal window
with two sliders and a button:

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\gearCreator')
import gears2_2027 as gears2
from maya import cmds

window = cmds.window(title="Gear Creator", widthHeight=(300, 150))
cmds.columnLayout(adjustableColumn=True)

teeth_slider = cmds.intSliderGrp(label='Teeth', field=True, minValue=4, maxValue=40, value=20)
length_slider = cmds.floatSliderGrp(label='Length', field=True, minValue=0.05, maxValue=2.0, value=0.3)

def on_create(*args):
    teeth = cmds.intSliderGrp(teeth_slider, query=True, value=True)
    length = cmds.floatSliderGrp(length_slider, query=True, value=True)
    g = gears2.Gear()
    g.create(teeth=teeth, length=length)
    cmds.headsUpMessage("Created gear with %d teeth" % teeth)

cmds.button(label="Create Gear", command=on_create)
cmds.showWindow(window)
```

Each click builds a fresh gear with the slider values. (This is also a
template for the exercise in Hour 5: *reuse `BaseWindow` from `tweener`
for the gear tool.*)

---

## Common pitfalls

| Symptom                                                     | Cause                                                                                        | Fix                                                                                       |
|-------------------------------------------------------------|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'gears1_2027'`        | The folder isn't on `sys.path`                                                               | Add the `sys.path.insert(...)` line before `import`. Use a **raw string** (`r'...'`).     |
| `NameError: name 'transform' is not defined`                | You imported the module but didn't **call** the function                                     | Add `transform, constructor, extrude = gears1.createGear()` after the import.             |
| The Script Editor shows nothing                             | You imported but never called anything                                                       | Same — call `createGear()` or `Gear().create()`. The file defines; you must invoke.       |
| `changeTeeth` works but creates a second gear               | You re-ran `createGear()` instead of using the saved constructor/extrude                     | Save the return values the first time; pass them back to `changeTeeth()`.                 |
| Class version: `TypeError: create() missing 1 required positional argument: 'self'` | You called `Gear.create()` instead of `g.create()` (instance method)         | Always create an instance first: `g = Gear()`, then `g.create()`.                         |
| `SyntaxError: invalid syntax` on `print`                    | You're running `gears1.py` (Python 2) in Maya 2022+                                          | Use `gears1_2027.py` instead.                                                             |
| Your second gear replaces the first                         | Both gears use the default Maya name `pPipe1` and you didn't rename                          | Not actually a bug — Maya auto-renumbers. But if you stored `transform` it now points to the old one. Use the class version to avoid this. |
| The teeth are on the inside of the pipe                     | `localTranslateZ` is going the wrong way for your Maya version                               | Pass a negative length: `createGear(length=-0.3)`.                                         |

---

## What you'll learn from reading these files

If you're using this repo for the [7-hour course](../teaching/SCHEDULE.md),
this demo is **Hour 4** (functions that build geometry + classes). Key
concepts to extract:

- **Multi-argument functions with defaults** — `def createGear(teeth=10, length=0.3)`.
- **Returning a tuple** — `return transform, constructor, extrude` returns
  three values at once; you unpack them on the left side.
- **Poly modeling commands** — `cmds.polyPipe`, `cmds.polyExtrudeFacet`,
  and the `edit=True` flag for modifying existing nodes vs. creating new ones.
- **`%` string formatting** — `'%s.f[%s]' % (transform, face)` builds names
  like `pPipe1.f[20]`.
- **`*args` list unpacking** — `cmds.setAttr(..., len(faces), *faces, ...)`
  expands a list in-place as function arguments. (See
  [`STUDENT_QA.md`](../teaching/STUDENT_QA.md) Q&A for more.)
- **Classes** — `gears2.py` is `gears1.py` rewritten as a class. Diff them
  to see the conceptual leap: state moves from function arguments to `self`.

---

## Exercises

1. **Add a `radius` parameter.** `cmds.polyPipe` accepts `radius=` and
   `height=`. Expose them in `createGear` / `Gear.create`.
2. **Add a helical gear twist.** After extruding, apply
   `cmds.poly twist` to the teeth. (Look up the command in the Script
   Editor trick — see Q5 in [`STUDENT_QA.md`](../teaching/STUDENT_QA.md).)
3. **Color the teeth.** Use `cmds.polyColorPerVertex` or assign a new
   material to the tooth faces only.
4. **Make a gear train.** Create three gears of different sizes, position
   them along a line, and rotate them so the teeth mesh. (Math: gear-pitch
   distance = sum of radii.)
5. **Add a `delete()` method to the `Gear` class.** Should call
   `cmds.delete(self.transform)` and reset the placeholders to `None`.
6. **Port to PyMEL.** Rewrite `Gear` using `pymel.core` — the syntax is
   more object-oriented (`gear.teeth.set(20)` instead of
   `cmds.setAttr(...)`). Good practice before Hour 7.
