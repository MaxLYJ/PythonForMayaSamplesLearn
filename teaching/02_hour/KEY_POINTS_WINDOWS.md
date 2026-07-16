# Hour 2 — Key Points (Windows edition): Real Scripts — File Management & Renaming on Disk

> **Companion to:** [`KEY_POINTS.md`](./KEY_POINTS.md) (the macOS/Linux edition).
> This is the **same lesson plan** with every shell command, path, and REPL
> transcript translated to **Windows / PowerShell**. Teach from whichever
> matches your machine — the Python is identical, only the shell differs.
>
> **Why a separate file?** The original `KEY_POINTS.md` uses `python3`,
> `mkdir -p`, `touch`, `~/` paths, and Ctrl+D. None of those work as-is on a
> stock Windows machine. This version uses what ships with Windows 10/11:
> **PowerShell** (the default terminal) and the **`python`** command.

> **Goal of hour 2:** Every student leaves having run a **pure-Python** script
> from a terminal that renames real files on disk — *no Maya involved* — and
> understands how the same loop pattern maps onto renaming nodes inside a
> Maya scene and onto asset-library management. The "aha": **Python isn't
> inside Maya, Python is a general-purpose tool that also happens to talk to
> Maya.**

**Time budget:** 60 minutes total. Five blocks (identical structure to the
macOS/Linux edition):

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
only demo in the repo with zero Maya dependency). You can find it at:

```
<repoRoot>\commandLine\renamer_2027.py
```

> **Note on the filename.** There is no file called `renamer2027.py` in this
> repo. The convention is an **underscore** before the year:
> `renamer_2027.py`. See `commandLine/` for:
> `renamer.py` (Py2 teaching original) and `renamer_2027.py` (the one you run).
> The same naming rule applies to `objectRenamer/renamer1_2027.py` and
> `objectRenamer/renamer2_2027.py`, which Hour 3 uses.

---

## Windows prerequisites — set these up BEFORE class

This hour runs Python **without Maya**, so every student needs a working
`python` on their machine *before* the clock starts. Walk the class through
the three steps below in the last 10 minutes of Hour 1 (or in a pre-class
email). **Do not skip Step 1** — installing Python live during Hour 2 will
burn 15 minutes you can't spare.

### Step 1 — Check whether Python is already installed

Open **PowerShell** (press the `Win` key, type `powershell`, press Enter) and
run:

```powershell
python --version
py --version
```

Interpret the output:

| What you see                                            | Meaning                                                                                           |
|---------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `Python 3.10.x` (or higher) from **either** command    | ✅ Python is installed. Go to **Step 3** (verify stdlib).                                          |
| `Python 2.7.x`                                          | ⚠️ Too old for this course. Install Python 3 from python.org (Step 2).                            |
| `'python' is not recognized...` AND `'py' is not...`   | ❌ Python is not installed. Go to **Step 2**.                                                      |
| A **Microsoft Store** window pops up                    | ❌ The Windows "app execution alias" is intercepting the command. See **Gotcha A** below, then install real Python (Step 2). |

> **`python` vs `py` vs `python3` on Windows.** After a normal python.org
> install, `python` is on PATH. The launcher `py` is installed by the same
> installer and is the officially recommended entry point — `py -3` always
> runs the newest Python 3 you have. There is **no `python3` alias** on
> Windows by default, so throughout this doc we use `python`.

### Step 2 — Install Python from python.org (only if Step 1 failed)

This is the single most error-prone step for beginners — the installer has
**two checkboxes that are unchecked by default and MUST be ticked**, or
nothing in this hour will work. Walk through it slowly.

1. **Download the installer.**
   - Open a browser and go to **<https://www.python.org/downloads/>**.
   - The page auto-detects Windows and shows a big yellow button labelled
     **"Download Python 3.x.x"**. Click it. (Any 3.10 or newer is fine for
     this course; the exact patch version does not matter.)
   - You'll get a file named something like `python-3.12.3-amd64.exe`.

2. **Run the installer — but STOP on the first screen.**
   - Double-click the downloaded `.exe`.
   - The first screen has a big "Install Now" button. **Do NOT click it yet.**
   - At the **bottom** of that window are two checkboxes. Tick **BOTH**:
     - ☑ **Add python.exe to PATH**  ← *this is the critical one; without it `python` won't be recognised in PowerShell*
     - ☑ **Use admin privileges when installing py.exe**  ← *installs the `py` launcher for all users*
   - Screenshot reference (describe it to the class): the two checkboxes sit
     just above the "Install Now" / "Customize installation" buttons and are
     **unchecked by default** — students will miss them if they rush.

