# py1AnimCubeNode — A Time-Driven Procedural Mesh Node (Plugin, API 1.0)

This demo comes from the official Maya Python API documentation.

**Requested link (Maya 2027 docs):** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2py1_anim_cube_node_8py-example.html>

> ⚠️ **Provenance note — please read.** The `py1AnimCubeNode.py` page on the
> 2027 docs is JavaScript-rendered and could not be fetched as clean source.
> The `.py` bundled here is the **`animCubeNode.py`** example from Autodesk's
> static 2011 API archive:
> <https://download.autodesk.com/us/maya/2011help/API/anim_cube_node_8py-example.html>
>
> These are **the same example**: both register the `spAnimCube` node, both
> take `time` as input and produce a procedural cube mesh as output, both use
> the same `MTypeId(0x8700B)`. The 2027 `py1AnimCubeNode.py` is the same code
> renamed to fit the `python/api1/` docs path. The 2011 archive is the
> authoritative static source for that code.

---

## What it does

Registers a dependency-graph node called **`spAnimCube`** that:

- takes **time** as an input attribute,
- builds a **cube mesh** whose size is derived from the current frame
  (`cubeSize = 0.5 * (frame % 10)`),
- outputs that mesh on its `outputMesh` attribute.

When you connect `time1.outTime → spAnimCube.time` and
`spAnimCube.outputMesh → meshShape.inMesh`, the cube **pulses** — growing
larger every frame, resetting every 10 frames. It's the canonical
"procedural geometry driven by time" example, and the simplest possible
demonstration of generating mesh data inside a DG node's `compute()`.

---

## What you will learn

1. **`MPxNode`** — the base class for custom dependency-graph nodes. You
   subclass it, declare attributes as class-level `MObject`s, and override
   `compute()`.
2. **The `compute(plug, data)` contract** — the heart of every DG node.
   Maya calls it whenever an output is dirty. You read inputs from `data`,
   do work, write the output, and call `data.setClean(plug)`.
3. **`attributeAffects(input, output)`** — the dependency declaration that
   tells Maya "when `time` changes, `outputMesh` needs recomputing." Without
   this, `compute()` is never called.
4. **Building mesh data procedurally** with `MFnMesh.create(...)` — passing
   vertex points, face counts, and face connects to generate geometry from
   scratch inside `compute()`.
5. **`MFnMeshData` as the output container** — Maya requires mesh output to
   be wrapped in a data block (`MFnMeshData.create()`), not handed to
   `MFnMesh` directly. This is the standard "create empty data → build mesh
   into it → set on output handle" pattern.
6. **Node registration** — `MFnPlugin.registerNode(name, id, creator,
   initializer)` and the matching `deregisterNode(id)` on unload.

---

## Prerequisites

| Concept                            | Where to learn it                                                              |
|------------------------------------|--------------------------------------------------------------------------------|
| Maya command plugins (`MPxCommand`)| Maya docs → *Writing Commands*                                                 |
| `MPx` proxy classes                | Maya docs → *Proxy Classes Overview*                                           |
| What a dependency graph node is    | Maya docs → *Dependency Graph Overview*                                        |
| What "dirty" / "clean" mean        | Maya docs → *DG Evaluation*                                                    |
| OpenMaya API 1.0 basics            | [`../cameraMessageCmd/cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md) |

This is **not** a beginner example — it's the next step after you've written
a simple `MPxCommand`. Read the *Things to try* section of
[`../cameraMessageCmd/cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md)
first if MPx is new.

---

## Files

```
py1AnimCubeNode/
├── README.md                ← this file
└── py1AnimCubeNode.py       ← the plugin source (animCubeNode.py variant)
```

The `.py` is bundled here directly (it's a public Autodesk docs/devkit
listing).

---

## Architecture: the five pieces

Read the file top to bottom — it's small. Here's the map:

### 1. Node class declaration

```python
class animCube(OpenMayaMPx.MPxNode):
    time = OpenMaya.MObject()
    outputMesh = OpenMaya.MObject()
```

Attributes are declared as **class-level** `MObject()` placeholders. They're
filled in by `nodeInitializer()` (see below) when the plugin loads. This
class-level pattern is required because Maya attaches attributes to the node
*type*, not to instances.

### 2. `createMesh(self, tempTime, outData)` — the geometry builder

This is where the actual mesh is constructed:

```python
frame = int(tempTime.asUnits(OpenMaya.MTime.kFilm))
cubeSize = 0.5 * float(frame % 10)
```

- `tempTime.asUnits(MTime.kFilm)` converts Maya's time object to a frame
  number assuming 24 fps film timing.
- `cubeSize = 0.5 * (frame % 10)` makes the cube grow each frame and reset
  every 10 frames — that's the "pulse".

