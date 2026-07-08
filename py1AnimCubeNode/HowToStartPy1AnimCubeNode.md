# HowToStart — py1AnimCubeNode

> A **plug-in** (not a script) that registers a custom Maya **dependency-graph
> node**, `spAnimCube`, which generates a cube mesh whose size is driven by the
> current time. It is the canonical reference for the `MPxNode` + `compute()`
> pattern — generating procedural geometry inside a DG node and handing it back
> to Maya through an `outputMesh` attribute.

This is the curriculum's **first `MPxNode` (dependency-node) plug-in**. Where
`mathTableControl` registered a *command* you invoke (`spMathTableControl …`),
this registers a *node type* you instantiate with `createNode("spAnimCube")` and
wire into the scene like any built-in node. It is never `import`-ed and called;
it is *loaded* by Maya's plug-in manager and then behaves like a native
generator node.

---

## Files

| File | Role |
|------|------|
| `py1AnimCubeNode.py` | The plugin source. Defines the `animCube(MPxNode)` class, its `time`/`outputMesh` attributes, the `compute()`/`createMesh()` geometry builder, the `nodeCreator`/`nodeInitializer` factories, and the `initializePlugin`/`uninitializePlugin` lifecycle hooks. The wiring recipe (transform + mesh + connections) is documented as a comment block at the top of the file. |

> **`_2027` convention note:** there is **no `_2027` sibling** for this demo.
> `py1AnimCubeNode.py` is the verbatim Autodesk API 1.0 original (its only
> dependency is `maya.OpenMaya` + `maya.OpenMayaMPx`, unchanged across modern
> Maya versions). The guide targets `py1AnimCubeNode.py` directly.

## Prerequisites

Before this demo you should already be comfortable with:

- Maya **command plug-ins** and the `loadPlugin` / `unloadPlugin` workflow — see
  `mathTableControl/HowToStartMathTableControl.md`. This demo reuses that
  lifecycle but adds the dependency-graph layer on top.
- What a **dependency-graph (DG) node** is, and what **dirty / clean / evaluate**
  mean. (Maya docs → *Dependency Graph Overview*, *DG Evaluation*.)
- **API 1.0** basics (`maya.OpenMaya`, `MObject`, `MFn*` function sets) — see
  `../manipulatorMath/` and `../cameraMessageCmd/`.
- How attributes are created with `MFnUnitAttribute` / `MFnTypedAttribute`.

> ⚠️ If DG evaluation or `MPx` proxy classes are new, do `mathTableControl` and
> `manipulatorMath` first. Generating mesh inside `compute()` is a step up.

## What the code actually does

The file has five logical pieces plus the standard plug-in entry points.

### Part 1 — the node class and its attributes

```python
class animCube(OpenMayaMPx.MPxNode):
    time = OpenMaya.MObject()        # class-level placeholder
    outputMesh = OpenMaya.MObject()  # class-level placeholder
```

Attributes are declared as **class-level `MObject()` placeholders**. They are
filled in (turned into real attribute objects) by `nodeInitializer()` when the
plugin loads. This class-level pattern is required because Maya attaches
attributes to the node *type*, not to individual instances — every `spAnimCube`
node shares the same `time` / `outputMesh` attribute definitions.

### Part 2 — `createMesh(self, tempTime, outData)`: the geometry builder

```python
frame = int(tempTime.asUnits(OpenMaya.MTime.kFilm))   # frame number at 24 fps
if frame is 0:                                         # ⚠ Python-2 'is' — see Q&A
    frame = 1
cubeSize = 0.5 * float(frame % 10)
```

- `tempTime.asUnits(MTime.kFilm)` converts Maya's time object to a floating frame
  number assuming **24 fps film** timing; `int()` truncates to an integer frame.
- `cubeSize = 0.5 * (frame % 10)` makes the cube grow each frame and reset every
  10 frames — the "pulse". See the verified table below.

It then builds **8 vertices** (`MFloatPoint` × 8) for the cube corners, each
scaled by `cubeSize`, and assembles them into a mesh with `MFnMesh.create(...)`,
passing `outData` (an `MFnMeshData` container) as the last argument so the new
mesh is attached to the output data block rather than floating free.

