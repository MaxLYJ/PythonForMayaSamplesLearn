# Hour 2 — Key Points: Real Scripts — File Management & Renaming on Disk

> **Goal of hour 2:** Every student leaves having run a **pure-Python** script
> from a terminal that renames real files on disk — *no Maya involved* — and
> understands how the same loop pattern maps onto renaming nodes inside a
> Maya scene and onto asset-library management. The "aha": **Python isn't
> inside Maya, Python is a general-purpose tool that also happens to talk to
> Maya.**

**Time budget:** 60 minutes total. Five blocks:

```
┌──────────────┬──────────────────┬──────────────────┬──────────────┬─────────────┐
│ A: 10 min    │  B: 20 min       │  C: 15 min       │  D: 10 min   │  E: 5 min   │
│  Bridge      │  stdlib live:    │  argparse +      │  Disk ↔ Maya │  Exercise   │
│  "Python     │  os / shutil /   │  __name__ guard  │  comparison  │  + wrap     │
│  outside Maya"│  re              │  → CLI tool      │  (renamer2,  │             │
│              │                  │                  │  controller  │             │
│              │                  │                  │  Library)    │             │
└──────────────┴──────────────────┴──────────────────┴──────────────┴─────────────┘
```

**Repo demo this hour builds toward:** `commandLine/renamer_2027.py` (the
only demo in the repo with zero Maya dependency).

---

## BLOCK A — Bridge from Hour 1: "Python Outside Maya" (10 min)

### A1. Recap + the framing pivot (3 min)

Spend 60 seconds on what hour 1 left them with:

- `print`, variables, lists, `from maya import cmds`.
- We ran everything inside Maya's Script Editor.

Then make the pivot **explicitly** — this is the whole point of hour 2:

> **Say this out loud:** *"Everything you did in hour 1 ran inside Maya. But
> Python is older than Maya and bigger than Maya. Today we leave Maya closed
> and write a script that runs from a normal terminal — and it will rename
> hundreds of files in one second. Then we'll come back to Maya and see that
> the same loop pattern is how you rename hundreds of objects in a scene."*

### A2. The real-world scenario — why this matters (4 min)

