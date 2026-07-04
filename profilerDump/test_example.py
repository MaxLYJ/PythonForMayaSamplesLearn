"""
test_example.py — runnable smoke test for profilerDump.py

Run this from the Maya Script Editor (Python tab). It:

    1. Clears the profiler buffer
    2. Starts sampling
    3. Does some measurable work (creates + deletes ~500 cubes)
    4. Stops sampling
    5. Asserts that events were captured
    6. Dumps the captured events to JSON (inline + indexed) and CSV

Expected output in the Script Editor:

    Captured events: <a few hundred or more>
    Done. Files written to: D:/2026MayaPython/profilerDump

See GUIDE.md in this folder for the full explanation.
"""

import os
import sys

# ── Make profilerDump.py importable ─────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import maya.cmds as cmds
import maya.OpenMaya as om
import profilerDump


# Where to write the output files. Override by setting PROFILER_OUT_DIR env
# var, otherwise defaults to this folder.
OUT_DIR = os.environ.get('PROFILER_OUT_DIR', HERE)


def run():
    # 1. Clean slate — stop sampling and clear the buffer
    cmds.profiler(sampling=False)
    cmds.profiler(reset=True)

    # 2. Start capturing
    cmds.profiler(sampling=True)

    # 3. Do some measurable work: fresh scene, ~500 cubes, then mass delete
    cmds.file(new=True, force=True)
    for _ in range(500):
        cmds.polyCube()
    cmds.select(all=True)
    cmds.delete()

    # 4. Stop capturing
    cmds.profiler(sampling=False)

    # 5. Sanity check — did we actually catch anything?
    count = om.MProfiler.getEventCount()
    print("Captured events:", count)
    if count == 0:
        raise RuntimeError(
            "No events captured. Make sure cmds.profiler(sampling=True) "
            "ran before the work block."
        )

    # 6. Dump in all three formats
    inline_path   = os.path.join(OUT_DIR, 'capture_inline.json')
    indexed_path  = os.path.join(OUT_DIR, 'capture_indexed.json')
    csv_path      = os.path.join(OUT_DIR, 'capture.csv')
    pretty_path   = os.path.join(OUT_DIR, 'capture_indexed_pretty.json')

    profilerDump.profilerToJSON(inline_path,  useIndex=False, durationMin=0.0)
    profilerDump.profilerToJSON(indexed_path, useIndex=True,  durationMin=0.0)
    profilerDump.profilerToCSV(csv_path, durationMin=0.0)
    profilerDump.profilerFormatJSON(indexed_path, pretty_path)

    print("Wrote:")
    for p in (inline_path, indexed_path, csv_path, pretty_path):
        print("  ", p)
    print("Done.")


if __name__ == "__main__":
    run()
