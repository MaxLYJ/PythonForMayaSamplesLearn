# HowToStart — Commands: Custom MPxCommand Plugins

> **Position in the curriculum.** This is the Advanced section's first **`MPxCommand` plugin** demo. The Intro folder showed the OpenMaya API used *interactively* (a Script-Editor script); here the same API is packaged into a **plugin** that Maya loads with `loadPlugin`, after which the code becomes a real command callable from `cmds`, MEL, shelves, and hotkeys exactly like a built-in. The folder also ships a supporting **pure-Python decorators lesson** (`decorators.py`) that teaches the `@classmethod` / `@staticmethod` / `functools.wraps` concepts that `distributeCmd.py` then *uses*.

This guide covers **three** files that form one pedagogical arc:

| File | Archetype | Maya scene needed? | Verified runnable? |
|---|---|---|---|
| `decorators.py` / `decorators_2027.py` | Pure-Python flat teaching script (no Maya import at all) | ❌ None | ✅ `_2027` executed & output captured; original is a `SyntaxError` on Python 3 |
| `helloWorldCmd.py` / `helloWorldCmd_2027.py` | `MPxCommand` plugin (API 2.0), minimal | ❌ None (just prints) | ⚠️ Logic source-verified; needs Maya to load |
| `distributeCmd.py` / `distributeCmd_2027.py` | `MPxCommand` plugin **with undo** | ✅ 3+ selected transforms | ⚠️ Algorithm hand-verified in pure Python; needs Maya to load |

## The `_2027` convention

Every teaching file has a `<name>_2027.py` sibling: a Python-3 / API-2.0 / Maya-2027-verified copy. For this folder the diffs are the **lightest possible**:

- **`helloWorldCmd.py` → `helloWorldCmd_2027.py`**: header comment only. The original was already Py3/API2-clean — there was nothing to modernize.
- **`distributeCmd.py` → `distributeCmd_2027.py`**: header comment only. (The `from __future__ import division` at the top is a harmless Py2 leftover that is a no-op on Python 3.)
- **`decorators.py` → `decorators_2027.py`**: header **plus two `print`-statement → `print()` conversions** at lines 96 and 133. These two lines are the only reason the original cannot run on Maya 2027 (see the critical warning below).

**On Maya 2027 (Python 3) always load / run the `_2027.py` file.** The originals are kept verbatim for reference.

## Prerequisites

- **Maya 2027 (Python 3)** running interactively (GUI). The two command plugins cannot be exercised from plain `python3`; only `decorators.py` is Maya-free.
- A Script Editor → Python tab.
- The absolute path to this folder, referred to below as `/abs/path/Commands/`.
- **⚠️ Critical for `decorators.py`:** the *original* `decorators.py` contains two Python-2 print statements (`print hello.__name__`, `print goodbye.__name__`) that are a hard **`SyntaxError`** on Python 3 (verified — `py_compile` fails at line 96). On Maya 2027 you **must** run `decorators_2027.py`; the original will not even parse.

## What the code actually does

### 1. `decorators.py` — a pure-Python lesson on function wrappers

This file has **no Maya dependency whatsoever** — it is the Advanced section's one pure-Python demo (the same family as `commandLine/renamer`). It is a **flat top-to-bottom script**: it defines `foo` and then *immediately calls* `foo()`, `spam(foo)`, etc. at module level as the file is read. So "running" it = pasting it (or importing it); the print statements are the output. It builds the decorator idea in four stages:

| Stage | Code | What it teaches | Verified output |
|---|---|---|---|
| Plain call | `foo()` | A bare function | `This is foo` |
| Manual wrap | `spam(foo)` — calls `foo` inside `spam` | Wrapping is just calling a function that calls your function | `This is spam` / `This is foo` / `Spam is done` |
| `foo = deferSpam(foo)` | `deferSpam` returns an inner `wrapperSpam` | A wrapper *factory*: the outer builds, the inner runs each call | `This is wrapper spam spam` / `This is foo` / `wrapperSpam is done` |
| `@deferSpam` | syntactic sugar for the line above | `@dec` above `def f` ≡ `f = dec(f)` at definition time | same as above |
| `@wraps(func)` inside `eggs` | `functools.wraps` copies `__name__`/`__doc__` | Fixes the "decorated function loses its identity" problem | `goodbye.__name__` stays `goodbye`, **not** `wrapper` |

