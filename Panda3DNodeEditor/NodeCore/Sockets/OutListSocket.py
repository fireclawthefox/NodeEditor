#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import OUTSOCKET
from Panda3DNodeEditor.NodeCore.Sockets.ListSocket import ListSocket

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode

class OutListSocket(ListSocket):
    def __init__(self, node, name):
        ListSocket.__init__(self, node, name)

        self.text.setX(-0.1)
        self.text["text_align"] = TextNode.ARight
        self.btnAddEntry.setX(-0.25)

        self.type = OUTSOCKET

    def resize(self, newWidth):
        self.frame["frameSize"] = (-newWidth, 0, -self.height, 0.1)
        self.text["frameSize"] = (-newWidth, 0, -self.height, 0.1)
