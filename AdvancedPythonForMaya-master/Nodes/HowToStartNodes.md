# HowToStartNodes.md — Custom Dependency Nodes (`Nodes/`)

> **Position in the curriculum.** This is the Advanced section's first **dependency-node plugin** demo. The `Commands/` folder showed the API packaged as a *command* — a one-shot action you invoke, then it is done. Here the same API is packaged as a **node** that *lives in the dependency graph*: it is instantiated with `createNode`, wired to other nodes with `connectAttr`, and **re-evaluates automatically whenever its inputs change**. Understanding `compute()` + `attributeAffects()` is the conceptual bridge between "a tool" and "a node that recomputes," and it is a prerequisite for the later deformer, transform, and locator demos.

This guide covers **two** files that are deliberately paired to teach one contrast: **API 2.0 vs API 1.0**.

| File | Archetype | Maya scene needed? | Verified runnable? |
|---|---|---|---|
| `minMaxNode.py` / `minMaxNode_2027.py` | `MPxNode` dependency node (**API 2.0**), pure numeric compute | ✅ A way to drive 3 inputs & read 1 output | ⚠️ Logic source-verified; needs Maya to load |
| `pushDeformer.py` / `pushDeformer_2027.py` | `MPxDeformerNode` (**API 1.0** — API 2.0 cannot make deformers), per-vertex geometry deformation | ✅ A mesh to deform | ⚠️ Logic source-verified; needs Maya to load |

> You met the `MPxNode` dependency-graph contract once before, in `py1AnimCubeNode/` (the animated cube). This folder's `minMaxNode` is the **minimal** member of that family (one numeric output, no time, no geometry); `pushDeformer` then shows the **geometry-filter** sub-family that mutates meshes.

## The `_2027` convention

Every teaching file has a `<name>_2027.py` sibling: a Python-3 / Maya-2027-verified copy. For this folder the diffs are the **lightest possible** — both originals were already version-clean:

- **`minMaxNode.py` → `minMaxNode_2027.py`**: header comment only. The code body is byte-identical (it already used `from maya.api import OpenMaya` and Py3 syntax).
- **`pushDeformer.py` → `pushDeformer_2027.py`**: header comment only. The code body is byte-identical.

**On Maya 2027 (Python 3) always load the `_2027.py` file.** The originals are kept verbatim for reference. (Confirmed: `diff` of the bodies shows only the header line; both `_2027` files pass `py_compile`; both are definitions-only — AST confirms no `if __name__ == '__main__'` guard.)

## Prerequisites

- **Maya 2027 (Python 3)** running interactively (GUI). Neither file can be exercised from plain `python3` — they both `import maya.*`, so they only parse/run inside Maya's interpreter (Script Editor → Python tab, or `mayapy`).
- The absolute path to this folder, referred to below as `/abs/path/Nodes/`.
- **⚠️ API-version split you must understand before reading the code.** The two files use *different* OpenMaya APIs on purpose:
  - `minMaxNode_2027.py` uses **API 2.0** (`from maya.api import OpenMaya`) and declares the `maya_useNewAPI()` sentinel.
  - `pushDeformer_2027.py` uses **API 1.0** (`from maya import OpenMaya` + `from maya import OpenMayaMPx`), and **has no `maya_useNewAPI()`**. This is intentional: **OpenMaya API 2.0 does not support authoring deformer nodes in Python**, so a deformer is one of the few places API 1.0 is still required.
- **⚠️ Performance caveat (from the folder README).** Only **one Python node can run at a time** in the dependency graph (whereas many C++ nodes evaluate in parallel). Python nodes can therefore bottleneck evaluation and block Parallel eval. They are excellent for *prototyping* a node idea but should usually be recompiled as C++ for production. This is *why* the final curriculum demo (`Compiling/minMaxPlugin`) recompiles `minMaxNode` in C++.
- **⚠️ Node-ID ownership.** Both nodes use a `MTypeId` in the **reserved-for-developers range `0x00000`–`0x7ffff`** (`minMaxNode` = `0x01010`, `pushDeformer` = `0x01012`). These are fine for local/teaching use. If you ever **release** a node publicly you must request a unique ID range from Autodesk — never ship an ID in the dev range, because two plugins that claim the same ID will corrupt each other's saved scenes.

## What the code actually does

### 1. `minMaxNode.py` — the minimal `MPxNode` (API 2.0)

