# HowToStart — `callbackManager` (Advanced Python for Maya · Utilities)

> **Where this sits in the curriculum.** This is the curriculum's first
> *architectural* demo. It takes the raw register→store→remove callback lifecycle
> you learned in `cameraMessageCmd` and wraps it in a reusable, fault-tolerant
> **manager**. The lesson is no longer "how do I register one callback?" — it is
> "how do I build infrastructure that lets a whole studio of tools register
> callbacks safely, without any single bad callback stalling or killing Maya?"
>
> Evolution: `cameraMessageCmd` (one raw callback, hand-managed ID list)
> **→** `callbackManager` (singleton hub, auto-generated register/deregister for
> *every* `MSceneMessage` signal, weak-reference storage so dead objects clean
> themselves up, and a single shared Maya handler that isolates exceptions).

This demo is part of `AdvancedPythonForMaya-master/Utilities/`, a folder that
also contains two *Python context-manager* demos (`contextExamples`,
`createdNodesContext`) covered by their own HowToStart files.

---

## Files in this demo

| File | Role | Run it? |
|---|---|---|
| `callbackManager.py` | The Autodesk original (Python 2 — bare `print` statements). | Avoid; use the `_2027` copy below. |
| `callbackManager_2027.py` | The verified Python-3 copy (only the two `print`s changed). | **Yes — target this file.** |
| `README.md` | Folder-level README covering Callbacks + Python Contexts. Accurate, but high-level. | Read for context. |
| `__init__.py` | Empty — marks `Utilities/` as a package. | N/A |

> **`_2027` convention.** `callbackManager_2027.py` is the version-neutral
> Python-3 copy you should target. A `diff` of the two files shows the **only**
> changes are the two Python-2→3 `print` conversions:
>
> ```python
> # callbackManager.py        (Python 2)
> print "Test Method"
> print "testFunction", args
>
> # callbackManager_2027.py   (Python 3)
> print("Test Method")
> print("testFunction", args)
> ```
>
> Every line of the `SceneCallbackManager` class, `testMethod`, `testFunction`,
> and `runTests` is byte-identical between the two files. All line references
> below cite `callbackManager_2027.py`.

## Prerequisites

- Maya 2027 (Python 3) — this demo imports `from maya.api import OpenMaya as om`
  (API 2.0), so it must run inside Maya's interpreter (Script Editor Python tab,
  or `mayapy`). It cannot run in plain CPython.
- **⚠️ `runTests()` calls `cmds.file(new=True, force=True)` twice** — it
  *discards whatever scene is open*. Run it only in a scene you are willing to
  lose (or save first). This is the single most important practical warning for
  this demo.

---

## What the code actually does

`callbackManager_2027.py` is a **hybrid archetype** (same shape as
`manipulatorMath` and `profilerDump`): a definitions-only library — the
`SceneCallbackManager` class — **plus** a runnable test driver `runTests()`.
There is **no `__main__` guard** (verified), so importing the module is silent;
you must call `runTests()` (or build your own manager) explicitly.

### The big idea: a signal multiplexer

A naïve tool registers its own callback directly with Maya:

```python
om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, my_func)   # direct
```

If `my_func` raises, Maya's callback dispatch for that signal can stall or, in
bad cases, destabilize the app. `SceneCallbackManager` instead registers
**exactly one** internal handler per signal with Maya, and that handler fans the
event out to every user callback registered for that signal — each call wrapped
in `try/except`. One bad callback logs an error and is skipped; the rest still
run. This is the "go-between" pattern the folder README describes.

### Class: `SceneCallbackManager`

| Member | Line | What it does |
|---|---|---|
| `_instance = None` | 24 | Class-level singleton slot. |
| `instance()` (classmethod) | 27–30 | Lazy singleton: `cls._instance = cls._instance or cls()`. Guarantees one shared manager. |
| `__init__` | 32–65 | Builds two private dicts (`__callbacks`, `__callbackIDs`) and **dynamically generates** a `register<NiceName>` / `deregister<NiceName>` pair for *every* `MSceneMessage` signal. |
| `__register(callback, signal)` | 67–117 | Validates callable, lazily registers the shared Maya handler, stores the callback via **weak reference**. |
| `__deregister(callback, signal=None)` | 119–154 | Removes the callback; when a signal's list empties, removes the shared Maya handler too. |
| `__handler(*args, **kwargs)` | 156–188 | The single shared Maya callback. Re-constitutes each stored callback, calls it inside `try/except`, logs failures. |
| `testMethod(self, *args)` | 190–193 | Trivial bound-method callback used by `runTests`. |
| `testFunction(*args)` | 196–199 | Trivial module-function callback used by `runTests`. |
| `runTests()` | 202–218 | The runnable driver: register function + method to `kAfterNew`, make a new file (should fire both), deregister, make a new file (should fire neither). |

