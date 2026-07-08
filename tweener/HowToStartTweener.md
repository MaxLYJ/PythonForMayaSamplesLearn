# How To Start: `tweener`

This is the **first animation demo** and the **first demo with a Maya-built UI**. It teaches two
new things at once: the **animation API** (`cmds.keyframe`, `cmds.setKeyframe`,
`cmds.currentTime`, `cmds.getAttr`/`setAttr` at a specific time) and **building a window inside
Maya** with `maya.cmds` (`cmds.window`, `cmds.columnLayout`, `cmds.floatSlider`, `cmds.button`,
`cmds.showWindow`).

Like `gearCreator`, these files are **definitions-only** — there is no `if __name__ == '__main__'`
block and no example call. Importing the file does **nothing visible**; you must *call* `tween()`
or instantiate `TweenerWindow().show()` yourself. (`py_compile` + a `grep` for `__main__` confirm
both `_2027` files are definitions-only.)

The payoff: a slider that, when dragged on a keyed object, **inserts an in-between key** at the
current frame, biased by the slider percentage. Drag to 50 → the new key sits halfway between the
surrounding keys. Drag to 25 → a quarter of the way. It is a one-click ease-in/out for animators.

The `reusableUI` file then **rewrites the same tweener** to demonstrate **class inheritance**: a
`BaseWindow` parent provides the `show()`/`close()` plumbing, and two child windows
(`TweenerWindow`, `GearWindow`) override only `buildUI()`. The `GearWindow` proves the reuse by
driving the `gearCreator` demo's `Gear` class from a second window.

## Files in this demo

| File | Target | Role |
|------|--------|------|
| `tweener.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Defines `tween()` + a standalone `TweenerWindow` class. |
| `tweener_2027.py` | Maya 2027, **Python 3** | The one you actually run. Verified identical to the original (no Py3 changes needed). |
| `reusableUI.py` | Maya 2017/2018, **Python 2.7** | Teaching original. Inheritance refactor: `BaseWindow` → `TweenerWindow` + `GearWindow`. |
| `reusableUI_2027.py` | Maya 2027, **Python 3** | The one you actually run. Verified identical to the original. |

> **`_2027` convention:** files ending in `_2027` target Maya 2027 / Python 3 and are the ones to
> paste into the Script Editor. The bare `.py` files are the heavily-commented Py2 teaching copies.
> See the repo root `AGENTS.md` for the full convention.

## Prerequisites

- Maya 2027 (Python 3). If you are on Maya 2017/2018, use the Py2 `.py` files instead.
- For `reusableUI` only: the `gearCreator/` folder must **also** be on `sys.path`, because
  `reusableUI` does `from gearCreator import gears2 as gear`. (`tweener.py` is self-contained — it
  imports only `maya.cmds`.)
- The Animation control set (Time Slider, playback controls) should be visible so you can scrub
  frames and watch keys appear.

## What the code actually does

- `tween(percentage, obj=None, attrs=None, selection=True)` → for the chosen object, finds every
  keyable attribute, and for each one that is actually keyed, locates the **nearest previous key**
  (`max` of keyframes `< currentTime`) and the **nearest next key** (`min` of keyframes
  `> currentTime`). It linearly interpolates between their values —
  `currentValue = previousValue + (nextValue - previousValue) * percentage / 100` — then writes
  that value and **sets a key** at the current frame. `percentage` is "how far toward the *next*
  key": `0` snaps to the previous key, `100` snaps to the next key, `50` is the midpoint.
- `TweenerWindow` (`tweener.py`) → a self-contained window class. `show()` deletes any existing
  window of the same name, builds the UI, and shows it. `buildUI()` lays out a label, a
  `floatSlider` (0–100, default 50) wired to `tween` via `changeCommand`, and Reset / Close buttons.
- `reusableUI.BaseWindow` → the reusable parent: `show()` (same delete-then-build-then-show
  pattern, but calls `self.close()` instead of `cmds.deleteUI` directly), `close()`, and placeholder
  `buildUI()`/`reset()` that subclasses are meant to override.
- `reusableUI.TweenerWindow(BaseWindow)` → overrides only `windowName`, `buildUI()`, and `reset()`.
  Gets `show()`/`close()` for free. Its slider is wired to `tweener.tween`.
- `reusableUI.GearWindow(BaseWindow)` → adds an `__init__` (stores `self.gear = None`), overrides
  `buildUI()` with an int slider + "Make Gear" button, and adds `makeGear()` (creates a
  `gearCreator.gears2.Gear`) and `modifyGear()` (live-edits the gear's tooth count as you drag).

> ⚠️ **Cannot be verified without Maya running.** Everything below depends on the live Maya scene,
> the animation API, and the `cmds` UI system. The code was read and cross-checked against the
> demo's `README.md` and the `gearCreator` demo it depends on, but the visible results were **not**
> executed in this environment. Treat the "expected result" notes as predictions to confirm in Maya.

---

## How to Create the Test Maya Scene

`tween()` does **not** create geometry — it only **sets keys**. So unlike `introduction/` or
`gearCreator/`, you must hand-build a scene that has **keyframes** for the tween to interpolate
between. The minimum viable test is **one object with two keys on one channel**, with the playhead
between them.

### Scene A — the minimum tween test (one cube, two keys)

Run this in the Script Editor (Python tab) to build the scene from scratch:

```python
from maya import cmds