A dependency node is a box with **input attributes** and **output attributes**. Maya calls your `compute()` whenever something downstream requests an output whose inputs are dirty. The canonical anatomy, every piece present here:

| Piece | In `minMaxNode.py` | Purpose |
|---|---|---|
| `maya_useNewAPI()` | `def maya_useNewAPI(): pass` | **Sentinel.** Its mere presence tells Maya this plugin uses API 2.0 semantics. The body does nothing. (`pushDeformer` omits it because it is API 1.0.) |
| `class MinMaxNode(om.MPxNode)` | the node class | Subclass `MPxNode` — the base class for all non-specialized nodes. |
| `kNodeName = 'minMax'` | class attribute | The node-type name users pass to `createNode`. |
| `kNodeID = om.MTypeId(0x01010)` | class attribute | A unique, persistent ID Maya uses to associate saved nodes with this plugin across sessions. **If it ever changes, scenes that reference the node break.** |
| `inputA/inputB/mode/output = None` | class placeholders | Slots filled in by `initialize()`. API 2.0 lets you use `None`; API 1.0 needs `om.MObject()`. |
| `creator()` (classmethod) | `return cls()` | Factory Maya calls to make a fresh node instance. (No `asMPxPtr` — that is an API-1.0-only ownership transfer.) |
| `initialize()` (staticmethod) | builds 4 attributes + wires them | Declares the node's attributes and the affect-relationships. |
| `compute(self, plug, data)` | the work | Computes the requested output from the inputs. |
| `initializePlugin(plugin)` | `registerNode(name, id, creator, initialize)` — **4 args** | Maya calls on `loadPlugin`. |
| `uninitializePlugin(plugin)` | `deregisterNode(id)` | Maya calls on `unloadPlugin`. |

**`initialize()` flow (verified):** build an `MFnNumericAttribute` function set → create `inputA` (`kDouble`, default `0.0`) and set `.storable=True`, `.keyable=True` → repeat for `inputB` → create `output` and set `.storable=True`, `.writable=True` (**note: output is NOT keyable**, so it appears in the Node Editor but not the Channel Box) → build an `MFnEnumAttribute` for `mode` with two fields `('min', 0)` and `('max', 1)` → `addAttribute` all four → **`attributeAffects` for all three inputs → output**.

> The `attributeAffects(input, output)` calls are the heart of the dependency graph: they tell Maya "when `input` is dirty, mark `output` dirty too, so `compute` will run." If you forget the `attributeAffects(mode, output)` line, **flipping the min/max dropdown will not recompute the output** — a silent, easy-to-miss bug.

