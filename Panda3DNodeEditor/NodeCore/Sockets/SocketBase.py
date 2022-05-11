#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d.core import TransparencyAttrib
from uuid import uuid4

from direct.gui.DirectFrame import DirectFrame
from direct.gui import DirectGuiGlobals as DGG

OUTSOCKET = 0
INSOCKET = 1

class SocketBase:
    def __init__(self, node, name):
        self.socketID = uuid4()
        self.node = node
        self.name = name
        self.height = 0.2
        self.type = None
        self.value = None
        self.connected = False
        self.frame = None
        self.allowMultiConnect = False

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

    def setValue(self, value):
        self.value = value

    def createPlug(self, parent):
        self.plug = DirectFrame(
            state = DGG.NORMAL,
            image="icons/Plug.png",
            image_scale=.05,
            frameColor=(0, 0, 0, 0),
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            parent=parent,
        )
        self.plug.setTransparency(TransparencyAttrib.M_multisample)
        self.setupBind()

    def setupBind(self):
        self.plug.bind(DGG.B1PRESS, self.startPlug)
        self.plug.bind(DGG.B1RELEASE, self.releasePlug)
        self.plug.bind(DGG.ENTER, self.endPlug)

    def startPlug(self, event):
        base.messenger.send("startPlug", [self])
        base.messenger.send("startLineDrawing", [self.plug.getPos(render2d)])

    def endPlug(self, event):
        taskMgr.remove("delayedPlugRelease")
        base.messenger.send("endPlug", [self])
        base.messenger.send("connectPlugs")

    def releasePlug(self, event):
        base.messenger.send("stopLineDrawing")
        taskMgr.doMethodLater(0.2, base.messenger.send, "delayedPlugRelease", extraArgs=["cancelPlug"])

    def updateConnectedNodes(self, *args):
        base.messenger.send("updateConnectedNodes", [self.node])

    def setConnected(self, connected):
        self.connected = connected
        if self.connected:
            self.plug["image"] = "icons/PlugConnectedGood.png"
        else:
            self.plug["image"] = "icons/Plug.png"