### Part 3 — `compute(self, plug, data)`: the DG evaluation entry point

```python
def compute(self, plug, data):
    if plug == animCube.outputMesh:
        timeData = data.inputValue(animCube.time)
        tempTime = timeData.asTime()
        outputHandle = data.outputValue(animCube.outputMesh)
        dataCreator = OpenMaya.MFnMeshData()
        newOutputData = dataCreator.create()
        self.createMesh(tempTime, newOutputData)
        outputHandle.setMObject(newOutputData)
        data.setClean(plug)                 # ← never forget this
    else:
        return OpenMaya.kUnknownParameter
```

The four-step contract every `compute()` follows:

1. **Check which plug asked for the value** (`if plug == animCube.outputMesh`).
   If it is not one you handle, return `kUnknownParameter` so Maya passes the
   request up the inheritance chain.
2. **Read inputs** via `data.inputValue(attr)`.
3. **Build the output** into a fresh data container (`MFnMeshData.create()`).
4. **Write the output and mark it clean** — `outputHandle.setMObject(...)`
   followed by `data.setClean(plug)`. **If you forget `setClean`, Maya calls
   `compute()` again forever** — the classic beginner bug.

### Part 4 — `nodeCreator()` and `nodeInitializer()`

```python
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( animCube() )    # hand Maya a raw pointer

def nodeInitializer():
    unitAttr   = OpenMaya.MFnUnitAttribute()
    typedAttr  = OpenMaya.MFnTypedAttribute()
    animCube.time       = unitAttr.create("time", "tm",  OpenMaya.MFnUnitAttribute.kTime, 0.0)
    animCube.outputMesh = typedAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)
    animCube.addAttribute(animCube.time)
    animCube.addAttribute(animCube.outputMesh)
    animCube.attributeAffects(animCube.time, animCube.outputMesh)   # ← critical
```

- `asMPxPtr` hands the Python object to Maya as a raw pointer — Maya takes
  ownership, same idiom as `mathTableControl`.
- **`time`** is a `MFnUnitAttribute` of type `kTime`; **`outputMesh`** is a
  `MFnTypedAttribute` of type `kMesh`.
- **`attributeAffects(time, outputMesh)`** is critical: it declares the
  dependency that drives evaluation. Without it, `compute()` is never triggered
  when time changes — Maya does not know the output depends on the input.

### Part 5 — `initializePlugin` / `uninitializePlugin`

```python
kPluginNodeName = "spAnimCube"
kPluginNodeId   = OpenMaya.MTypeId(0x8700B)

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    mplugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    mplugin.deregisterNode(kPluginNodeId)
```

Standard `registerNode` / `deregisterNode` boilerplate. `0x8700B` is reserved by
Autodesk for this example — see the Q&A on node IDs.

### The verified pulse table (re-derive it yourself)

`cubeSize = 0.5 * (frame % 10)`. Hand-derived:

| Frame | `frame % 10` | `cubeSize` | Visible cube half-extent |
|------:|-------------:|-----------:|--------------------------|
| 1     | 1            | 0.5        | 1.0 units wide |
| 2     | 2            | 1.0        | 2.0 |
| 3     | 3            | 1.5        | 3.0 |
| 4     | 4            | 2.0        | 4.0 |
| 5     | 5            | 2.5        | 5.0 |
| 6     | 6            | 3.0        | 6.0 |
| 7     | 7            | 3.5        | 7.0 |
| 8     | 8            | 4.0        | 8.0 |
| 9     | 9            | 4.5        | 9.0 (largest) |
| **10**| **0**        | **0.0**    | **cube collapses to a point — it vanishes** |
| 11    | 1            | 0.5        | 1.0 again |
| 12    | 2            | 1.0        | 2.0 |

> ⚠️ **Verified gotcha the README glosses over.** The cube does **not** "snap
> back to 0.5" every 10 frames — it collapses to **size 0** at frames 10, 20, 30,
> … (all 8 vertices land on the origin), then resumes at 0.5 on frame 11. While
> playing, you will see the cube **disappear for one frame every ten frames**.
> The README's "snapping back to 0.5" conflates frame 10 (size 0) with frame 1
> (size 0.5). This is real, visible behaviour — not a bug to fix, but a gotcha to
> understand (see Q&A).

