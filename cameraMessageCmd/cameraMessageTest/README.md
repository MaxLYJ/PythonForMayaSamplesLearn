# cameraMessageTest — Maya Camera Manipulation Callbacks

This demo comes from the official Maya Python API documentation:

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/camera_message_cmd_2camera_message_test_8py-example.html>

It shows how to use the **`MCameraMessage`** class to register callbacks that fire
when a user starts and stops tumbling / tracking / dollying a camera in the viewport.
It is the canonical "Hello World" for Maya message callbacks.

---

## What you will learn

By working through this demo you will understand:

1. **The Maya Message system** — how Maya lets your code react to events
   (selection changes, attribute edits, time changes, camera manipulation, …)
   instead of polling.
2. **`MCameraMessage`** specifically — the message subclass for camera events.
3. **The register → store ID → remove by ID** lifecycle that *every* Maya
   callback follows, and why skipping the last step leaks callbacks.
4. **`clientData`** — how to pass your own per-callback context (a widget, a
   settings dict, a camera name, …) into a callback without globals.
5. **API 1.0 object idioms** — `MSelectionList`, `MItSelectionList`,
   `MObject.hasFn(MFn.kCamera)`, and the fill-by-reference style of API 1.0.

---

## Prerequisites

| Concept                | Where to learn it                                          |
|------------------------|------------------------------------------------------------|
| Python basics          | `introduction/helloWorld.py`, `introduction/helloCube.py`  |
| `maya.cmds`            | `introduction/helloCube.py`                                |
| OpenMaya basics        | Maya docs → *Python API 1.0* overview                      |
| What an `MObject` is   | Maya docs → `OpenMaya.MObject`                             |

You do **not** need to know dependency graphs, nodes, or plug-in authoring to
read this demo. It is pure scene-level scripting with the API.

---

## Files

```
cameraMessageCmd/
└── cameraMessageTest/
    ├── README.md                 ← this file
    └── (place cameraMessageTest.py here — see "Get the code" below)
```

> The Python source itself is **not** bundled here because it is owned by
> Autodesk. Fetch it from the link at the top of this page and drop it next to
> this README.

---

## Get the code

1. Open the Source URL at the top of this file.
2. Copy the `cameraMessageTest.py` listing.
3. Save it as `cameraMessageTest.py` in this folder
   (`cameraMessageCmd/cameraMessageTest/`).

---

## How to run it

In the Maya Script Editor (Python tab):

```python
import cameraMessageTest as cmt

maya.cmds.file(f=True, new=True)   # fresh scene so 'perspShape' exists
cmt.test()                          # register the callbacks on persp
```

Now **tumble, track, or dolly the persp viewport with the mouse.** The Script
Editor output should print, on every manipulation:

```
Inside beginManipCB, clientData is 12345.5
Inside endManipCB, clientData is 54321.5
```

When you are done, tear the callbacks down so they don't linger:

```python
cmt.removeCallbacks()
```

---

## Read the code in this order

The file is small (~75 lines). Read it in this order to build understanding
rather than top-to-bottom:

1. **The two callback functions** (`beginManipCB`, `endManipCB`).
   Notice the `(node, clientData)` signature — every `MCameraMessage`
   manipulation callback looks like this.
2. **The `callbackIDs = []` module-level list.** This is where the returned
   `MCallbackId` handles live. You *must* keep them; without the ID you cannot
   remove a callback later.
3. **`addCallbacksToPerspCamera()`** — the body.
   - It uses `cmds.select('perspShape')` + `MSelectionList` +
     `MItSelectionList` to turn the current selection into `MObject`s. This is
     the standard API 1.0 "get selected nodes" idiom.
   - It type-checks each node with `dependNode.hasFn(OpenMaya.MFn.kCamera)`.
   - It registers `addBeginManipulationCallback` and
     `addEndManipulationCallback`, each returning an ID that gets pushed into
     `callbackIDs`.
4. **`removeCallbacks()`** — loops every stored ID and calls
   `MMessage.removeCallback(id)`, then clears the list. Always pair
   registration with cleanup.

---

## Key API reference links

* `OpenMaya.MCameraMessage` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_camera_message.html>
  `addBeginManipulationCallback`, `addEndManipulationCallback`
* `OpenMaya.MMessage` (base class — `removeCallback` lives here)
* `OpenMaya.MFn.kCamera` — the function-set enum used by `MObject.hasFn`

---

## Things to try next (exercises)

Once the basic demo prints, modify it to lock in the concepts:

1. **Print the camera name.** Inside `beginManipCB`, use
   `OpenMaya.MFnDagNode(node).partialPathName()` to print *which* camera was
   manipulated, not just the clientData string.
2. **Add a non-persp camera.** Create a second camera with
   `cmds.camera()` and call `addCallbacksToPerspCamera`-style logic on its
   shape. Confirm the right callback fires for the right camera.
3. **Use real clientData.** Replace the placeholder strings with a dict like
   `{'view': 'persp', 'log': my_logger}` and read it inside the callback.
4. **Port to API 2.0.** Rewrite using `import maya.api.OpenMaya as om`.
   Replace the selection-list iterator with
   `om.MGlobal.getActiveSelectionList()` (indexable directly). Callback
   signatures are identical.
5. **Auto-cleanup.** Register an `MSceneMessage` callback for "new/open scene"
   that calls `removeCallbacks()` automatically, so reloading the script
   during development doesn't leave ghost callbacks.

---

## Common pitfalls

* **Forgetting `removeCallbacks()`.** If you reload the module without
  removing old callbacks, you'll see duplicate prints — the old IDs are still
  live. Always clean up, or restart Maya.
* **Losing the IDs.** If `callbackIDs` goes out of scope (e.g. you stored it
  in a local variable instead of module-level), the callbacks become
  un-removable for the rest of the session.
* **`camFn` is unused in the demo.** Don't be misled — it's leftover
  boilerplate. You only need `MFnCamera(node)` if you want to read/write
  attributes like focal length.
* **This file imports `maya.OpenMaya` (API 1.0)** even though it lives in the
  "Python API 2.0 Reference" section of the docs. The 2.0 port is a one-line
  import change plus simpler selection handling.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — cameraMessageCmd/cameraMessageTest.py*,
Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/camera_message_cmd_2camera_message_test_8py-example.html>
