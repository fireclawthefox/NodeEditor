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
        """Add a new input socket of the given socket type"""
        inSocket = socketType(self, name)
        self.inputList.append(inSocket)

    def addOut(self, name):
        """Add a new output socket"""
        outSocket = OutSocket(self, name)
        self.outputList.append(outSocket)

    def logic(self):
        """Run the logic of this node, process all in and output data.
        This is a stub and should be overwritten by the derived classes"""
        pass

    def update(self):
        """Show all sockets and resize the frame to fit all sockets in"""
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
        """Place and show the node under the mouse and start draging it."""
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            newPos = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            self.frame.setPos(render2d, newPos)
        self._dragStart(self.frame, None)
        self.show()

    def show(self):
        """Shows the Node frame and updates its sockets"""
        self.update()
        self.frame.show()

    def hide(self):
        """Hide the Node frame"""
        self.frame.hide()

    def destroy(self):
        self.frame.destroy()

    def setupBind(self):
        """Setup the mousebutton actions for drag and drop feature"""
        self.frame.bind(DGG.B1PRESS, self._dragStart, [self.frame])
        self.frame.bind(DGG.B1RELEASE, self._dragStop)

    def select(self, select):
        """Set this node as selected or deselected"""
        if self.selected == select: return
        self.selected = select
        if self.selected:
            self.frame["frameColor"] = (0.45, 0.45, 0.45, 1)
        else:
            self.frame["frameColor"] = (0.25, 0.25, 0.25, 1)

    def _dragStart(self, nodeFrame, event):
        # Mark this node as selected
        base.messenger.send("selectNode", [self, True, base.mouseWatcherNode.isButtonDown(KeyboardButton.shift()), True])
        # tell everyone we started to drag this node
        base.messenger.send("dragNodeStart", [self])

        # Remove any previous started drag tasks
        taskMgr.remove("dragNodeDropTask")

        # get some positions
        vWidget2render2d = nodeFrame.getPos(render2d)
        vMouse2render2d = Point3(0)
        if event is not None:
            # we get the mouse position from the event
            vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        else:
            # we try to get the current mouse position from the mouse watcher
            mwn = base.mouseWatcherNode
            if mwn.hasMouse():
                vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        self.hasMoved = False

        # Initiate the task to move the node and pass it some initial values
        t = taskMgr.add(self.dragTask, "dragNodeDropTask")
        t.nodeFrame = nodeFrame
        t.editVec = editVec
        t.mouseVec = vMouse2render2d

    def dragTask(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            # get the current mouse position fitting for a render2d position
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])

            # check if the cursor has moved enough to drag this node
            # this gives us some puffer zone for clicking
            if not self.hasMoved and (t.mouseVec - vMouse2render2d).length() < 0.01: return t.cont

            # We actually have moved now
            self.hasMoved = True

            # calculate the new position
            newPos = vMouse2render2d + t.editVec

            # move the node to the new position
            t.nodeFrame.setPos(render2d, newPos)

            # tell everyone we moved the node
            base.messenger.send("dragNodeMove", [t.mouseVec, vMouse2render2d])

        return t.cont

    def _dragStop(self, event=None):
        self.ignore("mouse1-up")
        # remove the node dragging task
        taskMgr.remove("dragNodeDropTask")

        # check if the node has moved
        if not self.hasMoved:
            # we want to select this node as it has not been moved
            base.messenger.send("selectNode", [self, True, base.mouseWatcherNode.isButtonDown(KeyboardButton.shift())])
        # tell everyone we stopped moving the node
        base.messenger.send("dragNodeStop", [self])
