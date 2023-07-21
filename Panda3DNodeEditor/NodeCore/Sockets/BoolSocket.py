#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

import ast

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode

class BoolSocket(SocketBase):
    def __init__(self, node, name):
        SocketBase.__init__(self, node, name)

        self.type = INSOCKET

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0),
            parent=node.frame,
        )

        SocketBase.createPlug(self, self.frame)

        self.checkbox = DirectCheckButton(
            text = name,
            pos=(0.5,0,0),
            scale=.1,
            command=self.updateConnectedNodes,
            parent=self.frame)

        self.resize(1)

    def setValue(self, plug, value):
        if isinstance(value, str):
            value = True if value.lower() in ["1", "true", "#t"] else False
        self.checkbox["indicatorValue"] = value
        self.checkbox.setIndicatorValue()
        SocketBase.setValue(self, plug, value)

    def getValue(self):
        return self.checkbox["indicatorValue"]

    def show(self, z, left):
        self.frame.setZ(z)
        self.frame.setX(left)

    def resize(self, newWidth):
        self.frame["frameSize"] = (0, newWidth, -self.height/2, self.height/2)
        #self.text["frameSize"] = (0, newWidth, -self.height/2, self.height/2)

    def setConnected(self, connected, plug):
        if connected:
            self.checkbox["state"] = DGG.DISABLED
        else:
            self.checkbox["state"] = DGG.NORMAL
        SocketBase.setConnected(self, connected, plug)

    def getAst(self):
        #THIS MAY NOT WORK SINCE WE DON'T HAVE THE CONNECTION
        #if self.connected:
        #    return ast.Constant(self.)
        #else:
        #    return ast.Constant(self.getValue())
        ...
