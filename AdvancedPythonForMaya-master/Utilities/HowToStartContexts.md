# HowToStart — Utilities: Python Contexts (contextExamples & createdNodesContext)

> **Position in the curriculum.** This is the second theme of the final `AdvancedPythonForMaya-master/Utilities/` project. The first theme (`HowToStartCallbackManager.md`) taught the *event/callback* lifecycle (`MSceneMessage` register→store→remove). This file teaches the *scope/cleanup* lifecycle — the Python **`with`-statement context manager** — in two escalating files:
> * **`contextExamples`** — pure-Python theory of the `with` statement (no Maya at all): five escalating ways to guarantee cleanup.
> * **`createdNodesContext`** — the same `__enter__`/`__exit__` pattern applied to Maya: a context that captures **every node created inside its block** via `MDGMessage` and hands you the validated list.
>
> ⚠️ **Name check: these are *Python* context managers, not Maya `MPxContext` tools.** The word "context" is overloaded in Maya. A **Python context manager** (PEP 343, the `with obj as x:` statement) wraps a block in setup/teardown. A **Maya `MPxContext`** is a viewport *tool* (like the marquee-select or measure-distance tool) you author with `OpenMayaUI.MPxContext`. **This demo is only about the former.** Neither file imports `MPxContext` or registers a tool. The `Utilities/README.md` confirms: *"Contexts in Python let us wrap large blocks of code inside a temporary scope."*

---

## Files in this demo

| File | Archetype | Maya needed? | Runs on Maya 2027? |
|------|-----------|--------------|--------------------|
| `contextExamples.py` | Flat top-to-bottom script (no `def`/`class` *definition library* — it defines one class but **runs it immediately** at module level) | **No** — pure Python (only `open`, `print`, `contextlib`) | ✅ Original is already Py3-clean |
| `contextExamples_2027.py` | (verified copy) | No | ✅ Byte-identical to original after the header |
| `createdNodesContext.py` | Definitions + driver (class `CreatedNodesContext` + `test()`; **no `__main__` guard**) | **Yes** — `maya.cmds` + `maya.api.OpenMaya` | ❌ Original is a hard `SyntaxError` (Py2 `print`) |
| `createdNodesContext_2027.py` | (verified copy) | Yes | ✅ Header + one `print` conversion |

> **`_2027` convention.** Across the curriculum, `*_2027.py` is the Maya-2027 (Python 3) verified copy. For **`contextExamples`** the `_2027` file is **byte-identical to the original after the header comment** (diff-confirmed) — the file was already Py3-clean, there was genuinely nothing to modernize. For **`createdNodesContext`** the only real change is line 86→87: `print "..."` → `print("...")` plus an explanatory comment; the **original does not even parse** on Python 3 (`py_compile` reports `SyntaxError: Missing parentheses in call to 'print'`), so on Maya 2027 you **must** use `createdNodesContext_2027.py`.

## Prerequisites

* Maya 2027 (or any Maya whose Python is 3.x) with the Script Editor or `mayapy`.
* For `createdNodesContext`: an interactive Maya session (it calls `cmds.file`, `cmds.polyCube`, …). For `contextExamples`: **nothing Maya-specific** — it runs under plain `python3` and is fully exercised/verified in this guide without Maya.
* Read `HowToStartCallbackManager.md` first if you want the callback-lifecycle background (`addNodeAddedCallback` follows the same *register→store ID→remove* rule taught there).

---

## What the code actually does

### `contextExamples.py` — five escalating forms of the *same* cleanup idea

The file is one long tutorial comment chain. Each block re-implements "open a file, read it, guarantee it gets closed" with progressively more abstraction. It defines **one** class (`OpenFile`) but, unlike a definitions library, it **executes every block at module level** as it runs top-to-bottom — there is no `__main__` guard, so importing the module runs the whole demo (and it ends by raising an exception on purpose; see Run A).

