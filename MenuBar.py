#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d.core import TransparencyAttrib, ConfigVariableBool

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox
#from direct.gui.DirectOptionMenu import DirectOptionMenu
from directGuiOverrides.DirectOptionMenu import DirectOptionMenu

class MenuBar(DirectObject):
    def __init__(self):
        screenWidthPx = base.getSize()[0]

        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        #
        # Menubar
        #
        self.menuBar = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,screenWidthPx,-12, 12),
            pos=(0, 0, -12),
            parent=base.pixel2d)

        x = 0

        self.file = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["New", "Save", "Load", "Quit"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarFileCommand,
            parent=self.menuBar)
        self.file["text"] = "File"

        x += 65

        self.view = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["Zoom In", "Zoom Out", "Zoom 100%"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarViewCommand,
            parent=self.menuBar)
        self.view["text"] = "View"

        x += 65

        self.tools = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["Delete Node"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarToolsCommand,
            parent=self.menuBar)
        self.tools["text"] = "Tools"

        x += 65


        self.nodeMap = {
            "Numeric Input":"NumericNode",
            "Addition":"AddNode",
            "Divide":"DivideNode",
            "Multiply":"MultiplyNode",
            "Boolean Value":"BoolNode",
            "Boolean And":"BoolAnd",
            "Boolean Or":"BoolOr",
            "Simple Output":"TestOutNode"
        }

        self.nodes = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=list(self.nodeMap.keys()),
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarNodesCommand,
            parent=self.menuBar)
        self.nodes["text"] = "Nodes"

    def toolbarFileCommand(self, selection):
        if selection == "New":
            base.messenger.send("new")
        elif selection == "Save":
            base.messenger.send("save")
        elif selection == "Load":
            base.messenger.send("load")
        elif selection == "Quit":
            base.messenger.send("quit")

        self.file["text"] = "File"

    def toolbarToolsCommand(self, selection):
        if selection == "Delete Node":
            base.messenger.send("removeNode")
        #elif selection == "Options":
        #    base.messenger.send("showSettings")
        #elif selection == "Help":
        #    base.messenger.send("showHelp")

        self.tools["text"] = "Tools"

    def toolbarViewCommand(self, selection):
        if selection == "Zoom In":
            base.messenger.send("zoom", [True])
        elif selection == "Zoom Out":
            base.messenger.send("zoom", [False])
        elif selection == "Zoom 100%":
            base.messenger.send("zoom_reset")

        self.view["text"] = "View"

    def toolbarNodesCommand(self, selection):
        base.messenger.send("addNode", [self.nodeMap[selection]])

        self.nodes["text"] = "Nodes"

    def resizeFrame(self):
        screenWidthPx = base.getSize()[0]
        self.menuBar["frameSize"] = (0,screenWidthPx,-12, 12)
        self.menuBar.setPos(0, 0, -12)
