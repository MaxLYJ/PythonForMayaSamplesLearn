# profilerDump — Extract Maya Profiler Events to JSON / CSV (API 1.0)

This demo comes from the official Maya Python API documentation.

**Source:** <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2profiler_dump_8py-example.html>

It's a **utility module** with three functions that pull events out of Maya's
built-in `MProfiler` and write them to disk as **JSON** or **CSV**. Useful for
performance analysis: capture a profiling session, export it, then analyze it
in a spreadsheet or feed it to a separate visualization tool.

> ℹ️ The module is **not a plugin** despite having `initializePlugin` /
> `uninitializePlugin` stubs at the bottom — those are no-ops. The real entry
> points are the three public functions, called from the Script Editor.

---

## What you will learn

1. **`MProfiler`** — Maya's built-in profiling system. Records timing events
   for evaluation, redraw, file I/O, and anything else instrumented with
   `MProfilingScope`. This module shows how to *read* those events back out.
2. **Reading profiler events** — `getEventCount()`, `getEventName(i)`,
   `getEventDuration(i)`, `getEventTime(i)`, `getEventCategory(i)`, etc.
3. **Categories & names as enums** — events reference a category ID and a
   name string; the example shows both the indexed (compact) and
   non-indexed (human-readable) representations.
4. **Filtering by duration** — the `durationMin` parameter lets you skip
   events shorter than a threshold, which is how you strip noise out of a
   profile.
5. **JSON vs CSV output tradeoffs** — JSON keeps structure and supports the
   indexed form (smaller files); CSV is the right choice when the goal is to
   open the data in Excel / Numbers / Google Sheets.

---

## Prerequisites

| Concept                       | Where to learn it                                                              |
|-------------------------------|--------------------------------------------------------------------------------|
| `maya.cmds` basics            | `introduction/helloCube.py`                                                    |
| OpenMaya API 1.0              | [`../cameraMessageCmd/cameraMessageTest/`](../cameraMessageCmd/cameraMessageTest/README.md) |
| Python file I/O (`open`)      | standard Python tutorial                                                       |
| The `json` and `csv` modules  | Python standard library docs                                                   |
| What `MProfiler` is           | Maya docs → *Profiling API* (`MProfiler`, `MProfilingScope`)                   |

You don't need to have written a plugin before — this module is just a set
of functions you import and call.

---

## Files

```
profilerDump/
├── README.md                ← this file
└── profilerDump.py          ← the utility module
```

