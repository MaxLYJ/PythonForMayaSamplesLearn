# GUIDE — How to Run the profilerDump Test

This guide shows you how to actually exercise `profilerDump.py`. The module
itself only does **half** the job — it *reads* events out of Maya's profiler
and writes them to disk. To get events in the first place you need to
**capture** them with `cmds.profiler`.

A runnable test is provided in [`test_example.py`](./test_example.py).

---

## The two-part mental model

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  1. CAPTURE  (cmds.profiler)│  ───►   │  2. DUMP   (profilerDump.py)│
│  profiler(sampling=True)    │         │  profilerToJSON / CSV       │
│  ...do work...              │         │  → reads MProfiler          │
│  profiler(sampling=False)   │         │  → writes file              │
└─────────────────────────────┘         └─────────────────────────────┘
```

Key fact (corrected from the README): the on/off flag is
**`sampling=True/False`**, not `action='enable'`. Verified from the
[official `profiler` command docs](https://help.autodesk.com/cloudhelp/ENU/MayaCRE-Tech-Docs/CommandsPython/profiler.html).

---

## Quick start (3 steps)

### 1. Open the Maya Script Editor (Python tab)

### 2. Make `profilerDump.py` importable and run the test

If you cloned the repo to `D:\2026MayaPython`, the test auto-discovers the
module sitting next to it, so all you need is:

```python
import sys
sys.path.insert(0, r'D:\2026MayaPython\profilerDump')

import test_example
test_example.run()
```

(If your checkout lives elsewhere, just change the path above.)

### 3. Watch the output

In the Script Editor you should see something like:

```
Captured events: 1247
Wrote:
    D:/2026MayaPython/profilerDump/capture_inline.json
    D:/2026MayaPython/profilerDump/capture_indexed.json
    D:/2026MayaPython/profilerDump/capture.csv
    D:/2026MayaPython/profilerDump/capture_indexed_pretty.json
Done.
```

The exact event count varies — expect a few hundred to a few thousand after
creating + deleting 500 cubes.

---

## What the test does, step by step

| Step | Code                                   | Purpose                                            |
|-----:|----------------------------------------|----------------------------------------------------|
| 1    | `profiler(sampling=False)` + `reset=True` | Clean slate: stop any old session, wipe the buffer |
| 2    | `profiler(sampling=True)`              | Start recording                                    |
| 3    | `file(new=True)` → 500× `polyCube()` → `select(all=True)` → `delete()` | Generate measurable DG work |
| 4    | `profiler(sampling=False)`             | Stop recording                                     |
| 5    | `MProfiler.getEventCount()`            | Sanity check — bail out early if 0 events          |
| 6    | `profilerToJSON(...)` × 2 + `profilerToCSV(...)` + `profilerFormatJSON(...)` | Dump all three formats + pretty-print |

---

## Reading the output

### `capture.csv` (the most useful one)

Open it in Excel / VS Code / Numbers. Columns are:

| Column           | Meaning                                                          |
|------------------|------------------------------------------------------------------|
| `Event Time`     | When the event started (microseconds since session start)        |
| `Event Name`     | What the event was (`evaluate`, `compute`, `draw`, …)            |
| `Description`    | Free text from the instrumented code (may be blank)              |
| `Event Category` | Group (`DAG`, `Animation`, `Rendering`, …)                       |
| `Duration`       | How long the event took (**microseconds**)                       |
| `Thread Duration`| Time spent on the owning thread                                  |
| `Thread Id`      | Which thread ran it                                              |
| `CPU Id`         | Which CPU core ran it                                            |
| `Color Id`       | Color slot (used by the Profiler UI, not meaningful in CSV)      |

**The key move:** sort by `Duration` descending. The slowest events jump to
the top — that's where to spend your optimization effort.

### `capture_inline.json`

Human-readable JSON. Each event has its name and category written in full:

```json
{
  "time": 1234.5,
  "name": "evaluate",
  "desc": "...",
  "category": "DAG",
  "duration": 412.0,
  ...
}
```

### `capture_indexed.json` and `capture_indexed_pretty.json`

Compact form: event names and categories are written once as lookup tables
at the top (`"eventNames": [...]`, `"categories": [...]`), and each event
references them by integer:

```json
{
  "nameIdx": 0,
  "catIdx": 1,
  ...
}
```

Smaller files, but you have to decode the indexes with the lookup tables.
`capture_indexed_pretty.json` is the same data, key-sorted and indented for
diffing.

---

## Units warning

**Durations are in microseconds (µs).** Common conversions:

| µs        | ms      | seconds |
|-----------|---------|---------|
| 1000      | 1       | 0.001   |
| 1_000_000 | 1000    | 1       |

So a `Duration` of `412` means **0.412 ms** or **0.000412 s**.

---

## Troubleshooting

| Symptom                              | Cause                                              | Fix                                                                 |
|--------------------------------------|----------------------------------------------------|---------------------------------------------------------------------|
| Output file empty / not created      | `getEventCount()` returned 0                       | You forgot `profiler(sampling=True)` before the work, or ran `reset=True` *after* stopping |
| `b'evaluate'` appears in the JSON    | API 1.0's `getEventName` returns `bytes`           | Expected — the module already `.decode()`s; if you see it, you edited a local copy |
| Numbers look wrong (huge / tiny)     | Duration unit is microseconds, not ms              | Divide by `1000.0` (ms) or `1_000_000.0` (s)                       |
| Old events leak into the dump        | Buffer wasn't cleared between runs                 | Always call `profiler(reset=True)` before `sampling=True`          |
| `ImportError: No module named profilerDump` | `sys.path` doesn't include the folder      | Re-check the `sys.path.insert(...)` line                            |
| `ImportError: No module named maya.OpenMaya` | Running outside Maya                      | This module must run inside Maya (or `mayapy`), not standalone Python |

---

## A smaller "smoke test"

If 500 cubes feels heavy and you just want to confirm the pipeline is wired
correctly, drop this in the Script Editor instead:

```python
import maya.cmds as cmds
import maya.OpenMaya as om

cmds.profiler(sampling=False)
cmds.profiler(reset=True)

cmds.profiler(sampling=True)
print(sum(range(1_000_000)))   # any work at all
cmds.profiler(sampling=False)

print("Events:", om.MProfiler.getEventCount())
```

You should see a small nonzero count. If it's `0`, sampling didn't start —
re-check step 1 of Quick Start. Once that prints a real number, the dump
functions in `profilerDump.py` will work.

---

## Want to profile your own code?

Wrap the work you want measured between `sampling=True` and `sampling=False`,
or add your own instrumentation using `MProfilingScope` (API) / the
`profiler(beginTiming=...)` / `profiler(endTiming=...)` flags. Then run
`profilerDump.profilerToCSV(...)` and sort the output by `Duration`.

The profiler captures everything Maya instruments by default — you only need
custom instrumentation if you want a named block for your *own* functions
in the output.

---

## Sources

- [`profiler` command — Autodesk Maya Python Docs](https://help.autodesk.com/cloudhelp/ENU/MayaCRE-Tech-Docs/CommandsPython/profiler.html)
- [`OpenMaya.MProfiler` Class Reference](https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_profiler.html)
