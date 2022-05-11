#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode

from DirectGuiExtension.DirectSpinBox import DirectSpinBox

class NumericSocket(SocketBase):
    def __init__(self, node, name):
        SocketBase.__init__(self, node, name)

        self.type = INSOCKET

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

        self.spinBox = DirectSpinBox(
            pos=(0.5,0,0),
            value=5,
            minValue=-100,
            maxValue=100,
            repeatdelay=0.125,
            buttonOrientation=DGG.HORIZONTAL,
            valueEntry_text_align=TextNode.ACenter,
            borderWidth=(0.1,0.1),
            parent=self.frame,
            incButtonCallback=self.updateConnectedNodes,
            decButtonCallback=self.updateConnectedNodes,)
        self.spinBox.setScale(0.1)

        self.resize(1)

    def setValue(self, value):
        self.spinBox.setValue(value)

    def getValue(self):
        return self.spinBox.getValue()

    def show(self, z, left):
        self.frame.setZ(z)
        self.frame.setX(left)

    def resize(self, newWidth):
        self.frame["frameSize"] = (0, newWidth, -self.height/2, self.height/2)
        self.text["frameSize"] = (0, newWidth, -self.height/2, self.height/2)

    def setConnected(self, connected):
        if connected:
            self.spinBox["state"] = DGG.DISABLED
            self.spinBox.incButton["state"] = DGG.DISABLED
            self.spinBox.decButton["state"] = DGG.DISABLED
            self.spinBox.valueEntry["state"] = DGG.DISABLED
        else:
            self.spinBox["state"] = DGG.NORMAL
            self.spinBox.incButton["state"] = DGG.NORMAL
            self.spinBox.decButton["state"] = DGG.NORMAL
            self.spinBox.valueEntry["state"] = DGG.NORMAL
        self.connected = connected