---

## How to Create the Test Maya Scene

> ⚠️ **Cannot be fully verified without Maya running** — the wiring below is the
> exact recipe from the comment block at the top of `py1AnimCubeNode.py`
> (lines 39–45). It was read directly from the source, not inferred.

This demo needs a tiny hand-built network: a visible mesh shape, the `spAnimCube`
node, and two connections. **You do not create a `polyCube`** — the custom node
*generates* the mesh procedurally, so the shape starts empty and is filled by the
node's `compute()`.

**Step 1 — Load the plugin first** (see *How to Run* Step A below). The network
cannot be built until `spAnimCube` is a known node type.

**Step 2 — Build the network in the Script Editor (Python tab):**

```python
import maya.cmds as cmds

# The visible cube: a transform with an empty mesh shape underneath it
cmds.createNode("transform", name="animCube1")
cmds.createNode("mesh", name="animCubeShape1", parent="animCube1")
cmds.sets("animCubeShape1", add="initialShadingGroup")   # so it shades grey, not blank

# The custom generator node
cmds.createNode("spAnimCube", name="animCubeNode1")

# Wire scene time -> node, and node mesh out -> the shape's inMesh
cmds.connectAttr("time1.outTime", "animCubeNode1.time")
cmds.connectAttr("animCubeNode1.outputMesh", "animCubeShape1.inMesh")
```

**Step 3 — Expected Outliner / viewport state after wiring:**

```
animCube1           (transform — the cube's pivot/transform)
  └─ animCubeShape1 (mesh — driven by animCubeNode1.outputMesh)
animCubeNode1       (spAnimCube — the generator node; no transform)
```

- The viewport should show a cube whose size depends on the **current frame**.
  At frame 1 it is small (1.0 units); scrub to frame 9 and it is large (9.0).
- Open the **Node Editor** or **Hypergraph** and you will see
  `time1.outTime → animCubeNode1.time` and
  `animCubeNode1.outputMesh → animCubeShape1.inMesh`.

> **Why `time1`?** `time1` is Maya's built-in global clock node; its `outTime`
> attribute always reflects the current playhead. Connecting it to the node's
> `time` input is what makes the node react when you scrub or play.

> **Why an empty `mesh` shape rather than a `polyCube`?** The node *writes* its
> generated geometry onto `outputMesh`, which feeds `inMesh`. If you started from
> a `polyCube`, its construction history would be replaced the moment you connect
> — so you may as well start from an empty shape.

---

## How to Run the Functions

A plug-in node is *exercised*, not *called*. The workflow is: **load → wire →
scrub/play → unload.**

### Step A — Load the plugin

Either put `py1AnimCubeNode.py` on `MAYA_PLUGIN_PATH` and use
**Windows → Settings/Preferences → Plug-in Manager** (check *Loaded*), or in the
Script Editor (Python tab):

```python
import maya.cmds as cmds
cmds.loadPlugin(r'/abs/path/py1AnimCubeNode/py1AnimCubeNode.py')
```

- **Expected result:** no error. Confirm the node type is now registered:
  ```python
  cmds.nodeType("spAnimCube", isTypeName=True)   # -> True
  ```
- **If load fails** with a node-id conflict, `0x8700B` is already registered by
  another loaded copy of the example — unload the other one first
  (`cmds.unloadPlugin(...)`).

> ⚠️ **Filename vs. node name.** The *file* is `py1AnimCubeNode.py`; the *node*
> it registers is `spAnimCube`. You `loadPlugin` the **file** but `createNode`
> the **node type**. Two different names, easy to confuse (the same mismatch
> recurred in `mathTableControl`).

### Step B — Build the network (Step 2 above)

Run the six-line wiring script. Expected result: a cube appears in the viewport,
sized for the current frame.

### Step C — Drive it: scrub / play the timeline

- Drag the **time slider** to frame 1, 2, … 12 and watch the cube grow, then
  **vanish at frame 10**, then reappear small at frame 11 (see the pulse table).
