#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from NodeCore.NodeBase import NodeBase
from NodeCore.Sockets.InSocket import InSocket
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

class Node(NodeBase):
    def __init__(self, parent):
        NodeBase.__init__(self, "OR", parent)
        self.addOut("Out")
        self.addIn("In 1", InSocket)
        self.addIn("In 2", InSocket)
        #self.create()

    def logic(self):
        if self.inputList[0].value is None or self.inputList[1].value is None:
            self.outputList[0].value = None
            return
        self.outputList[0].value = self.inputList[0].value or self.inputList[1].value
