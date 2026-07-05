# cameraMessageTest2 — Maya Camera Manipulation Callbacks (API 2.0)

This is the **API 2.0** sibling of [`cameraMessageTest`](../cameraMessageTest/README.md).
It does exactly the same thing — registers `MCameraMessage` callbacks that fire
when a user starts/stops tumbling, tracking, or dollying a camera — but uses
`maya.api.OpenMaya` instead of `maya.OpenMaya`.

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/camera_message_cmd_2camera_message_test2_8py-example.html>

> Read the **cameraMessageTest** README first if you haven't. This file mainly
> exists to show the differences between API 1.0 and API 2.0, so it is
> intentionally terse where the two are identical.

---

## What you will learn (that's *new* vs. part 1)

1. **The `maya.api.OpenMaya` import** — the API 2.0 module that Autodesk
   recommends for new code. Faster, more Pythonic, returns values rather than
   filling objects by reference.
2. **No more pre-allocated wrapper objects.** In API 1.0 you had to write
   `dependNode = OpenMaya.MObject()` and pass it *into* `getDependNode(...)` to
   be filled. In API 2.0 the methods **return** the value directly:
   ```python
   dependNode = iter.getDependNode()   # API 2.0 returns it
   dagPath    = iter.getDagPath()      # API 2.0 returns it
   ```
3. **`MGlobal.getActiveSelectionList()` returns the list directly** — no
   fill-by-reference argument, and the list is indexable:
   ```python
   slist = OpenMaya.MGlobal.getActiveSelectionList()   # API 2.0
   # vs API 1.0:
   # slist = OpenMaya.MSelectionList()
   # OpenMaya.MGlobal.getActiveSelectionList(slist)
   ```
4. **Everything else is identical**: the callback signature
   `(node, clientData)`, the register → store ID → remove lifecycle, and the
   two callback classes (`MCameraMessage`, `MMessage`) are unchanged. This is
   the key insight — *moving callbacks to API 2.0 is mostly an import change
   plus simpler selection handling.*

---

## Prerequisites

| Concept                              | Where to learn it                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------------|
| The camera callback demo (part 1)    | [`../cameraMessageTest/`](../cameraMessageTest/README.md)                         |
| The register → store → remove pattern | same as above                                                                     |
| API 1.0 vs 2.0 differences           | Maya docs → *Using the Python API 2.0*                                            |

You should be comfortable with `cameraMessageTest.py` before reading this one —
it's literally the same example in a different dialect.

---

## Files

```
cameraMessageCmd/
├── cameraMessageTest/        ← API 1.0 version (read this first)
└── cameraMessageTest2/       ← this folder, API 2.0 version
    ├── README.md
    └── cameraMessageTest2.py
```

> The Python source is bundled here directly (it is a public Autodesk docs
> listing). The original is linked under **Source** above.

---

## How to run it

In the Maya Script Editor (Python tab):

```python
import cameraMessageTest2 as cmt2

maya.cmds.file(f=True, new=True)   # fresh scene so 'perspShape' exists
cmt2.test()                         # register the callbacks on persp
```

Tumble / track / dolly the persp viewport. Expected Script Editor output:

```
List length is 1
Node: perspShape
This is a camera, adding manipulation callbacks with payloads
Inside beginManipCB, clientData is 12345.5
Inside endManipCB, clientData is 54321.5
```

When done:

```python
cmt2.removeCallbacks()
```

---

## Side-by-side: API 1.0 → API 2.0 diff

The whole point of this example is the diff. Read it carefully.

| Concern                    | API 1.0 (`cameraMessageTest.py`)                                  | API 2.0 (`cameraMessageTest2.py`)                          |
|----------------------------|-------------------------------------------------------------------|------------------------------------------------------------|
| Import                     | `import maya.OpenMaya as OpenMaya`                                | `import maya.api.OpenMaya as OpenMaya`                     |
| Pre-allocate wrappers      | `dependNode = OpenMaya.MObject()`<br>`dagPath = OpenMaya.MDagPath()` | (removed — not needed)                                     |
| Get selection list         | `slist = OpenMaya.MSelectionList()`<br>`OpenMaya.MGlobal.getActiveSelectionList(slist)` | `slist = OpenMaya.MGlobal.getActiveSelectionList()`        |
| Get node from iterator     | `iter.getDependNode(dependNode)`                                  | `dependNode = iter.getDependNode()`                        |
| Get DAG path from iterator | `iter.getDagPath(dagPath)`                                        | `dagPath = iter.getDagPath()`                              |
| Callback signature         | `(node, clientData)`                                              | `(node, clientData)` (unchanged)                           |
| Register callback          | `OpenMaya.MCameraMessage.addBeginManipulationCallback(...)`        | identical (just the import differs)                        |
| Remove callback            | `OpenMaya.MMessage.removeCallback(id)`                            | identical                                                  |

**Takeaway:** The message API itself is unchanged between 1.0 and 2.0. Only the
surrounding `MObject` / `MDagPath` / `MSelectionList` plumbing changed.

---

## Things to try next (exercises)

1. **Diff the two files yourself.** Open
   `cameraMessageTest/cameraMessageTest.py` and
   `cameraMessageTest2/cameraMessageTest2.py` side by side and find every
   difference. There are exactly five meaningful ones (see the table above).
2. **Drop the `camFn`.** Like part 1, `MFnCamera()` is allocated but never
   used. Confirm you can delete that line and everything still works — a good
   test of "do I understand which lines matter?"
3. **Use the indexable selection list.** API 2.0's `getActiveSelectionList()`
   is indexable, so the iterator is overkill when you know you have exactly
   one item. Rewrite to:
   ```python
   slist = OpenMaya.MGlobal.getActiveSelectionList()
   dependNode = slist.getDependNode(0)   # no iterator needed
   ```
4. **Try the API 2.0 idiom for "find persp by name"** without using
   `cmds.select` at all:
   ```python
   slist = OpenMaya.MSelectionList()
   slist.add('perspShape')
   dependNode = slist.getDependNode(0)
   ```
   This is more robust than relying on the active selection.
5. **Port one of your own API 1.0 scripts to 2.0** using the table above as a
   checklist. The camera callbacks are a safe playground to practice on.

---

## Common pitfalls

* **Don't mix the imports.** Never do
  `import maya.OpenMaya as OpenMaya` **and**
  `import maya.api.OpenMaya as OpenMaya` in the same file — the `MObject`s
  from one are not compatible with the other. Pick one dialect per script.
* **API 2.0 `MObject`s are not the same objects as API 1.0 `MObject`s.** If
  you pass a 2.0 `MObject` to a 1.0 function (or vice versa) you'll get a
  cryptic type error. Always check the import at the top of the file.
* **The `reload(cmt2)` advice still applies.** During development, if you
  edit and re-import without removing callbacks, you'll get duplicate prints.
  Always call `removeCallbacks()` first.
* **`camFn = OpenMaya.MFnCamera()` is unused** here too — same leftover
  boilerplate as part 1. Ignore it.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — cameraMessageCmd/cameraMessageTest2.py*,
Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/camera_message_cmd_2camera_message_test2_8py-example.html>