> **⚠️ Verified comment bug (good Q&A material).** The inline comment at lines 91–93 claims calling `hello('David')` prints `This is spam / Hello, David / Spam is done`. The **actual** output (captured by running the file) is `This is wrapper spam spam / Hello, David / wrapperSpam is done`. The author copy-pasted the expected-output block from the earlier `spam()` example (lines 32–34) and never updated it. Always re-derive printed output by running, not by trusting inline comments.

The payoff line, demonstrated by the final two `print(__name__)` calls: a function decorated with a **bare** wrapper (`@deferSpam`) reports the *wrapper's* name (`wrapperSpam`); the same function decorated with a wrapper that uses **`@wraps(func)`** (`@eggs`) reports its *own* name (`goodbye`). That is the entire reason `functools.wraps` exists.

### 2. `helloWorldCmd.py` — the minimal `MPxCommand`

The canonical anatomy of an API-2.0 command plugin, every piece present here:

| Piece | In `helloWorldCmd.py` | Purpose |
|---|---|---|
| `maya_useNewAPI()` | `def maya_useNewAPI(): pass` | **Sentinel.** Its mere presence tells Maya this plugin uses API 2.0 semantics (not the legacy Python-1.0 plugin API). The body does nothing. |
| `class HelloWorldCmd(om.MPxCommand)` | the command class | Subclass `MPxCommand`; `MPx` = "classes you inherit from". |
| `kPluginCmdName = "hello"` | class attribute | The command name users type. Must be unique across Maya. |
| `kNameFlag / kNameLongFlag` | `'-n' / '-name'` | Short/long flag spelling constants. |
| `doIt(self, args)` | the action | Maya calls this when the command runs. Parse args, do work. |
| `cmdCreator()` | module function → returns `HelloWorldCmd()` | Factory Maya calls to make a fresh instance per invocation. |
| `syntaxCreator()` | module function → returns an `MSyntax` | Declares the flags/types the command accepts. |
| `initializePlugin(plugin)` | `MFnPlugin(plugin).registerCommand(name, cmdCreator, syntaxCreator)` | Maya calls on `loadPlugin`. |
| `uninitializePlugin(plugin)` | `MFnPlugin(plugin).deregisterCommand(name)` | Maya calls on `unloadPlugin`. |

**`doIt` flow (verified):** build `om.MArgDatabase(self.syntax(), args)` → `self.syntax()` returns the `MSyntax` that `registerCommand` stored → `argData.isFlagSet('-n')` → if set, `argData.flagArgumentString('-n', 0)` (the `0` = first occurrence of the flag); else default `'World'` → `om.MGlobal.displayInfo("Hello, %s!" % name)`. Result: `Hello, World!` with no flag, `Hello, David!` with `-n David`.

This command is **not undoable** (no `isUndoable`/`undoIt`/`redoIt`) — appropriate for a fire-and-forget print.

### 3. `distributeCmd.py` — an **undoable** `MPxCommand`

Same skeleton as `helloWorldCmd`, but it adds the full **undo/redo contract** and uses `@classmethod` / `@staticmethod`:

| Piece | In `distributeCmd.py` | Purpose |
|---|---|---|
| `@classmethod cmdCreator(cls)` | `return cls()` | A classmethod receives the *class*, so `cls()` builds the right subclass. `helloWorldCmd` used a plain module function instead — both work; classmethod is the "call something before it's instantiated" style the README highlights. |
| `@staticmethod syntaxCreator()` | returns an empty `MSyntax()` | A staticmethod has no `self`/`cls` — pure namespace organization. |
| `__init__` | `self.__undoStack = []` | Per-instance history of original positions, one dict per invocation. |
| `isUndoable(self)` | `return True` | **Gate.** Without this returning `True`, Maya treats the command as non-undoable and never calls `undoIt`/`redoIt`. |
| `doIt(self, args)` | `self.redoIt()` | First invocation delegates to `redoIt`. |
| `redoIt(self)` | the real work + records undo state | Called both from `doIt` (first run) and by Maya on **redo**. |
| `undoIt(self)` | restores cached positions | Called by Maya on **undo**. |