**`compute()` flow (verified):**
1. **Guard:** `if plug != MinMaxNode.output: return` — Maya calls `compute` for *every* affected plug; you must early-exit unless the requested plug is one you actually produce.
2. Read the three input values: `data.inputValue(attr).asDouble()` / `.asInt()`.
3. `if mode: value = max([ia, ib]) else: value = min([ia, ib])` — `mode` is `0` (min) or `1` (max), so the **truthy** `if mode:` means "if max."
4. Write the result: `data.outputValue(MinMaxNode.output).setDouble(value)`.
5. **`data.setClean(plug)`** — non-negotiable. If you omit it, Maya thinks the output is still dirty and **calls `compute()` forever** (the #1 beginner MPxNode bug → "Maya spins / hangs").

The math is trivial — `min(a,b)` or `max(a,b)` — but the *scaffolding* (guard, read, compute, write, clean) is the reusable template for every numeric dependency node you will ever write.

### 2. `pushDeformer.py` — a `MPxDeformerNode` (API 1.0)

A deformer is a dependency node whose input/output is **geometry** (a mesh), not a number. Maya hands you each geometry set and lets you move its vertices. The anatomy diverges from `minMaxNode` in several API-1.0-specific ways:

| Piece | In `pushDeformer.py` | API 1.0 difference vs `minMaxNode` |
|---|---|---|
| Imports | `from maya import OpenMaya as om` + `from maya import OpenMayaMPx as ompx` | API 1.0 lives under `maya.OpenMaya` / `maya.OpenMayaMPx`, not `maya.api.OpenMaya`. |
| (no `maya_useNewAPI`) | absent | Correct — the sentinel is an API-2.0 marker; this plugin is API 1.0. |
| Base class | `class PushDeformer(ompx.MPxDeformerNode)` | `MPxDeformerNode` is the geometry-filter base; it pre-declares the `inputGeometry[]`, `outputGeometry`, and `envelope` attributes for you. |
| `push = om.MObject()` | attribute placeholder | API 1.0 requires a real `MObject()`, not `None`. |
| `creator()` | `return ompx.asMPxPtr(cls())` | **Ownership transfer.** In API 1.0 you must wrap the instance in `asMPxPtr` so Maya takes C++ ownership; in API 2.0 (`minMaxNode`) ownership is automatic, so plain `cls()` suffices. |
| Attribute config | `nAttr.setKeyable(True)` / `.setStorable(True)` / `.setChannelBox(True)` | API 1.0 uses **methods**; API 2.0 uses **properties** (`nAttr.keyable = True`). |
| Built-in attrs lookup | the `kApiVersion < 201600` branch | See the callout below. |
| `deform(self, data, geoIterator, matrix, geometryIndex)` | the per-vertex work | The deformer equivalent of `compute`. |
| `initializePlugin` | `registerNode(name, id, creator, initialize, ompx.MPxNode.kDeformerNode)` — **5 args** | The extra `kDeformerNode` **classification** tells Maya this is a deformer so `cmds.deformer(type='push')` works and it appears in the deformer menus. |
| `makePaintable(...)` in `initialize` | enables weight painting | Makes the deformer's `weights` paintable with the Paint Attributes tool. |

> **⚠️ The geometry-filter rename (the `kApiVersion` branch).** In Maya 2016 the internal C++ base class was renamed from `MPxDeformerNode` to `MPxGeometryFilter`, and the SWIG `cvar` attribute names changed with it. The plugin therefore sniffs `cmds.about(apiVersion=True)` and looks up the four built-in attributes under the old or new name:
> ```
> inputAttr        = MPxDeformerNode_input        / MPxGeometryFilter_input
> inputGeomAttr    = MPxDeformerNode_inputGeom    / MPxGeometryFilter_inputGeom
> outputGeomAttr   = MPxDeformerNode_outputGeom   / MPxGeometryFilter_outputGeom
> envelopeAttr     = MPxDeformerNode_envelope     / MPxGeometryFilter_envelope
> ```
> These four `cvar` members are how Python reaches the *inherited* attributes of the deformer base class (they are not created by your code — they already exist on `MPxDeformerNode`). On Maya 2027 (`apiVersion >= 2026000`) the **`else` (2016+) branch** runs every time; the pre-2016 branch is dead code on modern Maya but is kept as a teaching reference for the API churn.

**`deform()` flow (verified):**
1. Read your own attribute: `data.inputValue(self.push).asFloat()` → `push`.
2. Read the inherited envelope: `data.inputValue(envelopeAttr).asFloat()` → `envelope` (a global 0–1 multiplier, default `1.0`).
3. Fetch the input mesh: `self.getInputMesh(data, geometryIndex)` — walks `inputAttr`'s array to element `geometryIndex`, then `.child(inputGeomAttr).asMesh()`.
4. Read **per-vertex normals** via `meshFn.getVertexNormals(True, normals, om.MSpace.kTransform)` — `True` = angle-weighted, `kTransform` = local object space.
5. **Loop over every vertex:** `index = geoIterator.index()` → `normal = om.MVector(normals[index])` → `position = geoIterator.position()` → `offset = normal * push * envelope` → multiply by the **painted weight** `self.weightValue(data, geometryIndex, index)` → `geoIterator.setPosition(position + offset)` → **`geoIterator.next()`** (forget this and you loop forever).
6. The visible effect: every vertex slides along its surface normal by `push * envelope * weight`. Positive `push` balloons the mesh outward; negative `push` sucks it inward. Where weights are painted to `0`, vertices don't move at all.

### 3. API 1.0 vs API 2.0 — the side-by-side this folder exists to teach

| Concern | `minMaxNode` (API 2.0) | `pushDeformer` (API 1.0) |
|---|---|---|
| Import | `from maya.api import OpenMaya as om` | `from maya import OpenMaya as om` + `from maya import OpenMayaMPx as ompx` |
| `maya_useNewAPI()` | **present** (sentinel) | **absent** |
| Base class | `om.MPxNode` | `ompx.MPxDeformerNode` |
| Creator | `return cls()` | `return ompx.asMPxPtr(cls())` |
| Attribute placeholder | `inputA = None` | `push = om.MObject()` |
| Attribute configuration | properties: `nAttr.storable = True` | methods: `nAttr.setStorable(True)` |
| Core method | `compute(self, plug, data)` | `deform(self, data, geoIterator, matrix, geometryIndex)` |
| `registerNode` args | 4 | 5 (+ `kDeformerNode` classification) |

The function-set pattern (`MFnNumericAttribute().create(...)`) and the `attributeAffects` / `setClean` discipline are **shared** between the two APIs — which is the real lesson: the *concepts* are identical; only the *plumbing* differs.

## How to Create the Test Maya Scene

`minMaxNode` and `pushDeformer` need different scenes.

### Scene A — for `minMaxNode` (a node with no geometry of its own)

A `minMax` node is just a math box; it has no shape and shows nothing in the viewport by itself. The minimum scene is:

1. `cmds.file(new=True, force=True)` — a fresh scene.
2. That's it for *geometry*. The interesting setup is **wiring** (see *How to Run*). Optionally create a visible **driven object** so the output is observable:
   - `cmds.polyCube()` → a cube you will later drive with the node's output (e.g. connect `output → translateY`).
   - `cmds.spaceLocator()` → a locator whose `translateY` you connect `output` to.

| Entry point | Scene / DG state it expects |
|---|---|
| `createNode minMax` then set attrs by hand | A fresh scene; nothing else required. |
| `createNode minMax` then `connectAttr` to drive a visible object | One driven transform (cube / locator) to receive `output`. |

### Scene B — for `pushDeformer` (a mesh to deform)

A deformer needs **geometry to act on**. The minimum scene is one mesh:

1. `cmds.file(new=True, force=True)` — a fresh scene.
2. `cmds.polySphere(radius=1)` → `pSphere1`. A sphere is ideal because its outward normals make the "balloon" effect obvious. (A `polyCube` also works — its normals are axis-aligned, so it grows into a rounded box.)
3. Optionally duplicate the sphere (`cmds.duplicate`) and hide it, so you can compare deformed vs. original.

| Entry point | Scene / DG state it expects |
|---|---|
| `cmds.deformer(type='push')` | One or more selected mesh shapes; the deformer is applied to the **current selection**. |
| Paint weights | The deformer already applied to a mesh (so its `weights` multi-element exists). |

## How to Run the Functions

> Both files are **definitions-only plugins** — there is no `__main__`, no test call. You never `import`-and-call them; you `loadPlugin` them, then drive them through `cmds`.

### Run A — load and exercise `minMaxNode`

Paste into the Script Editor → Python tab (replace `/abs/path/` with your real path):

```python
import maya.cmds as cmds
cmds.file(new=True, force=True)

PLUG = '/abs/path/Nodes/minMaxNode_2027.py'
loaded = cmds.loadPlugin(PLUG)            # returns the registered plugin name -> ['minMaxNode_2027']
print('plugin name:', loaded)             # Maya assigns the FILENAME STEM, NOT the node type

# Instantiate the node. The NODE TYPE is 'minMax' (kNodeName), independent of the filename.
node = cmds.createNode('minMax')          # -> 'minMax1'
print(cmds.nodeType(node))                # -> 'minMax'

# Drive the three inputs
cmds.setAttr(node + '.inputA', 3.0)
cmds.setAttr(node + '.inputB', 7.0)
cmds.setAttr(node + '.mode',   0)         # 0 = min

# Read the output (compute fires on demand)
print(cmds.getAttr(node + '.output'))     # -> 3.0   (min(3,7))

cmds.setAttr(node + '.mode', 1)           # 1 = max
print(cmds.getAttr(node + '.output'))     # -> 7.0   (max(3,7))
```

**Expected Script Editor output:** `minMax`, then `3.0`, then `7.0`. *(The `getAttr` calls are what trigger `compute` — without them the output plug may never be requested and you would see nothing.)*

To make the output **visible in the viewport**, wire it to a driven object:

```python
cube = cmds.polyCube()[0]
cmds.connectAttr(node + '.output', cube + '.translateY')
# Now scrubbing inputA/inputB/mode moves the cube up/down live in the viewport
```

You can also inspect the node visually: open **Windows → Node Editor**, tab-drag `minMax1` in, and you will see all four attributes — `inputA`/`inputB`/`mode` as inputs on the left and `output` on the right. Note the asymmetry the code builds on purpose: only `inputA` and `inputB` are `keyable=True`, so **only those two show in the Channel Box**; `mode` and `output` are merely `storable`, so they are visible/connectable in the Node Editor but do **not** appear in the Channel Box by default. Set `mode` through `setAttr` (as above) or by connecting another node's output into it — flipping it then recomputes `output` live.

### Run B — load and exercise `pushDeformer`

```python
import maya.cmds as cmds
cmds.file(new=True, force=True)

PLUG = '/abs/path/Nodes/pushDeformer_2027.py'
loaded = cmds.loadPlugin(PLUG)            # -> ['pushDeformer_2027'] (filename stem)

cmds.polySphere(radius=1)                 # -> pSphere1, selected
deformer = cmds.deformer(type='push')[0]  # applies to the selected mesh (type = kNodeName 'push')
print(deformer)                           # the pushDeformer node name

cmds.setAttr(deformer + '.push', 1.0)     # push each vertex 1 unit along its normal
```

**Expected viewport result:** the sphere **balloons outward** by roughly one unit of radius along every vertex normal — it visibly grows into a larger sphere. *(Exact visual growth depends on the mesh's scale; cannot verify the precise viewport appearance without Maya running.)*

Now exercise the rest of the deformer's knobs:

```python
# The inherited envelope halves the whole effect (0..1 global multiplier)
cmds.setAttr(deformer + '.envelope', 0.5) # sphere now grows by ~0.5 instead of ~1.0
cmds.setAttr(deformer + '.envelope', 0.0) # effect off (sphere returns to original size)

# Negative push sucks vertices inward
cmds.setAttr(deformer + '.push', -0.5)
cmds.setAttr(deformer + '.envelope', 1.0)
```

To use **painted weights** (the `makePaintable` + `weightValue` path): with the mesh selected, choose **Modify → Paint Attributes Tool**, set the tool to paint the `push` weights, paint part of the sphere white and leave part black, then set `push=1`/`envelope=1`. Only the white-painted vertices move; black-painted vertices stay put — producing a localized bulge. *(Paint-weights UI behavior cannot be verified without Maya running.)*

### Run C — one-shot paste for both nodes

```python
import maya.cmds as cmds
cmds.file(new=True, force=True)

P = '/abs/path/Nodes'
names = []
for f in ('minMaxNode_2027.py', 'pushDeformer_2027.py'):
    names += cmds.loadPlugin('/'.join([P, f]))   # capture each registered plugin name
print('plugins:', names)                          # e.g. ['minMaxNode_2027', 'pushDeformer_2027']

# minMax demo
n = cmds.createNode('minMax')
cmds.setAttr(n + '.inputA', 3.0); cmds.setAttr(n + '.inputB', 7.0)
print('min ->', cmds.getAttr(n + '.output'))   # 3.0
cmds.setAttr(n + '.mode', 1)
print('max ->', cmds.getAttr(n + '.output'))   # 7.0

# push demo
cmds.polySphere(radius=1)
d = cmds.deformer(type='push')[0]
cmds.setAttr(d + '.push', 1.0)
print('push applied:', d)
```

To **unload** a plugin afterwards, use the name `loadPlugin` returned (the filename stem, e.g. `minMaxNode_2027`) — not the node type `minMax`. Capture it as above and call `cmds.unloadPlugin(name, force=True)`.

> **Two distinct names, easy to confuse.** The **plugin name** (for `loadPlugin`/`unloadPlugin`) is the *filename stem* — `minMaxNode_2027`. The **node type** (for `createNode`/`nodeType`) is the *class's `kNodeName`* — `minMax`. They are independent: loading `minMaxNode_2027.py` gives you a plugin called `minMaxNode_2027` that registers a node type called `minMax`. (The same filename-stem-vs-registered-name split appears in the `Commands/` folder, where loading `helloWorldCmd_2027.py` registers the command `hello`.) ⚠️ The exact stem Maya assigns (whether it keeps the `_2027`) was not verified without Maya running — capture it from `loadPlugin`'s return to be safe.
>
> **Why `unloadPlugin(..., force=True)`?** A loaded plugin whose node type is instantiated in the scene cannot be cleanly unloaded; `force` detaches it. On modern Maya you must also delete the node instances before a non-forced unload will succeed — `force` is the pragmatic shortcut during development (the same pattern used by `distributeCmd` in the `Commands/` folder).

## Question and Answer

**Q1. Why is `pushDeformer` written in API 1.0 when everything else uses API 2.0?**
Because **OpenMaya API 2.0 cannot create deformer nodes in Python** — there is no API-2.0 equivalent of `MPxDeformerNode.deform()`. (The file's own header says so: *"OpenMaya 2 doesn't support creating deformers, therefore we must use the old OpenMaya."*) Deformers and a few other geometry-filter node types are the remaining legitimate uses of API 1.0. This is also why `pushDeformer` has **no `maya_useNewAPI()`** — that sentinel marks a plugin as API 2.0, which this one is not.

**Q2. `minMaxNode` works but the output never updates when I change an input. What did I forget?**
Almost certainly an `attributeAffects(input, output)` line. `compute()` is **never called unless** an affect-relationship declares that the dirty input should dirty the output. Here all three are wired (`inputA`, `inputB`, and `mode`). A learner who copies the node but only adds `attributeAffects(inputA, output)` / `attributeAffects(inputB, output)` will find that **flipping the `mode` dropdown does nothing** — `mode` was never declared to affect `output`.

**Q3. I removed `data.setClean(plug)` and now Maya freezes. Why?**
Without `setClean`, the output plug stays **dirty** after `compute`, so Maya concludes the value is still invalid and requests it again — calling `compute` again — forever. `setClean(plug)` is the "I have written the answer; it is now fresh" signal that breaks the loop. This is the single most common MPxNode bug.

**Q4. Why does `compute` start with `if plug != MinMaxNode.output: return`?**
Maya invokes `compute(self, plug, data)` for **every** plug on the node that has been requested downstream — including internal/array plugs you didn't author. The guard says "only do work when the plug being asked for is the one I actually produce." Without it you would recompute (and write) the output for unrelated requests, wasting work and potentially corrupting data. (The animated-cube node in `py1AnimCubeNode/` uses the identical guard pattern.)

**Q5. The `if mode:` line is confusing — what values does `mode` take, and why use truthiness?**
`mode` is an enum with two fields: `('min', 0)` and `('max', 1)`. `asInt()` returns the integer index, so `mode` is `0` or `1`. `if mode:` is shorthand for `if mode == 1:` — truthy means "max," falsy means "min." It works only because the indices happen to be `0`/`1`; if you added a third field `('average', 2)` the `if mode:` idiom would treat **both** max and average as truthy, which is wrong. For enums with more than two states, branch on the explicit value.

**Q6. Why does `minMaxNode`'s `creator()` return plain `cls()` while `pushDeformer`'s wraps it in `ompx.asMPxPtr(cls())`?**
It is an ownership difference between the two APIs. In **API 1.0**, the Python object you return is just a wrapper; Maya needs to take C++ ownership of the underlying node, and `asMPxPtr` performs that hand-off (otherwise the Python object can be garbage-collected while Maya still holds a dangling reference). In **API 2.0**, ownership is managed automatically, so `cls()` is sufficient and `asMPxPtr` is not used. The same split shows up in `minMaxNode` using `inputA = None` placeholders while `pushDeformer` uses `push = om.MObject()`.

**Q7. What is `ompx.cvar.MPxGeometryFilter_input`, and why the version check?**
A deformer node **inherits** four attributes (`inputGeometry`, `outputGeometry`, `envelope`, and the input array) from its C++ base class. In Python you reach those inherited attributes through the SWIG `cvar` object. In Maya 2016 the base class was renamed `MPxDeformerNode` → `MPxGeometryFilter`, so the `cvar` member names changed too. The `if kApiVersion < 201600` branch picks the right names; on Maya 2027 the `else` branch always runs. (On modern Maya the pre-2016 branch is dead code — kept only as a teaching note about API churn.)

**Q8. What do `envelope` and the painted `weights` actually do in `pushDeformer`?**
The final per-vertex offset is `normal * push * envelope * weight`. `push` is **your** attribute (how hard to push). `envelope` is an **inherited** 0–1 global multiplier every deformer has (a master fader; `0` turns the deformer off entirely). `weight` is the **per-vertex painted value** from `self.weightValue(...)` — `makePaintable` exposed it so you can sculpt *where* the effect applies. Set `envelope=0` and nothing moves no matter how large `push` is.

**Q9. What happens if I forget `geoIterator.next()` at the bottom of the `while` loop?**
An **infinite loop** inside `deform()` — `isDone()` never becomes true because the iterator never advances, so the same first vertex is processed forever and Maya hangs. The `compute`-without-`setClean` bug (Q3) and the iterator-without-`next` bug are the two classic "Maya freezes" mistakes, one per node family.

**Q10. Why does `registerNode` take five arguments for `pushDeformer` but only four for `minMaxNode`?**
The fifth argument, `ompx.MPxNode.kDeformerNode`, is a **classification** that tells Maya what *kind* of node this is. Marking it a deformer is what lets `cmds.deformer(type='push')` find it, what makes it show up in the Deform menus, and what enables the weight-painting machinery. `minMaxNode` passes no classification, so it is a plain utility node — which is exactly what you want for a math box.

**Q11. Can I have several `minMax` (or `push`) nodes in one scene?**
Yes — `createNode` can make any number of instances of the registered **node type**; each is an independent node (`minMax1`, `minMax2`, …) with its own attribute values, exactly like having many `multiplyDivide` nodes. What must be **unique** is the *type ID* (`MTypeId`) registered by the plugin across the whole Maya session — which is why two different plugins must never claim the same ID (see Prerequisites). Only **one Python node evaluates at a time**, however (the README bottleneck caveat), so a graph full of Python nodes serializes where a graph of C++ nodes would parallelize.

## Advanced Directions

1. **Add more operations to `minMaxNode` (a multi-mode math node).**
   Extend the `mode` enum with `add`/`subtract`/`multiply`/`divide`/`average` fields and dispatch in `compute()` on the explicit integer (replacing the two-state `if mode:`). Requires: an `eAttr.addField(...)` per new mode, a dispatch table in `compute`, and — critically — `attributeAffects(mode, output)` already present so the new modes recompute. Generalizes into a full "utility math" node family (`abs`, `clamp`, `blend`, `lerp`).

2. **Turn `pushDeformer` into a `softSelect`-aware or falloff-based deformer.**
   Currently the offset is strictly `normal * push * envelope * weight`. Add a **falloff** attribute and a center point so the push decays with distance from the center, or read Maya's soft-selection (`cmds.softSelect(q=True, ...)`) so the deformer respects the artist's current soft-selection. Requires: new numeric/`MFnMatrixAttribute` inputs, a `MFnMesh.getClosestPoint`/distance computation inside `deform`, and the corresponding `attributeAffects` wiring.

3. **Wrap each node in an undoable, AE-friendly `MPxCommand`.**
   Production nodes are usually created through a command that names them sensibly, wires them into the graph, supports undo, and exposes a custom Attribute-Editor template (as `Scene/characterRoot` does with `AEcharacterRootTemplate.mel`). Requires: an `MPxCommand` `makeMinMaxCmd` with `isUndoable`/`redoIt`/`undoIt` (the contract from `Commands/distributeCmd`), an `MSyntax` for flags, and an `AEminMaxTemplate.mel` file registered in `initializePlugin`.

4. **Add a `normalize`/`clamp`/range remap output and a second output plug.**
   Demonstrate a node with **multiple outputs** (e.g. `output` plus `outputNormalized`) computed from the same inputs, each guarded separately in `compute()` (`if plug == output: … elif plug == outputNormalized: …`) and each with its own `attributeAffects` lines. This is the template for any multi-output utility node and teaches that one node can serve several downstream consumers from shared inputs.

5. **Port `minMaxNode` from API 2.0 to C++ (the `Compiling/minMaxPlugin` path).**
   The folder README's whole point is that Python nodes are for prototyping; for production you recompile as C++. The follow-on `Compiling/minMaxPlugin` demo does exactly this. Conceptually requires: a `CMakeLists.txt`, the Maya devkit headers, the same `compute`/`initialize`/`registerNode` logic in C++, and a **reserved Autodesk ID** (not a dev-range `0x01010`) so the compiled node is safe to distribute. Doing this end-to-end (Python prototype → verify behavior → C++ port → benchmark the parallel-eval speedup) is the curriculum's capstone performance lesson.

6. **Add validation, painting-time feedback, and a per-component mode to `pushDeformer`.**
   Harden `deform()`: skip degenerate/zero-length normals to avoid blow-ups, add a `direction` enum (`normal` vs. a custom vector attribute) so artists can push along an arbitrary axis, and emit a `MUiMessage`/profiler marker so heavy deformations are diagnosable. Requires: an `MFnEnumAttribute` for direction, an `MFnVectorArrayData` custom-direction attribute, `om.MVector.normalize()` guards, and `MProfiler` category registration (the API from `profilerDump/`).
