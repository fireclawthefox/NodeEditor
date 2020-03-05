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
        NodeBase.__init__(self, "OUT", parent)
        self.addIn("In 1", InSocket)

    def logic(self):
        self.inputList[0].text["text"] = str(self.inputList[0].getValue())
