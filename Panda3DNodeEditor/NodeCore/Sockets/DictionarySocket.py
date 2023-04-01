#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode

class DictionarySocket():
    def __init__(self, node, name):
        self.numEntries = 0

        SocketBase.__init__(self, node, name)

        self.type = INSOCKET

        self.frame = None

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0),
            parent=node.frame,
        )

        SocketBase.createPlug(self, self.frame)

        self.text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 1, -self.height, 0),
            scale=(1, 1, 1),
            text=self.name,
            text_align=TextNode.A_left,
            text_scale=(0.1, 0.1),
            text_pos=(0.1, -0.02),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=self.frame,
        )

        self.resize(1)

    def setValue(self, value):
        self.value = value
        self.checkOthers()

    def getValue(self):
        value = {}

        for socket in self.dictSockets

        value = []
        for inSocket in self.node.inputList:
            if inSocket.name == self.name:
                value.append(self.value)
        # make sure the last empty entry is not added to the list
        return value[:-1]

    def checkOthers(self):
        for inSocket in self.node.inputList[:]:
            # remove all non-connected sockets with this name
            if inSocket.name == self.name \
            and inSocket.value is None:
                self.node.removeIn(inSocket)
        # Make sure we always have one new socket to extend the list
        self.node.addIn(self.name, ListSocket)
        self.node.update()

    def show(self, z, left):
        if self.frame is None:
            return
        self.frame.setZ(z)
        self.frame.setX(left)

    def resize(self, newWidth):
        if self.frame is None:
            return
        self.frame["frameSize"] = (0, newWidth, -self.height/2, self.height/2)
        self.text["frameSize"] = (0, newWidth, -self.height/2, self.height/2)