**The `MPxCommand` undo contract (the key teaching point):** when `isUndoable()` is `True`, Maya calls `doIt()` once on first run, `undoIt()` when the user undoes, and `redoIt()` directly when the user redoes. Therefore all real work must live in `redoIt()` (so first-run and redo share one code path), `doIt()` should only set up and delegate, and `redoIt()` must record everything `undoIt()` will need to reverse. This command follows that contract exactly.

**The distribute algorithm (hand-verified in pure Python):**

1. `selection = om.MGlobal.getActiveSelectionList()`; if `< 3` items → `displayWarning('Atleast 3 objects must be selected')` and return (still pushes an empty undo dict so the no-op is technically undoable).
2. Iterate the selection filtered to `om.MFn.kTransform` via `om.MItSelectionList`; for each transform store `MFnTransform.translation(kWorld)` into **two** dicts: `translations` (to modify) and `undo` (frozen originals, pushed onto `__undoStack`).
3. **For each axis `x`, `y`, `z` independently:** collect that axis's coordinates → `minVal`/`maxVal` → sort node names by that axis → `steps = (maxVal - minVal)/(n - 1)` → reassign each node (in sorted order) to `minVal + index*steps`.
4. Re-iterate the selection and `setTranslation(...)` each transform to its new computed position.

**Verified concrete example** (3 cubes, world X = 2 / 10 / 0):

| Object | Before X | After X |
|---|---|---|
| cube3 | 0 | 0 |
| cube1 | 2 | **5** |
| cube2 | 10 | 10 |

Result is evenly spaced `0, 5, 10` — cube1 snaps from 2 to the midpoint. `undoIt` pops the frozen dict and restores 2/10/0.

> **⚠️ Verified subtlety (good Q&A material).** Distribution is **per-axis independent**: each axis sorts nodes by *that axis* and reassigns the middle slot to whoever is the *middle of that axis*. For objects spread differently on X vs Y, the result is **not a clean straight line or grid**. Verified: nodes at `(0,0,0)`, `(10,5,0)`, `(20,0,0)` → the X-middle `(10,5,0)` is unchanged, but the Y-middle is the third object `(20,0,0)`, so its Y becomes `2.5`, landing at `(20, 2.5, 0)`. The three objects do **not** end up collinear. If you want a true "line them up" tool, see Advanced Directions.

## How to Create the Test Maya Scene

### For `decorators.py` — no scene needed

`decorators.py` is pure Python (no `maya.*` import). Its "scene" is just the Script Editor. This follows the same **no-scene convention** as `commandLine`, `manipulatorMath`, `fileDialog`, and `Intro/simple`.

### For `helloWorldCmd.py` — no scene needed

The command only prints; it reads nothing from the scene. An empty fresh scene is fine.

### For `distributeCmd.py` — build 3+ transforms

The command needs **3 or more transform nodes selected**, and it filters to transforms only (`om.MFn.kTransform`). Minimum reproducible scene:

1. `cmds.file(new=True, force=True)` — fresh scene.
2. Create three cubes that are *not* already evenly spaced, so the move is visible:
   ```python
   import maya.cmds as cmds
   cmds.polyCube(name='cube1'); cmds.move(2, 0, 0)   # X = 2
   cmds.polyCube(name='cube2'); cmds.move(10, 0, 0)  # X = 10
   cmds.polyCube(name='cube3'); cmds.move(0, 0, 0)   # X = 0
   ```
3. Select all three transforms (the cube `transform` nodes, **not** their shapes): `cmds.select('cube1', 'cube2', 'cube3')`.
4. To also exercise the warning path, keep a 2-object scene handy.

**Scene-state expectations:**

| Entry point | Required state |
|---|---|
| `decorators_2027.py` | None (pure Python) |
| `cmds.hello()` / `cmds.hello(n=...)` | None |
| `cmds.distribute()` | ≥ 3 **transform** nodes in the active selection |
| `cmds.distribute()` with < 3 selected | Warns and no-ops |

