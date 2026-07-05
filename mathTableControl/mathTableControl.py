import math, sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI

kPluginCmdName = "spMathTableControl"

kNopFlag = "-nop"
kNopLongFlag = "-noOperation"
kMultFlag = "-mul"
kMultLongFlag = "-multiplyVals"
kAddFlag = "-add"
kAddLongFlag = "-addVals"
kRedrawFlag = "-rd"
kRedrawFlagLong = "-redraw"

kNop = lambda x,y: "cell(%d,%d)" % (x,y)
kMult = lambda x,y: str(x*y)
kAdd = lambda x,y: str(x+y)

kPythonPtrTable = {}

class MathTableControlCmd(OpenMayaMPx.MPxControlCommand):
        def __init__(self):
                OpenMayaMPx.MPxControlCommand.__init__(self)

        def makeControl(self):
                control = MathTableControl(self)
                control.setOperation(kNop)
                control.setNumberOfRows(5)
                control.setNumberOfColumns(3)
                return OpenMayaMPx.asMPxPtr(control)

        def doEditFlags(self):
                theParser = self._parser()
                theControl = kPythonPtrTable.get(OpenMayaMPx.asHashable(self._control()), None)

                if theParser.isFlagSet(kNopFlag):
                        theControl.setOperation(kNop)
                elif theParser.isFlagSet(kMultFlag):
                        theControl.setOperation(kMult)
                elif theParser.isFlagSet(kAddFlag):
                        theControl.setOperation(kAdd)
                elif theParser.isFlagSet(kRedrawFlag):
                        theControl.redrawCells()
                        theControl.redrawLabels()
                else:
                        OpenMayaMPx.MPxControlCommand.doEditFlags(self)

        def doQueryFlags(self):
                return OpenMayaMPx.MPxControlCommand.doQueryFlags(self)

        def appendSyntax(self):
                theSyntax = self._syntax()
                theSyntax.addFlag(kNopFlag, kNopLongFlag)
                theSyntax.addFlag(kMultFlag, kMultLongFlag)
                theSyntax.addFlag(kAddFlag, kAddLongFlag)
                theSyntax.addFlag(kRedrawFlag, kRedrawFlagLong)

class MathTableControl(OpenMayaMPx.MPxUITableControl):
        def __init__(self, command):
                OpenMayaMPx.MPxUITableControl.__init__(self, command)
                self.__myOperation = None
                kPythonPtrTable[OpenMayaMPx.asHashable(self)] = self

        def __del__(self):
                del kPythonPtrTable[OpenMayaMPx.asHashable(self)]

        def cellString(self, row, column, isValidCell):
                result = ""
                if callable(self.__myOperation):
                        result = self.__myOperation(row, column)
                OpenMaya.MScriptUtil.setBool(isValidCell, bool(result))
                return result

        def labelString(self, labelType, index):
                value = ""
                if labelType == OpenMayaMPx.MPxUITableControl.kRowLabel:
                        value = "[Row %d]" % index
                elif labelType == OpenMayaMPx.MPxUITableControl.kColumnLabel:
                        value = "[Col %d]" % index
                return value

        def setOperation(self, op):
                self.__myOperation = op
                self.redrawCells()

def cmdCreator():
        return OpenMayaMPx.asMPxPtr(MathTableControlCmd())

def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject, "Autodesk", "1.0", "Any")
        try:
                mplugin.registerControlCommand(kPluginCmdName, cmdCreator)
        except:
                sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName)
                raise

def uninitializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.deregisterControlCommand(kPluginCmdName)
        except:
                sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
                raise