The `.py` is bundled here directly (it's a public Autodesk docs listing).

---

## Background: what is `MProfiler`?

Maya's profiler records timestamped events whenever instrumented code runs —
evaluation of a node, a redraw, a file open, a plugin's custom work, etc.
You can see them visually in **`Window → General Editors → Profiler`**
(the timeline view). Each event has:

- a **time** (when it started) and a **duration** (how long it took),
- a **name** (what the event is) and a **category** (which group it belongs
  to, e.g. "Rendering", "DAG", "Animation"),
- a **thread id** and **CPU id** (which thread ran it),
- an optional **description** (free text),
- a **color** (used by the UI).

This module reads all of those fields out programmatically. The typical
workflow: enable the profiler, do something slow in Maya, then call one of
the functions below to dump everything to a file you can analyze offline.

---

## The three public functions

### 1. `profilerToJSON(fileName, useIndex, durationMin)`

Dumps every event (above `durationMin`) to a JSON file.

```python
profilerDump.profilerToJSON('out.json', useIndex=True, durationMin=0.0)
```

- **`useIndex=True`** — emit a compact form where event names and categories
  are written once as lists at the top (`"eventNames": [...]`,
  `"categories": [...]`), and each event references them by integer index
  (`"nameIdx": 3`, `"catIdx": 1`). Much smaller files, but harder to read.
- **`useIndex=False`** — write the full strings inline (`"name": "evaluate"`,
  `"category": "DAG"`). Bigger files, but self-contained and greppable.
- **`durationMin`** — only include events whose duration is greater than this
  value (in whatever unit `MProfiler` reports). Set to `0.0` to keep
  everything; raise it to strip noise.

The output JSON looks roughly like:

```json
{
  "version": 1,
  "eventCount": 12345,
  "cpuCount": 8,
  "categories": ["DAG", "Rendering", "Animation"],
  "eventNames": ["evaluate", "draw", "compute"],
  "events": [
    { "time": 0.001, "nameIdx": 0, "desc": "...", "catIdx": 0,
      "duration": 0.4, "tDuration": 0.4, "tId": 1234, "cpuId": 0, "colorId": 5 }
  ],
  "eventsWritten": 12345
}
```

### 2. `profilerFormatJSON(fileName, fileName2)`

Tiny helper: reads a JSON file (e.g. produced by `profilerToJSON`), sorts the
keys, pretty-prints with 4-space indent, and writes it back out. Useful for
diffing two captures or making the indexed form more readable.

```python
profilerDump.profilerFormatJSON('out.json', 'out_pretty.json')
```

### 3. `profilerToCSV(fileName, durationMin)`

Same data as `profilerToJSON`, but in CSV. This is what you want when the
goal is **spreadsheet analysis** — open the file in Excel, sort by Duration
descending, and the slowest events jump to the top.

```python
profilerDump.profilerToCSV('out.csv', durationMin=0.0)
```

Columns: `Event Time, Event Name, Description, Event Category, Duration,
Thread Duration, Thread Id, CPU Id, Color Id`.

---

## How to run it

### 1. Enable the profiler in Maya

Before you can dump anything, there must be events to dump. Either:

- Open **`Window → General Editors → Profiler`** and hit **Record**, do
  something in the scene (play, render, evaluate), then **Stop**, **or**
- programmatically:
  ```python
  import maya.cmds as cmds
  cmds.profiler(action='enable')
  # ... do work ...
  cmds.profiler(action='disable')
  ```

### 2. Save and import the module

Place `profilerDump.py` on `PYTHONPATH` (or alongside your other Maya
scripts), then in the Script Editor:

```python
import profilerDump
```

### 3. Dump the captured events

```python
import profilerDump

# JSON, human-readable, no duration filter
profilerDump.profilerToJSON('capture.json', useIndex=False, durationMin=0.0)

# JSON, compact indexed form, skip events under 1ms
profilerDump.profilerToJSON('capture_compact.json', useIndex=True, durationMin=0.001)

# CSV for spreadsheet analysis
profilerDump.profilerToCSV('capture.csv', durationMin=0.0)
```

The files appear in Maya's current working directory (use absolute paths if
you want them somewhere specific).

### 4. (Optional) Pretty-print the JSON

```python
profilerDump.profilerFormatJSON('capture_compact.json', 'capture_compact_pretty.json')
```

---

## Walking through the code

The whole module is ~250 lines of straightforward iteration. Read it in
this order:

1. **`profilerToJSON`** — the biggest function. Notice the structure:
   - `om.MProfiler.getEventCount()` → how many events are there?
   - `om.MProfiler.getAllCategories(categories)` → fill a list of category
     names.
   - Loop every event index `i`, calling `getEventName/Duratuson/Time/...`
     to pull fields.
   - The `stripped` lambda filters out non-printable ASCII — important
     because event names come back as raw `bytes` and may contain control
     chars from some plugin sources.
2. **`profilerFormatJSON`** — just `json.load` + `json.dumps(..., sort_keys,
   indent=4)` + write. Five lines of real logic.
3. **`profilerToCSV`** — almost identical to `profilerToJSON` but writes via
   `csv.writer` instead of manual string concatenation. Note
   `quoting=csv.QUOTE_NONNUMERIC` — it auto-quotes strings and leaves
   numbers bare, which is what spreadsheets expect.

Key API calls you'll reuse anywhere you touch `MProfiler`:

| Method                              | Returns                                      |
|-------------------------------------|----------------------------------------------|
| `MProfiler.getEventCount()`         | total number of recorded events              |
| `MProfiler.getEventName(i)`         | `bytes` — name of event `i`                  |
| `MProfiler.getEventDuration(i)`     | float — how long event `i` took              |
| `MProfiler.getEventTime(i)`         | float — when event `i` started               |
| `MProfiler.getEventCategory(i)`     | int — category ID of event `i`               |
| `MProfiler.getCategoryName(catId)`  | `bytes` — human-readable category name       |
| `MProfiler.getThreadId(i)`          | int — thread that ran event `i`              |
| `MProfiler.getCPUId(i)`             | int — CPU core that ran event `i`            |
| `MProfiler.getAllCategories(list)`  | fills the passed list with all category names|

