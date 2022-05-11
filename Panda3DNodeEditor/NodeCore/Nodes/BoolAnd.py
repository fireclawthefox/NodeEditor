#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from Panda3DNodeEditor.NodeCore.Nodes.NodeBase import NodeBase
from Panda3DNodeEditor.NodeCore.Sockets.InSocket import InSocket

class Node(NodeBase):
    def __init__(self, parent):
        NodeBase.__init__(self, "AND", parent)
        self.addOut("Out")
        self.addIn("In 1", InSocket)
        self.addIn("In 2", InSocket)

    def logic(self):
        if self.inputList[0].value is None or self.inputList[1].value is None:
            self.outputList[0].value = None
            return
        self.outputList[0].value = self.inputList[0].value and self.inputList[1].value
