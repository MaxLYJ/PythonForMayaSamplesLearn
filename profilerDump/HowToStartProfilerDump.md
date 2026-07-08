# HowToStart — profilerDump

This is the curriculum's first **performance-profiling** demo. It does **not**
build or modify any scene geometry — instead it reads timing events out of
Maya's built-in **`MProfiler`** engine and writes them to disk as **JSON** or
**CSV**. Think of it as the data-export half of a performance-debugging tool
chain: capture a slow moment in Maya, dump it to a file, then sort the file in
a spreadsheet to find what was slow.

It is unusual in two ways that shape this guide:

1. **It is the verbatim official Autodesk example** (the header is Autodesk's).
   Unlike `introduction` / `gearCreator` / `objectRenamer` / `tweener` /
   `controllerLibrary` / `lightManager`, there is **no `_2027` sibling** —
   `profilerDump.py` *is* the modern original (same situation as `fileDialog`
   and `manipulatorMath`). There is nothing to modernize, so this guide targets
   it directly. Its only Python-2 leftover is `from builtins import range`, a
   harmless no-op on Maya 2027's Python 3.

2. **It is a *hybrid* archetype** — like `manipulatorMath`. `profilerDump.py`
   itself is the pure **definitions-only library** (no `__main__`, three
   functions you import and call, plus no-op `initializePlugin` stubs). But the
   folder *also* ships a **runnable driver**, `test_example.py`, which has a
   `__main__` guard and a `run()` function that captures 500 cubes worth of work
   and dumps all three formats. So "How to Run" has a real first step: just run
   the driver. Driving the individual functions by hand is where the real
   learning (and the real bugs) live.

⚠️ **You need Maya's Python** to run this — the first real import is
`maya.OpenMaya`, which only resolves inside a Maya install. Use the **Script
Editor**, or `mayapy` from the command line. You do **not** need any particular
scene open — but you **do** need a populated profiler buffer (see "How to
Create the Test Maya Scene" below).

---

## Files in this demo

| File               | What it is                                                                                                       | Run it how                                                                                              |
|--------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `profilerDump.py`  | The demo — 3 public functions (`profilerToJSON`, `profilerToCSV`, `profilerFormatJSON`) over `om.MProfiler`, plus no-op plugin stubs. API 1.0. | Script Editor: `sys.path.insert(0, r'/abs/path/profilerDump'); import profilerDump; profilerDump.profilerToCSV(...)`. |
| `test_example.py`  | A runnable smoke-test driver. Starts sampling, creates+deletes 500 cubes, stops, sanity-checks the count, and dumps all 3 formats + a pretty-printed copy. | Script Editor: `import test_example; test_example.run()` (auto-puts `profilerDump.py` on `sys.path`).   |
| `GUIDE.md`         | A polished runbook for `test_example.py`: the two-part capture/dump model, the microsecond-unit warning, a troubleshooting table. | Read for context — it is more accurate than `README.md` on one flag (see divergences).                  |
| `README.md`        | The book's narrative: per-function walk-through, an `MProfiler` API table, exercises, pitfalls.                  | Read for context — but verify its claims against the `.py` (several divergences, catalogued below).      |

> **`_2027` convention — not needed here.** In the other demos `foo_2027.py` is
> the verified Python-3 copy. `profilerDump` has **no `_2027` sibling**:
> `profilerDump.py` is the verbatim Autodesk API 1.0 original. There is nothing
> to modernize, so this guide targets it directly.

## Prerequisites

- Python file I/O (`open`, `read`/`write`), and the stdlib `json` / `csv`
  modules — any Python tutorial and the stdlib docs.
- Comfortable with the idea of a **profiler**: an engine that records, for
  every chunk of work Maya does, *when* it started and *how long* it took.
- A first look at **API 1.0** (`import maya.OpenMaya as om`). You only need the
  `MProfiler` static methods listed in the table below; nothing deeper.
- ⚠️ **Maya's Python interpreter** (`mayapy` or the Script Editor) — required
  because the file imports `maya.OpenMaya` and the capture step uses the
  `profiler` command. Nothing here can run in plain `python3`.
- Conceptually: **two separate halves** — *capture* (`cmds.profiler`) writes
  events into an in-memory buffer; *dump* (`profilerDump.py`) reads that buffer
  out to a file. The library does only the second half. Forgetting the first
  half is the #1 reason for an empty output file.

---

## What the code actually does

`profilerDump.py` is three independent export functions plus no-op plugin
stubs. Map of the file:

```
__all__ = ['profilerToJSON', 'profilerToCSV', 'profilerFormatJSON']

def profilerToJSON(fileName, useIndex, durationMin):   # the big one — writes JSON
def profilerFormatJSON(fileName, fileName2):            # 5-line pretty-printer
def profilerToCSV(fileName, durationMin):               # CSV variant of JSON
def initializePlugin(obj):  obj                          # NO-OP stub
def uninitializePlugin(obj): obj                         # NO-OP stub
```

### `profilerToJSON(fileName, useIndex, durationMin)`

Dumps every event whose `duration > durationMin` to a hand-built JSON file. It
does **not** use the `json` module for the events array — it concatenates the
JSON by hand (`file.write("{" ... )`) for full control over the indexed vs.
inline layout. Layout chosen by `useIndex`:

| `useIndex` | Top-level lookup tables written? | Per-event fields                                                              |
|------------|-----------------------------------|-------------------------------------------------------------------------------|
| `True`     | yes — `"categories": [...]`, `"eventNames": [...]` | `time, nameIdx, desc, catIdx, duration, tDuration, tId, cpuId, colorId` (ints for the indexes) |
| `False`    | no                                | `time, name, desc, category, duration, tDuration, tId, cpuId, colorId` (full strings) |

Both layouts always write the header block: `version`, `eventCount`, `cpuCount`,
and a closing `eventsWritten` (how many events passed the `durationMin`
filter). If `om.MProfiler.getEventCount() == 0` the function **silently
returns** without writing anything.

### `profilerFormatJSON(fileName, fileName2)`

A 5-line helper: `json.load` the first file, `json.dumps(result, sort_keys=True,
indent=4, separators=(',', ': '))`, write it to the second file. Useful for
diffing two captures or making the indexed form readable. (Note it re-loads a
file `profilerToJSON` already wrote — it does **not** talk to `MProfiler` at
all.)

### `profilerToCSV(fileName, durationMin)`

Same event loop and same `durationMin` filter as `profilerToJSON`, but writes
via `csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)`. That quoting mode
auto-quotes every **string** field and leaves every **numeric** field bare —
exactly what a spreadsheet expects. Columns: `Event Time, Event Name,
Description, Event Category, Duration, Thread Duration, Thread Id, CPU Id,
Color Id`. There is **no** `useIndex` parameter here (CSV is flat — indexing
saves nothing).

### The `MProfiler` static methods the functions call

These are the reusable API surface. Every one takes the event **index** `i`
(`0..eventCount-1`):

| Method                              | Returns (API 1.0)              | Meaning                                            |
|-------------------------------------|--------------------------------|----------------------------------------------------|
| `MProfiler.getEventCount()`         | int                            | total number of recorded events                    |
| `MProfiler.getEventName(i)`         | **bytes**                      | name of event `i` (e.g. `b'evaluate'`)             |
| `MProfiler.getEventDuration(i)`     | float (**µs**)                 | how long event `i` took                            |
| `MProfiler.getEventTime(i)`         | float (**µs**)                 | when event `i` started, since session start        |
| `MProfiler.getEventCategory(i)`     | int                            | category ID of event `i`                           |
| `MProfiler.getCategoryName(catId)`  | str/bytes (see Q&A)            | human-readable category (e.g. `"DAG"`)             |
| `MProfiler.getDescription(i)`       | str or empty                   | free text from the instrumented code               |
| `MProfiler.getThreadDuration(i)`    | float (**µs**)                 | time spent on the owning thread                    |
| `MProfiler.getThreadId(i)`          | int                            | which thread ran event `i`                         |
| `MProfiler.getCPUId(i)`             | int                            | which CPU core ran event `i`                       |
| `MProfiler.getColor(i)`             | int                            | color slot (Profiler UI only)                      |
| `MProfiler.getAllCategories(list)`  | fills the passed list          | every category name, in ID order                   |
| `MProfiler.getNumberOfCPUs()`       | int                            | core count (written to the JSON header)            |

> **Units:** every duration/time field is in **microseconds (µs)**. `412` means
> `0.412 ms` / `0.000412 s`. See the units Q&A — the `README.md` example passes
> `durationMin=0.001` with the comment "skip events under 1ms", which is
> inconsistent with this unit.

### The capture side (`cmds.profiler`) — *not* in this file

The functions above only **read** events. To **put** events in the buffer you
use the `profiler` command from the Script Editor (or `test_example.py`, which
does it for you):

```python
import maya.cmds as cmds
cmds.profiler(sampling=False)     # stop any old session
cmds.profiler(reset=True)         # wipe the buffer (clean slate)
cmds.profiler(sampling=True)      # START recording
# ... do measurable work ...
cmds.profiler(sampling=False)     # STOP recording
```

⚠️ The on/off flag is **`sampling=True/False`**, not the `action='enable'` /
`action='disable'` that `README.md` prints. The runnable `test_example.py`
uses `sampling=` and works; the `README.md` form is a stale flag name. (Exact
flag names are version-sensitive — confirm in your Maya's command docs — but
`sampling=` is what the shipped test uses.)

---

## How to Create the Test Maya Scene

**There is no geometry scene to build.** Not a single DAG node needs to exist.
What the three functions require is a **populated profiler buffer** — a
completed *capture session* — in memory. Think of the "scene" here as a capture
session, not a scene graph.

You have two ways to get events into the buffer:

### Way A — the runnable driver builds it for you (easiest)

`test_example.py` does the whole capture itself (fresh scene → 500 cubes → mass
delete), so you do **nothing** by hand. Skip to "How to Run the Functions → Run
A" below.

### Way B — capture by hand (the real lesson)

If you want to control what gets profiled, drive `cmds.profiler` yourself in the
Script Editor **before** calling any dump function:

```python
import maya.cmds as cmds

# 1. Clean slate
cmds.profiler(sampling=False)
cmds.profiler(reset=True)

# 2. Start recording
cmds.profiler(sampling=True)

# 3. Do something measurable. Examples (pick one):
cmds.file(new=True, force=True)          # fresh scene
for _ in range(50):                      # build some geometry
    cmds.polyCube()
cmds.select(all=True); cmds.delete()     # mass delete (lots of DG work)
# — or —
# cmds.play(wait=True)                   # play an animated scene
# — or —
# import time; sum(range(2_000_000))     # any work at all

# 4. Stop recording
cmds.profiler(sampling=False)
```

### Scene/capture-state each entry point expects

| Entry point                          | What it needs from you                                                                              | If missing                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| `profilerToJSON(file, useIndex, dur)` | A non-empty profiler buffer (≥1 event).                                                              | `getEventCount()==0` → function **silently returns**, writes nothing.      |
| `profilerToCSV(file, dur)`           | Same — a non-empty profiler buffer.                                                                  | Same silent no-op.                                                         |
| `profilerFormatJSON(in, out)`        | A JSON file on disk that parses (typically one written by `profilerToJSON`).                         | File missing/unreadable → silent return; bad JSON → `json.JSONDecodeError`.|
| `test_example.run()`                 | Nothing — it captures its own 500-cube workload. Needs the folder to be **writable** for output.    | Read-only folder → `open(file, "w")` raises `PermissionError`.             |

---

## How to Run the Functions

All three runs assume the repo lives at `/abs/path/PythonForMayaSamplesLearn`
and you are in the **Script Editor (Python tab)**.

### Run A — the full driver (recommended first run)

```python
import sys, os
sys.path.insert(0, r'/abs/path/profilerDump')

import test_example
test_example.run()
```

`test_example.run()` auto-inserts its own folder on `sys.path` so `import
profilerDump` resolves, then captures the 500-cube workload and dumps **four**
files into the demo folder:

| File written by the driver             | Produced by                                              | Format                                   |
|----------------------------------------|----------------------------------------------------------|------------------------------------------|
| `capture_inline.json`                  | `profilerToJSON(..., useIndex=False, durationMin=0.0)`   | JSON, full strings inline                |
| `capture_indexed.json`                 | `profilerToJSON(..., useIndex=True,  durationMin=0.0)`   | JSON, compact `nameIdx`/`catIdx` form    |
| `capture.csv`                          | `profilerToCSV(..., durationMin=0.0)`                    | CSV, spreadsheet-ready                   |
| `capture_indexed_pretty.json`          | `profilerFormatJSON('capture_indexed.json', ...)`        | the indexed file re-sorted + indented    |

Expected Script Editor output (event count varies — expect a few hundred to a
few thousand after 500 cubes):

```
Captured events: 1247
Wrote:
    /abs/path/profilerDump/capture_inline.json
    /abs/path/profilerDump/capture_indexed.json
    /abs/path/profilerDump/capture.csv
    /abs/path/profilerDump/capture_indexed_pretty.json
Done.
```

If you see `Captured events: 0` followed by `RuntimeError`, sampling did not
start before the work block — re-check Way B step 2.

### Run B — drive the functions by hand (headless)

```python
import sys, maya.cmds as cmds, maya.OpenMaya as om
sys.path.insert(0, r'/abs/path/profilerDump')
import profilerDump

# 1. Capture a tiny session by hand
cmds.profiler(sampling=False); cmds.profiler(reset=True)
cmds.profiler(sampling=True)
for _ in range(20):
    cmds.polyCube()
cmds.profiler(sampling=False)

print("events:", om.MProfiler.getEventCount())   # should be > 0

# 2. Dump each format
out = r'/abs/path/profilerDump'
profilerDump.profilerToJSON(out + '/my_inline.json',  useIndex=False, durationMin=0.0)
profilerDump.profilerToJSON(out + '/my_indexed.json', useIndex=True,  durationMin=0.0)
profilerDump.profilerToCSV   (out + '/my.csv',        durationMin=0.0)
profilerDump.profilerFormatJSON(out + '/my_indexed.json', out + '/my_pretty.json')
```

### Expected on-disk results (structures you can verify by opening the files)

The exact numbers are session-dependent, but the **structure** is fixed by the
code. Verify these shapes against your output:

**`my_inline.json`** — header + array of inline event objects:

```json
{
    "version": 1,
    "eventCount": 312,
    "cpuCount": 8,
    "events": [
    { "time" : 1543.0, "name" : "evaluate", "desc" : "", "category" : "DAG", "duration" : 88.0, "tDuration" : 87.0, "tId" : 12345, "cpuId" : 0, "colorId" : 5    }
    ,{ "time" : 1631.0, "name" : "draw",     "desc" : "", "category" : "Rendering", "duration" : 412.0, "tDuration" : 410.0, "tId" : 12345, "cpuId" : 0, "colorId" : 2    }
    ],
    "eventsWritten": 312
}
```

> Note the hand-written JSON indents oddly (a leading `\t,{ ` before every
> event after the first). It is **valid JSON**; `json.load` reads it fine. This
> is why `profilerFormatJSON` exists — it re-emits clean indented JSON.

**`my_indexed.json`** — adds two lookup tables; events reference them by int:

```json
{
    "version": 1,
    "eventCount": 312,
    "cpuCount": 8,
    "categories": ["DAG", "Rendering", "Animation"],
    "eventNames" : ["evaluate", "draw", "compute"],
    "events": [
    { "time" : 1543.0, "nameIdx" : 0, "desc" : "", "catIdx" : 0, "duration" : 88.0, "tDuration" : 87.0, "tId" : 12345, "cpuId" : 0, "colorId" : 5    }
    ],
    "eventsWritten": 312
}
```

Decode by hand: `eventNames[0]` → `"evaluate"`, `categories[0]` → `"DAG"`.

**`my.csv`** — one header row + one row per event, strings quoted, numbers bare
(`QUOTE_NONNUMERIC`):

```csv
"Event Time","Event Name","Description","Event Category","Duration","Thread Duration","Thread Id","CPU Id","Color Id"
1543.0,"evaluate","","DAG",88.0,87.0,12345,0,5
1631.0,"draw","","Rendering",412.0,410.0,12345,0,2
```

**The analysis move:** open `my.csv` in a spreadsheet, sort by `Duration`
descending — the slowest events jump to the top. That is where to spend
optimization effort.

### Run C — the no-op plugin trap (what *not* to expect)

```python
# This LOADS but does nothing — the initializePlugin/uninitializePlugin stubs
# are no-ops (the function body is just the bare expression `obj`).
cmds.loadPlugin(r'/abs/path/profilerDump/profilerDump.py')   # succeeds, silently
# No command, no node, no UI is registered. There is nothing to call.
```

The plugin stubs exist only because the file's structure mirrors a plugin; the
**real** entry points are the three imported functions, never `loadPlugin`.

---

## Question and Answer

**Q1. Is this a plugin or a library? The file has `initializePlugin`.**
A library. `initializePlugin(obj)` and `uninitializePlugin(obj)` are **no-op
stubs** — their entire body is the bare expression `obj` (line 215 / 219), so
loading the file as a plugin registers nothing. The `README.md` and `GUIDE.md`
both call this out. The real entry points are the three functions in `__all__`,
called from the Script Editor after a plain `import`. (See Run C.)

**Q2. Why does my output file come out empty / not get created at all?**
Because `getEventCount()` returned `0`, so the dump function hit its
`if eventCount == 0: return` guard and **silently** wrote nothing — no error,
no message. That means no capture happened first: you forgot
`cmds.profiler(sampling=True)` before the work, or you ran
`profiler(reset=True)` *after* stopping (which wipes the buffer you just
filled). Always start a session with `sampling=False` + `reset=True`, *then*
`sampling=True`, *then* the work, *then* `sampling=False`, *then* dump.

**Q3. The README says `cmds.profiler(action='enable')`; the test uses `sampling=True`. Which is right?**
`sampling=True/False` is the start/stop flag the shipped `test_example.py`
actually uses and that runs. `README.md`'s `action='enable'`/`action='disable'`
is a stale flag name. (Flag names are version-sensitive — confirm in your
Maya's `profiler` command docs — but trust the runnable test over the prose.)

**Q4. `profilerToCSV`'s docstring mentions a `useIndex` parameter, but the signature is `(fileName, durationMin)`. Is that a bug?**
Yes — a copy-paste leftover. `profilerToCSV(fileName, durationMin)` has **no**
`useIndex` argument (CSV is flat; indexing would save nothing), yet its
docstring still lists `useIndex : write events using index lookup…` verbatim
from `profilerToJSON`. Ignore the docstring; the signature is authoritative.

**Q5. `getEventName(i)` is `.decode('ascii','replace')`'d, but `getCategoryName(...)` is not. Will my categories show up as `b'DAG'`?**
Maybe — this is a latent inconsistency. `getEventName` returns **bytes** in API
1.0, so the code decodes it. The README's API table claims
`getCategoryName(catId)` *also* returns bytes, but the code writes
`eventCategoryName` straight into the JSON/CSV **without** decoding. If your
Maya version returns bytes for categories, you will see `b'DAG'`-style literals
in the output. Verify on your version; if it bites, add the same
`.decode('ascii','replace')` after line 83 / 196.

**Q6. The README example passes `durationMin=0.001` "to skip events under 1ms". Why does almost nothing get filtered?**
Unit mismatch. Durations are in **microseconds**, so `0.001` means
`0.001 µs` ≈ 1 nanosecond — essentially no event is that fast, so nothing is
filtered. To genuinely skip events under 1 millisecond, pass
`durationMin=1000.0` (1000 µs = 1 ms). The README conflated the microsecond
unit with a millisecond threshold.

**Q7. Why is the inline JSON indented so strangely (a tab, then a comma, then a brace on later events)?**
Because `profilerToJSON` builds the JSON by hand with `file.write(...)`, not via
the `json` module. The first event is written `\t{ … }`; every later event is
written `\t,{ … }` (tab, comma, brace). The result is **valid** JSON (arbitrary
whitespace is allowed between tokens), just ugly. `profilerFormatJSON` exists
precisely to re-emit it cleanly sorted and indented.

**Q8. Why are event names stripped with `"".join(i for i in s if 31 < ord(i) < 127)`?**
Some instrumented code (plugins, GPU/driver layers) emits event names or
descriptions containing non-printable control characters or stray UTF-8. If
those reach the hand-built JSON string concatenation they break the output
(unclosed quotes, corrupt CSV). The `stripped` lambda keeps only printable
ASCII (code points 32–126) so the file always parses. It is applied to *names*;
descriptions are **not** stripped, which is itself a latent fragility.

**Q9. The indexed form uses `categories.index(name)` and `list(nameDict.keys()).index(name)` inside the event loop. Is that a problem?**
It is an O(n) lookup inside an O(n)-event loop, so the indexed dump is O(n²) in
the event count. For a few thousand events it is fine; for a long capture
(tens/hundreds of thousands) it gets noticeably slow. A real version would
build `{name: index}` dicts once up front and do O(1) lookups. Good
optimization exercise.

**Q10. What does `csv.QUOTE_NONNUMERIC` actually do, and why might it crash?**
It quotes every **string** field and writes every **non-quoted** field as a
float. That is perfect for the current columns (times/durations/ids are all
numbers; name/description/category are strings). But it is fragile: if you add
a new column that is a **string** but you pass it without quotes, the writer
will try to `float()` it and raise `ValueError`. If you extend the columns,
either keep strings quoted or switch to `csv.QUOTE_MINIMAL`.

**Q11. How do I profile *my own* function so it shows up as a named event?**
Wrap the work you want measured between `profiler(sampling=True)` and
`profiler(sampling=False)` — everything Maya instruments during that window is
captured automatically. To get a **named block for your own code specifically**,
add explicit instrumentation with the `profiler(beginTiming="my label")` /
`profiler(endTiming="my label")` flags, or the `MProfilingScope` RAII class in
C++/API. Then dump as usual and your label appears in the `Event Name` column.

---

## Advanced Directions

Each idea lists the new function/class it would add to `profilerDump.py`.

1. **A `profilerToDataFrame` / `--category` filter.** Add
   `profilerToCSV(fileName, durationMin, category=None)` (or a new
   `profilerFilterCSV`) that accepts a category name or list and skips
   non-matching events — so you can export just `Rendering` or `Animation`
   events. Requires resolving `getCategoryName` once per category and comparing
   per event. Pairs with a `--thread` filter (group by `ThreadId`).

2. **Per-thread / per-category aggregation.** Add
   `profilerSummary(fileName, durationMin)` that walks the events once and
   prints/returns a table of total `Duration` grouped by `Event Name`, by
   `Category`, and by `ThreadId` — answering "is work balanced across threads
   or concentrated on one?" and "which event *type* is the overall time sink?"
   before you even open a spreadsheet.

3. **Hardened, atomic, self-validating dumps.** Wrap the three functions so
   they (a) write to a temp file and `os.replace` it on success (atomic — no
   half-written JSON if Maya crashes mid-dump), (b) `try/except` the `open()`
   and emit a friendly error instead of crashing, and (c) optionally
   post-validate by `json.load`-ing the file just written and asserting
   `eventsWritten` matches the array length. Fixes the "silent empty file" and
   "non-atomic write" pitfalls in one pass.

4. **Indexed-JSON decoder + round-trip test.** Add
   `decodeIndexed(fileName)` that reads an indexed JSON, resolves every
   `nameIdx`/`catIdx` against the `eventNames`/`categories` tables, and returns
   plain dicts — i.e. the inverse of `useIndex=True`. Then add a
   `test_roundtrip()` that dumps `useIndex=True`, decodes it, and asserts it
   equals the `useIndex=False` dump for the same capture. This is both a useful
   utility and a real test that the hand-built JSON is correct.

5. **A capture-context manager + one-shot `capture_and_dump`.** Add
   ```python
   class profilerCapture:           # context manager
       def __enter__(self):  cmds.profiler(sampling=False); cmds.profiler(reset=True); cmds.profiler(sampling=True);  return self
       def __exit__(self, *exc): cmds.profiler(sampling=False)
   ```
   and `capture_and_dump(work, out_dir, durationMin=0.0)` that wraps `work()`
   in the context then writes all three formats. Turns the error-prone 4-line
   start/stop dance into `with profilerCapture(): …`, eliminating the #1
   "empty file" mistake. Add `undoChunk`/`undoInfo(openChunk=True)` around
   `work()` if it modifies the scene, so profiling leaves the scene clean.

6. **An installable shelf tool + flame-graph export.** Package the module as a
   Maya shelf button: click → runs a capture of a user-named action → dumps CSV
   → opens it (or pipes it to `speedscope` / a Python flame-graph lib). Add a
   `profilerToFlameGraph(fileName)` writer that emits the nested
   `begin/endTiming` event tree as the speedscope JSON format. You have now
   built the data-pipeline half of a serious performance tool, wrapped as a
   one-click shelf tool.

---

## Source

- **Source code:** `profilerDump.py` is the verbatim official Autodesk Maya
  Python API 1.0 example `python/api1/profilerDump.py`, and `test_example.py` is
  its companion driver, Maya 2027 (ENU) API reference:
  <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2profiler_dump_8py-example.html>.
- **Verification:** the inline-JSON / indexed-JSON / CSV output structures were
  derived by tracing `profilerToJSON`/`profilerToCSV`'s `file.write` calls, and
  the MProfiler duration/time units (microseconds) and the three source bugs
  (the nonexistent `useIndex` param, the un-decoded `getCategoryName`, the
  double `getDescription`) were found by reading the code and `GUIDE.md`.
  Producing real capture data needs a running Maya with an active profiler
  session and is marked as such throughout this guide.