| # | Block | What it teaches | Cleanup guarantee |
|---|-------|-----------------|-------------------|
| 1 | `thisFile = open(__file__); …; thisFile.close()` (lines 7–15) | The naive way. | ❌ If code errors between open and close, the file leaks. |
| 2 | `with open(__file__) as thisFile:` (lines 19–20) | The built-in `with` statement. | ✅ Closes automatically, even on error. |
| 3 | `try: open(); … finally: …close()` (lines 24–29) | That `with` is "an advanced `try/finally`". | ✅ `finally` always runs; prints `Closing path in try/finally`. |
| 4 | `@contextmanager` `def openFile(path, mode='r'):` + `yield` (lines 38–53) | The decorator short-form from `contextlib`: code before `yield` is setup, after `yield` (in `finally`) is teardown. | ✅ Prints `Closing path in decorator context`. |
| 5 | `class OpenFile` with `__enter__`/`__exit__` (lines 58–90) | The class-based context manager — the form `createdNodesContext` will copy. `__enter__` does setup and returns the resource; `__exit__(exc_type, exc_val, exc_tb)` does teardown and receives any exception. | ✅ Prints `Closing path in class context`, then **re-raises** `exc_val`. |

The final line, `with OpenFile(__file__) as thisFile: raise RuntimeError('Test')` (line 90/94), is **deliberate**: it proves the body can error and `__exit__` still runs the cleanup before the exception propagates. Verified by execution (see Run A).

> **Verified behavior (ran `contextExamples_2027.py` under plain Python 3):** the three teardown prints fire in source order — `Closing path in try/finally` → `Closing path in decorator context` → `Closing path in class context` — and the program then exits with code 1 on an uncaught `RuntimeError: Test`. The cleanup message is printed **before** the traceback, confirming `__exit__` runs during exception unwinding.

### `createdNodesContext.py` — the same `__enter__`/`__exit__` idea, applied to Maya

A single class, `CreatedNodesContext`, that uses a **Maya Message callback** (`MDGMessage.addNodeAddedCallback`) to record every node created while the `with`-block is active. It is API 2.0 (`from maya.api import OpenMaya as om`), definitions-only (no `__main__`), plus a `test()` driver.

| Member | Line | Role |
|--------|------|------|
| `__init__` | 8 | Allocates the capture list `self.__nodes = []` and the callback-ID slot `self.__handlerID = None`. (Does **not** register yet — registration belongs in `__enter__`.) |
| `__enter__` | 14 | Registers `om.MDGMessage.addNodeAddedCallback(self.__handler, 'dependNode')`, stores the returned `MCallbackId`, and returns `self` (so `as cnc` gives you the context object). |
| `__exit__(exc_type, exc_val, exc_tb)` | 21 | **Always** (even on error): `removeCallback(self.__handlerID)` so no callback leaks, then `self.__nodes = []` to drop references. If `exc_val`, re-raises it. |
| `__handler(self, node, *args)` | 31 | The callback Maya calls for each new node. `node` is an `MObject`; it is appended to `self.__nodes`. `*args` absorbs the optional `clientData`. |
| `nodes()` | 36 | Returns the **validated** list of surviving node **path strings**: skip `isNull()` MObjects, get `partialPathName()` for DAG nodes vs `name()` for DG nodes, and re-validate each via `MSelectionList().add(path)` (skipping anything that throws). |
| `test()` | 79 | Driver: `file(new=True)` **outside** the context, then inside the `with`: `polyCube` + `polySphere` + `spaceLocator` + `delete(the cube)`, then prints `cnc.nodes()`. |

**The lifecycle (the whole point):** `__enter__` registers → the callback quietly collects MObjects while your code runs → `__exit__` removes the callback and clears the list. Because `__exit__` is *guaranteed* to run (that is what a context manager is), the callback is **always** removed — even if your block raises. This is the robust, no-leak upgrade of doing `addCallback(...)`/`removeCallback(...)` by hand, and the direct continuation of `HowToStartCallbackManager.md`'s register→store→remove rule.

---

## How to Create the Test Maya Scene

### For `contextExamples` — no scene needed

This file is **pure Python** (it only `open`s its own source file and `print`s). There is nothing to build in Maya — the "scene" is just the file-on-disk it reads. Run it from a terminal (`python3 contextExamples_2027.py`) **or** paste it into the Script Editor; the result is identical. *(Same no-scene convention as `commandLine`, `fileDialog`, and `manipulatorMath`.)*

