#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

import logging

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode

class OptionSelectSocket(SocketBase):
    def __init__(self, node, name, options):
        SocketBase.__init__(self, node, name)

        self.height = 0.21

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

        self.optionsfield = DirectOptionMenu(
            pos=(0.5,0,-0.01),
            borderWidth=(0.1,0.1),
            items=options,
            parent=self.frame,
            command=self.updateConnectedNodes,
            state=DGG.DISABLED)
        self.optionsfield.setScale(0.1)

        self.resize(1.7)

    def disable(self):
        self.optionsfield["state"] = DGG.DISABLED

    def enable(self):
        if not self.connected:
            self.optionsfield["state"] = DGG.NORMAL

    def setValue(self, plug, value):
        try:
            self.optionsfield.set(value)
        except:
            logging.error(f"couldn't set the value {value} for the option selection")
            return
        SocketBase.setValue(self, plug, value)

    def getValue(self):
        return self.optionsfield.get()

    def show(self, z, left):
        self.frame.setZ(z)
        self.frame.setX(left)

    def resize(self, newWidth):
        self.frame["frameSize"] = (0, newWidth, -self.height/2, self.height/2)
        self.text["frameSize"] = (0, newWidth, -self.height/2, self.height/2)

    def setConnected(self, connected, plug):
        if connected:
            self.optionsfield["state"] = DGG.DISABLED
        else:
            self.optionsfield["state"] = DGG.NORMAL
        SocketBase.setConnected(self, connected, plug)
