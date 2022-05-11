#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from NodeEditor.NodeCore.Nodes.NodeBase import NodeBase
from NodeEditor.NodeCore.Sockets.NumericSocket import NumericSocket

class Node(NodeBase):
    def __init__(self, parent):
        NodeBase.__init__(self, "IN", parent)
        self.addOut("Out")
        self.addIn("In", NumericSocket)

    def logic(self):
        self.outputList[0].value = self.inputList[0].getValue()
