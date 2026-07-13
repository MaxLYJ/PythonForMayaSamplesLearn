# HowToStart — Intro (simple + standalone)

> **Position in the curriculum:** This is the **gateway to the entire Advanced
> Python for Maya** section (OpenMaya API). Everything you have done so far
> (demos 1–11 of the basics course) talked to Maya through `maya.cmds` — a thin,
> friendly wrapper. From here on you talk to Maya through **OpenMaya**, the same
> C++ API the application itself is built from. These two small files exist to
> teach three things before you ever write a plugin:
>
> 1. There are **two** OpenMaya APIs (1.0 and 2.0) and they are imported from
>    *different* packages.
> 2. The API can be used **inside a normal script** — you do not need to write a
>    plugin to touch it.
> 3. The API is measurably **faster** than `cmds` for bulk queries, and here is
>    a benchmark that proves it.
>
> In the Advanced learning order this is **demo #1 (`simple`) and demo #3
> (`standalone`)**. (`decorators`, #2, sits between them and lives in
> `Commands/`.) Do `simple` first; it is literally a "is the API working?" test,
> the OpenMaya equivalent of basics demo #1 `helloWorld`.

⚠️ **`simple` needs no scene at all** — it only prints. `standalone` *can* run on
an empty scene but the benchmark is **meaningless** without animation data; see
"How to Create the Test Maya Scene" below.

---

## Files in this demo

| File | Purpose | Archetype |
|------|---------|-----------|
| `simple.py` | Print three messages via `print`, API 2.0 `MGlobal.displayInfo`, and API 1.0 `MGlobal.displayInfo` | Flat top-to-bottom script (same as basics `introduction/helloWorld`) |
| `simple_2027.py` | Verified Maya-2027 copy of `simple.py` | Flat script |
| `standalone.py` | Benchmark: query every keyframe in the scene 1000× with `cmds`, then 1000× with the OpenMaya API, and print which is faster | **Hybrid** — two functions *plus* an unguarded top-level driver loop |
| `standalone_2027.py` | Verified Maya-2027 copy of `standalone.py` | Hybrid |
| `README.md` | Course context: C++ vs Python table, standalone-vs-plugin, the `M`/`MFn`/`MIt`/`MPx` naming prefixes | — |
| `__init__.py` | Empty package marker (lets you do `from Intro import simple`) | — |

### The `_2027` convention

Every demo in `AdvancedPythonForMaya-master/` ships a `_2027.py` companion that
runs on **Maya 2027 (Python 3, OpenMaya API 2.0)**. The originals target Maya
2018 / Python 2 and are kept as teaching references. **Run the `_2027` versions.**

For this folder the `_2027` diffs are the lightest in the whole curriculum:

- **`simple.py` → `simple_2027.py`:** byte-identical body. The file was already
  Python-3 / API-2.0 clean; the only change is the added header comment. There
  is genuinely nothing to modernize.
- **`standalone.py` → `standalone_2027.py`:** the entire diff is the two final
  `print` statements (Python 2 `print "..."` → Python 3 `print(...)`). The two
  functions, the iterator, the function-set usage, and the 1000-iteration loop
  are unchanged.

Because the bodies are effectively identical, the run instructions below target
the `_2027` files and apply to the originals as well.

---

## Prerequisites

- **Maya 2027** open, with the **Script Editor** available (both files are meant
  to run *interactively inside* Maya, not from a plain OS shell).
- For a *meaningful* benchmark in `standalone`, a scene that contains
  **`animCurveTA` nodes** — i.e. keyframed **rotation** channels. A single keyed
  joint is enough to see the code work; a full animated skeleton is needed to
  see the API win. See the scene-setup steps below.
- (Optional) The Maya devkit + `mayaCode`/`mayaPy` VS Code extensions for
  autocomplete while editing — *not* required to run anything.

---

## What the code actually does

### `simple.py` / `simple_2027.py` — the three output paths