- Press **Play**. The cube pulses: growing larger each frame, disappearing for a
  single frame every ten frames, then resuming.

A one-shot that scrubs a few frames and prints the resulting bounding-box size
(so you can verify the pulse without watching the viewport):

```python
import maya.cmds as cmds
for f in [1, 5, 9, 10, 11]:
    cmds.currentTime(f)
    bb = cmds.exactWorldBoundingBox("animCubeShape1")   # [xmin,ymin,zmin,xmax,ymax,zmax]
    w = bb[3]-bb[0]
    print(f"frame {f:2d}: cube width = {w:.2f}")
# Expected: 1.00, 5.00, 9.00, 0.00, 1.00
```

> The `0.00` at frame 10 is the verified degenerate case — the mesh exists but
> all vertices sit on the origin, so the bounding box has zero width.

### Step D — Unload the plugin when done

```python
cmds.unloadPlugin('py1AnimCubeNode')   # pass the plugin (base) name, NOT the node name
```

- Maya will refuse to unload if any `spAnimCube` node still exists in the scene.
  Delete the node first (`cmds.delete("animCubeNode1")`) or it errors with a
  "node type in use" message.
- After unload, `cmds.nodeType("spAnimCube", isTypeName=True)` returns `False`.

---

## Question and Answer

**Q1. Why is this `loadPlugin`-ed and not `import`-ed?**
Because it is a **plug-in**, not a library module. Its entry point is
`initializePlugin(mobject)`, which Maya calls automatically when the plug-in
loads; that function registers the `spAnimCube` node type with Maya. After that,
the node behaves like a built-in — you create instances with `createNode`, not by
calling Python functions. `import py1AnimCubeNode` would run the file but
*nothing would register*, because `initializePlugin` is only ever called by
Maya's plug-in loader, never by a plain `import`.

**Q2. How is an `MPxNode` different from the `MPxCommand` in `mathTableControl`?**
`mathTableControl` registered a **command** — something you *invoke* once
(`cmds.spMathTableControl(...)`) and it runs to completion. `py1AnimCubeNode`
registers a **dependency-graph node** — something that *lives in the scene*,
holds attributes, and is **evaluated on demand by the DG** whenever its output is
needed. A command is "do this now"; a node is "be this, and recompute yourself
when your inputs change." The DG/node world is the foundation of everything
procedural in Maya (deformers, constraints, rigs).

**Q3. What actually triggers `compute()` to run?**
Two things together: (a) something downstream asks for `outputMesh` (here, the
connected mesh shape needs to draw), AND (b) `outputMesh` is **dirty**. Maya
marks `outputMesh` dirty whenever `time` changes *because* of the
`attributeAffects(time, outputMesh)` declaration. So the chain is: time changes →
Maya dirties `outputMesh` → downstream pull → `compute()` fires. Remove the
`attributeAffects` line and changing the time does nothing — `compute()` is never
called, because Maya has no way to know the output depends on the input.

**Q4. Why do I have to connect `time1.outTime` to the node's `time`?**
The node only *reads* its `time` attribute inside `compute()`; it does not look
at the global clock itself. With no connection, `time` sits at its default
(`0.0`, from `unitAttr.create(..., 0.0)`) forever, so the cube never changes.
Connecting `time1.outTime → spAnimCube.time` feeds the live playhead into the
attribute, which dirties `outputMesh` (via Q3) and drives the pulse. You could
instead connect *any* time/animation source — a custom anim curve, an expression,
another node's output — the node does not care that it is `time1` specifically.

**Q5. Why does the cube DISAPPEAR at frame 10, 20, 30…?**
Because `cubeSize = 0.5 * (frame % 10)`, and `10 % 10 == 0`, giving
`cubeSize = 0.0`. All eight vertices are computed as `MFloatPoint(±0, ±0, ±0)`,
so they all collapse to the origin — the mesh still exists and is topologically
valid (6 faces, 8 verts) but has zero volume, so the viewport shows nothing for
that single frame. The demo's README describes this as "snapping back to 0.5",
which is imprecise: frame 10 is size **0**, frame 11 is size **0.5**. It is not a
bug — it is the natural result of the modulo — but it is the first thing a
learner notices ("why does my cube flicker off every ten frames?").