### Dynamic method generation (the clever part)

`registerAfterNew`, `deregisterAfterNew`, `registerSelectionChanged`, … — **none
of these methods appear in the source text.** They are created at runtime in
`__init__` (lines 40–65):

```python
for signalName in dir(om.MSceneMessage):
    if not signalName.startswith('k'):           # only the kFoo enum constants
        continue
    signal = getattr(om.MSceneMessage, signalName)
    if not isinstance(signal, int):              # only real enum ints
        continue
    niceName = signalName[1:]                     # 'kAfterNew' -> 'AfterNew'
    setattr(self, 'register%s' % niceName,
            partial(self.__register, signal=signal))     # -> self.registerAfterNew
    setattr(self, 'deregister%s' % niceName,
            partial(self.__deregister, signal=signal))   # -> self.deregisterAfterNew
```

So the manager automatically gains a register/deregister pair for **every**
`MSceneMessage` signal Maya ships — `kAfterNew`, `kBeforeOpen`, `kAfterSave`,
`kSelectionChanged`, `kTimeChanged`, `kToolChanged`, and dozens more. Calling
`manager.registerAfterNew(cb)` is really
`self.__register(cb, signal=om.MSceneMessage.kAfterNew)`.

> Note these are **instance attributes** (set on `self`), not class methods. The
> singleton makes that irrelevant in practice, but it means
> `SceneCallbackManager.registerAfterNew` does not exist — only
> `instance().registerAfterNew` does.

### Weak-reference storage (why dead objects don't leak)

To avoid holding dead tools alive, the manager stores callbacks weakly, in two
different shapes depending on what they are (lines 95–117):

| Callback kind | Storage | Reason |
|---|---|---|
| **Bound method** (`inspect.ismethod` True) | `weakref.WeakKeyDictionary()` mapping `instance → func` | A bound method object can't be weak-ref'd directly; storing the *instance* as a weak dict key means the entry vanishes automatically when the owning object is deleted. |
| **Plain function** | `weakref.ref(callback)` | Functions support weakref; when the function is deleted/reloaded, the ref dereferences to `None`. |

Re-registration is deduplicated (lines 108, 116): the `if … not in callbackList`
guard. **Verified behavior:** two `weakref.ref(func)` to the *same* function
compare equal, and two `WeakKeyDictionary`s with identical contents also compare
equal — so registering the same callback twice stores it **once**, for both
functions and methods. (Confirmed with a pure-Python test outside Maya.)

### The shared handler (fault isolation)

`__handler` (lines 156–188) is the *only* function Maya ever calls back. It pops
its bound `signal` out of `kwargs`, walks the callback list, and re-constitutes
each callback:

```python
for callback in callbackList:
    if isinstance(callback, weakref.WeakKeyDictionary):   # a method
        for obj, method in callback.items():
            try:
                method(obj, *args, **kwargs)
            except:
                logger.exception('Failed to run method callback')
    else:                                                  # a function
        callback = callback()            # deref weakref -> function or None
        if callback is None:
            continue                      # function was GC'd; skip silently
        try:
            callback(*args, **kwargs)
        except:
            logger.exception('Failed to run function callback')
```

The `try/except` around every call is the whole point: a callback that raises is
logged and skipped — it cannot take down the others or stall Maya. (Caveat: it
is a **bare `except:`**, which also swallows `SystemExit`/`KeyboardInterrupt` —
see Q&A.) Errors are reported via `logger.exception(...)` at ERROR level; the
module logger is set to `WARNING` (lines 9–11), so errors *will* surface —
typically to **Maya's Output Window / the terminal stderr**, not necessarily the
Script Editor (confirm where your Maya routes stderr).

---

## How to Create the Test Maya Scene

**No geometry scene is needed** — consistent with the `manipulatorMath` /
`profilerDump` no-scene convention. The "scene state" this demo exercises is not
nodes or selections, it is **`MSceneMessage` event dispatch**. The only
preconditions are:

1. **An interactive Maya session** (the Script Editor Python tab is best).
   `runTests()` triggers `kAfterNew` by calling `cmds.file(new=True, force=True)`,
   which is meaningful interactively.