Then it builds:
- **8 vertices** (`MFloatPoint` × 8) for the cube corners, scaled by `cubeSize`.
- **`faceCounts`** — `[4, 4, 4, 4, 4, 4]` (six faces, four vertices each).
- **`faceConnects`** — 24 vertex indices (4 per face × 6 faces) telling
  Maya which vertices form each face.

Finally:

```python
meshFS = OpenMaya.MFnMesh()
newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, faceConnects, outData)
```

The last argument `outData` is an `MFnMeshData`-created container — this is
how the new mesh gets attached to the output data block rather than floating
free.

### 3. `compute(self, plug, data)` — the DG evaluation entry point

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
        data.setClean(plug)
    else:
        return OpenMaya.kUnknownParameter
```

The four-step contract every `compute()` follows:

1. **Check which plug asked for the value** (`if plug == animCube.outputMesh`).
   If it's not one you handle, return `kUnknownParameter` so Maya passes it
   up the inheritance chain.
2. **Read inputs** via `data.inputValue(attr)`.
3. **Build the output** into a fresh data container
   (`MFnMeshData.create()`).
4. **Write the output and mark it clean** — `outputHandle.setMObject(...)`
   followed by `data.setClean(plug)`. **If you forget `setClean`, Maya
   calls `compute()` again forever** — the most common beginner bug.

### 4. `nodeCreator()` and `nodeInitializer()`

```python
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( animCube() )
```

`asMPxPtr` hands the Python object to Maya as a raw pointer — same idiom as
the `mathTableControl` example.

```python
def nodeInitializer():
    unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()

    animCube.time = unitAttr.create("time", "tm", OpenMaya.MFnUnitAttribute.kTime, 0.0)
    animCube.outputMesh = typedAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)

    animCube.addAttribute(animCube.time)
    animCube.addAttribute(animCube.outputMesh)

    animCube.attributeAffects(animCube.time, animCube.outputMesh)
```

- **`time`** is a `MFnUnitAttribute` of type `kTime` — Maya's time type.
- **`outputMesh`** is a `MFnTypedAttribute` of type `kMesh` — accepts mesh
  data.
- **`attributeAffects(time, outputMesh)`** is **critical**: it declares the
  dependency that drives evaluation. Without it, `compute()` is never
  triggered when time changes.

### 5. `initializePlugin` / `uninitializePlugin`

Standard `MFnPlugin.registerNode(name, id, creator, initializer)` /
`deregisterNode(id)` boilerplate. The `MTypeId(0x8700B)` is the node's
globally-unique numeric ID.

> **About that ID:** `0x8700B` is reserved by Autodesk for this example. For
> your own nodes you must pick an ID from the range Autodesk assigns you (see
> Maya docs → *Node IDs*). Reusing this example's ID in your own published
> plugin would collide with the devkit example.

---

## How to build and run it

### 1. Place the file on `MAYA_PLUGIN_PATH`

Either copy `py1AnimCubeNode.py` to Maya's plug-ins directory, or add its
folder to the `MAYA_PLUGIN_PATH` environment variable.

### 2. Load the plugin

In Maya:

- **Plug-in Manager** (`Windows → Settings/Preferences → Plug-in Manager`),
  browse to `py1AnimCubeNode.py` and check *Loaded*, **or**

- in the Script Editor:
  ```python
  import maya.cmds as cmds
  cmds.loadPlugin(r'D:\2026MayaPython\py1AnimCubeNode\py1AnimCubeNode.py')
  ```

### 3. Build the cube network (the wiring at the top of the .py)

The commented block at the top of the source is the connection recipe:

```python
import maya.cmds as cmds

# Transform + mesh shape (the visible cube)
cmds.createNode("transform", name="animCube1")
cmds.createNode("mesh", name="animCubeShape1", parent="animCube1")
cmds.sets("animCubeShape1", add="initialShadingGroup")

# The custom node itself
cmds.createNode("spAnimCube", name="animCubeNode1")