### For `createdNodesContext` — the `test()` driver builds its own

You do **not** hand-build a scene. The `test()` driver constructs the minimum scene itself:

1. `cmds.file(new=True, force=True)` — fresh empty scene (the default cameras etc. are created **here, outside** the `with`, so they are *not* captured).
2. Inside the `with`: one `polyCube`, one `polySphere`, one `spaceLocator`, then `cmds.delete(cubes)` removes the cube (transform + shape + its construction-history node).
3. `cnc.nodes()` is called **inside** the block (important — see Q&A) and the surviving names are printed.

> **⚠️ Destructive:** `test()` calls `cmds.file(new=True, force=True)`, which discards your current scene without prompting. Run it in a throwaway scene.

If you want to drive `CreatedNodesContext` **headlessly** around your own rig-building code instead, any scene (including an empty one) is fine — see Run C.

| Entry point | Scene / state it expects |
|-------------|--------------------------|
| `contextExamples` (paste/run) | None (pure Python). |
| `createdNodesContext.test()` | Any scene — it force-resets to new first (⚠️ destructive). |
| Headless `with CreatedNodesContext()` | Any scene; build/modify nodes *inside* the block. |

---

## How to Run the Functions

### Run A — `contextExamples` (pure Python, runs anywhere)

Paste the **whole file** (either the original or `_2027` — both are Py3-clean) into the Script Editor and execute, **or** run it from a shell:

```bash
python3 contextExamples_2027.py
```

**Expected (verified by execution):** the file's own contents are printed several times (each `print(thisFile.read())` dumps the source), interspersed with the three teardown messages in order:

```
Closing path in try/finally
…
Closing path in decorator context
…
Closing path in class context
Traceback (most recent call last):
  …
  File "contextExamples_2027.py", line 90, in __exit__
    raise exc_val
RuntimeError: Test
```

The script exits non-zero. The `RuntimeError` is **the lesson**, not a bug: it demonstrates that `__exit__` ran the cleanup (`Closing path in class context`) before the exception escaped the `with`. (To see the demo *without* the crash, comment out the final `raise RuntimeError('Test')` line.)

### Run B — `createdNodesContext` via the `test()` driver (needs Maya)

In the Script Editor:

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')

import createdNodesContext_2027 as cnc  # NOTE: original .py is a Py3 SyntaxError; use _2027
cnc.test()
```

**Expected Script Editor output** (representative — exact names follow Maya's creation order; the key invariant is that the **cube's nodes are absent** because `test()` deleted them):

```
Created the following nodes:
	pSphere1
	pSphere1Shape
	polySphere1
	locator1
	locatorShape
```

* The cube (`pCube1` / `pCube1Shape` / `polyCube1`) is **gone** from the list — `isNull()` filtered those MObjects after `cmds.delete(cubes)`.
* `polySphere1` appears as a bare name (it's a DG/construction-history node → `name()`); the transforms/shapes appear via `partialPathName()` (DAG nodes).
* *Cannot verify the exact naming/order without Maya running; the set above is what the code's logic produces.*

### Run C — drive `CreatedNodesContext` headlessly around your own code

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import createdNodesContext_2027 as cnc
import maya.cmds as cmds

cmds.file(new=True, force=True)
with cnc.CreatedNodesContext() as ctx:
    cmds.joint(name='root_jnt')
    cmds.joint(name='spine_jnt')
    cmds.polyCube(name='block')
    created = ctx.nodes()        # call INSIDE the block!
print("I just created:", created)
```

**Expected:** `created` lists the two joints, the cube transform and its mesh shape, and the cube's construction-history node — every dependNode created between `with` and the call. After the block exits, `ctx.nodes()` would return `[]` (see Q&A).

### Run D — prove the callback is removed even when the block errors

```python
with cnc.CreatedNodesContext() as ctx:
    cmds.polySphere()
    raise RuntimeError('boom')   # body errors mid-block
# __exit__ still ran removeCallback(ctx._CreatedNodesContext__handlerID)
```

**Expected:** `RuntimeError: boom` propagates, but the callback was removed during unwinding (no "ghost callback" firing on later node creation). This is the safety guarantee a hand-written `try/finally` would give you, packaged as a `with`.

