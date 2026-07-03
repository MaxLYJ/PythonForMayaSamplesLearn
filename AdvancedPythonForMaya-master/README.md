# Advanced Python for Maya

In this project, we'll be learning how to use the Python API for OpenMaya to create a variety of plugins and tools for Maya.



The OpenMaya API gives us deeper access to Maya's internals than the Commands API that is used by MEL and Python,
without having to switch to using C++.

At the end of the course, we'll also be converting a Python Plugin to C++.

## Maya 2027 Versions

Every `.py` demo in this repo now has a **`_2027.py`** companion (e.g. `helloWorldCmd.py` → `helloWorldCmd_2027.py`) that runs in **Maya 2027** (Python 3 + OpenMaya API 2.0).

* The **original files** are kept intact as teaching references (they target Maya 2018 / Python 2).
* The **`_2027.py`** files are the ones you should load and run in Maya 2027.
* 6 demos were already Python 3-compatible and only needed verified copies; 6 demos needed real conversion (Python 2 `print` statements, hardcoded drive paths, and `None` guards for `os.getenv`).

## Demos by Difficulty & Learning Order

Here is the complete list of demos in this repo, organized into the order a beginner to the OpenMaya API should tackle them — from printing your first API message to compiling a C++ plugin.

| # | Demo | Difficulty | Concepts you learn |
|---|------|-----------|--------------------|
| 1 | `Intro/simple` | ★☆☆☆☆ | Importing OpenMaya API 1.0 vs 2.0, `MGlobal.displayInfo`, the difference between `maya.OpenMaya` and `maya.api.OpenMaya` |
| 2 | `Commands/decorators` | ★★☆☆☆ | Pure-Python warmup: function wrappers, `*args`/`**kwargs`, the `@decorator` syntax, `functools.wraps` |
| 3 | `Intro/standalone` | ★★☆☆☆ | Using the API outside a plugin, `MItDependencyNodes` iterator, `MFnAnimCurve`, benchmarking cmds vs API |
| 4 | `Commands/helloWorldCmd` | ★★★☆☆ | Your first **plugin**: `MPxCommand`, `maya_useNewAPI`, `MSyntax` + `MArgDatabase` for flags, `initializePlugin` / `uninitializePlugin` |
| 5 | `Commands/distributeCmd` | ★★★☆☆ | A full command with **undo/redo**: `MItSelectionList`, `MFnTransform`, `isUndoable`, `undoIt`, `redoIt`, classmethod/staticmethod creators |
| 6 | `Nodes/minMaxNode` | ★★★★☆ | Your first **dependency node**: `MPxNode`, `MTypeId`, `MFnNumericAttribute` / `MFnEnumAttribute`, `compute()`, `attributeAffects` |
| 7 | `Utilities/contextExamples` | ★★☆☆☆ | Python context managers (`with`), `__enter__`/`__exit__`, `@contextmanager` decorator, `try/finally` pattern |
| 8 | `Utilities/createdNodesContext` | ★★★☆☆ | A practical context manager using the API: `MDGMessage.addNodeAddedCallback`, tracking created nodes, `MFnDagNode` / `MFnDependencyNode` |
| 9 | `Utilities/callbackManager` | ★★★★★ | A production-grade **singleton callback system**: `MSceneMessage`, dynamic method generation via `setattr`, `weakref`, `inspect.ismethod`, graceful error handling |
| 10 | `Nodes/pushDeformer` | ★★★★☆ | A **deformer node** (requires OpenMaya API 1.0): `MPxDeformerNode`, `asMPxPtr`, `cvar` geometry-filter attributes, `deform()`, vertex normals, paintable weights |
| 11 | `Scene/characterRoot` | ★★★★☆ | A **custom transform node** (API 1.0): `MPxTransform`, `MPxTransformationMatrix`, metadata attributes, registering a custom AE template |
| 12 | `Scene/customLocator` | ★★★★★ | The capstone viewport demo: `MPxLocatorNode` + **Viewport 2.0 `MPxDrawOverride`**, `MUIDrawManager`, `MUserData`, custom shape drawing, draw registry |
| 13 | `Compiling/minMaxPlugin` | ★★★★★ | Bonus: converting the Python `minMaxNode` into a compiled **C++ plugin** with CMake and the Maya devkit |

> **Demos 10–13 are all "4–5 star".** They layer on top of everything before them — do them last, and in the order shown.

