# objectRenamer/renamer2 — Functions, Dictionaries, and Error Handling

A refactor of [`renamer1`](./renamer1_2027.py) that packages the renaming
logic into a reusable **function** with a docstring, default arguments,
dictionary-based suffix lookup, and proper error handling.

**The improvement over renamer1:** instead of a flat script that runs once,
`renamer2` exposes `rename(selection=False)` — call it from anywhere, get
back a list of what it changed, and it tells you clearly when you misused it.

> ⚠️ **The catch:** this file only **defines** the `rename` function.
> Running the file does nothing visible — you have to *call* it.

---

## Quick start

1. Set up something to rename. Easiest: create a few objects of mixed types:

   ```python
   from maya import cmds
   cmds.polyCube()
   cmds.joint()
   cmds.spaceLocator()
   cmds.camera()                    # cameras are skipped on purpose
   cmds.select(all=True)
   ```

2. Import and call `rename`:

   ```python
   import sys
   sys.path.insert(0, r'D:\2026MayaPython\objectRenamer')

   import renamer2_2027 as renamer2

   renamed = renamer2.rename(selection=True)
   print("Renamed:", renamed)
   ```

You should see output like:
```
Renamed: ['|pCube1_geo', '|joint1_jnt', '|locator1_grp']
```

The camera is missing from the list because `SUFFIXES["camera"] = None` —
the function's way of saying "skip this type."

---

## Why doesn't the file do anything when I run it?

Same pattern as the other teaching demos. The file **defines**:

```python
SUFFIXES = {"mesh": "geo", "joint": "jnt", "camera": None}
DEFAULT = "grp"

def rename(selection=False):
    ...
    return objects
```

…without ever calling `rename()`. Defining = writing the recipe. Calling =
cooking the meal. See [`gearCreator/README.md`](../gearCreator/README.md)
for the longer version of this explanation.

The point of structuring it this way is **reusability** — you can
`import renamer2` from any other script and call `rename()` without
accidentally triggering it at import time.

---

## The `rename()` API

Read the function signature and docstring (lines 35–46):

```python
def rename(selection=False):
    """
    Renames objects by adding suffixes based on the object type
    Args:
        selection (bool): Whether we should use the selection or not. Defaults to False

    Raises:
        RuntimeError: If nothing is selected

    Returns:
        list: A list of all the objects renamed
    """
```

Three things to internalize:

1. **`selection=False` is a default.** Callers can override it (`rename(selection=True)`)
   or omit it (`rename()`).
2. **`Raises: RuntimeError`** is a *promise* in the docstring. If you call
   `rename(selection=True)` with nothing selected, the function deliberately
   blows up with a clear message — not a silent no-op.
3. **`Returns: list`** means you can capture the result (`renamed = rename(...)`)
   and use it for logging, undo, or chaining.

### Three ways to call it

```python
# Rename the current selection
renamer2.rename(selection=True)

# Rename everything in the scene (DAG hierarchy)
renamer2.rename()                              # selection defaults to False
renamer2.rename(selection=False)               # explicit, same thing

# Capture the result
renamed = renamer2.rename(selection=True)
print("Changed %d objects" % len(renamed))
```

---

## The dictionary + `.get()` pattern (the key new concept)

Lines 17–24, 83:

```python
SUFFIXES = {
    "mesh": "geo",
    "joint": "jnt",
    "camera": None,           # None = skip
}
DEFAULT = "grp"

# In the loop:
suffix = SUFFIXES.get(objType, DEFAULT)
```

Compare this to `renamer1`, which used a chain of `if/elif/else`:

```python
# renamer1 style — verbose
if objType == "mesh":       suffix = 'geo'
elif objType == "joint":    suffix = 'jnt'
elif objType == 'camera':   continue
else:                       suffix = 'grp'

# renamer2 style — table lookup
suffix = SUFFIXES.get(objType, DEFAULT)
```

