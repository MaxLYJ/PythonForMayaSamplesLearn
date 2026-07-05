"""
Numbered-prefix renamer

A modification of objectRenamer/renamer1 that adds a zero-padded numbered
prefix (ctrl_01_, ctrl_02_, ...) instead of just a type-based suffix.

Pair with the create-50-controls snippet:

    from maya import cmds
    for _ in range(50):
        cmds.circle()
    cmds.select('nurbsCircle*')

Then run this script.

Teaching concepts:
  - enumerate() to loop with an index
  - zero-padded number formatting ("%02d" or f"{i:02d}")
  - adding a new type case (nurbsCurve -> ctrl) to the existing suffix logic
"""

from maya import cmds

# Get the current selection as full paths (long=True) so we never confuse
# two objects that happen to share a short name.
selection = cmds.ls(selection=True, long=True)
print("Selected:", len(selection), "objects")

# If nothing is selected, fall back to every DAG object in the scene.
if len(selection) == 0:
    selection = cmds.ls(long=True, dag=True)

# Sort longest-path first so we never rename a parent before its child
# (which would invalidate the child's path).
selection.sort(key=len, reverse=True)


# enumerate() gives us both an index and the item.
# start=1 makes the numbering human-friendly (01, 02, ... not 00, 01, ...).
for index, obj in enumerate(selection, start=1):

    # The name will be something like grandparent|parent|child
    # We just want the last segment, the short name.
    shortName = obj.split('|')[-1]

    # Figure out the object type. For transforms, check the shape child
    # (that's where the real type lives: mesh, nurbsCurve, camera, ...).
    children = cmds.listRelatives(obj, children=True) or []
    if len(children) == 1:
        objType = cmds.objectType(children[0])
    else:
        objType = cmds.objectType(obj)

    # Pick a suffix based on type.
    # NOTE: 'nurbsCurve' is the new case added vs. renamer1 -- without it,
    # controls fall through to the 'else' branch and get named '_grp'.
    if objType == "mesh":
        suffix = 'geo'
    elif objType == "joint":
        suffix = 'jnt'
    elif objType == 'camera':
        print("Skipping camera:", shortName)
        continue
    elif objType == 'nurbsCurve':
        suffix = 'ctrl'
    else:
        suffix = 'grp'

    # Build the new name with a zero-padded numbered prefix.
    # %02d means "integer, at least 2 digits, pad with leading zeros"
    #   -> 1 becomes "01", 9 becomes "09", 10 becomes "10", 50 becomes "50"
    # Zero-padding is what makes the names sort correctly in the Outliner.
    newName = "ctrl_%02d_%s" % (index, suffix)

    cmds.rename(obj, newName)
    print("Renamed: %s -> %s" % (shortName, newName))

print("Done. Renamed %d objects." % len(selection))


# ALTERNATIVE SYNTAX (Python 3.6+ / Maya 2022+):
#   newName = f"ctrl_{index:02d}_{suffix}"
# Both produce the same result; pick one style and be consistent.