This is a **flat script**: no `def`, no `class`, no `if __name__ == '__main__'`.
Like basics `helloWorld`, you run it by executing the whole file top-to-bottom.
It demonstrates the single most important thing to internalize before writing
any OpenMaya code:

| Line | What it does | Why it matters |
|------|--------------|----------------|
| `from maya import OpenMaya as om1` | Imports **API 1.0** — the direct C++-wrapper API | Older, verbose; still required for deformers and custom transforms (see `Nodes/pushDeformer`, `Scene/characterRoot`) |
| `from maya.api import OpenMaya as om` | Imports **API 2.0** — the modern Pythonic API | Note the extra `.api` package — this is the one most new code uses |
| `print("Hello, World! ...")` | Plain Python `print` | Goes to Python's `stdout` |
| `om.MGlobal.displayInfo("...")` | API 2.0 routed message | Goes through **Maya's** logging/routing system (Script Editor, output window, optional file log) |
| `om1.MGlobal.displayInfo("...")` | Same call through API 1.0 | Proves the two APIs look almost identical *to the user* even though they are very different internally |

The takeaway: `MGlobal.displayInfo` exists in **both** APIs with the same name,
which is why the file imports both — to show you that for day-to-day calls the
choice of API is mostly about where you import from, not a different vocabulary.

> **`M`-prefix cheat sheet** (from `README.md`, used by every Advanced demo):
> `M` = a Maya wrapper object (`MObject`, `MGlobal`, `MTime`); `MFn` = a
> **function set** that operates on an `MObject` of a given type
> (`MFnAnimCurve`, `MFnTransform`); `MIt` = an **iterator** (`MItDependencyNodes`,
> `MItSelectionList`); `MPx` = a **proxy** class you subclass to build a plugin
> (`MPxCommand`, `MPxNode`). You will meet all four prefixes in later demos.

### `standalone.py` / `standalone_2027.py` — the benchmark

This file is a **hybrid**: it defines two functions and then *immediately* runs a
1000-iteration benchmark at module level (lines 65–72) — **not** guarded by
`if __name__ == '__main__'`. That has a real consequence documented below in
"How to Run": **importing** this module executes the benchmark.

Both functions answer the same question — *"give me the set of unique keyframe
times across every rotation animation curve in the scene"* — two different ways:

**`commands()` — the `cmds` way:**

```python
curves = cmds.ls(type='animCurveTA')          # node names (strings)
keyframes = set(cmds.keyframe(curves, q=True))  # flat list of all key times
```

Two high-level calls. `cmds.ls` returns **names**, and `cmds.keyframe` re-resolves
those names and returns every key time flattened into one list.

**`api()` — the OpenMaya way:**

```python
it = om.MItDependencyNodes(om.MFn.kAnimCurveTimeToAngular)  # typed iterator
keyframes = set()
while not it.isDone():
    curveFn = oma.MFnAnimCurve(it.thisNode())   # function set on the real node
    for x in range(curveFn.numKeys):
        keyframes.add(curveFn.input(x).value)   # MTime -> frame number
    it.next()
```

One typed iterator that walks the **actual DG nodes** directly, with no
name→node round-trip and no re-resolution per call.

| Concept in the `api()` body | Meaning |
|-----------------------------|---------|
| `om.MItDependencyNodes(type)` | An iterator over every DG node of a given type. You advance it with `it.next()` and stop on `it.isDone()`. |
| `om.MFn.kAnimCurveTimeToAngular` | The **`MFn` type enum** for `animCurveTA` (Time → Angular). This is the API equivalent of `cmds.ls(type='animCurveTA')`. |
| `oma.MFnAnimCurve(it.thisNode())` | A **function set** bound to the real curve node (`it.thisNode()` returns its `MObject`). The function set is the handle you call `.numKeys` / `.input()` on. |
| `curveFn.input(x).value` | Key *x*'s time as an `MTime`; `.value` extracts the bare frame number. |

**The `animCurveTA` ↔ `MFn` enum mapping** (verified against the Autodesk `MFn`
and `MFnAnimCurve` references; Maya has 8 anim-curve node types — 4 time-input,
4 unitless-input):