Tell the **compositor story** (from hour 1's scenario list, now made concrete):

> *"A compositor rendered 500 frames. They're named `frame.0001.exr`,
> `frame.0002.exr`, …. But the pipeline expects
> `shot_24_beauty_v01.0001.exr`. Renaming 500 files by hand takes half an
> hour and you'll typo one. Or — you run one Python script and it's done in
> 0.2 seconds."*

Open a terminal, `cd` into a folder with a few dummy files, and **run the
finished tool cold** — before teaching how it works. (The payoff-first
principle from hour 1.)

```bash
# Set up the demo folder (do this before class)
mkdir -p ~/renamer_sandbox
cd ~/renamer_sandbox
touch frame_001.png frame_002.png frame_003.png keep_me.txt
```

Now run the finished tool:

```bash
python3 /abs/path/to/PythonForMayaSamplesLearn/commandLine/renamer_2027.py \
    frame render --duplicate
```

Everyone should see `render_001.png`, `render_002.png`, `render_003.png`
appear next to the originals. **The tool works. Now we open the hood.**

### A3. Open `renamer_2027.py` in VS Code (3 min)

Have everyone open `commandLine/renamer_2027.py` in VS Code. Point at the
top of the file:

```python
import argparse
import re
import os
import shutil
```

> **Say:** *"Four imports. None of them say `maya`. These are all Python
> standard library — they ship with Python itself. That's why this script
> runs without Maya."*

Tell the class: by the end of this hour, you'll understand every line of
this file. We'll build it up one module at a time.

---

## BLOCK B — The standard library live: `os`, `shutil`, `re` (20 min)

> **This is the core of the hour.** Students have never used Python without
> Maya. We build muscle memory for file operations by doing them **live in
> the Python REPL** (`python3` in a terminal), one operation at a time.
> Everyone follows along on their own machine.

### B1. `python3` REPL — your sandbox (2 min)

```bash
cd ~/renamer_sandbox
python3
```

You're now in the REPL (`>>>`). Anything you type runs immediately. This is
the fastest way to learn a new module. (To exit: `quit()` or Ctrl+D.)

### B2. The `os` module — talking to the operating system (8 min)

Walk through these one at a time. **Type each, hit enter, discuss the
output.**

```python
>>> import os
>>> os.getcwd()                      # where am I?
'/home/you/renamer_sandbox'

>>> os.listdir('.')                  # list files in current dir
['frame_001.png', 'frame_002.png', 'frame_003.png', 'keep_me.txt']

>>> os.path.join('a', 'b', 'c')      # builds a path with the RIGHT separator
'a/b/c'          # on Windows: 'a\\b\\c'

>>> os.path.exists('frame_001.png')  # does this file exist?
True
>>> os.path.exists('nope.txt')
False

>>> os.path.splitext('frame_001.png')   # split name and extension
('frame_001', '.png')
```

**Key teaching points to extract:**

| Function                | What it does                                          |
|-------------------------|-------------------------------------------------------|
| `os.getcwd()`           | "Get current working directory" — where you are.     |
| `os.listdir(path)`      | Returns a **list** of names in that folder. Flat, not recursive. |
| `os.path.join(a, b, …)` | Builds a path. **Always use this**, never `a + '/' + b` — Windows uses `\`. |
| `os.path.exists(p)`     | Boolean — does this path exist?                      |
| `os.path.splitext(f)`   | Returns `(name, extension)` tuple — the safe way to peel off an extension. |

> **Critical habit to instil:** *"Never build paths with string concatenation.
> Always `os.path.join`. Your script will then run on your Windows laptop AND
> your studio's Linux render farm without changes."*

### B3. The `os.rename` and `shutil.copy2` operations (5 min)

Now actually mutate the disk — this gets everyone's attention.

```python
>>> os.rename('frame_001.png', 'render_001.png')
>>> os.listdir('.')
['render_001.png', 'frame_002.png', 'frame_003.png', 'keep_me.txt']
```

> **Say:** *"That's it. That's a rename. There's no confirmation dialog, no
> undo. Python does exactly what you tell it. Which means we have to be
> careful — and that's why we'll add a `--duplicate` flag later."*

Now copy one:

```python
>>> import shutil
>>> shutil.copy2('render_001.png', 'backup_001.png')
>>> os.listdir('.')
```

> **Q to ask the class:** *"`shutil.copy2` vs `os.rename` — what's the
> difference?"* Answer: `copy2` **duplicates** (original stays); `rename`
> **moves** (original disappears). The `2` in `copy2` means "also copy
> metadata like modification time."

### B4. The `re` module — regex substitution (5 min)

Plain string replace is easy: `'frame_001'.replace('frame', 'render')`. But
what if you want to match *any* digits? That's regex.

```python
>>> import re
>>> re.sub(r'frame_(\d+)', r'render_\1', 'frame_001.png')
'render_001.png'

>>> re.sub(r'frame_(\d+)', r'render_\1', 'frame_999.png')
'render_999.png'
```

**Two ideas to convey:**

1. `r'frame_(\d+)'` — `\d+` means "one or more digits". Parens **capture** them.
2. `r'render_\1'` — `\1` means "insert whatever group 1 captured".

> **Don't go deep on regex.** Just enough that students recognise the syntax
> when they see the `--regex` flag in `renamer_2027.py`. Say: *"Regex is a
> whole language of its own — you'll learn it by needing it. Today, just
> know it exists and that `re.sub` is the substitute function."*

> Exit the REPL now: `quit()`.

---

## BLOCK C — `argparse` + the `__name__` guard: turning it into a CLI tool (15 min)

> We have all the building blocks. Now we package them as a **command-line
> tool** — something you can call as `python renamer.py frame render`.

### C1. The shape of `renamer_2027.py` (3 min)

Back in VS Code, look at the file's two-function structure:

```python
def main():              # ← entry point: parses CLI args, calls rename()
    ...

def rename(inString, outString, duplicate=True, ...):   # ← the worker
    ...

if __name__ == '__main__':
    main()
```

> **Say:** *"Two functions. `main()` is the wrapper that reads command-line
> flags. `rename()` is the actual work. Keeping them separate means we can
> `import` this file from another script and call `rename()` directly without
> ever touching the command line. This is called **library vs script** design
> and it's a habit worth building now."*

### C2. `argparse` — positional vs keyword arguments (8 min)

The whole of `main()` is `argparse` plumbing. Walk through the parser
building, drawing the parallel to function arguments from hour 1:

```python
parser = argparse.ArgumentParser(description="...")

# Positional arguments — REQUIRED, in order. Just like def f(a, b)
parser.add_argument('inString')     # ← notice: no dash prefix
parser.add_argument('outString')

# Keyword arguments — OPTIONAL, have defaults. Just like def f(a, b, c=True)
parser.add_argument('-d', '--duplicate', action='store_true')  # ← dash prefix
parser.add_argument('-r', '--regex', action='store_true')
parser.add_argument('-o', '--out')

args = parser.parse_args()
# args.inString, args.outString, args.duplicate (bool), args.regex (bool), args.out (str|None)
```

**Three teaching points:**

1. **Positional vs keyword — same idea as function arguments.**
   - `python renamer.py hello goodbye` → `inString='hello'`, `outString='goodbye'`.
   - `python renamer.py --duplicate hello goodbye` → same + `duplicate=True`.

2. **`action='store_true'` means "flag is a boolean switch."**
   - Without it: `--duplicate True` (need to give a value).
   - With it: just `--duplicate` (presence → True, absence → False).

3. **`argparse` builds `--help` for free.** Demo it:

   ```bash
   python3 /abs/path/to/.../renamer_2027.py --help
   ```

   > **Say:** *"Every argparse tool you ever write gets a correct `--help`
   > for free. This alone is worth using argparse over hand-parsing `sys.argv`."*

### C3. The `if __name__ == '__main__':` guard (4 min)

The single most confusing line for beginners. Spend 4 real minutes on it.

```python
if __name__ == '__main__':
    main()
```

**The explanation in 3 beats:**

1. Every Python file has a hidden variable called `__name__`.
2. When you **run** a file directly (`python renamer.py …`), Python sets
   `__name__` to the string `"__main__"`.
3. When you **import** the same file (`import renamer`), Python sets
   `__name__` to the module name (`"renamer"`).

So the guard says: *"If I'm being run directly, call `main()`. If I'm being
imported, just define the functions and sit quietly."*

**Prove it live** — this is the moment it clicks:

```bash
# Run directly — main() fires
python3 /abs/path/to/.../renamer_2027.py hello HI --duplicate
```

Then in a separate terminal, open a REPL:

```python
>>> import sys
>>> sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/commandLine')
>>> import renamer_2027       # ← imports, does NOT rename anything
>>> renamer_2027.rename('hello', 'HI', inDir=r'/home/you/renamer_sandbox')  # ← explicit call
```

> **Say:** *"Same file, two completely different behaviours. Run it → it's
> a tool. Import it → it's a library. That's the `__name__` guard doing its
> job."*

---

## BLOCK D — Disk ↔ Maya comparison (10 min)

> **This is the connective tissue back to the rest of the course.** Same
> loop shape, different APIs. Show it side by side.

### D1. The big side-by-side table (5 min)

Open `commandLine/renamer_2027.py` in the left pane and
`objectRenamer/renamer2_2027.py` in the right. Walk the table:

| Concept                | On disk (this hour)                                  | In a Maya scene (next hour, hour 3)                       |
|------------------------|------------------------------------------------------|-----------------------------------------------------------|
| **List things**        | `os.listdir(inDir)`                                  | `cmds.ls(selection=True, dag=True)`                       |
| **List with filter**   | `[f for f in os.listdir(d) if f.endswith('.png')]`   | `cmds.ls(type='mesh')`                                    |
| **Get the short name** | `os.path.basename(path)` or `f.split('\|')[-1]`      | `obj.split('\|')[-1]`                                     |
| **Get the "type"**     | `os.path.splitext(f)[1]` → `.png`, `.ma`             | `cmds.objectType(node)` → `'mesh'`, `'joint'`             |
| **Rename one**         | `os.rename(src, dest)`                               | `cmds.rename(obj, newName)`                               |
| **Copy / duplicate**   | `shutil.copy2(src, dest)`                            | `cmds.duplicate(obj)`                                     |
| **Skip a thing**       | `if f.startswith('.'): continue`                     | `if objType == 'camera': continue`                        |
| **Sort parents-first** | n/a (files are flat)                                 | `objects.sort(key=len, reverse=True)`                     |
| **Walk hierarchy**     | `os.walk(dir)`                                       | `cmds.listRelatives(allDescendents=True)`                 |
| **Persist to disk**    | `open(path, 'w')` / `json.dump(d, f)`                | `cmds.file(save=True)`                                    |

> **The line to land the block on:** *"Look at those two columns. Every row
> is the same idea expressed in two dialects. Once you can read one column,
> you can read the other. That's why we spent an hour on disk files — it
> makes the Maya version trivial."*

### D2. `controllerLibrary` — the bridge example (5 min)

Open `controllerLibrary/controllerLibrary_2027.py`. Point at the imports
(line 8 onward):

```python
import json         # ← from this hour (stdlib, disk side)
import os           # ← from this hour (stdlib, disk side)
from maya import cmds   # ← from hour 1 (Maya side)
```

Then point at the `save()` method — it uses **both**:

```python
DIRECTORY = os.path.join(cmds.internalVar(userAppDir=True), 'controllerLibrary')
#           ^^^ disk-side                    ^^^ Maya-side

path = os.path.join(directory, '%s.ma' % name)    # build a path on disk
cmds.file(rename=path)                            # tell Maya to save there
cmds.file(save=True, force=True)                  # Maya writes the file

with open(infoFile, 'w') as f:                    # stdlib writes a sidecar JSON
    json.dump(info, f, indent=4)
```

> **Say:** *"This is what real tools look like. `controllerLibrary` is half
> disk management (where do files live, how do I find them, how do I write
> a JSON index) and half Maya (export the controller, take a screenshot via
> playblast). The two halves are inseparable. That's why hour 2 matters even
> though it has no Maya in it — every tool you build from here on will use
> these `os` / `json` / `shutil` skills alongside `cmds`."*

The same `find()` pattern from renamer shows up here too — `os.listdir`,
filter by extension, loop:

```python
# controllerLibrary.find():
files = os.listdir(directory)
mayaFiles = [f for f in files if f.endswith('.ma')]   # ← list comprehension!
for ma in mayaFiles:
    name, ext = os.path.splitext(ma)
    ...
```

> **Call this out:** *"That's the exact loop shape from `renamer_2027.py`.
> List → filter → loop → process. We just learned it on plain files; here it
# is indexing a controller library."*

---

## BLOCK E — Exercise brief + wrap (5 min)

### E1. The exercise (3 min)

Hand out (or display) the exercise. **Students do this in the last 5 minutes
of class or as homework:**

> **Exercise:** Modify `renamer_2027.py` so every output file gets a
> version suffix `_v01` before the extension. So `frame_001.png` becomes
> `frame_001_v01.png`.
>
> **Hint:** use `os.path.splitext` to split `'frame_001.png'` into
> `('frame_001', '.png')`, then reassemble as `name + '_v01' + ext`.
>
> **Bonus:** add a `--version` flag that takes a number, so you can do
> `--version 2` and get `_v02`.

Reference solution shape (don't show them — let them try first):

```python
name, ext = os.path.splitext(f)
new_name = name + '_v01' + ext
```

### E2. What they now know — wrap list (2 min)

End the hour by listing what's now in their toolkit:

- ✅ The Python standard library exists and is importable without Maya
- ✅ `os.getcwd`, `os.listdir`, `os.path.join`, `os.path.exists`, `os.path.splitext`, `os.rename`
- ✅ `shutil.copy2` for duplication
- ✅ `re.sub` for regex substitution
- ✅ `argparse` for CLI tools (positional vs keyword args, `--help` for free)
- ✅ The `if __name__ == '__main__':` guard — script vs library
- ✅ The **list → filter → loop → process** pattern (same on disk and in Maya)
- ✅ How `controllerLibrary` bridges disk-side and Maya-side Python

**Preview hour 3:** *"Next hour we take this exact loop pattern into a Maya
scene. We'll build `objectRenamer` — select 50 controls, run one script, all
of them get suffixes (`_grp`, `_jnt`, `_geo`) based on their type. Same
shape as today's renamer; different API."*

---

## Common student questions to anticipate

| Question                                                       | Answer to give                                                                                                              |
|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| "Do I need to install Python separately for this?"             | No. Use `python3` from your system (install from python.org if needed). This hour deliberately doesn't use `mayapy` — the whole point is the script runs anywhere. |
| "Why `os.path.join` and not just `'/'`?"                       | Windows uses `\`, Unix uses `/`. `os.path.join` picks the right one. Scripts that hand-concat paths break across studios.    |
| "What's the difference between `shutil.copy`, `copy2`, `copyfile`?" | `copyfile` = contents only. `copy` = contents + permissions. `copy2` = contents + permissions + metadata (mtime). For renames you usually want `copy2`. |
| "`args.duplicate` defaults to `False` but the function's `duplicate=True`. Why?" | The `--duplicate` flag uses `action='store_true'` → False unless passed. So the CLI is **destructive by default**; the function is **safe by default**. Always pass `-d` on the command line if you want to keep originals. (See `commandLine/HowToStartCommandLine.md` Q2.) |
| "Why `re.sub` and not just `str.replace`?"                     | `str.replace` is literal — `'\d+'` would mean nothing. `re.sub` understands patterns and capture groups. Use plain replace for "replace the word hello with goodbye"; use regex for "match any digits." |
| "Can I run `renamer.py` from inside Maya's Script Editor?"     | Technically yes (`subprocess.run`), but there's no reason to — the tool has no Maya dependency. Run it from a normal terminal. The whole point of the demo is that Python-for-Maya skills transfer to ordinary CLI tools. |
| "Does `os.listdir` recurse into subdirectories?"               | No — it returns only the immediate children of the folder. Use `os.walk(dir)` for recursion. (Left as the #1 advanced extension in `HowToStartCommandLine.md`.) |
| "Why does `cmds.ls()` return long paths with `\|`?"            | That's Maya's scene-graph separator. `group\|child\|grandchild`. We'll cover it next hour — same `split('\|')[-1]` trick as today's `splitext`. |
| "What if my regex is wrong — will it destroy my files?"        | It can. Always run with `--duplicate` first to verify the output, then re-run without it. (Exercise for students: add a `--dry-run` flag that prints planned renames without touching disk.) |
| "Why is `controllerLibrary` both disk and Maya?"               | Because a real asset library is a *folder of files on disk* (`.ma`, screenshots, JSON index) plus *Maya knowledge* (how to export, how to take a viewport screenshot). Most production tools are this hybrid. |

---

## Timing safety margin

- Block A: 10 min (mostly narrative — hard to overrun)
- Block B: 20 min (REPL live-coding — protect this; it's the substance)
- Block C: 15 min (argparse + `__name__` guard — the `__name__` demo alone needs 4 min)
- Block D: 10 min (comparison — can compress to 7 if running late)
- Block E: 5 min (exercise brief + wrap)
- **= 60 min exactly.**

> **If you're running late:** cut A2 (the finished-tool cold demo) down to
> 90 seconds — just show the output, don't teach the command yet. **Do not
> cut Block B.** The REPL muscle memory is the whole value of the hour.

> **If you have extra time:** walk through Advanced Direction #2 in
> `commandLine/HowToStartCommandLine.md` (add a `--dry-run` flag). It's a
> 10-minute exercise that reinforces argparse and introduces a real
> safety pattern.