### One-shot paste (both files)

```python
# --- A: pure-Python context theory (safe to run anywhere) ---
import sys, os
UTIL = r'/abs/path/AdvancedPythonForMaya-master/Utilities'
sys.path.insert(0, UTIL)
exec(open(os.path.join(UTIL, 'contextExamples_2027.py')).read())  # prints closing msgs, ends in RuntimeError (by design)

# --- B: Maya node-capture context ---
import createdNodesContext_2027 as cnc
cnc.test()   # ⚠️ cmds.file(new=True, force=True) — discards current scene
```

---

## Question and Answer

**Q1. The folder is called "Contexts" — are these Maya `MPxContext` viewport tools (like the marquee-select tool)?**
No. These are **Python `with`-statement context managers** (PEP 343) — objects with `__enter__`/`__exit__` that wrap a code block in setup/teardown. A Maya `MPxContext` is a *viewport tool* (`OpenMayaUI.MPxContext`). Neither file imports `MPxContext`; `contextExamples` doesn't import Maya at all. The overload of the word "context" is the single biggest source of confusion here.

**Q2. `contextExamples.py` ends by raising `RuntimeError('Test')` — is the file broken?**
No — it's deliberate. The last `with OpenFile(__file__) as thisFile: raise RuntimeError('Test')` proves the body can error and `__exit__` **still** closes the file (prints `Closing path in class context`) before the exception propagates. Verified: the cleanup prints fire, *then* the traceback, and the script exits non-zero. That cleanup-runs-on-error guarantee *is* the demo.

**Q3. Why three different ways to make a context (`with` builtin, `@contextmanager`, `__enter__`/`__exit__` class)?**
They are escalating-abstraction teaching steps toward the same result. The builtin `with open()` is the user-facing form; `try/finally` shows what it expands to; `@contextmanager` is the concise decorator short-form (`yield` separates setup from teardown); the `__enter__`/`__exit__` class is the most explicit and is the **form `createdNodesContext` copies** because it needs to hold state (the node list + the callback ID) across the block.

**Q4. The original `createdNodesContext.py` won't import on Maya 2027 — why?**
Line 86 is `print "Created the following nodes:\n\t%s" % …` — a Python-2 print *statement*. Python 3 requires `print(…)`. `py_compile` reports `SyntaxError: Missing parentheses in call to 'print'`. Only `createdNodesContext_2027.py` (which fixes that one line) runs. This is the same Py2-print `SyntaxError` pattern seen in `Commands/decorators.py` and several Intro files.