## How to Run the Functions

### Run A — `decorators.py` (watch the wrapper stages print)

On Maya 2027 you must use the `_2027` file (the original will not parse). Paste the whole file into a Python tab and execute, **or** run it headlessly:

```python
exec(open('/abs/path/Commands/decorators_2027.py').read())
```

**Verified expected output** (abridged; full output captured during writing):

```
Calling Foo without any wrappers
This is foo
foo
...
Calling foo wrapped by wrapperSpam created by deferSpam
This is wrapper spam spam
This is foo
wrapperSpam is done
...
Calling hello wrapped by wrapperSpam created by deferSpam
This is wrapper spam spam
Hello, David
wrapperSpam is done
wrapperSpam          <-- hello.__name__: identity LOST (no @wraps)
This is eggs
Goodbye, Mary
Eggs is done
goodbye              <-- goodbye.__name__: identity PRESERVED (@wraps)
```

The two `__name__` lines are the punchline: `wrapperSpam` (lost) vs `goodbye` (preserved by `functools.wraps`). ⚠️ The inline comment mis-labels the `hello` block — trust the actual output above, not the comment.

### Run B — `helloWorldCmd.py` (load → call)

```python
import maya.cmds as cmds
# load the _2027 plugin directly by path (no sys.path needed)
cmds.loadPlugin('/abs/path/Commands/helloWorldCmd_2027.py')
```

Then exercise the command:

```python
cmds.hello()              # -> Script Editor: Hello, World!
cmds.hello(n='David')     # -> Hello, David!
cmds.hello(name='Maya')   # long flag also works -> Hello, Maya!
```

Confirm it is a real registered command: `cmds.pluginInfo('/abs/path/Commands/helloWorldCmd_2027.py', q=True, command=True)` returns `['hello']`. Unload when done: `cmds.unloadPlugin('helloWorldCmd')` (the unload name is the **filename stem**, see Q&A).

### Run C — `distributeCmd.py` (load → distribute → undo → redo)

```python
import maya.cmds as cmds
cmds.loadPlugin('/abs/path/Commands/distributeCmd_2027.py')

# build the 3-cube scene from above and select the three transforms
cmds.select('cube1', 'cube2', 'cube3')
print(cmds.xform('cube1', q=True, t=True, ws=True))  # before: [2,0,0]

cmds.distribute()
print(cmds.xform('cube1', q=True, t=True, ws=True))  # after:  [5,0,0]  (snapped to midpoint)
```

Expected viewport: the three cubes are now evenly spaced at world X = `0, 5, 10`. Now exercise the undo contract the command was built for:

```python
cmds.undo()   # undoIt() fires -> cubes return to 2 / 10 / 0
cmds.redo()   # redoIt() fires  -> cubes re-distribute to 0 / 5 / 10
```

**Warning path:** `cmds.select('cube1', 'cube2'); cmds.distribute()` → Script Editor shows `Atleast 3 objects must be selected` and nothing moves.

The docstring's load recipe uses `unloadPlugin('distributeCmd', force=True)` — `force=True` matters because an undoable command that is still on Maya's undo queue can block a plain unload; `force` lets Maya drop it. ⚠️ Exact multi-cycle undo/redo stack behavior was not verified without Maya; the single undo→redo cycle is correct by construction.

### Run D — one-shot paste (load both commands + exercise)

```python
import maya.cmds as cmds
P = '/abs/path/Commands'
for f in ('helloWorldCmd_2027.py', 'distributeCmd_2027.py'):
    try: cmds.unloadPlugin(f.replace('_2027.py',''), force=True)
    except: pass
    cmds.loadPlugin('/'.join([P, f]))

cmds.hello(n='curriculum')                       # Hello, curriculum!
cmds.polyCube(); cmds.move(-3,0,0); a=cmds.last
cmds.polyCube(); cmds.move( 0,2,0); b=cmds.last
cmds.polyCube(); cmds.move( 4,0,0); c=cmds.last
cmds.select(a,b,c); cmds.distribute()            # 3 cubes spread evenly
cmds.undo()                                       # back to scattered
```

