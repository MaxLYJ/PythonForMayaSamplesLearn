# Showcase — Real-World Maya Python Tools

Curated examples to show students in Block A of Hour 1 ("Why Python in
Maya?"). Each entry includes what it does, why it's impressive, and a link
to see it in action.

> **How to use this in class:** Don't show all of them. Pick **2 or 3** that
> match your students' interests (rigging → mGear; modeling → Batch Renamer;
> animation → StudioLibrary). Demo the tool, then say: *"This is built with
> the same Python you'll write today."*

---

## The "wow" demos — lead with one of these

### 1. mGear — Modular Rigging Framework
- **What:** Open-source rigging framework for Maya. Build a full character
  rig in minutes using modular components (spine, arm, leg, finger), with
  IK/FK switching, constraints, and a synoptic picker UI.
- **Why it's impressive:** It's what real animation studios use. Fully
  open-source on GitHub, you can read every line.
- **See it:** [mgear-framework.com](https://mgear-framework.com/) ·
  [github.com/mgear-dev](https://github.com/mgear-dev) ·
  [Quick Character Rigging demo (YouTube)](https://www.youtube.com/watch?v=FDYsVEccEmE)
- **Class hook:** *"You'll learn the building blocks of tools like this
  today — classes (hour 4), Qt UIs (hour 6). mGear is the same ingredients,
  just more of them."*

### 2. AdvancedSkeleton — Auto-Rigging
- **What:** Free-for-personal-use auto-rigger. Place guide joints, click
  "Build," get a production-ready rig with controls, IK, and skinning
  helpers. Supports any body configuration (3 heads, 5 legs, 100 fingers).
- **Why it's impressive:** 25+ years of refinement. The de facto auto-rigger
  for many freelancers and small studios.
- **See it:** [Autodesk App Store](https://marketplace.autodesk.com/apps/0c4ed61a-df53-4950-839b-4e2de21c879d) ·
  [Character Rigging Tutorial (YouTube)](https://www.youtube.com/watch?v=M0W7cT2DUDY)
- **Class hook:** *"This entire tool is a Python program. The buttons, the
  rig generation, the UI — all Python talking to Maya."*

### 3. StudioLibrary — Animation & Pose Library
- **What:** Open-source tool to save, organize, and re-apply poses and
  animations. Icon gallery, drag-drop, mirroring, etc.
- **Why it's impressive:** Looks like a polished commercial app. Used at
  studios worldwide. Pure Python + Qt.
- **See it:** [github.com/AntonyCarpenter/studiolibrary](https://github.com/AntonyCarpenter/studiolibrary)
- **Class hook:** *"By hour 6 today you'll have built the foundation of a
  tool exactly like this — a Qt window with icon galleries and JSON
  save/load. The `controllerLibrary` demo is a stripped-down version."*

---

## Renaming & scene cleanup — close to demo 1

These map directly to the `objectRenamer` demo students will build in hour 3.

### 4. Batch Renamer (RassoulEdji)
- **What:** Python tool for renaming hundreds of objects in large scenes.
  Prefix/suffix/numbering/search-replace.
- **See it:** [github.com/RassoulEdji/Batch-Renamer](https://github.com/RassoulEdji/Batch-Renamer)
- **Class hook:** *"This is exactly what `objectRenamer` does — but polished
  for production. Same Python, more features."*

### 5. Renamer 2.1 (commercial add-on)
- **What:** A polished paid renaming tool with regex, numeration, presets.
- **See it:** [cgchannel.com review](https://www.cgchannel.com/2024/05/check-out-maya-productivity-add-on-renamer-2-1/)
- **Class hook:** *"People charge money for tools like the one you'll build
  free today. The skills are real."*

### 6. EzRename
- **What:** Free renaming tool with a Qt UI, published on ArtStation.
- **See it:** [artstation.com/artwork/ybzlB8](https://www.artstation.com/artwork/ybzlB8)
- **Class hook:** *"The whole UI is Python + PySide. That's hour 6."*

---

## Pipeline & studio tools — the long view

### 7. Python for Maya course — Alexander Richter TD
- **What:** A 12-hour commercial video course covering pipeline tool
  development end-to-end. Good reference for what comes after this workshop.
- **See it:** [alexanderrichtertd.com/python-maya](https://www.alexanderrichtertd.com/python-maya)

### 8. Tech-Artists.org — "Base 3D Pipeline Tool Set"
- **What:** Community thread outlining the actual tools every studio
  pipeline needs: project manager, export/import, asset library, publish
  system, etc.
- **See it:** [tech-artists.org discussion](https://www.tech-artists.org/t/maya-python-tools-question-3d-pipeline-example-tools/6211)
- **Class hook:** *"This is what tech artists actually build. Today's demos
  are the foundation; these are the destination."*

### 9. Python for Maya Artists (VFX Pipeline, YouTube)
- **What:** Free video series showing custom Maya tool building with
  Python + PyMEL.
- **See it:** [youtube.com/watch?v=IBFi6SUHnzg](https://www.youtube.com/watch?v=IBFi6SUHnzg)

---

## Open-source auto-riggers — for the curious

### 10. leixingyu/autoRigger
- **What:** Procedural modular auto-rigger for Maya with templates for
  biped, quadruped, etc.
- **Why useful:** Read the source — it's a real-world example of the class
  architecture we cover in hour 4.
- **See it:** [github.com/leixingyu/autoRigger](https://github.com/leixingyu/autoRigger)

### 11. Xrod21/Auto-Rig-Tool
- **What:** Simpler Python auto-rig starter. Easier to read than mGear.
- **See it:** [github.com/Xrod21/Auto-Rig-Tool](https://github.com/Xrod21/Auto-Rig-Tool)

### 12. morganloomis/ml_tools
- **What:** Collection of animation and rigging utilities for Maya.
  Battle-tested, well-documented.
- **See it:** [github.com/morganloomis/ml_tools](https://github.com/morganloomis/ml_tools)

---

## Reading & community

### 13. *Maya Python for Games and Film* (Mechtley et al.)
The classic book. If students ask "where do I learn more deeply," this is
the answer.

### 14. Python Inside Maya (Google Group)
Industry-grade Q&A. Most Maya Python experts hang out here.
- [groups.google.com/forum/#!forum/python_inside_maya](https://groups.google.com/forum/#!forum/python_inside_maya)

### 15. Tech-Artists.org forums
The professional community for technical artists.
- [tech-artists.org](https://tech-artists.org/)

---

## Map: showcase → which hour teaches the building blocks

| Showcase tool                | Uses concepts from…              |
|------------------------------|----------------------------------|
| Batch Renamer                | Hour 3 (`objectRenamer`)         |
| EzRename                     | Hours 3 + 6 (Qt UI)              |
| StudioLibrary                | Hour 6 (`controllerLibrary`)     |
| mGear / AdvancedSkeleton     | Hours 4 + 5 + 6 (everything)     |
| ml_tools                     | Hours 3 + 4 + 5                  |
| This repo's `lightManager`   | Hour 7 (capstone, pulls it together) |

> **The pitch to students:** *"Every tool on this list is built from the
> same ingredients you'll learn today. The only difference between you and
> these tools is time and practice — not different knowledge."*

---

## Sources

- [mGear Framework](https://mgear-framework.com/) · [mGear on GitHub](https://github.com/mgear-dev)
- [AdvancedSkeleton on Autodesk App Store](https://marketplace.autodesk.com/apps/0c4ed61a-df53-4950-839b-4e2de21c879d)
- [StudioLibrary on GitHub](https://github.com/AntonyCarpenter/studiolibrary)
- [Batch Renamer on GitHub](https://github.com/RassoulEdji/Batch-Renamer)
- [Renamer 2.1 on CG Channel](https://www.cgchannel.com/2024/05/check-out-maya-productivity-add-on-renamer-2-1/)
- [EzRename on ArtStation](https://www.artstation.com/artwork/ybzlB8)
- [Python for Maya — Alexander Richter TD](https://www.alexanderrichtertd.com/python-maya)
- [Python for Maya Artists — VFX Pipeline YouTube](https://www.youtube.com/watch?v=IBFi6SUHnzg)
- [Tech-Artists.org pipeline thread](https://www.tech-artists.org/t/maya-python-tools-question-3d-pipeline-example-tools/6211)
- [leixingyu/autoRigger](https://github.com/leixingyu/autoRigger)
- [Xrod21/Auto-Rig-Tool](https://github.com/Xrod21/Auto-Rig-Tool)
- [morganloomis/ml_tools](https://github.com/morganloomis/ml_tools)
- [Python Inside Maya Google Group](https://groups.google.com/forum/#!forum/python_inside_maya)
- [Character Rigging with Advanced Skeleton (YouTube)](https://www.youtube.com/watch?v=M0W7cT2DUDY)
- [Quick Character Rigging with mGear (YouTube)](https://www.youtube.com/watch?v=FDYsVEccEmE)