| `cmds` node type | `MFn` enum | Output |
|------------------|------------|--------|
| `animCurveTA` | `kAnimCurveTimeToAngular` | Angular (rotation) ← *this demo* |
| `animCurveTL` | `kAnimCurveTimeToLinear` | Linear (translation) |
| `animCurveTT` | `kAnimCurveTimeToTime` | Time |
| `animCurveTU` | `kAnimCurveTimeToUnitless` | Unitless (e.g. visibility/envelope) |

**The driver loop (lines 65–72):**

```python
cmdTotal = 0
apiTotal = 0
for x in range(1000):
    apiTotal += api()
    cmdTotal += commands()
print("Commands took: %ss and API took %ss" % (cmdTotal, apiTotal))
print("Commands took %s times longer" % (cmdTotal / apiTotal))
```

It runs **each** function 1000 times, sums the per-call wall-clock time
(`time.time()` deltas), and prints two totals plus the ratio
`cmdTotal / apiTotal`. The file's own comment (and the README) state the API
version takes *almost half* the time — i.e. `cmds` is roughly **~2× slower**.
The exact ratio depends on scene size and machine; what is reliable is the
**direction** (API wins), not the precise factor.

> Note on the local `keyframes = set(...)`: both functions build the set of
> frames but **never return it** — only the `delta` timing is returned. The set
> is there so the functions do *real work* (otherwise you'd be timing an empty
> loop). It is not a bug; the demo only cares about timing.

---

## How to Create the Test Maya Scene

### For `simple.py`

**No scene needed.** It only prints. Open a fresh empty scene and proceed to
"How to Run." (Same convention as the no-scene basics demos `fileDialog`,
`commandLine`, `manipulatorMath`.)

### For `standalone.py` — you need rotation animation

`animCurveTA` nodes are created whenever you **key a rotation channel**
(`rotateX`/`rotateY`/`rotateZ`) on any transform or joint. The more keyed
rotation channels, the more curves, and the clearer the API's advantage.

**Minimum scene (enough to see the code run):**

1. **File → New Scene.**
2. Switch to the **Animation** menu set (top-left).
3. **Create → Joint Tool**, click once in the viewport, press Enter → you have
   `joint1`.
4. Select `joint1`. Set the time slider to **frame 1**, select the `rotateY`
   channel (or press the channel-box `rotateY`), press **S** to key it.
5. Go to **frame 24**, set `rotateY` to **90**, press **S** again.
6. You now have one `animCurveTA` (`joint1_rotateY`). Scrub the timeline to
   confirm `joint1` rotates.