cmds.file(newFile=True, force=True)          # start clean

cmds.polyCube(name='tweenCube')              # a polygon cube

# Key translateX at frame 1 (value 0) and frame 24 (value 10)
cmds.setKeyframe('tweenCube', time=1,  attribute='translateX', value=0)
cmds.setKeyframe('tweenCube', time=24, attribute='translateX', value=10)

# Park the playhead in the middle — frame 12
cmds.currentTime(12)

# Select the cube (tween's default behavior uses the selection)
cmds.select('tweenCube')
```

**What you should see:** in the Channel Box, `translateX` is now orange (keyed). On the Time
Slider there are red key ticks at frames 1 and 24. With the playhead at frame 12, the cube sits at
`translateX = 5` (Maya's default linear interpolation between 0 and 10).

This is the scene every "run the tweener" step below assumes.

### Scene B — a richer test (three keys, multiple channels)

To see the tween handle several attributes and a non-midpoint playhead, add a couple more keys:

```python
cmds.setKeyframe('tweenCube', time=1,  attribute='translateY', value=0)
cmds.setKeyframe('tweenCube', time=24, attribute='translateY', value=4)
cmds.setKeyframe('tweenCube', time=10, attribute='rotateY',    value=0)
cmds.setKeyframe('tweenCube', time=20, attribute='rotateY',    value=90)
cmds.currentTime(15)                         # between the rotateY keys
cmds.select('tweenCube')
```

Now `tween(percentage=50)` will insert keys on **all three** channels at once at frame 15.

### Scene state the code expects

| Entry point | Selection required? | Scene state it expects |
|-------------|---------------------|------------------------|
| `tween(percentage)` (defaults) | **Yes** — uses `cmds.ls(sl=1)[0]` | Selected object must have ≥ 1 keyed keyable attribute; playhead should sit **between** two keys for an interesting result. |
| `tween(percentage, obj='X')` | No | Named object `X` must exist and have keyed attrs. |
| `tween(percentage, obj='X', selection=False)` | No | Same; `selection=False` is what lets you skip the selection entirely. |
| `tween(percentage, selection=False)` (no obj) | — | **Errors immediately** — `ValueError: No object given to tween`. |
| `TweenerWindow` (UI) | Yes (when you drag the slider) | Same as `tween()` defaults — it just calls `tween(value)`. |
| `reusableUI.GearWindow` (UI) | No | **Empty scene is fine** — "Make Gear" builds its own gear. Dragging the slider only edits a gear after you click "Make Gear". |

---

## How to Run the Functions

### Run A — `tweener` (open the window, the animator's path)

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/tweener')

import tweener_2027 as tweener

win = tweener.TweenerWindow()   # KEEP the reference in `win` (see pitfall below)
win.show()
```

> Replace `/abs/path/to/...` with the real absolute path to the `tweener/` folder.

