#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from uuid import uuid4
from Panda3DNodeEditor.NodeCore.Sockets.SocketPlug import SocketPlug

OUTSOCKET = 0
INSOCKET = 1

class SocketBase:
    def __init__(self, node, name):
        self.socketID = uuid4()
        self.node = node
        self.name = name
        print("MY NAME:", self.name)
        self.height = 0.2
        self.type = None
        self.value = None
        self.connected = False
        self.frame = None
        self.allowMultiConnect = False
        # A JSON serializable list of extra arguments
        self.extraArgs = []
        self.plugs = []

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

    def getValue(self):
        """Returns a string serializable value stored in this node"""
        return self.value

    def setValue(self, plug, value):
        plug.setValue(value)
        self.value = value
        self.update()

    def hasCustomValue(self):
        """Returns True if the value on this socket is set through the
        socket itself and not through another node"""
        return self.connected == False and self.value is not None

    def createPlug(self, parent, prefixes=[], idOverwrite=None, removable=False):
        self.plugs.append(
            SocketPlug(self, parent, prefixes, idOverwrite, removable))

    def removeEntry(self, plug):
        if plug in self.plugs:
            plug.removePlug()
            self.plugs.remove(plug)

    def updateConnectedNodes(self, *args):
        base.messenger.send("updateConnectedNodes", [self.node])

    def setConnected(self, connected, plug):
        self.connected = connected
        plug.setConnected(connected)

    def update(self):
        """Call the nodes logic and update connections once this socket
        gets updated"""
        # update our nodes logic
        self.node.logic()

        # update connections
        self.updateConnectedNodes()