**Q5. I called `ctx.nodes()` *after* the `with`-block and got an empty list — why?**
`__exit__` sets `self.__nodes = []` when the block ends (line 25). So `nodes()` **must** be called *inside* the `with` (as `test()` does on line 87). This is a deliberate cleanup (it drops references to `MObject`s so they don't keep nodes alive), but it's an easy trap: snapshot the list with `created = ctx.nodes()` before the block closes.

**Q6. In `test()`, a cube is created and then deleted — does `nodes()` still list it?**
No. `cmds.delete(cubes)` nullifies those `MObject`s, and `nodes()` skips anything where `node.isNull()` is true (line 46–47). That's exactly why the printed list shows the sphere and locator but **not** `pCube1`/`pCube1Shape`/`polyCube1`. The context is robust to deletion: it never hands you back stale/deleted nodes.

**Q7. What does the `'dependNode'` argument in `addNodeAddedCallback` do?**
It's the **node-type filter**. `dependNode` is the base class of *every* dependency node, so the callback fires for **every** node created — transforms, shapes, construction history, the lot. Pass a more specific type (`'mesh'`, `'joint'`, `'transform'`) to capture only that kind. This is the lever to tame the "captures everything" noise.

**Q8. Why does `nodes()` use `partialPathName()` for DAG nodes but `name()` for DG nodes?**
DAG nodes live in the hierarchy and can share leaf names (`pCube1` under two different parents), so a bare name is ambiguous — `partialPathName()` gives the shortest *unique* path. DG (dependency) nodes have no hierarchy and always have a unique name, so `name()` suffices. This is the same DAG-vs-DG distinction introduced in `Intro/standalone`.

**Q9. The callback fires for *every* node — isn't that noisy?**
Yes, and that's the trade-off. Creating one `polyCube` actually fires the callback for the transform, the mesh shape, **and** the `polyCube1` construction-history node (3 nodes), plus anything Maya creates internally. The power is "give me everything created in this block"; the cost is you usually want to filter the result (by type, by name pattern, etc.) before using it.

**Q10. `OpenFile.__exit__` explicitly does `if exc_val: raise exc_val` — isn't that redundant?**
Mostly yes, and that's a fine observation. When the `with`-body raises and `__exit__` returns a falsy value (`None`), the exception propagates **anyway** — so the explicit re-raise is harmless teaching theater. The *real* control is the **return value** of `__exit__`: return `True` to **suppress** the exception, return `None`/`False` to let it propagate. (`createdNodesContext.__exit__` has the same redundant re-raise; both are being explicit rather than relying on the implicit rule.)

**Q11. Does `CreatedNodesContext` leak the callback if my block raises?**
No — that's the whole reason it exists. `__exit__` runs `removeCallback(self.__handlerID)` **unconditionally** (before the `if exc_val: raise`), so even on error the callback is removed. Compare with doing `addNodeAddedCallback(...)`/`removeCallback(...)` by hand, where an exception between them leaks a ghost callback (the trap from `HowToStartCallbackManager.md`). The `with` turns that discipline into a guarantee.

---

## Advanced Directions

1. **A self-cleaning `DeleteCreatedNodesContext` (rollback on error).** Same capture mechanism, but `__exit__` *deletes* every captured node when the block raises — a transactional "undo my partial work" context for rig-building scripts. Add an `__init__(self, cleanup_on_error=True)` flag and have `__exit__` call `cmds.delete(ctx.nodes())` when `exc_val` is set (and `cleanup_on_error`), then re-raise. This is the natural "undo a failed build" companion to `Commands/distributeCmd`'s undo stack.

2. **Wrap the block in an undo chunk.** Add `cmds.undoInfo(openChunk=True)` in `__enter__` and `cmds.undoInfo(closeChunk=True)` in `__exit__` so the *entire* block collapses to a single Undo step (the same chunking idiom taught in `controllerLibrary`/`lightManager`). Pair with #1 so one Ctrl+Z rolls back the whole context. New members: chunk open/close in `__enter__`/`__exit__`, and a guard so an exception still closes the chunk.

3. **Parameterize the node-type filter: `CreatedNodesOfTypeContext(nodeType='mesh')`.** Replace the hard-coded `'dependNode'` (line 17) with a constructor argument so callers can capture only meshes, joints, animCurves, etc. Add `__init__(self, nodeType='dependNode')` and thread it into `addNodeAddedCallback`. Useful for "list every curve created by this build" without post-filtering.

4. **A generic `MayaCallbackContext` base class (DRY over all `MMessage` callbacks).** Generalize the register-in-`__enter__`/remove-in-`__exit__` pattern: an abstract base whose `__enter__` calls a `_register()` subclass hook and stores the ID, and whose `__exit__` always `removeCallback`s it. `CreatedNodesContext`, a future `SelectionChangedContext`, etc. become tiny subclasses. This directly mirrors the `SceneCallbackManager` singleton from the sibling demo but scoped to a *single block* rather than the whole session.

5. **"Capture then group" organizing context.** After capture, auto-group all created DAG nodes under a single parent transform so a procedural build lands in one tidy hierarchy. Add `__exit__` logic that, on clean exit, `cmds.group(ctx.nodes(dag_only=True), name=…)`. Turns the node-list side-effect into an automatic scene-organization tool.

6. **Performance + creation census context (cross-demo).** Compose this demo with `profilerDump`: `__enter__` starts an `MProfiler` capture *and* a `CreatedNodesContext`; `__exit__` stops the profiler and returns **both** the created-node list and the timing JSON. You get, in one `with`, "what nodes did this rig-build create, and how long did each phase take" — a combined rig-audit tool that ties the Utilities/Contexts and profilerDump demos together. New: a `ProfiledNodesContext` wrapping both, exposing `.nodes()` and `.profile()`.