**Scene for a meaningful benchmark** (recommended — the demo points to
Autodesk's free animation samples; a quick do-it-yourself version):

1. Repeat the joint workflow but build a small chain: `joint1` → `joint2` →
   `joint3` → `joint4` (parented automatically by the Joint Tool).
2. Key **all three rotation channels** (`rotateX/Y/Z`) on **every** joint at
   frames 1 and 24 (select all joints, press **S** at each frame, or use
   **Animate → Key Selected** after highlighting the channels).
3. A 4-joint chain with 3 keyed rotation channels each gives you **12
   `animCurveTA` nodes** — enough that the per-call overhead difference between
   `cmds` and the API becomes visible.

> **Why rotation specifically?** `animCurveTA` = Time→Angular. If you key
> *translation* you create `animCurveTL` nodes, which this demo's iterator
> (`kAnimCurveTimeToAngular`) will **not** find. To benchmark translation you'd
> change both the `cmds.ls(type=...)` filter and the `MFn` enum — see Q&A.

> **The overloaded word "standalone".** Despite the filename, this file does
> **not** call `maya.standalone.initialize()`. Here "standalone" means *"a
> regular script, not a plugin"* — you can use the OpenMaya API without writing
> a plugin at all. Running it **truly** headless under `mayapy` (no GUI) is a
> separate technique covered in Advanced Directions. As shipped, `standalone.py`
> is meant for the **interactive Script Editor**.

---

## How to Run the Functions

Open the Script Editor (**Windows → General Editors → Script Editor**), switch to
the **Python** tab.

### Run A — `simple` (the API "is it working?" test)

Paste the whole file and execute:

```python
from maya import OpenMaya as om1
from maya.api import OpenMaya as om

print("Hello, World! I am writing this using the standard Python print statement")
om.MGlobal.displayInfo("Hello, World! I am writing this using the OpenMaya API")
om1.MGlobal.displayInfo("Hello, World! This is using the old API")
```

**Expected result** — three lines appear in the Script Editor's history pane:

```
Hello, World! I am writing this using the standard Python print statement
Hello, World! I am writing this using the OpenMaya API    // displayInfo
Hello, World! This is using the old API                    // displayInfo
```

All three look identical in the history, but `print` and the two
`displayInfo` calls arrived via **different channels** (Python `stdout` vs Maya's
routed message system). If you see all three lines, your OpenMaya imports work.

### Run B — `standalone` (the benchmark, full file)

With an animated scene open (see scene setup), paste the **entire** `standalone_2027.py`
and execute. The 1000-iteration loop runs, then prints something like:

```
Commands took: 1.42s and API took 0.61s
Commands took 2.33 times longer
```

Your numbers will differ, but `Commands took ___ times longer` should be **> 1.0**
(the README claims roughly ~2×). On an **empty scene** both functions operate on
zero curves, so both totals are dominated by call overhead and the ratio is
noisy / near 1.0 — that is not a meaningful measurement, it just confirms the
code runs.

> ⚠️ **Paste the whole file, do not `import` it.** The benchmark loop is at
> **module level** (not under `if __name__ == '__main__'`), so
> `import standalone` would execute the 1000-iteration loop as a side effect of
> the import. The file is written as a paste-and-run teaching script, not an
> importable library. (See Q&A.)

### Run C — `standalone`, run each function once (headless single-shot)

To call the two functions directly without the 1000× loop, paste only the two
function definitions, then:

```python
print("cmds path took: %ss" % commands())
print("api  path took: %ss" % api())
```

Each call returns the wall-clock seconds for **one** pass over the scene's
`animCurveTA` curves. This is the building block the loop wraps.

### Run D — inspect the work product (the discarded keyframe set)

Both functions build a `set` of unique frame numbers but throw it away. To see
what they actually computed, redefine one inline and print it:

```python
def api_frames():
    it = om.MItDependencyNodes(om.MFn.kAnimCurveTimeToAngular)
    keyframes = set()
    while not it.isDone():
        curveFn = oma.MFnAnimCurve(it.thisNode())
        for x in range(curveFn.numKeys):
            keyframes.add(curveFn.input(x).value)
        it.next()
    return keyframes

print(sorted(api_frames()))   # e.g. [1.0, 24.0] for the 2-key minimum scene
```

**Expected:** for the minimum scene (joint1 keyed at frames 1 and 24) you get
`{1.0, 24.0}`; for the 12-curve benchmark scene you still get just `{1.0, 24.0}`
because every curve keys the same two frames — the *set* dedupes them. To get
more distinct frames, key at additional times.

> 🧪 **Cannot be verified without Maya running:** the precise benchmark ratio and
> the exact Script Editor routing of `displayInfo` vs `print` are
> version/machine-dependent. The directions above (API wins; three lines appear)
> are the reliably observable facts.

---

## Question and Answer

**Q1. What is the actual difference between `from maya import OpenMaya` and
`from maya.api import OpenMaya`?**
The first is **API 1.0** (`maya.OpenMaya`), a thin, direct wrapper over the C++
API — verbose, uses pre-allocated "wrapper" objects filled by reference, and is
still the *only* option for a few node types (deformers, custom transforms). The
second is **API 2.0** (`maya.api.OpenMaya`), a newer, more Pythonic API where
methods return values directly. They share most class/method *names*
(`MGlobal.displayInfo` works in both) but live in different packages and behave
differently internally. Pick API 2.0 for new code; reach for 1.0 only when a
subclass you need is missing from 2.0.

**Q2. `simple.py` imports both APIs (`om1` and `om`) and then calls
`MGlobal.displayInfo` on each. Isn't that redundant?**
It's intentional — the whole point of `simple.py` is to show the two imports
side by side and prove that the *user-facing* call is nearly identical even
though the plumbing differs. Importing both in real code is wasteful; pick one
and alias it consistently (this curriculum uses `om` for API 2.0, matching
`standalone.py`).

**Q3. What is the practical difference between `print(...)` and
`om.MGlobal.displayInfo(...)`?**
`print` writes to Python `stdout`; in the GUI that shows in the Script Editor
history, but it bypasses Maya's logging. `MGlobal.displayInfo` (and its siblings
`displayWarning`, `displayError`) go through **Maya's message routing**, so they
respect the user's logging configuration — they can land in the Script Editor,
the Output Window, or a file log, and they carry a severity level Maya can color
or react to. The file's comment calls this out as the main reason to prefer
`displayInfo` in tooling that ships to other users.

