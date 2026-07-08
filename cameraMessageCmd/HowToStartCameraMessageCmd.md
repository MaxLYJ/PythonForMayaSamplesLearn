# HowToStart — cameraMessageCmd

This is the curriculum's first **message / event-callback** demo. Instead of
your code *doing* something to the scene, the scene *notifies* your code when
something happens — here, when the user **interactively tumbles, tracks, or
dollies the persp camera** in the viewport. It is the canonical "Hello World"
for the Maya Message system.

The folder ships two sibling files that do the **same thing in two dialects**:

* `cameraMessageTest/cameraMessageTest.py` — **API 1.0** (`import maya.OpenMaya`)
* `cameraMessageTest2/cameraMessageTest2.py` — **API 2.0** (`import maya.api.OpenMaya`)

Both are **definitions-only libraries** (verified by AST: no `__main__` guard, no
top-level executable call — the block at the bottom is a plain string literal,
not code). Importing them does nothing visible; you must call `test()`.

It is the **first event-driven archetype** in the curriculum. The single most
important idea — worth more than any individual API call — is the universal
Maya-callback lifecycle every one of your future callbacks will follow:

> **register → keep the returned `MCallbackId` → remove it by that ID when done.**

Skip the last step and the callback outlives the script, firing forever
("ghost callback"). That lifecycle is the whole lesson; the camera-specific part
is just the example payload.

⚠️ **You need Maya's Python** to run this — the very first real line is
`import maya.OpenMaya`, which only resolves inside a Maya install. Use the
**Script Editor** (Python tab) or `mayapy`. You also need an **interactive
viewport you can tumble with the mouse** — the callback fires on user
manipulation, *not* on scripted camera moves.

---

## Files in this demo

| File | What it is | Run it how |
|------|-----------|------------|
| `cameraMessageTest/cameraMessageTest.py` | API 1.0 version — 5 functions (`beginManipCB`, `endManipCB`, `test`, `addCallbacksToPerspCamera`, `removeCallbacks`) + module-level `callbackIDs = []`. | Script Editor: `import cameraMessageTest as cmt; cmt.test()`. |
| `cameraMessageTest2/cameraMessageTest2.py` | API 2.0 version — identical except the `MObject`/`MSelectionList` plumbing returns values instead of filling by reference. | Script Editor: `import cameraMessageTest2 as cmt2; cmt2.test()`. |
| `cameraMessageTest/README.md` | The book's narrative for the 1.0 version: what the Message system is, read-the-code order, exercises, pitfalls. | Read for context — but verify its claims against the `.py` (see divergences below). |
| `cameraMessageTest2/README.md` | The book's narrative for the 2.0 version + the canonical 1.0→2.0 diff table. | Read for context. Its diff table is accurate (5 meaningful differences — verified). |

> **`_2027` convention — not needed here.** In the other demos `foo_2027.py` is
> the verified Python-3 copy. `cameraMessageCmd` has **no `_2027` sibling**:
> both files are the verbatim Autodesk originals (public docs listings), already
> Python-3 clean. There is nothing to modernize, so this guide targets them
> directly (same situation as `fileDialog` / `manipulatorMath` / `profilerDump`).
> The only Python-2 leftover is the trailing comment block's bare `reload(cmt)`,
> which in Python 3 is `importlib.reload(cmt)`.

## Prerequisites

