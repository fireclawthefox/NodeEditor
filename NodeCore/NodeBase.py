#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
from direct.showbase.DirectObject import DirectObject
from NodeCore.Sockets.OutSocket import OutSocket
from NodeCore.Sockets.InSocket import InSocket
from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from panda3d.core import (
    Point3,
    LPoint3,
    LVecBase3,
    LVecBase4,
    TextNode,
    Vec3,
    KeyboardButton,
)

class NodeBase(DirectObject):
    def __init__(self, name, parent):
        DirectObject.__init__(self)
        self.right = 0.5
        self.left = -0.5
        self.name = name
        self.inputList = []
        self.outputList = []
        self.selected = False

        self.frame = DirectFrame(
            state = DGG.NORMAL,
            text=name,
            text_align=TextNode.A_left,
            text_scale=0.1,
            text_pos=(self.left, 0.12),
            text_fg=(1,1,1,1),
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(-0.5, 0.5, -.6, 0.2),
            parent=parent)

        self.setupBind()
        self.hide()

    def addIn(self, name, socketType):
        inSocket = socketType(self, name)
        self.inputList.append(inSocket)

    def addOut(self, name):
        outSocket = OutSocket(self, name)
        self.outputList.append(outSocket)

    def logic(self):
        pass

    def update(self):
        z = 0

        for outSocket in self.outputList:
            outSocket.show(z, self.right)
            z -= outSocket.height

        for inSocket in self.inputList:
            inSocket.show(z, self.left)
            z -= inSocket.height

        fs = self.frame["frameSize"]
        self.frame["frameSize"] = (fs[0], fs[1], z, fs[3])

    def create(self):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            newPos = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            self.frame.setPos(render2d, newPos)
        self._dragStart(self.frame, None)
        self.show()

    def show(self):
        self.update()
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def destroy(self):
        self.frame.destroy()

    def setupBind(self):
        self.frame.bind(DGG.B1PRESS, self._dragStart, [self.frame])
        self.frame.bind(DGG.B1RELEASE, self._dragStop)

    def select(self, select):
        if self.selected == select: return
        self.selected = select
        if self.selected:
            self.frame["frameColor"] = (0.45, 0.45, 0.45, 1)
        else:
            self.frame["frameColor"] = (0.25, 0.25, 0.25, 1)

    def _dragStart(self, nodeFrame, event):
        base.messenger.send("selectNode", [self, True, base.mouseWatcherNode.isButtonDown(KeyboardButton.shift()), True])
        base.messenger.send("dragNodeStart", [self])
        taskMgr.remove("dragNodeDropTask")
        vWidget2render2d = nodeFrame.getPos(render2d)
        vMouse2render2d = Point3(0)
        if event is not None:
            vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        else:
            mwn = base.mouseWatcherNode
            if mwn.hasMouse():
                vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        self.hasMoved = False
        t = taskMgr.add(self.dragTask, "dragNodeDropTask")
        t.nodeFrame = nodeFrame
        t.editVec = editVec
        t.mouseVec = vMouse2render2d

    def dragTask(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])

            if not self.hasMoved and (t.mouseVec - vMouse2render2d).length() < 0.01: return t.cont
            self.hasMoved = True

            newPos = vMouse2render2d + t.editVec

            t.nodeFrame.setPos(render2d, newPos)

            base.messenger.send("dragNodeMove", [t.mouseVec, vMouse2render2d])

        return t.cont

    def _dragStop(self, event=None):
        self.ignore("mouse1-up")
        if not self.hasMoved:
            base.messenger.send("selectNode", [self, True, base.mouseWatcherNode.isButtonDown(KeyboardButton.shift())])
        base.messenger.send("dragNodeStop", [self])
        taskMgr.remove("dragNodeDropTask")
