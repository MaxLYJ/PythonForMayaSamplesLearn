# HowToStart — commandLine

This demo is **different from every other one in this repo**: it has **nothing to do with Maya**.
It is a standalone, pure-Python **command-line batch file renamer** (`renamer.py`), built to show
that the Python skills you learn for Maya also let you write ordinary CLI tools that run from a
terminal. It uses only the Python standard library (`argparse`, `re`, `os`, `shutil`) — no
`maya.cmds`, no Qt, no Maya at all.

Because it is plain Python, **every behavior in this document was actually executed and verified**
on the host machine (not merely inferred). The verification log is summarized under each step.

## Files in this demo

| File | Target | Role |
|------|--------|------|
| `renamer.py` | Python 2.7 | Teaching original, heavily commented. |
| `renamer_2027.py` | Python 3 | The one you run. Byte-for-byte the same logic; just adds a header note. |

> Note: unlike the Maya demos, here the `_2027` file makes **no logic changes** — `argparse`/`re`/
> `os`/`shutil` code is identical across Py2 and Py3. Pick whichever Python you have.

## Prerequisites

- Any Python 3 interpreter (`python3 --version`). No Maya required.
- A terminal / command prompt.
- A throwaway folder of test files (built below). **Do not run this against a real project folder
  without `--duplicate`** — see the gotcha in Q2.

## What the code actually does

Two functions:

- `main()` — builds an `argparse` parser, parses CLI flags, and calls `rename(...)`. Runs **only**
  when the file is executed directly (`if __name__ == '__main__'`), not when imported.
- `rename(inString, outString, duplicate=True, inDir=None, outDir=None, regex=False)` — the real
  worker. Walks every file in `inDir`, skips dotfiles, applies a find/replace (plain or regex),
  skips files whose name is unchanged, then either **copies** (`duplicate=True`) or **renames in
  place** (`duplicate=False`) to `outDir`. Raises `IOError` if `inDir`/`outDir` don't exist.

---

## How to Create the Test Maya Scene

> ⚠️ **There is no Maya scene for this demo.** It operates on files on disk, so the "scene" is a
> folder of dummy files. The section is kept under this canonical heading for curriculum
> consistency, but the setup is purely filesystem.

Build a sandbox folder (do this in a terminal, not Maya):

```bash
mkdir -p ~/renamer_sandbox/src
cd ~/renamer_sandbox/src
touch hello_a.txt hello_b.txt hello_c.txt keep_me.txt data.csv .secret
```

You now have:
- Three files containing `hello` (these will be renamed).
- Two files with no `hello` (`keep_me.txt`, `data.csv`) — these must be left untouched.
- One dotfile (`.secret`) — must be skipped (hidden file).

> On Windows, use `echo. > hello_a.txt` etc. in `cmd`, or just create the files in Explorer.

---

## How to Run the Functions

You can run this demo **two ways**: as an imported library (call `rename()` directly) or as a CLI
(`python renamer_2027.py ...`, which calls `main()`). Both are shown and were verified.

> In all commands, replace `/abs/path/to` with the real path to your clone, e.g.
> `/home/you/PythonForMayaSamplesLearn/commandLine`.

### Run A — library mode (call `rename()` directly)

This is the "reused by other python libraries" mode the docstring mentions.

```python
import sys
sys.path.insert(0, r'/abs/path/to/PythonForMayaSamplesLearn/commandLine')
import renamer_2027 as r

# duplicate=True (the FUNCTION default): keep originals, write copies named with 'HI'
r.rename('hello', 'HI', duplicate=True, inDir=r'/home/you/renamer_sandbox/src',
         outDir=r'/home/you/renamer_sandbox/src')
```

**Verified result:** the folder now contains *both* `hello_a.txt`/`hello_b.txt`/`hello_c.txt`
(originals) **and** `HI_a.txt`/`HI_b.txt`/`HI_c.txt` (copies). `keep_me.txt`, `data.csv`, and
`.secret` are untouched. ✅ (Test 1)

**Overwrite mode** (`duplicate=False`): originals are *removed* and replaced by the renamed files:

```python
r.rename('hello', 'HI', duplicate=False, inDir=r'...', outDir=r'...')
```
**Verified result:** only `HI_a.txt`/`HI_b.txt`/`HI_c.txt` + `keep_me.txt` remain; the `hello_*`
originals are gone. ✅ (Test 2)