2. **An empty / disposable scene.** `runTests()` makes a new file twice with
   `force=True`, discarding whatever is open. Start from `File ▸ New Scene`, or
   save your work first.
3. (Optional, for Run B) A couple of objects in the viewport if you want to
   visibly change the selection to fire `kSelectionChanged`.

| Entry point | Precondition / scene state |
|---|---|
| `runTests()` | Disposable scene (it will be replaced by `file(new=True)` twice). |
| Headless `registerSelectionChanged` (Run B) | Any objects you can click to change selection. |
| Bad-callback isolation (Run C) | Disposable scene (triggers `kAfterNew` via `file(new=True)`). |
| Singleton / discovery (Run D) | None — pure introspection. |

---

## How to Run the Functions

In every snippet below, replace `/abs/path/` with the absolute path to
`AdvancedPythonForMaya-master/Utilities/` on your machine.

### Run A — the built-in driver `runTests()` (function + method, then cleanup)

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import callbackManager_2027 as cm

cm.runTests()
```

**Expected Script Editor output** (order matters — the function was registered
first, so it fires first):

```
Creating new file to test functions were registered
testFunction ()
Test Method
Creating new file to test functions were deregistered
```

What happened: `runTests` registered `testFunction` (a module function) and
`manager.testMethod` (a bound method) to `kAfterNew`; the first `file(new=True)`
fired both; then both were deregistered, so the second `file(new=True)` fired
neither. (`testFunction (*args)` receives no args from `kAfterNew`, so it prints
the empty tuple `()`.)

### Run B — headless: register your own callback to a different signal

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import callbackManager_2027 as cm
from maya import cmds

mgr = cm.SceneCallbackManager.instance()

def on_selection(*args):
    print("  >> selection changed")

mgr.registerSelectionChanged(on_selection)
print("Registered. Now click different objects in the viewport / outliner.")
# ...select objects in Maya — each change prints "  >> selection changed"...

mgr.deregisterSelectionChanged(on_selection)
print("Deregistered. Selection changes are silent again.")
```

`kSelectionChanged` → niceName `SelectionChanged` → `registerSelectionChanged`
was auto-generated in `__init__`. Expected: every selection change prints the
line while registered; silent after deregister. (Selection changes fire *very*
often — deregister promptly.)

### Run C — demonstrate fault isolation (one bad callback does not break the rest)

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import callbackManager_2027 as cm
from maya import cmds

mgr = cm.SceneCallbackManager.instance()

def good1(*a): print("good1 ran")
def bad(*a):   raise RuntimeError("boom")
def good2(*a): print("good2 ran")

mgr.registerAfterNew(good1)
mgr.registerAfterNew(bad)
mgr.registerAfterNew(good2)

cmds.file(new=True, force=True)   # fires kAfterNew -> handler walks the list

mgr.deregisterAfterNew(good1)
mgr.deregisterAfterNew(bad)
mgr.deregisterAfterNew(good2)
```

**Expected:** `good1 ran`, then `bad` raises (a traceback is **logged** via
`logger.exception` — look in Maya's Output Window / stderr), then `good2 ran`
**still runs**. The bad callback is isolated; order and the surviving callbacks
are preserved.

### Run D — the singleton + auto-generated methods (introspection only)

```python
import sys
sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import callbackManager_2027 as cm

a = cm.SceneCallbackManager.instance()
b = cm.SceneCallbackManager.instance()
print("singleton: a is b ->", a is b)          # True

