# Python For Maya: Artist Friendly Programming
test
## Table of Contents

* [Hands-On Learning Curriculum (all 19 demos)](CURRICULUM.md)
* [Course Outline](#course-outline)
  * [Demos by Difficulty & Learning Order](#demos-by-difficulty--learning-order)
* [Software Being Used](#tools-that-will-be-used)
* [Resources](#other-resources)
  * [Books](#books)
  * [Websites](#websites-and-blogs)

## Course Outline

Code samples for people who take part in my Python for Maya course

The course is available here
<a href="https://www.udemy.com/python-for-maya/?couponCode=TWITTER16BF">
<p>Python For Maya: Artist Friendly Programming</p>
<br/><img src="http://dgovil.com/wp-content/uploads/2016/11/1009476_7f51_2.jpg">
</a>

This course will teach Python for Maya using an artist friendly approach, by breaking down concepts into small digestible pieces and giving projects with real world use.

> 📚 **Learning this codebase hands-on?** Every demo ships a step-by-step `HowToStart<Demo>.md` guide — *how to build the test scene → how to run each function → Q&A → advanced extensions*. The complete **[CURRICULUM.md](CURRICULUM.md)** indexes all **19 guides** across 7 learning phases, including the eight API/plugin demos (`fileDialog`, `manipulatorMath`, `mathTableControl`, `py1AnimCubeNode`, `profilerDump`, `cameraMessageCmd`) and the entire `AdvancedPythonForMaya-master` section that the basics table below does not cover. If you want to *run* the demos rather than just read them, start there.

### About Me

You can also find more information about me on my website

[http://www.dgovil.com](http://dgovil.com/)

### Projects We'll Be Completing

During the course, we'll create a few different projects to both showcase how Python is useful in a real world context,and to learn new concepts

* Create and prop geometry with a simple rig ([LINK](introduction/))
* Rename and organize a scene ([LINK](objectRenamer/))
* Automatically create Gears for modelling with a configurable amount of teeth ([LINK](gearCreator/))
* An Animation Tweener with a simple UI ([LINK](tweener/))
* A Library tool for Rigging Controls with a UI ([LINK](controllerLibrary/))
* A Light Manager ([LINK](lightManager/))
* A command line file tool to manage image sequences ([LINK](commandLine/))

### Demos by Difficulty & Learning Order

Here is the complete list of demos in this repo, organized into the order a beginner should tackle them — from absolute basics to the most advanced tool. This mirrors the natural progression of the course.

| # | Demo | Difficulty | Concepts you learn |
|---|------|-----------|--------------------|
| 1 | `introduction/helloWorld` | ★☆☆☆☆ | `print`, comments, strings — the "is Python even working?" test |
| 2 | `introduction/helloCube` | ★☆☆☆☆ | `from maya import cmds`, creating nodes, variables, lists, indexing, `setAttr`/`parent` |
| 3 | `commandLine/renamer` | ★★☆☆☆ | `argparse`, file I/O (`os`, `shutil`), `def main()`, the `if __name__ == '__main__'` pattern |
| 4 | `objectRenamer/renamer1` | ★★☆☆☆ | `cmds.ls`/`listRelatives`/`objectType`, `for` loops, `if/elif/else`, string split & concat |
| 5 | `objectRenamer/renamer2` | ★★★☆☆ | Functions with defaults, dictionaries + `.get()`, docstrings, `raise` exceptions |
| 6 | `gearCreator/gears1` | ★★★☆☆ | Multi-arg functions, returning tuples, poly-modeling cmds, `%` string formatting, `*args` unpacking |
| 7 | `gearCreator/gears2` | ★★★☆☆ | **Classes**: `class`, `__init__`, `self`, methods, storing state on the instance |
| 8 | `tweener/tweener` | ★★★★☆ | Animation API (`keyframe`, `setKeyframe`, `currentTime`), list comprehensions, **first Maya UI** (`cmds.window`, sliders, buttons) |
| 9 | `tweener/reusableUI` | ★★★★☆ | Class **inheritance** (`BaseWindow` → child windows), reusable UI scaffolding, `*args` callbacks |
| 10 | `controllerLibrary/controllerLibrary` | ★★★★★ | **PySide/Qt UI**, `json` save/load, screenshot via `playblast`, `QListWidget`, icon galleries |
| 11 | `lightManager/lightManager` | ★★★★★ | The capstone: **PyMel**, custom Qt `Signal`s, `OpenMayaUI` + `wrapInstance`, dockable UI, presets |

> **Demos 10 & 11 are both "5-star" but 11 builds on 10.** Do `controllerLibrary` first, then `lightManager`.

#### Suggested learning path

**Phase 1 — Python fundamentals inside Maya** (demos 1–2)
You're just learning to talk to Maya: print, variables, lists, and creating a cube. If `helloCube` runs, your setup works.

**Phase 2 — Real scripts & functions** (demos 3–5)
Now you write reusable code: command-line tools, looping over selections, packaging logic into functions with docstrings and error handling. By the end of `renamer2` you can write a clean, importable utility.

**Phase 3 — Object-oriented programming** (demos 6–7)
`gears1` shows the functional approach; `gears2` rewrites it as a class. This is the key conceptual leap — understanding `self` and storing state on an object.

**Phase 4 — Animation & Maya's built-in UI** (demos 8–9)
You learn the animation API and build your first windows with `cmds`. `reusableUI` then teaches inheritance by reusing one base window for two different tools (tweener + gear creator).

**Phase 5 — Qt/PySide professional UIs** (demos 10–11)
The two big tools. `controllerLibrary` is the gentler intro to Qt; `lightManager` is the most complex sample in the repo and pulls together everything: PyMel, signals, docking, and the Maya API.

#### A few notes

* **`lightManager/lightManager2016Below`** is not a separate demo — it's the *same* tool using the legacy `dockControl` API for Maya 2016 and earlier. Skip it unless you specifically need old-Maya support; use `lightManager` instead.
* **Each demo has a `_2027.py` companion** (e.g. `helloCube_2027.py`, `lightManager_2027.py`) that runs in **Maya 2027** (Python 3 + PySide6). Learn from the original commented files; run the `_2027` versions. The 6 demos that were already Python 3-compatible (gears, tweener, command-line renamer, renamer2) have verified copies with a header note.
* **The 7 empty `__init__.py` files** just mark the folders as Python packages — they contain no demos.
* Don't skip from demo 5 to demo 10 — the Qt demos assume you already understand functions, classes, and inheritance from the earlier ones.

## Tools That Will Be Used

For the course we will use the following

* **Maya 2017**

  This is currently the latest version of Maya and has some major changes that will be covered.
  Feel free to use an older version of Maya (as low as 2011), as I will cover the differences and give you the knowledge to adapt
  
  You can download an education version of Maya 2017 here: http://www.autodesk.com/education/free-software/maya
  You can download a Maya 2017 trial here: http://www.autodesk.com/products/maya/free-trial
  
* **Python 2.7**

  Obviously, this course will use Python, but it is important to note we will be using Python 2.7 and not Python 3.x
  
  If you do not already have Python installed, I recommend downloading Anaconda instead.
  It is a packaged version of Python that comes with a lot of great libraries prebuilt for you, and is much easier to get started with than the official Python.
  Please remember to download the Python 2.7 version

  https://www.continuum.io/downloads
  
  Maya 2017 uses Python 2.7 and this is also the agreed upon standard by the VFX Reference Platform www.vfxplatform.com
  Maya 2014-2016 also use Python 2.7, whereas Maya 2011-2013 use Python 2.6.
  
  The latest version of Python is Python 3.5, however Python 3.x has introduced many breaking changes to Python.
  These changes are for the better but due to large investment into Python 2 code, Maya will continue to be on Python 2 for a while longer.
  
* **PyCharm**

  PyCharm is a very well established IDE with a lot of useful features for a beginner to both learn with and grown into a full fledged developer.
  It is my editor of choice today.
  
  I would recommend downloading PyCharm Edu from here: https://www.jetbrains.com/pycharm-edu/
  
  PyCharm Edu is a version of PyCharm with a simplified interface (optional) and coursework that will help a user learn Python in their spare time.
  
* **Maya DevKit**

  Unfortunately from Maya 2016 onwards, Autodesk stopped shipping the Maya developer kit with Maya.
  This isn't super necessary for our course, but it does provide some nice autocomplete features in our editors.
  
  If you're on **Maya 2016** download the zip file from here: https://github.com/autodesk-adn/Maya-devkit
  
  If you're on **Maya 2017 or higher** download it from here: https://www.autodesk.com/developer-network/platform-technologies/maya
  
  
  Instructions on how to set up your directories for your specific OS are here: http://help.autodesk.com/view/MAYAUL/2017/ENU//?guid=__files_Setting_up_your_build_environment_htm
  
* **Qt.py**

  For the Qt portion of our course, there are several Qt libraries we can use.
  If you're using Maya 2017 or above, you can use PySide2  or PyQt5. If you're using Maya 2016 or below, you can use PySide or PyQt4.
  
  Rather than having to develop for all these options, we can use a library that can make use of whichever one it finds.
  This library is called **Qt.py** and you can download it here: https://github.com/mottosso/Qt.py
  
  
* **Other Editors**

  There are a lot of other editors, and I will personally not be using them for this course.
  However, if you have a preference for other editors, I will go over setting up some of the editors with Maya.
  The following editors will be covered
  
  * Sublime Text
  * Atom
  * Visual Studio Code
  * Eclipse
  
* **Operating System**
  My preferred operating system is **Windows** and it will be what I will be using for the entire course.
  That said, I also use **macOS** and **Linux** and where anything should be treated differently, I will make mention of it.
  

## Libraries That Will Be Covered

The course will cover the following libraries

* `maya.cmds`
* `pymel`
* `Qt`
* `PySide` / `PySide2`


## Other Resources

### Books

Just a note that these links are affiliate links that will go to your local Amazon storefront.

* [Maya Python For Games And Film](http://go.redirectingat.com?id=101037X1556917&xs=1&url=https%3A%2F%2Fwww.amazon.com%2FMaya-Python-Games-Film-Reference%2Fdp%2F0123785782%2Fref%3Dsr_1_1%3Fie%3DUTF8%26qid%3D1479605478%26sr%3D8-1%26keywords%3Dmaya%2Bpython%2Bfor%2Bfilm%2Band%2Bgames)

  This was the book that I learned Python from, and I cannot recommend it enough. It goes a lot more in depth on each topic, as only a book can do, and it's probably the resource I recommend the most.
  
* [Practical Maya Programming With Python](http://go.redirectingat.com?id=101037X1556917&xs=1&url=https%3A%2F%2Fwww.amazon.com%2FPractical-Programming-Python-Robert-Galanakis%2Fdp%2F1849694729%2Fref%3Dsr_1_1%3Fie%3DUTF8%26qid%3D1479605681%26sr%3D8-1%26keywords%3Dpractical%2Bpython%2Bmaya)

  Rob Galanakis is a fantastic resource on Python, who runs the [Tech-Artists](http://tech-artists.org/) forum, which is where I often went to get help when I was stuck on issues, or wanted to learn what other people were doing. His book is a great resource as well.
  
* [Rapid GUI Programming with Python and Qt: The Definitive Guide to PyQt Programming](http://go.redirectingat.com?id=101037X1556917&xs=1&url=https%3A%2F%2Fwww.amazon.com%2FRapid-GUI-Programming-Python-Definitive-ebook%2Fdp%2FB004YW6LNA%2Fref%3Dsr_1_1%3Fie%3DUTF8%26qid%3D1479605837%26sr%3D8-1%26keywords%3Drapid%2Bpyqt)

  If you're interested in learning more about Qt, this is the best book to have in my opinion. He goes from very basic Qt useage to very advanced concepts. The book is based around PyQt4, but if you've watched my course, it should be easy enough to switch to whichever Qt library you're using
  
* [Complete Maya Programming: An Extensive Guide to MEL and C++ API](http://go.redirectingat.com?id=101037X1556917&xs=1&url=https%3A%2F%2Fwww.amazon.com%2FComplete-Maya-Programming-Extensive-Kaufmann%2Fdp%2F1558608354%2Fref%3Dsr_1_1%3Fie%3DUTF8%26qid%3D1479607371%26sr%3D8-1%26keywords%3DMEL%2BC%252B%252B)

 This is for MEL and C++ obviously, and quite an old book, but it's one that is still incredibly useful if you're interested in those languages, and one that many developers have learned from.
 
 
### Websites and Blogs

* [Rigging Dojo] (http://www.riggingdojo.com/)

 Rigging Dojo is **the** online school for rigging and technical skills. They have a ton of great mentored courses on Python, C++, Rigging etc..
 
* [Python For Maya: Google Group] (https://groups.google.com/forum/?fromgroups#!forum/python_inside_maya)

  A great google group run by Justin Israel, where people can ask questions about Python and get help from other Python developers.

* [Learn X in Y Minutes: Python](https://learnxinyminutes.com/docs/python/)

  A website dedicated to giving a really quick introduction to programming languages.

* [TDsAnonymous] (http://www.tdsanonymous.com/)

  A companion site for an online community I'm part of. The community is invite only, but the site is a place where we can contain resources that we find useful.
  
* [Zetcode PyQt4](http://zetcode.com/gui/pyqt4/) and [Zetcode PyQt5](http://zetcode.com/gui/pyqt5/)

 A quick introduction to using PyQt4 and PyQt5. If you're using PySide, just replace the library name.
 This is where I learned to use PyQt4 from when I was teaching myself Python, and it's the first place I point people to when they want to learn.

* [CodeHeadWords](https://codeheadwords.com/)

  This is a blog run by John Hood who is a coworker of mine who's taught me a ton. 
