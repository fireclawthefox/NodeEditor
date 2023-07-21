#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiExtension import DirectGuiHelper as DGH
from panda3d.core import TextNode
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

class ListSocket(SocketBase):
    def __init__(self, node, name):
        SocketBase.__init__(self, node, name)
        self.numEntries = 0
        self.height = 0.2

        self.type = INSOCKET

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0.2),
            parent=node.frame,
        )

        self.listPlugsHolderFrame = DirectBoxSizer(
            self.frame,
            orientation=DGG.VERTICAL,
            frameColor=(0,0,0,0))

        self.text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 1, -self.height, 0),
            scale=(1, 1, 1),
            text=f"{name} List",
            text_align=TextNode.A_left,
            text_scale=(0.1, 0.1),
            text_pos=(0.1, 0.035),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=self.frame,
        )

        self.btnAddEntry = DirectButton(
            text="Add",
            scale=0.1,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            frameColor=(0.35, 0.35, 0.35, 1),
            pos=(0.5, 0, -0.1),
            parent=self.frame,
            relief=DGG.FLAT,
            command=self.addEntry,
        )

        self.createListSocket()

        self.resize(1)

    def addEntry(self):
        self.createListSocket()

    def removeEntry(self, plug):
        plugIDData = plug.plugID.split(":")
        plugPairID = plugIDData[0]

        hasRemoved = False
        if plug in self.plugs:
            self.listPlugsHolderFrame.removeItem(
                plug.plugWidget,
                False)
            plug.removePlug()
            self.plugs.remove(plug)
            hasRemoved = True

        if hasRemoved:
            self.numEntries -= 1
            self.btnAddEntry.setPos(
                self.btnAddEntry.getX(),
                self.btnAddEntry.getY(),
                self.btnAddEntry.getZ()+0.1)
            self.updateFrameSize()

    def createListSocket(self):
        self.createPlug(self.frame, ["listEntry"], removable=True)

        self.listPlugsHolderFrame.addItem(self.plugs[-1].plugWidget)

        self.numEntries += 1
        self.btnAddEntry.setPos(
            self.btnAddEntry.getX(),
            self.btnAddEntry.getY(),
            self.btnAddEntry.getZ()-0.1)
        self.updateFrameSize()

    def updateFrameSize(self):
        self.height = 0.1 * self.numEntries + 0.2
        self.frame["frameSize"] = (-1, 0, -self.height, 0.2)
        self.listPlugsHolderFrame.refresh()
        self.node.update()
        self.resize(1)

    def setValue(self, plug, value):
        SocketBase.setValue(self, plug, value)
        self.value = self.getValue()

    def getValue(self):
        value = []
        for plug in self.plugs:
            value.append(plug.getValue())

    def show(self, z, left):
        if self.frame is None:
            return
        self.frame.setZ(z)
        self.frame.setX(left)

    def resize(self, newWidth):
        if self.frame is None:
            return
        self.frame["frameSize"] = (0, newWidth, -self.height, 0.1)
        self.text["frameSize"] = (0, newWidth, -self.height, 0.1)