**Why the dict is better:**
- **Add a new type by editing data, not code.** Just add a line to `SUFFIXES`.
- **`.get(key, default)`** returns the default if the key isn't found — no
  KeyError, no `if` chain.
- **`None` is a real value.** The `camera: None` entry + the
  `if not suffix: continue` check on line 87 means cameras get skipped.

> **Teaching moment:** Whenever you write a 5-case `if/elif` chain that's
> just mapping inputs to outputs, you almost always want a dict instead.

---

## What's different from renamer1 (the whole point of this demo)

| Aspect                   | renamer1                                  | renamer2                                            |
|--------------------------|-------------------------------------------|-----------------------------------------------------|
| Code shape               | Flat script, runs top to bottom           | One function, callable from anywhere                |
| Suffix lookup            | `if/elif/else` chain                      | Dict + `.get()`                                     |
| Error on empty selection | Silent no-op (or unexpected behavior)     | Raises `RuntimeError` with a clear message          |
| Skipping already-renamed | Not handled                               | `if shortName.endswith('_'+suffix): continue`       |
| Return value             | None — you can't tell what changed        | A list of full paths renamed                        |
| Docstring                | None                                      | Full Args / Raises / Returns contract               |
| Camera handling          | Hardcoded `continue`                      | `None` sentinel in the dict → `continue`            |

**The meta-lesson:** renamer1 → renamer2 is a microcosm of "script vs.
function." Scripts are great for one-off tasks. Functions are reusable,
testable, and document themselves.

---

## Common pitfalls

| Symptom                                                      | Cause                                                                              | Fix                                                                              |
|--------------------------------------------------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'renamer2_2027'`       | Folder not on sys.path                                                             | Add `sys.path.insert(0, r'.../objectRenamer')` before importing.                 |
| `RuntimeError: You don't have anything selected`             | You called `rename(selection=True)` with nothing picked                            | Select something first, or call `rename()` (no args) to do the whole scene       |
| Objects got renamed twice (e.g. `cube_geo_geo`)              | You ran it twice without checking                                                  | The `endswith('_'+suffix)` guard prevents this — re-running should be a no-op. If you see double suffixes, you edited the code |
| Camera got renamed to `_grp`                                 | You deleted the `"camera": None` line from SUFFIXES                                | Cameras need the `None` value to trigger the skip logic                          |
| `IndexError` on `objects.index(obj)`                         | You renamed the object before this line runs, so the list still has the old name   | That's exactly why line 103 rewrites the list — make sure you didn't delete it   |
| Function returns an empty list                               | Nothing in the scene matched any SUFFIXES key, and everything fell through to skip | Add some geometry or joints to test against                                      |

---

## Exercises

1. **Add a `nurbsCurve` → `ctrl` mapping.** Controls currently fall through
   to `DEFAULT = "grp"`. Add the entry to `SUFFIXES` and confirm controls
   now get `_ctrl`.
2. **Add a `prefix` argument.** Default to empty string. When provided,
   prepend it: `prefix='char1_'` → `char1_cube_geo`. Useful for separating
   characters in a merged scene.
3. **Add a `dry_run` argument.** When `True`, print what *would* be renamed
   but don't actually do it. Invaluable for previewing on big scenes.
4. **Don't add a suffix twice.** The `endswith` check is case-sensitive
   (`_GRP` slips through). Make it case-insensitive with
   `shortName.lower().endswith('_'+suffix)`.
5. **Handle cameras differently.** Instead of skipping, give them a `_cam`
   suffix. Just change the dict entry from `None` to `"cam"`.
6. **Return a structured result.** Instead of a list of strings, return a
   list of `(oldName, newName, suffix)` tuples. Now callers can build
   undo logs.

---

## Source

This is a teaching demo from the original [PythonForMayaSamples](https://github.com/dgovil/PythonForMayaSamples)
repo. The `_2027.py` versions are verified Python-3-compatible copies for
Maya 2022+.
