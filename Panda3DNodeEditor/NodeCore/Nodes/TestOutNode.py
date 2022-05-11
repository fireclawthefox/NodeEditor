#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import (
    Point3,
    LPoint3,
    LVecBase3,
    LVecBase4,
    TextNode,
    Vec3,
)

from DirectGuiExtension import DirectGuiHelper as DGH

from Panda3DNodeEditor.NodeCore.Nodes.NodeBase import NodeBase
from Panda3DNodeEditor.NodeCore.Sockets.InSocket import InSocket

class Node(NodeBase):
    def __init__(self, parent):
        NodeBase.__init__(self, "OUT", parent)
        self.addIn("In 1", InSocket)

    def logic(self):
        """Simply write the value in the nodes textfield"""
        if self.inputList[0].value is None:
            self.inputList[0].text["text"] = "In 1"
            self.inputList[0].text.resetFrameSize()
            self.inputList[0].resize(1)
            self.update()
            return
        self.inputList[0].text["text"] = str(self.inputList[0].getValue())
        self.inputList[0].text["frameSize"] = None
        self.inputList[0].text.resetFrameSize()

        newSize = max(1, DGH.getRealWidth(self.inputList[0].text) + 0.2)
        self.inputList[0].resize(newSize)

        self.update()