3. **Click "Install Now".**
   - Wait ~30 seconds. Windows may show a UAC prompt — click **Yes**.
   - When it finishes, you'll see a *"Setup was successful"* screen.

4. **(Recommended) Disable the PATH length limit.**
   - On the final screen there's a button labelled **"Disable path length
     limit"**. Click it. This prevents obscure "path too long" errors later
     when you start installing packages. Requires admin — if you don't have
     it, skip; it's not blocking for this hour.

5. **Close the installer AND close the PowerShell window you opened in
   Step 1, then open a fresh PowerShell.**
   - This is non-negotiable: **PATH changes only apply to new shells.** If a
     student keeps the old PowerShell open, `python --version` will still
     fail even though the install succeeded. This is the #1 false-alarm in
     the whole hour.

6. **Re-run Step 1's check.** You should now see:
   ```powershell
   python --version     # -> Python 3.12.3  (or similar)
   py --version         # -> Python 3.12.3
   ```

> **PowerShell vs cmd.** This doc targets PowerShell (the Win10/11 default).
> Where cmd.exe differs materially, a callout notes it. If you only have cmd,
> the Python lines are all identical — only file creation and `cd ~` differ.

### Step 3 — Verify the standard library is intact

Once `python --version` works, confirm the four stdlib modules this hour
needs are importable (they ship with Python itself — no `pip install`
required):

```powershell
python -c "import os, shutil, re, argparse; print('stdlib ok')"
# Expected output:  stdlib ok
```

If this prints `stdlib ok`, the student is ready for Hour 2. If it errors
with `ModuleNotFoundError`, something is wrong with the install — uninstall
from *Settings → Apps*, then redo Step 2 from scratch.

### Install gotchas (anticipate these)

**Gotcha A — Typing `python` opens Microsoft Store.**
Windows 10/11 ships with "App execution aliases" that intercept `python` and
`python3` and route them to the Store instead of running real Python. Fix:

```
Settings → Apps → Advanced app settings → App execution aliases
→ turn OFF both "App Installer  python.exe" and "python3.exe"
```