**Q6. The README's face table says face 3 is "back / -Z" and face 4 is "left /
-X" — is that right?**
**No — those two labels are swapped.** The *vertex indices* in the README are
correct, but the spatial labels for faces 3 and 4 are transposed. Reading the
actual `faceConnects` from the source and checking which axis is constant across
each face's four vertices:

| Face | Vertices (from source) | Constant axis | Correct label |
|-----:|------------------------|---------------|---------------|
| 0 | `[0,1,2,3]` | all `Y=-s` | bottom (**-Y**) ✓ README |
| 1 | `[4,5,6,7]` | all `Y=+s` | top (**+Y**) ✓ README |
| 2 | `[3,2,6,5]` | all `Z=+s` | front (**+Z**) ✓ README |
| 3 | `[0,3,5,4]` | all `X=-s` | **left (-X)** — README wrongly says back/-Z |
| 4 | `[0,4,7,1]` | all `Z=-s` | **back (-Z)** — README wrongly says left/-X |
| 5 | `[1,7,6,2]` | all `X=+s` | right (**+X**) ✓ README |

The README author even left a "wait, source has 0 3 5 4" self-doubt comment but
did not resolve the transposition. If you edit the geometry (Q in Advanced
Directions), trust the **vertex indices**, not the prose labels.

**Q7. The line `if frame is 0:` looks odd — is that correct Python?**
It is **Python 2 syntax** and raises a `SyntaxWarning: "is" with 'int' literal.
Did you mean "=="?` on Maya 2027's Python 3. It happens to *work* by accident —
CPython caches small integers (−5…256) as singletons, so `int(0.0) is 0` resolves
`True` — but you must never rely on `is` for integer equality. In modern code
write `if frame == 0:`. The bundled source keeps the original line for fidelity
with the Autodesk example.

**Q8. What happens if I forget `data.setClean(plug)` at the end of `compute()`?**
Maya calls `compute()` **every evaluation, forever.** Because the output is never
marked clean, Maya assumes it is stale and re-pulls it on the next DG pass — an
infinite recompute that can hang or "spin" Maya. This is the single most common
`MPxNode` beginner bug. Symptom: Maya becomes sluggish/unresponsive the moment
the node is wired in. Always end a handled `compute()` branch with
`data.setClean(plug)`.

**Q9. Why `MTypeId(0x8700B)` specifically, and can I reuse it for my own node?**
`0x8700B` is a hex node-type ID **reserved by Autodesk for this devkit example**.
Every DG node type needs a globally-unique numeric ID so Maya can distinguish it
across files, scenes, and plug-ins. For your own published nodes you must obtain
an ID **range from Autodesk** (Maya docs → *Node IDs and User-defined Node IDs*)
and pick from your assigned range. Reusing `0x8700B` in your own plugin will
collide with this example if both are ever loaded together, causing a plug-in
load failure. It is fine to reuse it while *learning*, never while *shipping*.

**Q10. Why does `nodeCreator()` return `asMPxPtr(animCube())` instead of just
`animCube()`?**
`animCube()` creates a Python object, but Maya's C++ DG wants a raw pointer it
can own and call back into. `OpenMayaMPx.asMPxPtr(...)` hands Maya that pointer
and transfers ownership. If you returned the bare Python object, Maya could not
take ownership, the node would not register correctly, and your object would be
garbage-collected out from under Maya. This is the same `asMPxPtr` idiom used in
`mathTableControl`'s `makeControl`.

**Q11. Can I drive the cube with my own animation instead of the live playhead?**
Yes — the node reads its `time` *attribute*, not the global clock directly. Any
source that outputs a time value works. For example, keyframe the node's own
`time` attribute, or connect another node's time-typed output to it. You could
even disconnect `time1` entirely and set `animCubeNode1.time` to a fixed value to
freeze the cube at a chosen frame.

---

## Advanced Directions