**Regex mode** (e.g. turn `frame_001.png` → `render_001.png` using a backreference):

```python
r.rename(r'frame_(\d+)', r'render_\1', duplicate=False, inDir=r'...', outDir=r'...', regex=True)
```
**Verified result:** `frame_001.png`/`frame_002.png`/`frame_010.png` → `render_001.png`/`render_002.png`/
`render_010.png`. The `\1` backreference correctly carries the captured digits. ✅ (Test 3)

**Redirect output to another folder** (`outDir`):

```python
r.rename('hello', 'HI', duplicate=True, inDir=r'.../src', outDir=r'.../outbox')
```
**Verified result:** originals stay in `src`, copies land in `outbox`. ✅ (Test 4)

**Bad directory raises immediately:**

```python
r.rename('a', 'b', outDir='/no/such/dir')   # → IOError
```
**Verified result:** `IOError: /no/such/dir does not exist!` ✅ (Test 5)

### Run B — command-line mode (`main()` via `__main__`)

From a terminal, in the folder that contains your test files:

```bash
cd ~/renamer_sandbox/src
python3 /abs/path/to/PythonForMayaSamplesLearn/commandLine/renamer_2027.py hello HI --out .
```

**Verified result:** `hello_a.txt` etc. become `HI_a.txt` etc. (originals removed). ✅ (Test 6)

The CLI flags (straight from `main()`):

| Flag | Meaning |
|------|---------|
| `inString` (positional, required) | The text/regex to find. |
| `outString` (positional, required) | The replacement text/regex. |
| `-d`, `--duplicate` | If given, **copy** instead of overwrite. `store_true` → **defaults to False** (overwrite!). |
| `-r`, `--regex` | Treat inputs as regex. `store_true` → defaults to False. |
| `-o`, `--out PATH` | Output directory. Defaults to the current working directory. |

Show the built-in help to see exactly this:

```bash
python3 /abs/path/to/.../renamer_2027.py --help
```

### Run C — confirm importing does NOT auto-run anything

Because of the `if __name__ == '__main__'` guard, `import renamer_2027` does **not** rename files.
**Verified:** after a bare `import renamer_2027 as r`, the test folder was unchanged. ✅ Only
`python3 renamer_2027.py ...` (direct execution) triggers `main()`.

---

## Question and Answer

**Q1. Why does `import renamer_2027` do nothing, but `python renamer_2027.py hello goodbye` renames
files?**
The `if __name__ == '__main__': main()` guard at the bottom. When you *run* the file directly,
Python sets the module's `__name__` to `"__main__"`, so `main()` fires. When you *import* it,
`__name__` is the module name (`"renamer_2027"`), the guard is false, and only the function
*definitions* are loaded — nothing executes. This lets the file be both a runnable tool *and* a
reusable library. (Verified in Test C.)

**Q2. The CLI overwrote my files by default, but `rename()`'s default is `duplicate=True`. Why the
mismatch?**
This is the most important gotcha in the demo, and it's real (verified). The **function**
`rename(..., duplicate=True)` defaults to *safe copying*. But the **CLI** flag is
`--duplicate` with `action='store_true'`, which means `args.duplicate` is `False` *unless you pass
the flag*. So `main()` calls `rename(..., duplicate=False)` by default → **overwrite**. In short:
calling the function is safe-by-default; running the CLI is destructive-by-default. Always pass
`-d`/`--duplicate` on the command line if you want to keep originals.

**Q3. What's the difference between `-r/--regex` mode and plain mode?**
Plain mode uses Python's `str.replace(inString, outString)` — literal substring substitution, no
special characters. Regex mode uses `re.sub(inString, outString, f)`, so `inString` is a regular
expression and `outString` may contain backreferences like `\1`. Use regex for patterns like
`frame_(\d+)`; use plain mode for simple "replace the word hello with goodbye" jobs.

**Q4. Why does the loop skip files whose name starts with a dot (`.`)?**
Dot-prefixed files are hidden files on Unix/macOS (`.gitignore`, `.DS_Store`, etc.). The
`if f.startswith('.'): continue` guard leaves them alone so the tool never clobbers system or VCS
metadata. (Verified: `.secret` was untouched in every test.)

**Q5. What happens if `outDir` doesn't exist?**
It raises `IOError: <path> does not exist!` *before* touching any file. The code deliberately
validates both `inDir` and `outDir` up front (`os.path.exists`) so it fails fast instead of
half-renaming your folder then crashing. (Verified in Test 5.)