### Suggested learning path

**Phase 1 — Meet the API** (demos 1–3)
Start by seeing how OpenMaya differs from `maya.cmds`, brush up on decorators (which plugin creators rely on), and run a standalone benchmark that proves the API is faster than cmds.

**Phase 2 — Your first plugins: Commands** (demos 4–5)
Build a command plugin, then a real one with undo/redo. This is where the `initializePlugin` / `uninitializePlugin` lifecycle clicks.

**Phase 3 — Dependency nodes & math** (demo 6)
The conceptual leap from "command" to "node that lives in the dependency graph and recomputes when inputs change." Understanding `compute()` + `attributeAffects` is essential before the deformer and locator.

**Phase 4 — Python mastery: contexts & callbacks** (demos 7–9)
Context managers clean up after themselves; the callback manager shows how to safely hook Python functions into Maya's scene messages without leaking memory or crashing Maya.

**Phase 5 — Advanced node types** (demos 10–12)
The deformer (API 1.0), the custom transform (API 1.0), and the custom locator with a Viewport 2.0 draw override (API 2.0). These are the hardest samples and pull together everything.

**Phase 6 — C++** (demo 13)
Optional finisher: take a working Python node and recompile it as a C++ plugin for speed.

### A few notes

* **Two APIs coexist.** `maya.api.OpenMaya` (API 2.0) is the modern, Pythonic one used by most demos. `maya.OpenMaya` + `maya.OpenMayaMPx` (API 1.0) is the older C++ wrapper still required for **deformers** (`pushDeformer`) and **custom transforms** (`characterRoot`). The `_2027` files keep each demo on the same API its original used.
* **Node/Plugin IDs** (e.g. `MTypeId(0x01010)`) are hardcoded in each plugin. They're in the safe development range `0x00000`–`0x7FFFF`; if you release plugins publicly you must request a unique range from Autodesk.
* **The `maya_useNewAPI()` function** is a marker that tells Maya a plugin is written against API 2.0. It appears in every API 2.0 plugin and does nothing — but it must be present.
* **Empty `__init__.py` files** mark the folders as Python packages so you can do `from Commands import helloWorldCmd` — they contain no demos.
* **Loading a plugin** in Maya 2027: `cmds.loadPlugin(path_to_2027_file)` then call the command / create the node as shown in each file's trailing docstring example.

# Software Used

For this course I'll be using the following programs:

* Autodesk Maya 2018

    While you can follow most of this course in Maya 2011 and above, I highly recommend using Maya 2018 if possible.

    A trial is available here:

    https://www.autodesk.ca/en/products/maya/free-trial

    You can also get a student edition if you are part of an officially recognized educational institution:

    https://www.autodesk.com/education/free-software/maya

* PyCharm

    You can use any text editor you like, but I will be using PyCharm because it is my personal preference.

    You can get PyCharm EDU here:

    https://www.jetbrains.com/pycharm-edu/download/



# Resources

## Maya Documentation

Autodesk has great documentation for the Maya API. I highly recommend giving it a read

### General Documentation

This is a general overview of how the API is structured and how it interacts with Maya.
Most of this is written with C++ in mind, but it is a very useful resource.

http://help.autodesk.com/view/MAYAUL/2018/ENU//?guid=__files_API_Introduction_htm

### Python 2.0 API

This is the documentation for the API we'll be covering.

It isn't as complete as the API for C++ but is easier to read

http://help.autodesk.com/view/MAYAUL/2018/ENU//?guid=__py_ref_index_html


### C++ API

The C++ is the main API for Maya, and is the best reference for any of the code we'll be using.

If you can't find information on something in the Python API docs, this is the best place to fallback to.

http://help.autodesk.com/view/MAYAUL/2018/ENU//?guid=__cpp_ref_index_html


## Devkit

You will want to get the Maya developer kit so that you can use autocompletion and see some of Autodesks code examples.

You can get the devkit for Maya 2016 and above here: https://www.autodesk.com/developer-network/platform-technologies/maya#

Read here on how to install the devkit

http://help.autodesk.com/view/MAYAUL/2018/ENU//?guid=__files_Setting_up_your_build_environment_htm

Older versions of Maya will either have it bundled or can reuse the devkits from above.

## Books and Blogs

There are many other bits of content that are extremely useful to learn the API.

I'll be adding them here.

* **Chad Vernons Blog** : http://www.chadvernon.com/blog/


