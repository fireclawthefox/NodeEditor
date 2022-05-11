#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, OUTSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode

class OutSocket(SocketBase):
    def __init__(self, node, name):
        SocketBase.__init__(self, node, name)

        self.type = OUTSOCKET

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0),
            parent=node.frame,
        )

        SocketBase.createPlug(self, self.frame)

        self.text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 0, -self.height, 0),
            scale=(1, 1, 1),
            text=self.name,
            text_align=TextNode.A_right,
            text_scale=(0.1, 0.1),
            text_pos=(-0.1, -0.02),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=self.frame,
        )

        self.resize(1)

    def show(self, z, right):
        self.frame.setZ(z)
        self.frame.setX(right)

    def resize(self, newWidth):
        self.frame["frameSize"] = (-newWidth, 0, -self.height/2, self.height/2)
        self.text["frameSize"] = (-newWidth, 0, -self.height/2, self.height/2)
