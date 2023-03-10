#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode

class ArgumentsSocket(SocketBase):
    def __init__(self, node, name, defaultArguments=[]):
        SocketBase.__init__(self, node, name)

        self.type = INSOCKET

        self.frame = None

        if len(defaultArguments) > 0:
            self.height = 0
            self.setValue(defaultArguments)
            return

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
        if self.value is not None:
            for socketName in self.value:
                self.node.removeOutByName(socketName)

        if type(value) is list:
            self.value = value

        if self.value is None:
            return

        for socketName in self.value:
            if socketName is None:
                continue
            self.node.addOut(socketName)

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