- Python functions, module-level variables, and `global` — any Python tutorial.
- What an `MObject` is (Maya's opaque handle to a node) and what `maya.OpenMaya`
  vs `maya.api.OpenMaya` are (API 1.0 fill-by-reference vs API 2.0 return-direct).
- Comfortable tumbling a Maya viewport with **Alt + left/middle/right-drag**
  (tumble / track / dolly). That mouse gesture is what the callback listens for.
- ⚠️ **Maya's Python interpreter** (Script Editor or `mayapy`) — required only
  because the file imports `maya.OpenMaya`. The callback lifecycle and the
  1.0-vs-2.0 diff described below were verified by reading the source; the
  actual firing requires a live Maya GUI and was not exercised headlessly.

---

## What the code actually does

Five pieces per file. They are identical between the two files **except for the
selection-list plumbing** (called out at the end).

### The two callback functions — `beginManipCB(node, clientData)` / `endManipCB(node, clientData)`

```python
def beginManipCB(node, clientData):
    print("Inside beginManipCB, clientData is %s" % clientData)
def endManipCB(node, clientData):
    print("Inside endManipCB, clientData is %s" % clientData)
```

This `(node, clientData)` signature is **fixed by Maya** for camera-manipulation
callbacks (the C++ docs call the function type `MMessage::MNodeFunction`).
`node` is the camera `MObject` being manipulated; `clientData` is whatever you
handed to the register call and want passed back. Here both just `print`. In a
real tool this is where your reaction logic lives.

### `callbackIDs = []` (module-level)

```python
callbackIDs = []
```

The single most important line in the file. Every `add…Callback` returns an
**`MCallbackId`** — an opaque handle. That ID is the **only** way to remove the
callback later. The module stashes them in this list. Two rules follow:

1. **Keep it at module level.** If `callbackIDs` were a local, it would be
   garbage-collected when the function returns, and the IDs would become
   un-removable for the rest of the session.
2. **Never reassign it to `[]` without first removing the old IDs** — otherwise
   you lose the handles and leak the callbacks (see Run D / Q&A).

### `test()` → `addCallbacksToPerspCamera()`

`test()` is a one-line alias for `addCallbacksToPerspCamera()`. The real work:

```python
maya.cmds.select('perspShape')                       # hard-coded: always persp
slist = OpenMaya.MSelectionList()                    # API 1.0 (see diff below)
OpenMaya.MGlobal.getActiveSelectionList(slist)
iter = OpenMaya.MItSelectionList(slist)
print("List length is %d" % slist.length())
while not iter.isDone():
    iter.getDependNode(dependNode)
    iter.getDagPath(dagPath)
    print("Node: %s" % dagPath.partialPathName())
    if dependNode.hasFn(OpenMaya.MFn.kCamera):       # type-check
        payloadBegin = "12345.5"
        payloadEnd   = "54321.5"
        callbackIDs.append(
            OpenMaya.MCameraMessage.addBeginManipulationCallback(dependNode, beginManipCB, payloadBegin))
        callbackIDs.append(
            OpenMaya.MCameraMessage.addEndManipulationCallback(dependNode, endManipCB, payloadEnd))
    else:
        print("This node is not a camera...")
    next(iter)                                        # advance (see Q&A)
```

Read it as three steps: (1) force-select `perspShape`, (2) turn the selection
into an `MObject` via the selection-list iterator, (3) if it is a camera,
register the two callbacks and store their IDs. The `clientData` payloads are
just the placeholder strings `"12345.5"` / `"54321.5"` so you can see them echo
back when the callback fires.

### `removeCallbacks()`

```python
def removeCallbacks():
    global callbackIDs
    for id in callbackIDs:
        OpenMaya.MMessage.removeCallback(id)
    callbackIDs = []
```

The mandatory cleanup half of the lifecycle. `MMessage.removeCallback(id)` tears
down one callback by its handle; then the list is cleared so a future `test()`
starts fresh. **Always pair registration with cleanup.**

### The `MCameraMessage` static methods the functions call

| Method | Fires when | Signature in Python |
|--------|-----------|---------------------|
| `MCameraMessage.addBeginManipulationCallback(camera, func, clientData=None)` | The user **starts** an interactive tumble/track/dolly gesture on `camera`. | `func(node, clientData)` |
| `MCameraMessage.addEndManipulationCallback(camera, func, clientData=None)` | The user **ends** that gesture (mouse-up). | `func(node, clientData)` |
| `MMessage.removeCallback(id)` (base class) | You call it — removes one callback by its `MCallbackId`. | — |

Both `add…` methods return an `MCallbackId`. The official C++ reference
describes them as registering "camera manipulation **beginning** /
**ending** messages." Key consequence: **one tumble gesture = one begin + one
end**, not a continuous stream. And they are **interactive-only** — a scripted
camera move (`cmds.view`, `cmds.xform` on the camera, an animated camera) does
**not** trigger them.

### API 1.0 → 2.0: what actually changed (the whole point of the second file)

The `MCameraMessage` API itself is **unchanged**. Only the surrounding
`MObject` / `MSelectionList` plumbing differs. There are exactly **5 meaningful
differences** (matches `cameraMessageTest2/README.md`'s diff table — verified):

| Concern | API 1.0 (`cameraMessageTest.py`) | API 2.0 (`cameraMessageTest2.py`) |
|---------|----------------------------------|-----------------------------------|
| Import | `import maya.OpenMaya as OpenMaya` | `import maya.api.OpenMaya as OpenMaya` |
| Pre-allocate wrappers | `dependNode = MObject()`<br>`dagPath = MDagPath()` | (removed — not needed) |
| Get selection list | `slist = MSelectionList()`<br>`MGlobal.getActiveSelectionList(slist)` | `slist = MGlobal.getActiveSelectionList()` |
| Get node from iterator | `iter.getDependNode(dependNode)` | `dependNode = iter.getDependNode()` |
| Get DAG path from iterator | `iter.getDagPath(dagPath)` | `dagPath = iter.getDagPath()` |

### Dead code & quirks worth knowing (good Q&A)

- **`camFn = OpenMaya.MFnCamera()` is allocated and never used — in BOTH files**
  (line 28 in the 1.0 file, line 26 in the 2.0 file). Leftover boilerplate. You
  only need `MFnCamera(node)` if you want to read/write attributes like focal
  length; this demo never does. Both READMEs flag this.
- **The `else: "This node is not a camera..."` branch is effectively unreachable
  through the public API.** `cmds.select('perspShape')` hard-codes the selection
  to the persp camera's shape, so the loop can only ever iterate a camera. The
  only way to hit the else is to edit the `cmds.select` line. (Great teaching
  point — see Q&A.)
- **`next(iter)` advances the iterator and the variable name `iter` shadows
  Python's builtin `iter()`.** It works because Maya's `MItSelectionList`
  implements `__next__`; the more idiomatic Maya form is `iter.next()`.

---

## How to Create the Test Maya Scene

This demo needs almost **no hand-built geometry** — the "scene" is just the
**default `persp` camera** plus a viewport you can tumble. The callbacks are
wired to `perspShape`, so the only hard requirement is that `persp` exists.

1. **Start a fresh scene** so the default cameras exist:
   - Menu: **File → New Scene** (don't save the old one), *or*
   - Script Editor (Python):
     ```python
     import maya.cmds as cmds
     cmds.file(f=True, new=True)
     ```
2. **Confirm `persp` / `perspShape` exist** (the demo will fail if you deleted them):
   ```python
   print(cmds.ls('perspShape'))   # should print ['perspShape']
   ```
   In the Outliner: turn on **Display → Shapes** and look for `persp` → `perspShape`.
   ⚠️ **Do not delete `persp`.** The whole demo depends on it.
3. **Make sure you are looking through `persp`.** In the default layout the large
   perspective panel uses `persp`, so this is already the case. (If you panes
   into an ortho or a custom camera, tumbling it will *not* fire these callbacks
   — they are attached to `perspShape` specifically.)

That is the entire scene. There is no geometry to create — you are about to
watch the **viewport camera** report its own manipulation.

### Scene/capture-state each entry point expects

| Entry point | Selection / scene state it requires |
|-------------|--------------------------------------|
| `test()` / `addCallbacksToPerspCamera()` | A node named **`perspShape`** must exist (it force-selects it). Nothing else. |
| Firing the callbacks | You must **interactively tumble/track/dolly the persp viewport** with the mouse while looking through `persp`. |
| `removeCallbacks()` | `callbackIDs` must still hold the IDs returned by a prior `test()` (don't blank the list by hand first). |

---

## How to Run the Functions

> **Both files live in nested sub-folders**, so you must put the right folder on
> `sys.path` before importing, *or* rely on Maya's userSetup path. The snippets
> below use the explicit `sys.path.insert` form so they work no matter where
> Maya is launched. Replace `/abs/path/to/` with the real path on your machine
> (e.g. `/home/maxliu/PythonForMayaSamplesLearn/`).

### Run A — the API 1.0 version (read this first)

In the **Script Editor → Python tab**, paste and run:

```python
import sys
sys.path.insert(0, r'/abs/path/to/cameraMessageCmd/cameraMessageTest')

import maya.cmds as cmds
cmds.file(f=True, new=True)          # fresh scene → perspShape exists

import cameraMessageTest as cmt
cmt.test()                            # register the two callbacks on persp
```

Expected **immediate** Script Editor output (this is the registration phase):

```
List length is 1
Node: perspShape
This is a camera, adding manipulation callbacks with payloads
```

> ⚠️ **README divergence:** `cameraMessageTest/README.md`'s "How to run" block
> shows *only* the two `Inside …ManipCB` lines and **omits the three lines
> above** that `test()` prints during registration. `cameraMessageTest2`'s
> README gets it right. Don't be surprised when you see the extra lines.

Now **tumble the persp viewport** — hold **Alt + left-drag** and move the mouse.
On each gesture you should see, in the Script Editor:

```
Inside beginManipCB, clientData is 12345.5
Inside endManipCB, clientData is 54321.5
```

(begin fires when the gesture starts, end when you release — one pair per
tumble.) Track (**Alt + middle-drag**) and dolly (**Alt + right-drag**) fire the
same pair. When you are done, tear the callbacks down:

```python
cmt.removeCallbacks()
```

(no output — it just clears the IDs.) Tumble again: **nothing prints**.
That silence is the proof cleanup worked.

### Run B — the API 2.0 version

Identical, swapping the folder and the module name:

```python
import sys
sys.path.insert(0, r'/abs/path/to/cameraMessageCmd/cameraMessageTest2')

import maya.cmds as cmds
cmds.file(f=True, new=True)

import cameraMessageTest2 as cmt2
cmt2.test()                           # register on persp (API 2.0 plumbing)
```

Expected output is **byte-for-byte identical** to Run A — the 1.0/2.0 plumbing
difference is invisible at runtime. Tumble → same `Inside …ManipCB` pair →
`cmt2.removeCallbacks()`. The point of running both is to *feel* that the
callback API itself never changed; only how you obtain the `MObject` did.

### Run C — the "not a camera" branch (requires a one-line edit)

The public `test()` can never reach the `else` branch because it force-selects
`perspShape`. To see it, temporarily change the `cmds.select` line in
`cameraMessageTest.py` to a non-camera and re-run:

```python
# edit line 32 of cameraMessageTest.py to:
maya.cmds.select('persp')            # the TRANSFORM, not the shape
```

then `importlib.reload(cmt); cmt.test()` and you will see:

```
List length is 1
Node: persp
This node is not a camera...
```

No callbacks are registered, so tumbling prints nothing. This demonstrates the
`hasFn(MFn.kCamera)` type-gate: only a camera **shape** passes. (Revert the edit
afterward, or you'll wonder why Run A stopped working.)

### Run D — the ghost-callback leak (why `removeCallbacks()` matters)

This is the most important run. **Without** removing first, reload and re-register:

```python
import importlib
importlib.reload(cmt)                 # Python 3 reload
cmt.test()                            # registers a SECOND pair on top of the first
```

Now tumble once. You will see the `Inside …ManipCB` lines **twice** — the old
IDs from the first `test()` are still live (reloading the module re-runs
`callbackIDs = []`, wiping *your reference* to them, but Maya still holds the
callbacks). You can no longer reach the old IDs to remove them. This is a
**leaked / ghost callback**, and it is the #1 Maya-callback beginner trap.
Lesson: **always `removeCallbacks()` before re-importing/reloading.**

> The demo's own trailing comment uses bare `reload(cmt)`. That is Python-2
> syntax; in Maya 2027's Python 3 it must be `importlib.reload(cmt)`.

### One-shot paste (shortest path to "it loads")

```python
import sys; sys.path.insert(0, r'/abs/path/to/cameraMessageCmd/cameraMessageTest')
import maya.cmds as cmds; cmds.file(f=True, new=True)
import cameraMessageTest as cmt; cmt.test()
# ...tumble the persp viewport with Alt+drag...
# cmt.removeCallbacks()   # when done
```

---

## Question and Answer

**Q1. Why is this a definitions-only file with no `__main__` — why not just run it?**
Because callback registration must **persist in the module namespace** for
`callbackIDs` (and the callback functions themselves) to stay alive. If the file
ran top-to-bottom and exited, the module would be torn down and Maya would hold
dangling references to dead Python objects. Defining functions + a module-level
list, then calling `test()` interactively, keeps everything reachable for as
long as the session lasts.

**Q2. Why must `callbackIDs` live at module level, and why must I keep the IDs?**
The `MCallbackId` Maya returns is the **only handle** to that callback — there is
no "remove all my callbacks" by function pointer. If the list goes out of scope
(or you blank it without removing first), the callbacks become un-removable for
the rest of the session: they keep firing and you cannot reach them. Storing IDs
at module scope keeps them reachable; `removeCallbacks()` spends them.

**Q3. When exactly do `beginManipCB` / `endManipCB` fire? Continuously while dragging?**
No — **once per gesture**: begin when you start the tumble/track/dolly, end when
you release the mouse. They are for **interactive** camera manipulation only.
A scripted move (`cmds.view(...)`, `cmds.xform('persp', ...)`, or a camera with
keyframed rotation) does **not** trigger them — there is no user gesture to
begin/end. If you need to react to *any* camera change including scripted ones,
`MCameraMessage` is the wrong tool (use `MNodeMessage.addAttributeChangedCallback`
on the camera's rotate/translate instead).

**Q4. The `else: "This node is not a camera..."` branch — when does it run?**
Effectively **never**, through the public API. `addCallbacksToPerspCamera`
hard-codes `cmds.select('perspShape')`, so the selection is always a camera and
the loop always takes the `if` branch. The `else` is dead code left over from a
more general design. To exercise it you must edit the `cmds.select` line (Run C).
It's a good reminder: a type-check that the surrounding code makes unreachable
is a smell, not a safety net.

**Q5. I want to watch *my own* camera, not persp. How?**
Two changes: (1) replace `cmds.select('perspShape')` with the name of your
camera's shape (e.g. `cmds.select('myCamShape')`), and (2) make sure the panel
you tumble is **looking through that camera** (Panels → Look Through Selected,
or `cmds.lookThru('myCamShape')`). The callback is attached to whichever camera
**shape** `MObject` you pass to `addBeginManipulationCallback`, so generalizing
this is a one-line edit (see Advanced Directions).

**Q6. What is `clientData` actually for? Why pass strings like `"12345.5"`?**
`clientData` is per-callback context Maya passes straight back to your function
— a way to carry state into the callback **without globals**. In a real tool
you'd pass a dict (`{'view': 'persp', 'log': my_logger}`) or the camera name, so
the *same* callback function can react differently per camera. The placeholder
strings here exist only so you can see the value echo in the print.

**Q7. `camFn = OpenMaya.MFnCamera()` — what does that line do?**
Nothing. It is dead boilerplate in both files — allocated, never referenced.
You'd only need `MFnCamera(node)` to read/write camera attributes (focal length,
clipping planes, etc.); this demo never does. You can delete the line and
nothing changes. It's worth recognizing dead allocation when you see it, because
in API 1.0 it *looks* like the fill-by-reference setup that `dependNode` /
`dagPath` legitimately need.

**Q8. What actually changed between the API 1.0 and 2.0 files?**
Nothing about the callbacks. The `MCameraMessage` methods, the `(node,
clientData)` signature, the `MCallbackId` return, and `MMessage.removeCallback`
are identical. Only the **plumbing** for obtaining the camera `MObject` differs
(5 differences — see the table above): API 1.0 makes you pre-allocate `MObject`
/ `MDagPath` wrappers and fill them by reference; API 2.0 returns them directly.
So porting a callback script 1.0 → 2.0 is mostly an import change plus simpler
selection handling.

**Q9. Why `next(iter)` to advance, and why is the variable named `iter`?**
Maya's `MItSelectionList` implements `__next__`, so the Python builtin `next(obj)`
advances it — that's what `next(iter)` does. The variable name `iter` shadows
Python's builtin `iter()` function (mildly confusing but harmless inside this
function). The more idiomatic Maya form is `iter.next()`; both work in current
Maya. The standard `while not iter.isDone(): … iter.next()` loop and the
`for … in iter:` form are interchangeable here.

**Q10. I reloaded the module and now each tumble prints twice (or more). Why?**
Ghost callbacks. `importlib.reload(cmt)` re-runs `callbackIDs = []`, wiping your
reference to the **old** IDs — but Maya is still holding those callbacks, so they
keep firing alongside the new pair. You can no longer reach the old IDs to remove
them. **Fix:** always `cmt.removeCallbacks()` *before* reloading, or restart
Maya. This is the central pitfall of the whole Message system and the reason the
register → store → **remove** lifecycle has three steps, not two.

**Q11. Do these callbacks fire if I animate the camera (keyframe its rotation)?**
No. They fire on **interactive user manipulation** only. Keyframed or
scripted camera motion changes the camera without a "manipulation gesture," so
begin/end never fire. If you need to react to *any* camera transform change,
watch the camera node's attributes with `MNodeMessage.addAttributeChangedCallback`
instead — but expect it to fire far more often (every DG dirty/eval).

---

## Advanced Directions

1. **Generalize to *any* selected camera (or the active panel's camera).**
   Replace the hard-coded `cmds.select('perspShape')` with a helper that either
   uses the current selection (`cmds.ls(selection=True, shapes=True,
   type='camera')`) or reads the panel the mouse is over
   (`cmds.getPanel(withFocus=True)` → `cmds.modelEditor(panel, q=True,
   camera=True)`). New: `addCallbacksToCamera(shapeName)` taking the shape as an
   argument, and a `registerAllSceneCameras()` that loops `cmds.ls(type='camera')`
   so every camera in the scene is watched at once.

2. **Real `clientData` — identify *which* camera was manipulated.**
   Pass a dict like `{'name': 'persp', 'logger': log}` as `clientData`, and in
   the callback print `MFnDagNode(node).partialPathName()` plus the stored name.
   This turns the placeholder `"12345.5"` into a genuinely useful per-camera
   context and removes the need for any global state. New: a small
   `CameraEvent` dataclass / dict schema for the payload, and a `make_callback(name)`
   factory so each camera gets a closure with its own context.

3. **Auto-cleanup on scene switch (no more ghost callbacks).**
   Register an `MSceneMessage` callback for `kBeforeNew` / `kBeforeOpen` that
   calls `removeCallbacks()` automatically, so a New/Open File during development
   can't strand live callbacks. New: `autoCleanup()` registering the scene
   messages, and a `teardown()` that removes *both* the camera callbacks and the
   scene-message callback itself (the scene-message ID must be stored too, or it
   leaks the same way).

4. **A reusable `CallbackManager` context manager.**
   Wrap register/store/remove in a class — `with CallbackManager() as cm:
   cm.add_camera_manip(cam, on_begin, on_end)` — whose `__exit__` removes
   everything, so a callback set can never leak past its block. New:
   `CallbackManager` holding a `list[MCallbackId]`, `.add_*()` helpers per
   message family, and `__enter__`/`__exit__`. This generalizes beyond cameras to
   `MNodeMessage`, `MDGMessage`, `MEvent`, etc. (compare the
   `AdvancedPythonForMaya-master/Utilities/callbackManager` demo for a relative).

5. **React to the manipulation — a "match this view" tool.**
   On `endManipCB`, snapshot the camera's `translate`/`rotate`/`focalLength` and
   write them to a log or populate a UI, so an artist can copy the framing to
   another camera. New: `snapshot_camera(node)` returning a dict, a small Qt
   window showing the last N framings, and a `apply_framing(target_cam, snap)`
   to bake a snapshot onto another camera (with an undo chunk).

6. **Wrap as an installable shelf tool with a UI toggle.**
   Package the manager + a one-button shelf item that opens a small Qt window
   with a "Log camera manipulation on/off" checkbox, a camera picker, and a live
   event feed. New: a `CameraMessageUI(QtWidgets.QWidget)` with
   start/stop/clear buttons, a `feed` QListWidget, and an installable Maya
   package (`userSetup.py` shelf button) — turning this Hello-World into a
   real debugging instrument for viewport-camera behavior.