reg = [m for m in dir(a) if m.startswith('register')]
dere = [m for m in dir(a) if m.startswith('deregister')]
print("register* methods:", len(reg), " deregister* methods:", len(dere))
# One register/deregister pair per MSceneMessage signal (dozens).
print("has registerAfterNew:", hasattr(a, 'registerAfterNew'))   # True
```

Expected: `a is b -> True` (the singleton returns the same instance), and the
`register*` / `deregister*` counts are equal and large (one pair per
`MSceneMessage` signal — do not assume an exact number; it varies by Maya
version).

### One-shot paste (Run A condensed)

```python
import sys; sys.path.insert(0, r'/abs/path/AdvancedPythonForMaya-master/Utilities')
import callbackManager_2027 as cm; cm.runTests()
```

---

## Question and Answer

**Q1. In `cameraMessageCmd` I registered callbacks directly with Maya. Why build
a whole manager class here?**
A. Direct registration couples every tool to Maya's callback dispatch and to
each other: one tool's callback that raises can stall the signal for everyone,
and every tool has to remember its own `MCallbackId` and clean it up. The manager
adds three things: (1) a **single shared handler per signal** that multiplexes
to all user callbacks, (2) **exception isolation** (each user callback runs in
its own `try/except`, so a bad one is logged and skipped, not fatal), and (3)
**weak-reference storage** so callbacks belonging to deleted objects clean
themselves up instead of leaking.

**Q2. `registerAfterNew` and `deregisterAfterNew` aren't in the source text. How
do they exist?**
A. They are generated dynamically in `__init__` (lines 40–65). The loop walks
`dir(om.MSceneMessage)`, keeps every `k`-prefixed `int` enum, strips the `k`
(`kAfterNew` → `AfterNew`), and `setattr`s a `partial(self.__register,
signal=…)` / `partial(self.__deregister, signal=…)` pair onto the instance. The
manager therefore auto-supports *every* `MSceneMessage` signal Maya ships,
including ones added in future versions — with zero code changes.

**Q3. Why are methods stored in a `WeakKeyDictionary` but functions in a plain
`weakref.ref`?**
A. Two different weak-reference shapes for two different object lifetimes. A
bound method object (`instance.method`) is created fresh each time you access it
and can't be weak-ref'd directly, so the manager stores the **owning instance**
as the weak dict *key* (mapping to the underlying function). When the instance is
deleted, the dict entry vanishes automatically. A plain `def` function supports
weakref directly, so a simple `weakref.ref(callback)` is enough — when the
function is deleted or its module reloaded, the ref dereferences to `None` and
the handler skips it.

**Q4. What happens if I register a lambda inline, like
`mgr.registerAfterNew(lambda: print("hi"))`?**
A. **It silently never fires.** The lambda is passed in, stored as
`weakref.ref(callback)`, and returned from `register` — but the lambda has no
other strong reference anywhere, so Python garbage-collects it immediately. The
next time the handler runs, `callback()` dereferences to `None` and the callback
is skipped (lines 179–182). This is **verified**: a pure-Python test shows an
inline lambda's weakref is `None` the moment `register()` returns. The source
calls this out explicitly (lines 90–93) and leaves lambda/partial support as an
exercise. **Store your callback in a variable first** (`cb = lambda: …;
register(cb)`) if you need it to survive.

**Q5. Why does one raising callback not break the others?**
A. `__handler` wraps every individual callback call in `try/except` (lines
170–174 for methods, 185–188 for functions). When a callback raises, the
exception is caught, reported with `logger.exception(...)`, and the loop moves
on to the next callback. So a faulty tool degrades gracefully instead of
poisoning the signal. This isolation is the manager's headline feature.

**Q6. The `except:` in `__handler` is bare. Is that safe?**
A. It is intentional but slightly risky. A bare `except:` catches *everything*,
including `SystemExit` and `KeyboardInterrupt` (which inherit from `BaseException`,
not `Exception`). That means a callback that calls `sys.exit()` or is interrupted
with Ctrl-C would be silently swallowed rather than propagated. The robust form
is `except Exception:`, which still isolates normal errors while letting
control-flow exceptions through. Worth flagging if you harden this for production.

**Q7. Why `SceneCallbackManager.instance()` instead of just constructing one?**
A. The singleton (`_instance`, lines 24–30) guarantees one shared manager. If
two managers existed, each would register its *own* shared handler for the same
signal with Maya, doubling the work and splitting the callback lists — and
deregistering on one wouldn't affect the other. The singleton also means the
private `__callbacks` / `__callbackIDs` dicts are the single source of truth for
the whole session. (The singleton only holds if everyone goes through
`instance()`; calling `SceneCallbackManager()` directly bypasses it.)

**Q8. `runTests()` threw away my scene! Why?**
A. `kAfterNew` fires when a new file is created, so the test has to actually
create one — twice (`cmds.file(new=True, force=True)`, lines 212 and 216) — to
prove the callbacks fire when registered and are silent when deregistered.
`force=True` means it discards the current scene without prompting. Always run
`runTests()` in a disposable scene, or save first. This is the demo's most
important practical gotcha.

**Q9. I reloaded the module with `importlib.reload(cm)` and now my callbacks fire
twice / can't be removed. Why?**
A. The **ghost-callback-on-reload trap** from `cameraMessageCmd` applies here
too. `reload` re-runs the module: the `SceneCallbackManager` *class* is
redefined, `cm.SceneCallbackManager.instance()` now returns a *new* instance with
empty `__callbacks`/`__callbackIDs`, and `_instance` is reset — but **Maya still
holds references to the old `partial(self.__handler, …)` handlers** registered
with `MSceneMessage.addCallback`. Those old handlers keep firing (referencing the
old, now-orphaned instance), and because the new manager has no record of their
IDs, you cannot `removeCallback` them. **Always deregister everything (or quit
the session) before reloading** a callback module.

**Q10. If I register the same callback twice, does it fire twice?**
A. **No — for both functions and methods it is stored once.** Verified outside
Maya: two `weakref.ref(func)` to the same function compare equal, and two
`WeakKeyDictionary`s with identical `{instance: func}` contents also compare
equal. So the `if … not in callbackList` guard (lines 108, 116) correctly
prevents duplicates. (The dedup is *content-based*, not identity-based — which is
why it works despite each registration building a fresh container object.)

**Q11. The source says lambdas and `functools.partial` aren't supported. Why?**
A. Lambdas go through the function branch but, as in Q4, an *inline* lambda has
no surviving strong reference and is GC'd before it can fire. `functools.partial`
objects historically lacked a `__weakref__` slot, so `weakref.ref(partial(...))`
could raise `TypeError` — though this is **Python-version-dependent** (it
succeeds on some recent builds). The robust fix is the top Advanced Direction:
keep a strong-reference side-table for callables that can't be safely weak-ref'd.

---

## Advanced Directions

1. **Add lambda / partial / arbitrary-callable support (strong-ref side-table).**
   Today an inline lambda is GC'd immediately (Q4) and partials are unreliable
   (Q11). Add a `_strong = []` list on the manager; in `__register`, if
   `weakref.ref(callback)` raises `TypeError` (or the callable is a
   `partial`/`lambda` with no other owner), append it to `_strong` and store a
   sentinel in the callback list. Requires: a `_make_ref(callable)` helper that
   tries weakref and falls back to strong, a matching `_strong.remove(...)` path
   in `__deregister`, and a `deregister_all()` / `shutdown()` that clears
   `_strong`. Mirror the design of the PySignal library the source references.

2. **Self-cleaning sweep (fix the dead-entry leak).** When an instance is deleted
   or a function reloaded, its `WeakKeyDictionary` empties and its `weakref.ref`
   dereferences to `None` — but the now-empty container **stays in the list
   forever**. Add a `_sweep(signal)` call at the top of `__handler` that removes
   any list entry whose weak dict is empty or whose ref is `None`. Requires: a
   small filter pass; optionally a periodic sweep driven by `kSelectionChanged`
   or an idle timer to amortize cost.

3. **Per-signal introspection and enable/disable API.** Right now there is no way
   to ask "what's registered?" or to temporarily mute a signal. Add
   `callbacks(signal=None)` (returns the stored refs, dereferenced),
   `is_registered(callback, signal)`, `disable(signal)` / `enable(signal)` (a
   `_disabled` set the handler checks before dispatching), and `clear(signal)`.
   Turns the manager into something you can debug and operate, not just use.

4. **Harden the handler: `except Exception` + structured error reporting.**
   Replace the bare `except:` (Q6) with `except Exception`, add optional
   per-callback retry/timeout, and route failures to a configurable sink (a Qt
   toast, a log file, or a `kSceneMessage`-driven error panel) instead of only
   `logger.exception`. Requires: an `error_handler` callable set on the manager
   and a `set_error_sink(fn)` configurator.

5. **Generalize from `MSceneMessage` to a unified event hub.** `MNodeMessage`,
   `MDGMessage`, `MCameraMessage` (the system from `cameraMessageCmd`), and
   `MEventMessage` all share the register→store→remove lifecycle but with
   different "add callback" calls and signatures. Refactor `__init__`'s
   generation loop into a `_SignalFamily` abstraction (name, enum_class,
   add_callback_fn, signature) and generate register/deregister methods for each
   family — giving the whole studio one consistent `manager.registerNodeAdded(cb,
   node_type=...)` style API across every Maya message system.

6. **Auto-cleanup + installable package.** Ship the manager as a pip-installable
   package that auto-instantiates the singleton in `userSetup.py`, registers a
   `kMayaExiting` / `kAfterSoftwareRender` cleanup that calls
   `removeCallback` on every stored ID (preventing the reload trap of Q9 on
   quit), and exposes a tiny shelf button that prints the live registration table
   (building on Direction 3). Requires: a `pyproject.toml`, a `shutdown()`
   method, and a `userSetup.py` entry point.