## Question and Answer

**Q1. Why does `decorators.py` throw a `SyntaxError` on Maya 2027 but `decorators_2027.py` runs fine?**
The original has two Python-2 print statements — `print hello.__name__` (line 96) and `print goodbye.__name__` (line 133). In Python 3 `print` is a function, so those are syntax errors (`py_compile` fails at line 96). The `_2027` sibling converts exactly those two lines to `print(...)`. This is the *only* Maya-2027 incompatibility in the file. Lesson: when a teaching file won't even parse, check for Py2 `print`/`except X, e:`/`raise E, msg` syntax before debugging anything else.

**Q2. The comment above `hello('David')` says the output is `This is spam / Hello, David / Spam is done`, but it actually prints `This is wrapper spam spam / Hello, David / wrapperSpam is done`. Why?**
The comment is wrong — copy-pasted from the earlier `spam(foo)` example (lines 32–34) and never updated for `deferSpam`. `deferSpam`'s inner function is named `wrapperSpam`, and its print strings are `"This is wrapper spam spam"` and `"wrapperSpam is done"`. Verified by running the file. Trust executed output over inline expected-output comments.

**Q3. What does `functools.wraps` actually fix?**
A decorated function is *replaced* by its wrapper, so it inherits the wrapper's `__name__`, `__doc__`, `__module__`. Without `@wraps`, `hello.__name__` is `'wrapperSpam'`; with `@wraps(func)` inside `eggs`, `goodbye.__name__` stays `'goodbye'`. This matters for tooling that introspects functions — `help()`, docstrings, tracebacks, frameworks that dispatch on function names.

**Q4. `distributeCmd` uses `@classmethod` for `cmdCreator` and `@staticmethod` for `syntaxCreator`. What is the difference, and why bother?**
A `@classmethod` receives the class (`cls`) as its first arg, so `return cls()` builds an instance of whichever subclass it is called on — useful for factories and inheritance. A `@staticmethod` gets neither `self` nor `cls`; it is just a function parked on the class for namespace organization. `helloWorldCmd` used plain *module-level* functions for both — equally valid. The classmethod/staticmethod forms are a stylistic/organizational choice the README is teaching, not a functional requirement.

**Q5. What is `maya_useNewAPI()` doing? It just `pass`es.**
Its mere presence (a module-level function of that exact name) is a **sentinel** telling Maya to treat this as an API-2.0 plugin. Without it Maya assumes the legacy Python-1.0 plugin protocol and the `om.MPxCommand`/`om.MFnPlugin` calls behave differently. The body is intentionally empty.

**Q6. The `unloadPlugin` name is `'helloWorldCmd'` but the command is `hello`. Why the mismatch?**
Maya registers a Python plugin under its **filename stem** (`helloWorldCmd`, from `helloWorldCmd_2027.py` → Maya strips the version/path), while the *command* it exposes is `kPluginCmdName = 'hello'`. They are independent names. This filename-vs-command-name split recurs across plugin demos (e.g. `mathTableControl.py` exposes the `spMathTableControl` command). To unload you use the filename stem; to *call* you use the command name.

**Q7. Why does the `distributeCmd` docstring's unload use `force=True`?**
An undoable command instance (and its `__undoStack`) can remain referenced on Maya's undo queue after it runs, which blocks a normal `unloadPlugin`. `force=True` tells Maya to drop the plugin even though something still references it. `helloWorldCmd` does not need `force` because it is non-undoable and leaves nothing on the queue.

**Q8. What happens if I run `distribute` with only two objects selected?**
`redoIt` sees `selection.length() < 3`, calls `displayWarning('Atleast 3 objects must be selected')`, appends an **empty** undo dict to `__undoStack`, and returns — nothing moves. Note it still pushed an entry, so the no-op sits on the undo queue (an `undo` will pop the empty dict and also do nothing). Also note the typo `Atleast` (should be "At least").