**Q4. The file is named `standalone.py` but it never calls
`maya.standalone.initialize()`. Why?**
Because "standalone" is **overloaded** in Maya. In this demo it means *"using the
API outside a plugin"* — i.e. from a normal script in the Script Editor, no
`loadPlugin`/`initializePlugin` involved. The separate `maya.standalone` *module*
means something else entirely: running Python against Maya **without the GUI**,
via the `mayapy` interpreter, which requires
`import maya.standalone; maya.standalone.initialize(name='python')`. This demo is
the first sense; to run it the second way you must add that init call yourself
(see Advanced Directions). The name is about *not being a plugin*, not about
running headless.

**Q5. Why `om.MFn.kAnimCurveTimeToAngular` instead of just writing
`'animCurveTA'` like `cmds.ls` does?**
`cmds` identifies node types by their string name (`animCurveTA`). The API
identifies them by a **typed enum** in the `MFn` (function-set) namespace. The
two are a fixed mapping: `animCurveTA` ↔ `kAnimCurveTimeToAngular`,
`animCurveTL` ↔ `kAnimCurveTimeToLinear`, etc. (eight anim-curve types total).
The enum is what the typed iterator `MItDependencyNodes` expects, and it lets the
API filter nodes without ever converting to/from strings.

**Q6. Why does the driver loop run **1000** iterations instead of once?**
Because `time.time()` resolution and OS scheduling noise make a single call's
duration unreliable — a `cmds.keyframe` call might report 0.0002s one run and
0.0008s the next purely from jitter. Running 1000 times and summing averages out
the noise and amplifies the *real* per-call cost difference into something you
can read off the totals. This is a standard micro-benchmarking discipline, not
Maya-specific.

**Q7. I ran `standalone.py` on an empty scene and it said "Commands took 1.0
times longer" — is the API not faster?**
The code ran fine; the measurement was just meaningless. With no `animCurveTA`
curves, `cmds.ls` returns `[]` and the iterator is immediately `isDone()`, so
both functions do essentially zero work and the totals are pure call overhead —
which is similar for both. The API's advantage is the *per-curve* work it skips
(name resolution, re-querying). You need a scene **with animation** for that
work to exist. Populate the scene (see scene setup) and rerun.

**Q8. Why is the API version faster than `cmds` here?**
`cmds.keyframe(curves, q=True)` is a high-level command: Maya takes the list of
**names**, resolves each back to a node, builds a flat list of all key times,
and returns it — lots of per-call bookkeeping repeated 1000×. The API version
gets a **typed iterator** over the real DG nodes directly (no name round-trip),
binds a lightweight function set once per curve, and reads `.input(x).value`
straight out of the curve data. Less interpretation per item = less time,
especially as curve count grows.