After that, `python` will correctly find the python.org install (or report
"not recognized" if you haven't installed it yet, which is the honest signal).

**Gotcha B — "I ticked the PATH box but `python` still isn't recognised."**
You didn't open a **new** PowerShell after installing. Close every PowerShell
window, open a fresh one, retry. (Step 2.5 above.)

**Gotcha C — "It installed to my AppData folder and feels weird."**
That's normal. The per-user install (the default "Install Now") lands in
`C:\Users\<you>\AppData\Local\Programs\Python\Python3x\`. You never need to
visit that folder — `python` and `py` on the command line are all you'll use.

**Gotcha D — Should I use the Microsoft Store Python instead?**
It works, but **don't** for this course. The Store version sandboxes file
access, which will bite you the moment a script tries to read or write
outside your `Documents` folder (exactly what `renamer_2027.py` does). Use
the python.org installer — it has unrestricted filesystem access, which is
what a file-renaming tool needs.

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

Open PowerShell, `cd` into a folder with a few dummy files, and **run the
finished tool cold** — before teaching how it works. (The payoff-first
principle from hour 1.)

```powershell
# Set up the demo folder (do this before class)
$sandbox = "$HOME\renamer_sandbox"
New-Item -ItemType Directory -Force -Path $sandbox | Out-Null
Set-Location $sandbox
'frame_001.png','frame_002.png','frame_003.png','keep_me.txt' |
    ForEach-Object { New-Item -ItemType File -Path $_ } | Out-Null

dir       # confirm the four files exist
```

> **cmd.exe equivalent** (if a student is on cmd instead of PowerShell):
> ```cmd
> mkdir %USERPROFILE%\renamer_sandbox
> cd %USERPROFILE%\renamer_sandbox
> type nul > frame_001.png
> type nul > frame_002.png
> type nul > frame_003.png
> type nul > keep_me.txt
> dir
> ```

Now run the finished tool (note `-d` so we keep the originals — see Q2 in the
QA table about why this matters):

```powershell
python C:\abs\path\to\PythonForMayaSamplesLearn\commandLine\renamer_2027.py `
    frame render -d
```

> The backtick `` ` `` is PowerShell's **line continuation** character (on the
> macOS/Linux edition it would be a backslash `\`). You can also write the
> whole command on one line.

Everyone should see `render_001.png`, `render_002.png`, `render_003.png`
appear next to the originals. **The tool works. Now we open the hood.**

### A3. Open `renamer_2027.py` in VS Code (3 min)

Have everyone open `commandLine\renamer_2027.py` in VS Code. Point at the
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
> the Python REPL** (`python` with no arguments), one operation at a time.
> Everyone follows along on their own machine.

### B1. `python` REPL — your sandbox (2 min)

```powershell
Set-Location $HOME\renamer_sandbox
python
```

You're now in the REPL (`>>>`). Anything you type runs immediately. This is
the fastest way to learn a new module. **To exit: type `quit()` or press
Ctrl+Z then Enter** (NOT Ctrl+D — that's the macOS/Linux convention and does
nothing in the Windows REPL).

### B2. The `os` module — talking to the operating system (8 min)

Walk through these one at a time. **Type each, hit enter, discuss the
output.** (Sample transcript shown on Windows; `C:\Users\you` is your
`$HOME`.)

```python
>>> import os
>>> os.getcwd()                      # where am I?
'C:\\Users\\you\\renamer_sandbox'
# Note the doubled backslashes — that is just Python repr-escaping a single '\'.

>>> os.listdir('.')                  # list files in current dir
['frame_001.png', 'frame_002.png', 'frame_003.png', 'keep_me.txt']

>>> os.path.join('a', 'b', 'c')      # builds a path with the RIGHT separator
'a\\b\\c'         # ← on Windows. On macOS/Linux the same call returns 'a/b/c'.

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
| `os.path.join(a, b, …)` | Builds a path. **Always use this**, never `a + '\\' + b` — macOS/Linux uses `/`. |
| `os.path.exists(p)`     | Boolean — does this path exist?                      |
| `os.path.splitext(f)`   | Returns `(name, extension)` tuple — the safe way to peel off an extension. |

> **Critical habit to instil:** *"Never build paths with string concatenation.
> Always `os.path.join`. Your script will then run on your Windows laptop AND
> your studio's Linux render farm without changes."*
>
> (The macOS/Linux edition shows `'a/b/c'` from the same call. On Windows you
> see `'a\\b\\c'`. **The function is identical; only the separator differs** —
> which is the whole point of using `os.path.join`.)

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

> Exit the REPL now: type `quit()` (or Ctrl+Z, Enter).

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

   ```powershell
   python C:\abs\path\to\...\renamer_2027.py --help
   ```

   > **Say:** *"Every argparse tool you ever write gets a correct `--help`
   > for free. This alone is worth using argparse over hand-parsing
   > `sys.argv`."*

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

```powershell
# Run directly — main() fires
python C:\abs\path\to\...\renamer_2027.py hello HI -d
```

Then in a separate PowerShell window, open a REPL:

```python
>>> import sys
>>> sys.path.insert(0, r'C:\abs\path\to\PythonForMayaSamplesLearn\commandLine')
>>> import renamer_2027       # ← imports, does NOT rename anything
>>> renamer_2027.rename('hello', 'HI', inDir=r'C:\Users\you\renamer_sandbox')  # ← explicit call
```

> **Say:** *"Same file, two completely different behaviours. Run it → it's
> a tool. Import it → it's a library. That's the `__name__` guard doing its
> job."*

---

## BLOCK D — Disk ↔ Maya comparison (10 min)

> **This is the connective tissue back to the rest of the course.** Same
> loop shape, different APIs. Show it side by side.

### D1. The big side-by-side table (5 min)

Open `commandLine\renamer_2027.py` in the left pane and
`objectRenamer\renamer2_2027.py` in the right. Walk the table:

| Concept                | On disk (this hour)                                  | In a Maya scene (next hour, hour 3)                       |
|------------------------|------------------------------------------------------|-----------------------------------------------------------|
| **List things**        | `os.listdir(inDir)`                                  | `cmds.ls(selection=True, dag=True)`                       |
| **List with filter**   | `[f for f in os.listdir(d) if f.endswith('.png')]`   | `cmds.ls(type='mesh')`                                    |
| **Get the short name** | `os.path.basename(path)` or `f.split('\\')[-1]`      | `obj.split('\|')[-1]`                                     |
| **Get the "type"**     | `os.path.splitext(f)[1]` → `.png`, `.ma`             | `cmds.objectType(node)` → `'mesh'`, `'joint'`             |
| **Rename one**         | `os.rename(src, dest)`                               | `cmds.rename(obj, newName)`                               |
| **Copy / duplicate**   | `shutil.copy2(src, dest)`                            | `cmds.duplicate(obj)`                                     |
| **Skip a thing**       | `if f.startswith('.'): continue`                     | `if objType == 'camera': continue`                        |
| **Sort parents-first** | n/a (files are flat)                                 | `objects.sort(key=len, reverse=True)`                     |
| **Walk hierarchy**     | `os.walk(dir)` or the `find_files()` helper below    | `cmds.listRelatives(allDescendents=True)`                 |
| **Persist to disk**    | `open(path, 'w')` / `json.dump(d, f)`                | `cmds.file(save=True)`                                    |

> **The line to land the block on:** *"Look at those two columns. Every row
> is the same idea expressed in two dialects. Once you can read one column,
> you can read the other. That's why we spent an hour on disk files — it
> makes the Maya version trivial."*

> **Windows-only note on `split('\\')[-1]`:** on macOS/Linux the path
> separator is `/`, so the same trick there is `split('/')[-1]`. The
> portable version is `os.path.basename(path)` — it picks the right
> separator for the platform. This is exactly why we drilled
> `os.path.join` in Block B.

### D2. `controllerLibrary` — the bridge example (5 min)

Open `controllerLibrary\controllerLibrary_2027.py`. Point at the imports
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
> is indexing a controller library."*

### D3. Bonus — the recursive `find_files()` helper (optional; teach if you have extra time)

`renamer_2027.py` ships a second worker — **`find_files(directory, name=None,
pattern=None, recursive=True)`** — which is a *genuinely recursive* function.
When it meets a subdirectory, it calls *itself* on that subdirectory and
gathers the results. Use it the moment a student asks "how do I find a file
that's buried somewhere in my project?":

```python
>>> import sys
>>> sys.path.insert(0, r'C:\abs\path\to\PythonForMayaSamplesLearn\commandLine')
>>> import renamer_2027
>>> # Where is body_ctrl.ma, anywhere under D:\assets?
>>> renamer_2027.find_files(r'D:\assets', name='body_ctrl.ma')
['D:\\assets\\rigs\\chars\\body_ctrl.ma']
>>> # Every .ma file anywhere under the project root
>>> renamer_2027.find_files(r'D:\my_project', pattern='.ma')
['D:\\my_project\\scenes\\a.ma', 'D:\\my_project\\shots\\b.ma']
```

#### How the recursion works — the walkthrough to give students

Open `commandLine\renamer_2027.py` at the `find_files` definition and talk
through the function in **four beats**. This is the first time in the course
students see a function that calls itself, so go slowly:

1. **Entry point.** The caller hands the function a folder, e.g.
   `find_files(r'D:\proj', pattern='.ma')`. The function's job is to return
   every matching file *anywhere* under that folder — not just the top level.

2. **Loop over the folder's children.** `os.listdir(directory)` returns the
   immediate children — a flat list of filenames and subfolder names. The
   function then branches on each one.

3. **Branch on each entry — this is where the recursion lives:**
   - **Subdirectory → RECURSIVE CASE.** The function **calls itself** on the
     subfolder (`find_files(full_path, ...)`) and folds the returned list
     into its own `matches` with `.extend(...)`. That self-call repeats the
     exact same logic one level deeper — and so on, until a folder has no
     more subfolders.
   - **File → BASE CASE.** Apply the `name` / `pattern` filters and either
     append the path to `matches` or skip it. No further recursion happens
     here; this is where the descent stops for this branch.

4. **Return.** Once the loop finishes, return `sorted(matches)`. Each
   recursive call returns its own sorted sublist, which the parent folds in,
   so the final list comes out fully sorted regardless of how deep each
   match was.

**The question a sharp student will ask:** *"How does this not loop
forever?"* Answer: a filesystem is a **finite tree**. Each recursive call
descends into a strictly smaller subtree (one specific subfolder), and
`os.listdir` does not follow symlinks as directories by default, so there
is no cycle to infinite-loop on. Every branch eventually hits a folder with
only files in it — the base case — and returns.

**One more thing to call out before moving on:** the `name` and `pattern`
filters are passed *unchanged* through every recursive call, so a match at
any depth surfaces in the final list. Students sometimes expect deep files
to be filtered out; they aren't.

> **Say:** *"This is the recursive cousin of the `os.listdir` loop we just
> wrote. It is the on-disk analogue of `cmds.listRelatives(allDescendents=True)`,
> which you'll meet next hour for walking a Maya hierarchy. Same idea —
> 'walk every descendant, do something at each leaf' — different API."*
>
> The relevant source lives in `commandLine\renamer_2027.py` (and is mirrored
> in the Py2 teaching original `renamer.py`). The two comment lines labelled
> `# RECURSIVE CASE` and `# BASE CASE` are the branches you just walked
> through — point at them in the editor as you talk.

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

> **Bonus exercise for fast students:** turn `find_files()` into
> `find_files_ui()` — a tiny function that prints each match prefixed with
> its index, so the user can pick one. Reinforces both recursion and
> `enumerate()`.

### E2. What they now know — wrap list (2 min)

End the hour by listing what's now in their toolkit:

- ✅ The Python standard library exists and is importable without Maya
- ✅ `os.getcwd`, `os.listdir`, `os.path.join`, `os.path.exists`, `os.path.splitext`, `os.rename`
- ✅ `shutil.copy2` for duplication
- ✅ `re.sub` for regex substitution
- ✅ `argparse` for CLI tools (positional vs keyword args, `--help` for free)
- ✅ The `if __name__ == '__main__':` guard — script vs library
- ✅ The **list → filter → loop → process** pattern (same on disk and in Maya)
- ✅ A genuinely **recursive** file finder (`find_files`) for walking folders
- ✅ How `controllerLibrary` bridges disk-side and Maya-side Python
- ✅ The Windows shell equivalents: `python`, `New-Item`, `$HOME`, Ctrl+Z to exit the REPL

**Preview hour 3:** *"Next hour we take this exact loop pattern into a Maya
scene. We'll build `objectRenamer` — select 50 controls, run one script, all
of them get suffixes (`_grp`, `_jnt`, `_geo`) based on their type. Same
shape as today's renamer; different API."*

---

## Common student questions to anticipate (Windows-specific deltas)

The full QA table in [`KEY_POINTS.md`](./KEY_POINTS.md) applies unchanged
— the Python is identical. Only these rows differ on Windows:

| Question                                                       | Answer to give                                                                                                              |
|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| "`python3` is not recognised — the slides say `python3`!"      | The macOS/Linux edition uses `python3`; on Windows use `python` (or the launcher `py`). Install from python.org and tick "Add Python to PATH". There is no `python3` alias by default on Windows. |
| "How do I exit the REPL? Ctrl+D does nothing."                 | Ctrl+D is the Unix convention. On the Windows REPL use **Ctrl+Z then Enter**, or just type `quit()`. |
| "`touch` / `mkdir -p` aren't commands."                        | Those are Unix. In PowerShell use `New-Item -ItemType File -Path name` and `New-Item -ItemType Directory -Force -Path dir`. In cmd, `type nul > name` and `mkdir dir`. |
| "`cd ~/renamer_sandbox` errors out."                           | PowerShell understands `~`, but cmd does not. The portable forms are `cd $HOME\renamer_sandbox` (PowerShell) or `cd %USERPROFILE%\renamer_sandbox` (cmd). |
| "Do I need to install Python separately for this?"             | No Maya needed, but you DO need Python from python.org (tick "Add to PATH"). This hour deliberately doesn't use `mayapy` — the whole point is the script runs anywhere. |
| "Why `os.path.join` and not just `'\\'`?"                      | macOS/Linux uses `/`. `os.path.join` picks the right one for the OS. Scripts that hand-concat paths break across studios (your laptop is Windows; the render farm is probably Linux). |
| "`os.listdir` only shows the top folder — how do I search subfolders?" | Use the recursive `find_files(directory, pattern='...')` helper shipped in `renamer_2027.py`, or the stdlib `os.walk(dir)`. `find_files` calls itself on every subdirectory it meets. |
| "PowerShell says 'running scripts is disabled on this system'." | That's ExecutionPolicy blocking `.ps1` files — it does NOT block `python`. You can still run every command in this doc. If you want to run `.ps1` scripts later: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (one-time, admin not needed). |
| "Why do my Windows paths show `\\` in the REPL?"               | A single backslash. Python's `repr()` doubles it for unambiguous display. `print(path)` shows the single `\` you expect. This is why raw strings (`r'C:\folder'`) are the safe way to write Windows paths in Python source. |

For the rest of the QA (function-vs-CLI default mismatch, regex vs plain
replace, can I run it from Maya's Script Editor, etc.), see the parent
[`KEY_POINTS.md`](./KEY_POINTS.md) — every answer there is OS-independent.

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

> **If you have extra time:** demo the recursive `find_files()` helper
> (Block D3) live, or walk through Advanced Direction #2 in
> `commandLine\HowToStartCommandLine.md` (add a `--dry-run` flag). Either is
> a ~10-minute extension that reinforces the core ideas.