---

## Key API reference links

- `OpenMaya.MProfiler` — <https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_profiler.html>
- `OpenMaya.MProfilingScope` — the RAII class used to *create* events
- `cmds.profiler` — the MEL command for controlling the profiler UI
- Python standard library: [`json`](https://docs.python.org/3/library/json.html),
  [`csv`](https://docs.python.org/3/library/csv.html)

---

## Things to try next (exercises)

1. **Capture and analyze your scene.** Enable the profiler, play your scene
   for a few seconds, then export CSV. Open in a spreadsheet, sort by
   Duration descending, and identify the top 5 slowest event types. This is
   the core workflow for performance debugging.
2. **Add a `--category` filter.** Modify `profilerToCSV` to accept a category
   name (or list) and skip events that don't match. Useful when you only
   care about Rendering or Animation events.
3. **Add a thread breakdown.** Group events by `ThreadId` and print the total
   duration per thread. This tells you whether work is balanced across
   threads or concentrated on one.
4. **Strip the indexed form.** Read an indexed JSON output back and resolve
   the indexes to full names — i.e. decode `nameIdx: 3` to
   `name: "evaluate"`. Good practice working with two representations of the
   same data.
5. **Port to API 2.0.** Rewrite using `import maya.api.OpenMaya as om`. Most
   calls are identical; the main change is that `getEventName(i)` returns a
   `str` directly (no `.decode('ascii')` needed). Good API-1.0-to-2.0
   practice.
6. **Generate a flame graph.** Take the CSV output and feed it to a tool like
   `speedscope` or a Python flame-graph library. You've now built the data
   pipeline half of a serious performance tool.
7. **Add error handling.** What happens if `open(...)` fails (disk full,
   permission denied)? What if `getEventCount()` returns 0? Wrap the public
   functions in `try/except` and print friendly errors instead of crashing.

---

## Common pitfalls

* **You must capture first.** All three functions silently return if
  `getEventCount() == 0`. If your output file is empty or missing, you
  forgot to enable the profiler before running.
* **`getEventName(i)` returns `bytes`, not `str`** (API 1.0). The code
  calls `.decode('ascii', 'replace')` on it before writing. Forget the
  decode and you'll get Python `b'...'` literals in your JSON.
* **The `stripped` lambda matters.** Some instrumented code emits event
  names or descriptions with non-printable characters (control codes, stray
  UTF-8). Stripping to printable ASCII (32–126) avoids corrupt JSON / CSV.
* **Indexed JSON requires client-side decode.** `nameIdx: 3` is meaningless
  without the matching `eventNames` list at the top of the file. If you
  strip that list when post-processing, you've lost the data.
* **CSV `quoting=csv.QUOTE_NONNUMERIC` quotes strings, not numbers.** If you
  add a new column that's a string but you forget the writer assumes it's a
  float, the writer will crash. Use `csv.QUOTE_MINIMAL` if you're unsure.
* **The `initializePlugin` / `uninitializePlugin` stubs are no-ops.** Don't
  load this file as a plugin — it won't do anything. Just `import` it.
* **Output paths are relative to Maya's CWD.** On Windows that's usually
  `C:\Users\<user>\Documents\maya\projects\default\` or similar. Pass
  absolute paths to be sure where files land.
* **`getEventCategory(i)` returns an int, not a name.** You must call
  `getCategoryName(int)` to resolve it. Calling `getCategoryName` on the
  event index directly is a common mistake.
* **The file writes are not atomic.** If Maya crashes mid-dump you get a
  half-written JSON. For production tools, write to a temp file then rename
  on success.

---

## Source

Autodesk, *Maya Python API 2.0 Reference — python/api1/profilerDump.py*,
Maya 2027 (ENU).
<https://help.autodesk.com/cloudhelp/2027/ENU/MAYA-API-REF/py_ref/python_2api1_2profiler_dump_8py-example.html>