**Q6. In duplicate mode it uses `shutil.copy2`, not `shutil.copy`. Why `copy2` specifically?**
`shutil.copy2` copies the file *and* preserves metadata (modification time, permissions). `shutil.copy`
copies contents only. For a renaming/archiving tool you usually want to keep timestamps, so `copy2`
is the right choice. In non-duplicate mode it uses `os.rename`, which is an atomic move (no copy).

**Q7. Can I use regex capture groups / backreferences?**
Yes — in `-r`/regex mode, `re.sub` supports them. **Verified:** `frame_(\d+)` → `render_\1` turned
`frame_010.png` into `render_010.png`. You can also use `$`-style lookarounds, character classes,
etc. — anything `re.sub` accepts. Remember to quote/escape your shell's special characters.

**Q8. A file didn't match the pattern — what happens to it?**
Nothing. After computing the new name, the code does `if name == f: continue` — if the find/replace
produced an identical name, the file is skipped (no wasted work, and no accidental "rename to
itself"). Unmatched files therefore pass through untouched. (Verified: `keep_me.txt`, `data.csv`
were never changed.)

**Q9. Could I run this from inside Maya's Script Editor?**
Technically yes — Maya bundles a Python interpreter, so `import subprocess; subprocess.run([...])`
could shell out to it. But there's no reason to: this tool has no Maya dependency, and the Script
Editor is the wrong place for a filesystem batch job. Run it from a normal terminal. (The whole
*point* of the demo is that Python-for-Maya skills transfer to ordinary CLI tools.)

**Q10. Does it recurse into subdirectories?**
No — `os.listdir(inDir)` returns only the immediate children of `inDir`, and the loop processes
each as a flat filename. Subfolders inside `inDir` are seen as "files" and, because their name
likely doesn't change, are skipped. Recursion is a natural extension (see Advanced Directions #1).

---

## Advanced Directions

The tool is a solid 100-line foundation. Here are scoped ways to evolve it, each with the new
function/class it would require.

1. **Add recursive directory walking + a `--recursive` flag.** Replace the flat `os.listdir` loop
   with `os.walk(inDir)` when `--recursive` is set, rebuilding `src`/`dest` relative to each
   subfolder (and creating matching subfolders under `outDir` with `os.makedirs(..., exist_ok=True)`).
   New code: a `walk = args.recursive` branch and an `_process_tree()` helper.
2. **Add a `--dry-run` / preview mode.** A flag that prints the planned `src → dest` mappings
   *without* touching the disk, so users can sanity-check regexes before committing. New code: a
   `--dry-run` `store_true` flag and a `preview` path inside `rename()` that yields tuples instead
   of calling `copy2`/`rename`. Optionally print a colored diff.
3. **Frame-sequence renumbering.** Many studios need `frame_1.png … frame_999.png` padded to a fixed
   width (`frame_0001.png …`). Add a dedicated `renumber_sequence(directory, padding=4, pattern=...)`
   function that detects existing sequences, sorts them, and renames with zero-padded indices — plus
   a `--renumber` CLI flag. New code: `renumber_sequence()` and a small sequence-detection helper.
4. **Undo support via a log.** Write every `src → dest` mapping to a hidden `.renamer_log.json` in
   `outDir`, and add an `undo(log_path)` function (and `--undo` flag) that reverses the last run.
   This makes the destructive default far safer. New code: `json` logging in `rename()` and an
   `undo()` function.
5. **Package it as an installable command.** Add a `pyproject.toml` with a console-script entry
   point (`[project.scripts] rename-batch = "renamer:main"`), so `pip install .` gives a global
   `rename-batch` command instead of typing the full path. Optionally wrap with `typer`/`click` for
   richer flags and auto-generated completion. New code: `pyproject.toml` + (optional) refactor of
   `main()` to a `click`/`typer` app.
6. **Add a Qt GUI variant.** For users who avoid the terminal, port the flags into a small
   `BatchRenamerUI(QWidget)` with text fields for find/replace, checkboxes for duplicate/regex/dry-
   run, a folder browser for `inDir`/`outDir`, and a preview table — reusing the existing `rename()`
   as the model. (This mirrors the model/view split used by `controllerLibrary` and `lightManager`.)
   New code: a `batch_renamer_ui.py` Qt module.