**Expected result:** a small window titled **TweenerWindow** appears with the text *"Use this
slider to set the tween amount"*, a slider (starting at 50), and **Reset** / **Close** buttons.
With Scene A built and `tweenCube` selected, **drag the slider to 50**:
- The cube jumps to `translateX = 5` and a **new red key tick appears at frame 12**.
- Drag to 25 → cube moves to `translateX = 2.5`, key at 12 updates.
- Drag to 100 → cube snaps to `translateX = 10` (the next key's value); drag to 0 → snaps to 0.

### Run B — `tweener` (call `tween()` directly, no UI)

Useful for scripting, batching, or testing without the window. Build Scene A first, then:

```python
import tweener_2027 as tweener
from maya import cmds

cmds.currentTime(12)
cmds.select('tweenCube')

tweener.tween(percentage=50)                                   # all keyable attrs on the selection
tweener.tween(percentage=25, obj='tweenCube', attrs=['translateX'])   # one explicit channel
tweener.tween(percentage=75, obj='tweenCube', selection=False)        # ignore the selection
```

**Expected result:** each call inserts/updates a key at the current frame on the targeted
channels. After `tween(percentage=50)` at frame 12 on Scene A, `cmds.getAttr('tweenCube.translateX')`
returns `5.0` and a key exists at frame 12. Check with:

```python
print(cmds.keyframe('tweenCube.translateX', query=True))   # -> [1.0, 12.0, 24.0]
print(cmds.getAttr('tweenCube.translateX', time=12))        # -> 5.0
```

**The error cases (try them to see the guards fire):**

```python
tweener.tween(percentage=50, selection=False)
# -> ValueError: No object given to tween   (no obj AND selection off)

cmds.select(clear=True)
tweener.tween(percentage=50)
# -> IndexError: list index out of range    (nothing selected, so cmds.ls(sl=1)[0] fails)
```

### Run C — `reusableUI` (run the inheritance refactor)

`reusableUI` imports **both** `tweener` and `gearCreator.gears2`, so **both** folders go on
`sys.path`:

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/tweener')
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/gearCreator')

import reusableUI_2027 as rui

# The tweener, rewritten to inherit from BaseWindow — behaves identically to A.
twin = rui.TweenerWindow()
twin.show()

# A second window that proves the reuse: it drives gearCreator's Gear class.
gwin = rui.GearWindow()
gwin.show()
```

> ⚠️ **Keep the reference.** Both lines above assign the window to a variable (`twin` / `gwin`)
> before `.show()`. If you write `rui.TweenerWindow().show()` with no variable, the temporary
> instance can be garbage-collected once the statement ends and its bound-method callbacks
> (`self.reset`, `self.makeGear`, etc.) die with it — see the window-reference pitfall in the Q&A.
> This applies equally to `GearWindow`: its `__init__` storing `self.gear` does **not** protect it,
> because every callback is still a bound method that needs `self` alive.

**Expected result — `GearWindow`:** a window titled **GearWindow** appears with a label showing
`10`, an integer slider (5–30, default 10), and **Make Gear** / **Reset** / **Close** buttons.
- Click **Make Gear** → a polygon gear appears in the viewport (built by `gearCreator.gears2.Gear().create(teeth=10)`; see `HowToStartGearCreator.md`).
- **Drag the slider** → the gear's tooth count updates **live as you drag** (dragCommand), and the
  label updates to match. (Caveat from the gear demo: on some Maya versions the teeth extrude
  inward — that is a `gears2`/`polyPipe` quirk, not a `reusableUI` bug.)
- Click **Reset** → the current gear is "released" (`self.gear = None`), so the next drag will
  **not** edit the old gear; the slider and label snap back to 10.

### Run D — one-shot paste (shortest path to a working tweener)

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/tweener')
from maya import cmds

# --- build the minimum scene ---
cmds.file(newFile=True, force=True)
cmds.polyCube(name='tweenCube')
cmds.setKeyframe('tweenCube', time=1,  attribute='translateX', value=0)
cmds.setKeyframe('tweenCube', time=24, attribute='translateX', value=10)
cmds.currentTime(12)
cmds.select('tweenCube')

# --- open the window and drag the slider to 50 ---
import tweener_2027 as tweener
win = tweener.TweenerWindow()
win.show()
```

Drag the slider: at 50 the cube lands at `translateX = 5` with a new key at frame 12.

---

## Question and Answer

**Q1. Running the file does nothing. Why?**
Because `tweener_2027.py` only **defines** `tween()` and `TweenerWindow` — there is no
`if __name__ == '__main__'` block and no example call at module scope (confirmed: the file ends at
the `close()` method). Defining is writing the recipe; calling is cooking. You must instantiate the
window (`TweenerWindow().show()`) or call `tween(50)` yourself. This is the same definitions-only
pattern as `gearCreator`.

**Q2. Why is `percentage` the *first* parameter when the UI is what people use?**
Because of how the slider is wired: `cmds.floatSlider(..., changeCommand=tween)`. When the slider
moves, Maya **calls the callback and passes the slider's current value as its first argument** —
i.e. Maya calls `tween(67)`. So the function's first parameter *has* to be the percentage for the
UI to work. This is a recurring Maya-UI idiom: the callback's first parameter is the control's
value. (Notice `GearWindow.modifyGear(self, teeth)` follows the same rule — `dragCommand` passes the
slider value in as `teeth`.)

**Q3. What does `percentage=0` vs `percentage=100` actually do?**
They **snap** rather than "do nothing." The math is
`currentValue = previousValue + (nextValue - previousValue) * percentage / 100`. So `0` →
`previousValue` (snap to the earlier key), `100` → `nextValue` (snap to the later key), `50` → the
exact midpoint. There is no "hold" position; 0 and 100 are the two surrounding keys themselves.

**Q4. What happens if the playhead is sitting exactly on a keyframe?**
That key is **excluded** from both lists, because the comparisons are strict (`k < currentTime` for
previous, `frame > currentTime` for later). So sitting on the frame-12 key, the tween interpolates
between the key *before* 12 and the key *after* 12, then **overwrites** the key at 12 with the
interpolated value. If you tween while parked on a key, you will replace that key — a common
surprise. Step off the key (e.g. frame 11 or 13) to insert a genuinely new in-between.

**Q5. Why does the code set the value with *both* `setAttr` and `setKeyframe`?**
The comment on line 108 says it: *"Sometimes Maya doesn't update the viewport when just setting a
key."* `cmds.setKeyframe(..., value=currentValue)` records the key, but the viewport/modelEditor can
lag and still show the old evaluated value. The preceding `cmds.setAttr(attrFull, currentValue)`
forces the channel to the new value immediately so the object visibly moves *now*, then the keyframe
ensures the value is saved at the current time. Belt and suspenders.

**Q6. `tween()` raises `ValueError`, but with nothing selected I got `IndexError`. Why two different errors?**
They guard two different misuse modes:
- `ValueError("No object given to tween")` — you passed `selection=False` **and** no `obj=`. This
  one is caught explicitly up front ("error early").
- `IndexError: list index out of range` — you left `selection=True` (the default) but selected
  nothing, so `cmds.ls(sl=1)[0]` returns `[]` and the `[0]` blows up. This is **not** caught by the
  code; it's an unguarded edge. The fix is either to select something or to pass `obj=` explicitly.

**Q7. The window appears then immediately disappears (or its buttons stop working). What happened?**
You wrote `TweenerWindow().show()` without keeping a reference, so the temporary `TweenerWindow`
instance can be garbage-collected once the statement ends — and its bound-method callbacks
(`self.reset`, `self.close`) die with it. This is the demo `README.md`'s documented pitfall. Always
keep the reference: `win = TweenerWindow()` then `win.show()`. (The slider callback is fine because
it points at the module-level `tween` function, not a bound method.)

**Q8. Why does `TweenerWindow` use `changeCommand` but `GearWindow` uses `dragCommand`?**
They fire at different moments. `dragCommand` fires **continuously while you drag**; `changeCommand`
fires when the value is **committed** (typically on mouse-up). The tweener sets a *key* on each
change, so committing once per drag (avoiding a key per pixel) is sensible → `changeCommand`. The
gear window wants **live** feedback — the gear should rebuild its teeth in real time as you scrub →
`dragCommand`. (The exact firing semantics of slider commands can vary slightly across Maya
versions; worth confirming on yours, but that is the intended distinction.)

**Q9. `reusableUI.TweenerWindow` has no `show()` or `close()` defined. How does the window still work?**
**Inheritance.** `TweenerWindow(BaseWindow)` inherits `show()` and `close()` from `BaseWindow`
unchanged. It overrides only `windowName` (so each window has a unique name), `buildUI()` (the
window-specific contents), and `reset()`. When the inherited `show()` calls `self.buildUI()`,
Python's method resolution finds the overridden version in the child. That is the whole lesson of
`reusableUI`: write the shared plumbing once in the parent, override only what differs.

**Q10. `tween()` processes "every keyable attribute." Doesn't that include `visibility`?**
Yes — `cmds.listAttr(obj, keyable=True)` returns all keyable channels, including `visibility`, and
`tween()` will happily interpolate it like a number. That is semantically odd (a 0/1 channel gets a
fractional value like 0.5), and how Maya stores/rounds that fractional visibility key is
version-dependent. If you only want to tween transforms, pass `attrs=['translateX', 'translateY',
'translateZ']` (or whichever channels you mean) explicitly instead of relying on the default.
*(Behavior of fractional visibility values not verified in Maya here — worth a quick test.)*

---

## Advanced Directions

1. **Multi-selection tweening.** Right now `tween()` only touches `cmds.ls(sl=1)[0]` — the first
   selected object. Promote it to loop over **every** selected object so an animator can ease a
   whole control rig at once. New shape: `def tween(percentage, objs=None, selection=True)` that
   iterates `cmds.ls(sl=1)` when `objs` is None, with an `all_or_nothing` flag deciding whether one
   bad object aborts the batch or is skipped-and-reported.

2. **Easing curves (non-linear interpolation).** The current math is pure linear. Add an `ease`
   parameter (`'linear'`, `'ease_in'`, `'ease_out'`, `'ease_in_out'`) and remap `percentage` through
   a curve function *before* computing `currentValue`. Requires a small `Easing` helper module
   (e.g. `ease_in_out(t): return t*t*(3-2*t)`) and a `cmds.optionMenu` in the UI to pick the curve.

3. **"Key on drag" preview checkbox.** Every slider move currently commits a key via
   `setKeyframe`. Add a `cmds.checkBox` ("Set key on drag"); when unchecked, call only `setAttr`
   (scrub-style preview) and skip `setKeyframe`, so the animator can audition values without
   littering the timeline. Needs the checkbox value read inside `tween()` (or a `commit_key=True`
   argument) and the checkbox wired with a `changeCommand`.

4. **Frame-range / batch mode.** Instead of one in-between at the current frame, let the user pick a
   **frame range** and have `tween()` walk every frame in it, biasing each toward the surrounding
   keys — useful for smoothing mo-cap or evenly spacing holds. Requires a `def tween_range(start,
   end, percentage, step=1)` that loops `cmds.currentTime(f)` + `tween(...)`, ideally wrapped in a
   single `cmds.undoInfo(openChunk=True/…)` so the whole batch is one undo.

5. **Refactor `tween` into the window class (and generalize `BaseWindow`).** `tween` is a free
   function the slider calls by value-passing. Convert it to a method
   `TweenerWindow.tween(self, percentage)` that reads the selection/slider from `self`, and extend
   `BaseWindow` into a generic `ToolWindow` mixin that supplies a standard header (title label +
   Reset + Close row) every child window inherits — turning `reusableUI` into a real mini-framework
   for course-built tools.

6. **Installable shelf tool + undo safety.** Wrap `TweenerWindow().show()` behind a shelf button
   and wrap each `tween()` call in `cmds.undoInfo(openChunk=True)` … `closeChunk` so a single drag
   is one undo step (currently every slider commit can be a separate undo). Package the `tweener/`
   folder as an importable module with a `tweener/__init__.py` `show()` entry point so a one-line
   `import tweener; tweener.show()` is all a shelf button needs.