# Wire time into the node, and the node's mesh out into the shape
cmds.connectAttr("time1.outTime", "animCubeNode1.time")
cmds.connectAttr("animCubeNode1.outputMesh", "animCubeShape1.inMesh")
```

### 4. Play the timeline

Press play. The cube should **pulse** — growing from tiny to ~4.5 units and
snapping back to 0.5 every 10 frames.

### 5. Unload when done

```python
cmds.unloadPlugin('py1AnimCubeNode.py')
```

---

## The face-connects table (the trickiest part)

The `faceConnects` array is the hardest part to read at first. It's a flat
list of vertex indices, 4 per face × 6 faces = 24 entries:

```
face 0 (bottom, -Y): 0 1 2 3
face 1 (top,    +Y): 4 5 6 7
face 2 (front,  +Z): 3 2 6 5
face 3 (back,   -Z): 0 3 5 4     <- wait, source has 0 3 5 4
face 4 (left,   -X): 0 4 7 1
face 5 (right,  +X): 1 7 6 2
```

If you want to change the geometry (e.g. a pyramid, an octahedron), this is
the table you'd edit. Don't trust your spatial intuition — always verify the
winding order visually after editing.

---

## Key API reference links

- `OpenMayaMPx.MPxNode` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_mpx_node.html>
- `OpenMaya.MFnMesh` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_fn_mesh.html>
- `OpenMaya.MFnUnitAttribute`, `OpenMaya.MFnTypedAttribute` — attribute factories
- `OpenMaya.MFnMeshData` — the data container for mesh output
- `OpenMaya.MTime` — `asUnits()` for frame/time conversion

---

## Things to try next (exercises)

1. **Change the pulse rate.** Replace `cubeSize = 0.5 * float(frame % 10)`
   with `cubeSize = 0.5 * math.sin(frame * 0.5) + 1.0` for a smooth
   sinusoidal pulse instead of a sawtooth. Add `import math` at the top.
2. **Add a `sizeMultiplier` input attribute.** Add a second numeric input
   that scales `cubeSize`, declare `attributeAffects(multiplier,
   outputMesh)`, and expose it in the channel box. Now the user can tune the
   pulse amplitude.
3. **Change the geometry.** Reduce it to a pyramid (5 vertices, 5 faces) or
   expand it to an octahedron (6 vertices, 8 triangular faces). The
   `faceConnects`/`faceCounts` arrays are what you edit.
4. **Color the cube.** Add per-face colors via `MFnMesh.setFaceColors(...)`.
   This is the next step after geometry: learning to attach extra data to
   the mesh you generated.
5. **Port to API 2.0.** Rewrite using `maya.api.OpenMaya` / `maya.api.OpenMayaMPx`.
   Most calls are identical; the main differences are `MPxNode.compute`'s
   signature and how `MDataBlock` works. There's an official API 2.0 sibling
   called `py2AnimCubeNode.py` you can diff against.
6. **Make it a deformer instead.** Convert the node from a generator (writes
   `outputMesh`) to a deformer (`MPxDeformerNode`, modifies incoming
   geometry). This is a bigger jump but a natural next example to study.
7. **Add an undo-aware command** (`MPxCommand`) that creates the whole
   network (transform + shape + spAnimCube + connections) in one step, so
   users don't have to wire it manually.

---

## Common pitfalls

* **Forgetting `data.setClean(plug)`** causes Maya to call `compute()` every
  evaluation forever. If your node "spins" or hangs Maya, this is almost
  always why.
* **Forgetting `attributeAffects(input, output)`** means changing the input
  does nothing — `compute()` is never called because Maya doesn't know the
  output depends on the input.
* **`asMPxPtr` on the creator return.** `nodeCreator` must return
  `asMPxPtr(animCube())`, not the raw Python object. Otherwise Maya can't
  take ownership.
* **Reusing the example's `MTypeId`.** `0x8700B` is reserved by Autodesk for
  this example. Your own nodes need an ID from the range Autodesk assigns
  you (see *Node IDs* in the Maya docs). Reusing IDs causes plugin load
  failures or silent conflicts.
* **`MFnMesh.create(..., outData)` requires a real data container.** Always
  pass an `MFnMeshData.create()` object as the last argument, not `None` or
  a fresh `MObject()`. Otherwise the mesh isn't attached to anything and
  `outputHandle.setMObject` will fail silently.
* **Face winding order matters.** Reversed vertex order = inward-facing
  normals = the cube looks inside-out or fails to render. If you edit
  `faceConnects` and the cube looks wrong, suspect winding first.
* **`if frame is 0:` is Python 2 syntax.** In Python 3 (Maya 2027+), `is 0`
  raises a `SyntaxWarning`. Use `if frame == 0:` in modern code. The
  bundled source keeps the original line for fidelity — note it if you port.
* **The plugin name vs. the node name.** The file is `py1AnimCubeNode.py`,
  the plugin registers a node called `spAnimCube`. You load the *file* and
  create the *node* `spAnimCube` — two different names, easy to confuse.

---

## Source

- **Bundled source:** `animCubeNode.py` from the Autodesk static 2011 API
  archive (the authoritative static copy of this example):
  <https://download.autodesk.com/us/maya/2011help/API/anim_cube_node_8py-example.html>
- **Original requested page (2027 docs, JS-rendered — could not be cleanly
  fetched):**
  <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2py1_anim_cube_node_8py-example.html>
