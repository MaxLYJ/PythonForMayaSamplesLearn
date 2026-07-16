# Before Our Next Class — Windows Setup (20 min)

> **For:** students with a Windows laptop attending Hour 2 ("Real Scripts:
> Command-Line Tools & Batch Operations").
> **Time required:** about 20 minutes, all before class. Please do this at
> home — we will not have time to install Python during the hour.
> **You don't need Maya for this homework.** Hour 2 is pure Python, run from
> a normal terminal.

Please complete the **three steps below** before the next session. At the
bottom there's a troubleshooting section for the common Windows pitfalls —
if anything fails, jump there first.

---

## What you need — checklist

- [ ] **Python 3 installed** on your Windows laptop (Step 1)
- [ ] **The course repo downloaded** to a folder you can find (Step 2)
- [ ] **VS Code opened once** with the repo folder (Step 3)

That's it. You don't need to read any code in advance or install anything
else. The four modules we use (`os`, `shutil`, `re`, `argparse`) all ship
inside Python itself — no extra downloads.

---

## Step 1 — Install Python 3 on Windows (~10 min)

This step is the one most students get wrong, so go slow and read each line.
The installer has **two checkboxes that are unchecked by default and you
must tick both**, or nothing in class will work.

### 1.1 Check whether Python is already installed

Open **PowerShell** (press the `Win` key, type `powershell`, press Enter) and
run:

```powershell
python --version
py --version
```

Read the result:

| What you see                                          | What it means                                                    |
|-------------------------------------------------------|------------------------------------------------------------------|
| `Python 3.10.x` or higher, from **either** command    | Python is installed. Skip to [Step 1.4](#14-verify-the-install) to confirm, then move on to Step 2. |
| `Python 2.7.x`                                        | Too old for this course. Continue with 1.2 below to install Python 3. |
| `'python' is not recognized...` AND `'py' is not...`  | Python is not installed. Continue with 1.2 below. |
| A **Microsoft Store** window pops up                  | Windows is hijacking the command. See [Troubleshooting → Gotcha A](#gotcha-a--typing-python-opens-microsoft-store), then come back here. |

### 1.2 Download the installer

1. Open a browser and go to **<https://www.python.org/downloads/>**.
2. The page auto-detects Windows. Click the big yellow button labelled
   **"Download Python 3.x.x"** (any 3.10 or newer is fine; the exact patch
   number doesn't matter).
3. A file named something like `python-3.12.3-amd64.exe` will download.

### 1.3 Run the installer — and tick BOTH checkboxes

1. Double-click the downloaded `.exe` file.
2. The first screen has a big **"Install Now"** button. **Do not click it
   yet.**
3. Look at the **bottom** of that same window. There are two checkboxes.
   Tick **both**:

   - ☑ **Add python.exe to PATH**  ← *the most important one; without this, PowerShell will not find `python`*
   - ☑ **Use admin privileges when installing py.exe**  ← *installs the `py` launcher for everyone on the machine*

   These two boxes are **unchecked by default**. If you rush past them, you
   will have to uninstall and redo this step.

4. **Now** click **"Install Now"**.
5. Windows may show a "Do you want this app to make changes?" prompt — click
   **Yes**.
6. Wait about 30 seconds. When you see *"Setup was successful"*, look for a
   button labelled **"Disable path length limit"** at the bottom and click
   it (recommended, prevents obscure errors later; skip if it asks for admin
   you don't have).
7. **Close the installer.**

### 1.4 Close and RE-OPEN PowerShell — this is critical

PATH changes only apply to **new** PowerShell windows. If you keep using the
same one you opened in 1.1, `python` will still not be recognised even though
the install succeeded. So:

1. Close every PowerShell window you have open.
2. Open a **fresh** PowerShell (Win key → type `powershell` → Enter).
3. Run:

   ```powershell
   python --version     # should print: Python 3.12.x  (or similar)
   py --version         # should print the same
   ```

If both commands print a Python 3 version number, **Python is installed
correctly.** Continue to Step 2.

If either one fails, go to [Troubleshooting](#troubleshooting) before moving
on — do not skip ahead, because Step 2 and Step 3 depend on Python working.

---

## Step 2 — Download the course repo (~3 min)

The code we'll work through lives in a folder of Python files. You need your
own copy on your laptop.

### Option A — Download as a ZIP (easiest)

1. Ask your instructor for the repo URL (or look in the class invitation
   email). It will look like `https://github.com/<...>/PythonForMayaSamplesLearn`.
2. Open that URL in a browser.
3. Click the green **"<> Code"** button, then **"Download ZIP"**.
4. **Right-click the downloaded `.zip` → "Extract All…"** and pick a short,
   memorable location, for example:

   ```
   C:\Users\<you>\MayaPython\
   ```

   Avoid deeply nested paths like your Desktop's downloads subfolder — long
   paths make Python commands painful to type.

5. After extraction you should have a folder like
   `C:\Users\<you>\MayaPython\PythonForMayaSamplesLearn\` containing
   `commandLine\`, `objectRenamer\`, `gearCreator\`, etc.

### Option B — Clone with git (if you already use git)

```powershell
cd C:\Users\<you>\
git clone <repo-url> MayaPython\PythonForMayaSamplesLearn
```

Either way, **remember the full path** to the `PythonForMayaSamplesLearn`
folder — you'll need it in class.

---

## Step 3 — Open the repo in VS Code once (~2 min)

We'll be reading and editing code in **Visual Studio Code** (free). If you
don't have it yet, install from <https://code.visualstudio.com/> (default
options are fine).

Then do this once, before class, so the first launch isn't awkward during
the lesson:

1. Open VS Code.
2. **File → Open Folder…** → navigate to the
   `PythonForMayaSamplesLearn` folder you extracted in Step 2 → click
   **Select Folder**.
3. In the left sidebar, expand `commandLine` and click `renamer_2027.py`.
   You should see the file's code on the right.
4. **Install the Python extension** (recommended): click the Extensions icon
   on the left (or `Ctrl+Shift+X`), search for "Python" (the one by
   Microsoft, with millions of installs), click **Install**.

You don't need to run anything yet — just confirm the file opens and is
readable.

---

## You're done — what to bring to class

- Your Windows laptop, fully charged.
- Python installed (you verified `python --version` works in a fresh
  PowerShell).
- The `PythonForMayaSamplesLearn` folder extracted somewhere you can find.
- VS Code installed and able to open `renamer_2027.py`.

You do **not** need to install Maya for this class — Hour 2 is pure Python.
(Maya comes back in Hour 3.)

---

## Troubleshooting

If anything in Steps 1–3 failed, work through this section. Each gotcha
includes the exact fix.

### Gotcha A — Typing `python` opens Microsoft Store

**Symptom:** You type `python --version` and instead of running, a Microsoft
Store window pops up advertising Python.

**Cause:** Windows 10/11 has "App execution aliases" that intercept the
words `python` and `python3` and try to send you to the Store instead of
running any real Python you installed.

**Fix:**

1. Open **Settings** (`Win + I`).
2. Go to **Apps → Advanced app settings → App execution aliases**.
3. Find both **"App Installer  python.exe"** and
   **"App Installer  python3.exe"** and toggle them **OFF**.
4. Close and reopen PowerShell.
5. Run `python --version` again. Now it either finds your real Python
   install, or honestly says "not recognized" (in which case go back to
   Step 1.2 and actually install Python).

### Gotcha B — "I ticked the PATH box but `python` still isn't recognised"

**Symptom:** You completed the installer, ticked both checkboxes, but in
PowerShell `python --version` still says `'python' is not recognized`.

**Cause:** You're still using the same PowerShell window you had open before
installing. PATH changes only apply to shells opened *after* the install.

**Fix:** Close every PowerShell window. Open a brand new one. Retry.

### Gotcha C — `'py' is not recognized` but `python` works (or vice versa)

**Symptom:** One command works, the other doesn't.

**Fix:** You only need **one** of them to work for class. If `python
--version` prints a Python 3 version, you're ready — ignore `py`. If only
`py` works, that's also fine; in class, substitute `py` every time you see
`python` in the instructions.

### Gotcha D — The installer put Python in a weird AppData folder

**Symptom:** You went looking for where Python landed and found it under
`C:\Users\<you>\AppData\Local\Programs\Python\Python3x\`.

**Cause:** That's the normal location for a per-user install (the default
"Install Now" option).

**Fix:** None needed. You never have to open that folder. `python` and `py`
on the command line are all you'll ever use.

### Gotcha E — "Should I just use the Microsoft Store Python instead?"

**Short answer:** No, not for this class.

**Why:** The Store version sandboxes file access. The tool we'll build —
`renamer_2027.py` — renames and copies real files on disk. The Store Python
will block it the moment it touches a file outside your Documents folder,
and you'll spend the whole class fighting permissions. The python.org
installer (Step 1.2 above) has unrestricted filesystem access, which is what
a file-renaming tool needs.

### Gotcha F — `python -c "import os, shutil, re, argparse"` fails

**Symptom:** You run

```powershell
python -c "import os, shutil, re, argparse; print('stdlib ok')"
```

and you get `ModuleNotFoundError` instead of `stdlib ok`.

**Cause:** Something is wrong with the Python install itself.

**Fix:** Uninstall Python from **Settings → Apps → Installed apps →
Python 3.x → Uninstall**, then redo Step 1.2 from scratch. Make sure you
**tick both checkboxes** in the installer this time.

### Still stuck?

Email your instructor **before** class with:
- The exact command you ran.
- The exact error message (copy-paste the whole thing, or screenshot the
  PowerShell window).
- Whether you ticked both checkboxes in the Python installer.

We'll get you sorted before the hour starts. Do **not** wait until class —
we won't have time to install Python live.
