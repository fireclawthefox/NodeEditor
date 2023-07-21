#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from uuid import uuid4
from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import SocketBase, INSOCKET

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiExtension import DirectGuiHelper as DGH
from panda3d.core import TextNode
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

class DictionarySocket(SocketBase):
    def __init__(self, node, name):
        SocketBase.__init__(self, node, name)
        self.numEntries = 0
        self.height = 0.4

        self.type = INSOCKET

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0.2),
            parent=node.frame,
        )

        self.dictPlugsHolderFrame = DirectBoxSizer(
            self.frame,
            orientation=DGG.VERTICAL,
            frameColor=(0,0,0,0))

        self.text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 1, -0.2, 0),
            scale=(1, 1, 1),
            text=f"{name} Dictionary",
            text_align=TextNode.A_left,
            text_scale=(0.1, 0.1),
            text_pos=(0.1, 0.035),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=self.frame,
        )

        self.btnAddEntry = DirectButton(
            text="Add pair",
            scale=0.1,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            frameColor=(0.35, 0.35, 0.35, 1),
            pos=(0.5, 0, -0.1),
            parent=self.frame,
            relief=DGG.FLAT,
            command=self.addEntry,
        )

        self.createKeyValuePairSocket()

        self.resize(1)

    def addEntry(self):
        self.createKeyValuePairSocket()

    def removeEntry(self, plug):
        plugIDData = plug.plugID.split(":")
        plugPairID = plugIDData[0]

        hasRemoved = False
        for myPlug in self.plugs[:]:
            myPlugIDData = myPlug.plugID.split(":")
            myPlugPairID = myPlugIDData[0]
            if myPlugPairID == plugPairID:
                self.dictPlugsHolderFrame.removeItem(
                    myPlug.plugWidget,
                    False)
                myPlug.removePlug()
                self.plugs.remove(myPlug)
                hasRemoved = True

        if hasRemoved:
            self.numEntries -= 1
            self.btnAddEntry.setPos(
                self.btnAddEntry.getX(),
                self.btnAddEntry.getY(),
                self.btnAddEntry.getZ()+0.2)
            self.updateFrameSize()

    def createKeyValuePairSocket(self):
        pairID = str(uuid4())
        self.createPlug(self.frame, [pairID, "key"], removable=True)
        self.createPlug(self.frame, [pairID, "value"])

        self.dictPlugsHolderFrame.addItem(self.plugs[-2].plugWidget)
        self.dictPlugsHolderFrame.addItem(self.plugs[-1].plugWidget)

        self.numEntries += 1
        self.btnAddEntry.setPos(
            self.btnAddEntry.getX(),
            self.btnAddEntry.getY(),
            self.btnAddEntry.getZ()-0.2)
        self.updateFrameSize()

    def updateFrameSize(self):
        self.height = 0.2 * self.numEntries + 0.2
        self.frame["frameSize"] = (-1, 0, -self.height, 0.2)
        self.dictPlugsHolderFrame.refresh()
        self.node.update()
        self.resize(1)

    def setValue(self, plug, value):
        SocketBase.setValue(self, plug, value)
        print("SET VALUE TO:", value)
        print(plug.value)
        print("HAS IT?")
        self.value = self.getValue()

    def getValue(self):
        tempdict = {}
        for plug in self.plugs:
            plugIDData = plug.plugID.split(":")
            plugPairID = plugIDData[0]
            plugPairPart = plugIDData[1]
            if plugPairID in tempdict.keys():
                tempdict[plugPairID][plugPairPart] = plug.value
            else:
                tempdict[plugPairID] = {plugPairPart:plug.value}

        print(tempdict)

        retValue = {}
        for key, pairs in tempdict.items():
            if pairs["key"] is None:
                continue
            retValue[pairs["key"]] = pairs["value"]
        return retValue

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