**Q9. Why are there two dictionaries, `translations` and `undo`, holding what looks like the same data?**
`translations` is mutated in place during the compute loop (`translations[node][i] = ...`), while `undo` must keep the pristine originals for `undoIt`. They are populated by two separate `tranFn.translation(kWorld)` calls, which return **fresh** `MVector`s each time, so editing one does not corrupt the other. The comment about "dictionaries are mutable" is the author flagging the reason for the copy; the design is correct.

**Q10. After `distribute`, my objects are not in a straight line / clean grid. Is that a bug?**
It is by design, though surprising. The algorithm sorts and re-spaces **each axis independently**, so the object that is the "middle of X" need not be the "middle of Y". Verified: `(0,0,0)`, `(10,5,0)`, `(20,0,0)` → the third object's Y is set to `2.5` because it is the Y-middle, producing `(20, 2.5, 0)` — the three are not collinear. For objects already varying on only one axis (the common case) you get a clean even spacing. A "line them up along one axis" mode is a natural extension (see Advanced Directions).

**Q11. What is the `MPxCommand` undo contract — exactly which methods does Maya call, and when?**
When `isUndoable()` returns `True`: Maya calls `doIt()` on first invocation (convention: it delegates to `redoIt()`), `undoIt()` when the user undoes, and `redoIt()` **directly** on redo. So the real work must live in `redoIt()` (shared by first-run and redo), `doIt()` only sets up and delegates, and `redoIt()` must record everything `undoIt()` needs. This command implements exactly that. The one subtlety: `redoIt` appends to `__undoStack` on every call, so on the redo path (after an undo popped the stack) it re-pushes — fine for typical single undo/redo use.

## Advanced Directions

1. **Add flags to `distribute`** (`-axis`/`-a` to restrict to a subset of axes, `-space` for world-vs-object, `-count` to distribute onto N evenly-spaced new positions). Requires: extend `syntaxCreator` with `syntax.addFlag(...)`, parse them in `doIt` via `MArgDatabase`, thread the options into `redoIt`'s per-axis loop, and gate each axis on the `-axis` selection. Mirrors `helloWorldCmd`'s single-flag pattern, scaled up.

2. **A true "align to line/grid" mode.** Add a `-principal` flag that picks one dominant axis (e.g. the axis of greatest spread) and distributes along *only* it, optionally collapsing the other two to a grid. Requires: a `computePrincipalAxis(translations)` helper and a single-sorted spacing pass instead of three independent ones — directly fixes the not-collinear subtlety from Q10.

3. **Generalize `helloWorldCmd` into a `announce` command** with `-message`/`-m` (string) and `-type`/`-t` (`info|warning|error`) flags that route to `MGlobal.displayInfo`/`displayWarning`/`displayError`. Requires: a second flag (`MSyntax.kString`) and a small dispatch in `doIt`. Turns the "hello world" skeleton into a reusable routed-logging command.

4. **A decorator-driven command-registration helper.** Promote `decorators.py`'s lesson into real plugin infrastructure: a `@command('name', flags=[...])` decorator (built with `functools.wraps` + a metaclass or registry) that auto-generates `cmdCreator`/`syntaxCreator` and a single `initializePlugin` that registers every decorated command. Requires: a `CommandRegistry` class, the `@command` decorator, and a generic `makeSyntax(flags)` factory — collapsing the boilerplate that `helloWorldCmd`/`distributeCmd` each hand-write.

5. **A compound undoable command.** Wrap a multi-step rig operation (e.g. *distribute → parent under a control → add a constraint*) as **one** undoable `MPxCommand` whose `redoIt` performs all sub-steps and `undoIt` reverses them in order — so a single Ctrl+Z undoes the whole rig-build. Requires: a `CompoundCmd(MPxCommand)` that owns a list of sub-command objects, each with its own `redo`/`undo`, plus careful `__undoStack` ordering.

6. **Ship as an installable Maya module.** Package all three (with the `_2027` files as canonical) as a Maya module/plug-in on `MAYA_MODULE_PATH`, add a `userSetup.py` that `loadPlugin`s both commands on startup, and provide shelf-button MEL/Python that calls `hello`/`distribute`. Requires: a `.mod` file, a `userSetup.py`, and shelf-install snippets — turning the demo into a permanent, version-stamped studio tool.
