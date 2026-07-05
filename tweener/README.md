# tweener — Animation Tweening Tool (Logic + UI)

This demo inserts a key between two existing keys, biased by a percentage.
Drag a slider to 50% → the in-between key sits halfway. 25% → it sits a
quarter of the way. It's a one-click ease-in/out for animators.

**Source files:** [`tweener_2027.py`](./tweener_2027.py) (logic + window),
[`reusableUI_2027.py`](./reusableUI_2027.py) (refactor showing inheritance).

> ⚠️ **The catch:** this file only defines a `tween()` function and a
> `TweenerWindow` class. **Running the file does nothing visible** — you
> have to *call* them. This README shows how.

---

## Quick start (the shortest path to a working tweener window)

1. Open Maya's Script Editor (Python tab).
2. Paste this and press `Ctrl+Enter`:

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\tweener')

import tweener_2027 as tweener

# Show the window
win = tweener.TweenerWindow()
win.show()
```

A small window appears with a slider and Reset / Close buttons.

### Now make it actually do something

The tweener needs keys to interpolate between. Set up a test:

```python
from maya import cmds

# Make a cube, key it at frame 1 and frame 24, then go to frame 12
cmds.polyCube()
cmds.setKeyframe(time=1, attribute='translateX', value=0)
cmds.setKeyframe(time=24, attribute='translateX', value=10)
cmds.currentTime(12)

# Select the cube, then drag the tweener slider.
# At 50%, the cube should jump to x=5. At 25%, x=2.5.
cmds.select('pCube1')
```

Drag the slider — the cube snaps to the tweened value and a key is set at
the current frame.

---

## Why doesn't the file do anything when I run it?

Because `tweener_2027.py` only **defines** things:

```python
def tween(percentage, obj=None, attrs=None, selection=True):
    ...

class TweenerWindow(object):
    def show(self): ...
    def buildUI(self): ...
```

Defining = writing the recipe. Calling = cooking the meal. See
[`gearCreator/README.md`](../gearCreator/README.md) for the same pattern
in more detail.

---

## Three ways to use this code

### Way 1 — Use the UI (what most animators want)

```python
import tweener_2027 as tweener
tweener.TweenerWindow().show()
```

Then drag the slider on a keyed selection.

### Way 2 — Call `tween()` directly (no UI)

Useful inside another script or for batching:

```python
# Tween every keyable attr on the current selection by 50%
tweener.tween(percentage=50)

# Tween a specific object's translateX by 25%
tweener.tween(percentage=25, obj='pCube1', attrs=['translateX'])

# Tween without using the selection — pass an explicit object
tweener.tween(percentage=75, obj='pCube1', selection=False)
```

**The function signature** (look at lines 9–17 of the file):
```python
def tween(percentage, obj=None, attrs=None, selection=True):
```
- `percentage` — **required** (no default). 0 to 100.
- `obj` — optional; defaults to using the current selection.
- `attrs` — optional; defaults to every keyable attr on the object.
- `selection` — optional; set `False` if you passed `obj` and don't want
  the function touching the selection.

### Way 3 — Use the slider value programmatically

If you build your own UI, you can pull the slider value and call `tween()`:

```python
slider_value = 50   # imagine this came from your UI
tweener.tween(percentage=slider_value, obj='pCube1')
```

---

## How the UI callbacks are wired (worth understanding)

Lines 154, 157, 168, 172 are the key bits:

```python
self.slider = cmds.floatSlider(min=0, max=100, value=50, step=1,
                               changeCommand=tween)