1. **Smooth the pulse (sinusoid instead of sawtooth).** Replace
   `cubeSize = 0.5 * float(frame % 10)` with a sine, e.g.
   `cubeSize = 1.0 + math.sin(frame * 0.5)` (add `import math` at the top). The
   cube then breathes smoothly instead of growing-then-vanishing — and removes
   the frame-10 degeneration entirely. Requires editing only `createMesh`.

2. **Add a `sizeMultiplier` (or `speed`) input attribute.** Add a second numeric
   input (`MFnUnitAttribute.kDouble`), declare
   `attributeAffects(multiplier, outputMesh)` alongside the existing
   `time→outputMesh` relationship, and multiply `cubeSize` by it inside
   `createMesh`. New pieces: the attribute in `nodeInitializer`, the
   `attributeAffects` line, and one line in `createMesh`. Expose it via
   `unitAttr.channelBox = True` / `isKeyable` so users can tune or animate the
   pulse amplitude in the Channel Box.

3. **Change the geometry: pyramid or octahedron.** The shape is fully defined by
   the `points`, `faceCounts`, and `faceConnects` arrays in `createMesh`. A
   square pyramid = 5 vertices, 5 faces (1 quad base + 4 triangles); an
   octahedron = 6 vertices, 8 triangular faces. Rewrite those three arrays and
   update `numVertices`/`numFaces`/`numFaceConnects`. *Always verify the winding
   order visually after editing* — reversed winding gives inward normals and an
   inside-out-looking shape (the Q6 label swap is exactly the kind of trap to
   watch for).

4. **Wrap the whole network in an undo-aware `MPxCommand`.** Right now the user
   must run six lines to build the transform + shape + node + two connections. A
   companion `MPxCommand` (e.g. `cmds.spMakeAnimCube()`) would `createNode` the
   transform, shape and `spAnimCube`, do both `connectAttr`s, support undo via
   `MPxCommand.undoIt`/`redoIt`, and return the created node names — turning the
   demo into a one-click shelf tool. New classes: `makeAnimCubeCmd(MPxCommand)`
   with `doIt`/`undoIt`/`redoIt` plus `cmdCreator`, registered with
   `mplugin.registerCommand`.

5. **Per-face or per-vertex colors.** After `MFnMesh.create(...)`, use
   `MFnMesh.setFaceColors(colorArray, faceIndexArray, ...)` to assign a color per
   face (e.g. color-code by which face it is). This is the natural next step
   after generating geometry: attaching extra per-component data, and learning
   the `MFnMesh` "set" family of mutators.

6. **Port to API 2.0 (`maya.api.OpenMaya`).** Rewrite using `maya.api.OpenMaya`
   and `maya.api.OpenMayaMPx`. Most calls are nearly identical; the notable
   differences are that `compute(self, plug, data)` works the same way but
   `MPxNode` lives in `maya.api.OpenMayaMPx`, `MDataBlock`/`MDataHandle` are used
   similarly, and you no longer wrap creators with `asMPxPtr` (API 2.0 manages
   Python ownership for you). Autodesk ships an official API 2.0 sibling,
   `py2AnimCubeNode.py`, that you can diff against line-by-line — an excellent
   way to learn the API-1.0→2.0 migration on a node you already understand.

---

## Source

- **Bundled source:** `py1AnimCubeNode.py` — the `animCubeNode.py` example from
  Autodesk's static 2011 API archive, the authoritative static copy of this
  example (same `spAnimCube` node, same `MTypeId(0x8700B)`, same `time`→mesh
  contract as the 2027 docs page, which is JavaScript-rendered and not fetchable
  as clean source). See `py1AnimCubeNode/README.md` for the full provenance note.
- **Verified facts in this guide:** the cube-size pulse table and the
  frame-10/20/30 degeneration were hand-derived from `cubeSize = 0.5*(frame%10)`
  in pure Python; the face→axis mapping (and the README's face-3/4 label swap)
  was derived by checking which coordinate is constant across each face's four
  vertex indices in the source; the `if frame is 0` `SyntaxWarning` was confirmed
  under Python 3. The Maya-specific wiring/registration steps were read from the
  source and the top-of-file comment block; they require a running Maya to
  execute and are marked as such.
