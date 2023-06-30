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
        self.node = node
        self.name = name
        self.socketDict = {}
        self.height = 0.4
        self.connected = False
        self.frame = None
        self.allowMultiConnect = False

        SocketBase.__init__(self, node, name)

        self.type = INSOCKET

        self.frame = None

        self.frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -self.height, 0),
            parent=node.frame,
        )

        self.text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 1, -0.2, 0),
            scale=(1, 1, 1),
            text="Dictionary",
            text_align=TextNode.A_left,
            text_scale=(0.1, 0.1),
            text_pos=(0.1, -0.02),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=self.frame,
        )

        #TODO: Add a button to add new entries?

        self.resize(1)

    def createKeyValuePairSocket(self):
        frame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-1, 0, -0.4, 0),
            pos=(0,0,-0.2*(self.numEntries+1)),
            parent=self.frame,
        )

        text = DirectLabel(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 1, -self.height, 0),
            scale=(1, 1, 1),
            text=self.name,
            text_align=TextNode.A_left,
            text_scale=(0.1, 0.1),
            text_pos=(0.1, -0.02),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0),
            parent=frame,
        )

        keySocket = SocketBase(self.node, "Key")
        keySocket.createPlug(frame)
        valueSocket = SocketBase(self.node, "Value")
        valueSocket.createPlug(frame)

        self.socketDict[keySocket] = valueSocket

        self.frame["frameSize"] = (-1, 0, -0.4 * (self.numEntries * 2) - 0.4, 0)
        self.numEntries += 1
        self.node.update()

    def remove(self):
        if self.frame is not None:
            self.frame.removeNode()

    def enable(self):
        """Enable any elements on the node"""
        pass

    def disable(self):
        """Disable any elements on the node that could possbily interfer with
        the mouse watcher and the drag/drop feature"""
        pass

    def setValue(self, value):
        self.value = value
        self.checkOthers()

    def getValue(self):
        value = {}

        for socket in self.dictSockets:
            pass

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