**Q9. Both functions build `keyframes = set(...)` but only `return delta`. Is the
set a bug / dead code?**
Not a bug — it's *payload*. Without computing the set you'd be timing empty
loops, which would make `cmds` look artificially cheap (it wouldn't actually
query anything). The set forces both paths to do the real work (resolve + read
every key) so the timing comparison is honest. The set is discarded because the
demo's deliverable is the **timing**, not the frames. (Run D shows how to return
it instead if you want the data.)

**Q10. Why is there no `if __name__ == '__main__'` guard around the benchmark
loop?**
Because the file is a **paste-and-run teaching script**, not an importable
module. Putting the loop at module scope means the moment you `import
standalone`, Python executes the 1000-iteration benchmark as a side effect —
which is surprising and slow. A production version would wrap the loop in
`def main():` and guard it with `if __name__ == '__main__': main()` so importing
the file only *defines* the functions. This is exactly the "library vs script"
distinction from basics demo `commandLine/renamer`.

**Q11. How would I extend this to benchmark translation (`animCurveTL`) too?**
Two coordinated edits: change `cmds.ls(type='animCurveTA')` →
`cmds.ls(type='animCurveTL')`, **and** change `om.MFn.kAnimCurveTimeToAngular` →
`om.MFn.kAnimCurveTimeToLinear`. They must match — if you change one but not the
other, the two functions will be measuring *different* sets of curves and the
comparison is invalid. (To measure all anim curves at once, iterate without a
type filter or union the four time-input enums.)

---

## Advanced Directions

These two tiny files are the seed for several real tools. Each idea lists the new
functions/classes it would add.

1. **A reusable benchmark harness.** Generalize the 1000× loop into
   `bench(label, fn, iterations=1000)` that returns `(total, per_call, result)`,
   plus a `workload` registry so you can register multiple queries (count nodes,
   read all `rotateX` values, list shapes) and print a comparative table in one
   shot. *New:* `bench()`, `register_workload()`, `run_all()`, a `Result` dataclass.

2. **True headless `mayapy` runner.** Wrap the script so it runs from the OS
   shell with **no GUI** via the `mayapy` interpreter: add
   `import maya.standalone; maya.standalone.initialize(name='python')` at the top
   and `maya.standalone.uninitialize()` at the end, behind a `def main()` guarded
   by `if __name__ == '__main__'`. Lets you benchmark on CI / a render farm.
   *New:* `main()` with `initialize`/`uninitialize`, a `--scene` argument.

3. **Per-curve breakdown with `MProfiler`.** Replace the single total with a
   `profile_run()` that uses `om.MProfiler` categories (or per-curve
   `time.time()`) to show *where* the API wins — function-set reuse vs per-call
   name resolution — and emit a breakdown table (curve count, keys/curve, ms/curve).
   Turns "API is faster" into "API is faster *because*…".
   *New:* `profile_run()`, `breakdown_table()`, a `PerfRow` dataclass.

4. **All four time-input anim-curve types.** Generalize the iterator to walk
   `kAnimCurveTimeToAngular/Linear/Time/Unitless` and `cmds.ls` to all four node
   types, building a complete **keyframe census** of the scene: how many curves
   of each type, total keys, distinct keyed frames. *New:* `TYPE_MAP` constant,
   `census_curves()`, `distinct_frames()`.

5. **A keyframe audit / export tool.** Take the `api()` function's discarded
   `set` of frames and make it the *deliverable*: detect keyframe collisions
   (two channels keyed at the same frame), find sparse/dense ranges, and export
   the frame list + per-curve key counts to CSV/JSON. This is the realistic
   evolution from "benchmark" to "useful animation utility."
   *New:* `audit_keyframes()`, `detect_collisions()`, `export_frames(path)`.

6. **A routed logging utility.** Make `simple.py`'s
   `MGlobal.displayInfo` claim concrete by building a small `log()` helper with a
   `LogLevel` enum that routes to `displayInfo` / `displayWarning` / `displayError`
   and optionally to a file, demonstrating the routing/severity advantage the
   `print` vs `displayInfo` contrast was pointing at. *New:* `LogLevel`,
   `log(level, msg)`, `FileLogHandler`.