cmds.button(label="Reset", command=self.reset)
cmds.button(label="Close", command=self.close)
```

- **`changeCommand=tween`** — every time the slider moves, Maya calls
  `tween(value)`. The slider's current value gets passed as the first
  argument. **This is why `tween`'s first parameter is `percentage`.**
- **`command=self.reset`** — pass the method, don't call it. Writing
  `command=self.reset()` would call it once at build time (wrong).
- **`def reset(self, *args)`** — the `*args` absorbs the extra arguments
  Maya passes to button callbacks. Without it, your callback crashes.

> **Teaching moment:** The whole "wire a function to a UI element" pattern
> reduces to one line — `element(command=function)`. Everything else is
> window dressing.

---

## `reusableUI_2027.py` — the inheritance refactor

The `reusableUI` file is the **same tweener** rewritten to demonstrate
**class inheritance**, plus a second window (`GearWindow`) that proves the
reuse.

### Run it

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\tweener')
sys.path.insert(0, r'D:\2026MayaPython\gearCreator')   # reusableUI imports gears2

import reusableUI_2027 as rui

# Show the tweener (inherits from BaseWindow)
rui.TweenerWindow().show()

# Show the gear maker (also inherits from BaseWindow)
rui.GearWindow().show()
```

Both windows appear, both share the same `BaseWindow` parent class for
their `show()` / `close()` plumbing.

> ⚠️ **`reusableUI` imports `tweener` and `gearCreator.gears2`.** Both
> folders must be on `sys.path` (the snippet above adds both).

### What the file teaches

The whole point is in the class declarations:

```python
class BaseWindow(object):           # provides show(), close()
    def buildUI(self): pass         # subclasses override this

class TweenerWindow(BaseWindow):    # inherits show(), close() from BaseWindow
    def buildUI(self): ...          # overrides with tweener-specific UI

class GearWindow(BaseWindow):       # same parent, different buildUI
    def buildUI(self): ...
```

`TweenerWindow` and `GearWindow` never redefine `show()` or `close()` —
they get those for free from `BaseWindow`. Each only writes the parts that
are different. That's inheritance in one sentence.

---

## Common pitfalls

| Symptom                                            | Cause                                                                                  | Fix                                                                                       |
|----------------------------------------------------|----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'tweener_2027'` | Folder not on sys.path                                                                | Add the `sys.path.insert(...)` line before import.                                        |
| Window opens but slider does nothing               | You didn't select a keyed object, or it has no keys to interpolate                     | Set up the cube-with-two-keys test from Quick start                                       |
| `IndexError: list index out of range` on `cmds.ls(sl=1)[0]` | Nothing selected and you didn't pass `obj=`                                       | Either select something, or call `tween(50, obj='pCube1')`                                |
| `ValueError: No object given to tween`             | You passed `selection=False` but no `obj=`                                             | Pass `obj='something'` or omit `selection=False`                                          |
| Window appears then immediately disappears         | You created the window object but didn't keep a reference (`win = ...; win.show()`)    | `win = TweenerWindow()` then `win.show()`. If you skip the variable, Python garbage-collects it |
| Slider moves but value jumps to one end            | `previousFrame` or `nextFrame` is None at the start/end of an animation                | Expected behavior at the boundaries. Add keys on both sides of the playhead.              |
| `reusableUI` ImportError for `gears2`              | You only added `tweener/` to sys.path, not `gearCreator/`                              | Add both folders (see the snippet in the reusableUI section)                              |
| Tweener keys the wrong attribute                   | `attrs=None` defaults to *every* keyable attr                                          | Pass `attrs=['translateX']` explicitly                                                    |

---

## Exercises

1. **Add a "key on drag" checkbox.** Currently the slider always sets a key
   via `setKeyframe`. Add a `cmds.checkBox` that, when off, only does
   `setAttr` (preview without committing).
2. **Add an "ease curve" dropdown.** Linear interpolation is boring. Add
   options like `ease_in`, `ease_out`, `ease_in_out` and apply a curve to
   `percentage` before computing `currentValue`.
3. **Refactor to a class.** `tween` is currently a free function. Convert
   it to a method on `TweenerWindow` so the slider can be queried directly
   instead of Maya passing its value.
4. **Multiple selection.** Right now `tween` only operates on `ls(sl=1)[0]`
   (one object). Extend it to loop over every selected object.
5. **Frame range mode.** Instead of interpolating between adjacent keys,
   let the user pick a frame range and apply the tween across all frames
   in that range — useful for smoothing mo-cap.

---

## Source

This is a teaching demo from the original [PythonForMayaSamples](https://github.com/dgovil/PythonForMayaSamples)
repo. The `_2027.py` versions are verified Python-3-compatible copies for
Maya 2022+.
