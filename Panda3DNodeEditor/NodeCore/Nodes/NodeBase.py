#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
from uuid import uuid4

from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import (
    Point3,
    TextNode,
    Vec3,
    KeyboardButton,
)

from DirectGuiExtension import DirectGuiHelper as DGH

from Panda3DNodeEditor.NodeCore.Sockets.OutSocket import OutSocket

class NodeBase(DirectObject):
    def __init__(self, name, parent):
        self.right = 0.5
        self.left = -0.5
        self.name = name
        self.typeName = typeName
        self.nodeID = uuid4()
        self.inputList = []
        self.outputList = []
        self.selected = False
        self.allowRecursion = False
        self.hasError = False
        self.customAttributes = {}

        # a special variable to store everything needed to re-create
        # this specific node
        self.recreation = []

        self.normalColor = (0.25, 0.25, 0.25, 1)
        self.highlightColor = (0.45, 0.45, 0.45, 1)
        self.errorColor = (1, 0.25, 0.25, 1)
        self.errorHighlightColor = (1, 0.45, 0.45, 1)

        self.frame = DirectFrame(
            state = DGG.NORMAL,
            text=name,
            text_align=TextNode.A_left,
            text_scale=0.1,
            text_pos=(self.left, 0.12),
            text_fg=(1,1,1,1),
            frameColor=self.normalColor,
            frameSize=(self.left, self.right, -.6, 0.2),
            parent=parent)
        self.frame.setBin("fixed", 10)


        self.setupBind()
        self.hide()

        self.setPos = self.frame.setPos
        self.getPos = self.frame.getPos

    def addIn(self, name, socketType, allowMultiConnect=False, extraArgs=None):
        """Add a new input socket of the given socket type"""
        if extraArgs is not None:
            inSocket = socketType(self, name, *extraArgs)
            inSocket.extraArgs = extraArgs
        else:
            inSocket = socketType(self, name)
        inSocket.allowMultiConnect = allowMultiConnect
        self.inputList.append(inSocket)

    def removeIn(self, socket):
        if socket in self.inputList:
            socket.remove()
            self.inputList.remove(socket)

    def hasInSocketNamed(self, name):
        for socket in self.inputList:
            if socket.name == name:
                return True
        return False

    def removeInByNameAndType(self, name, socketType):
        for socket in self.inputList[:]:
            if socket.name == name and type(socket) == socketType:
                self.removeIn(socket)

    def addOut(self, name, socketType=None):
        """Add a new output socket"""
        if not socketType:
            socketType = OutSocket
        outSocket = socketType(self, name)
        self.outputList.append(outSocket)

    def removeOut(self, socket):
        if socket in self.outputList:
            socket.remove()
            self.outputList.remove(socket)

    def removeOutByName(self, name):
        for socket in self.outputList[:]:
            if socket.name == name:
                self.removeOut(socket)

    def hasOutSocketNamed(self, name):
        for socket in self.outputList:
            if socket.name == name:
                return True
        return False

    def isLeaveNode(self, left=True):
        """Returns true if this is a leave node.
        Leave nodes do not have any input (if left is set to True) or
        output connections. Either if no sockets on that side are
        defined at all or none of the sockets are connected."""

        if left:
            # check if we have any input sockets and if so if any of them are connected
            socketList = self.inputList
        else:
            # check if we have any output sockets and if so if any of them are connected
            socketList = self.outputList

        for socket in socketList:
            if socket.connected: return False
        return True

    def setError(self, hasError):
        self.hasError = hasError
        self.setColor()

    def logic(self):
        """Run the logic of this node, process all in and output data.
        This is a stub and should be overwritten by the derived classes.
        By default it will compile a list of values of all input sockets
        and assigns that to all output sockets"""
        print("UPDATE NODE LOGIC!")
        value = []
        for inSocket in self.inputList:
            value.append(inSocket.getValue())
        print("GOT VALUES:", value)
        for outSocket in self.outputList:
            outSocket.setValue(value)
            outSocket.plugs[0].setValue(value)

    def update(self):
        """Show all sockets and resize the frame to fit all sockets in"""
        z = 0

        fs = self.frame["frameSize"]
        maxWidth = fs[1]


        for socket in self.inputList + self.outputList:
            if socket.frame:
                maxWidth = max(maxWidth, DGH.getRealWidth(socket.frame))
        self.left = -maxWidth / 2
        self.right = maxWidth / 2

        for outSocket in self.outputList:
            outSocket.resize(maxWidth)
            outSocket.show(z, self.right)
            z -= outSocket.height

        for inSocket in self.inputList:
            inSocket.resize(maxWidth)
            inSocket.show(z, self.left)
            z -= inSocket.height

        self.frame["frameSize"] = (self.left, self.right, z, fs[3])
        self.frame["text_pos"] = (self.left, 0.12)

        base.messenger.send("NodeEditor_updateConnections")

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

    def enable(self):
        for socket in self.inputList + self.outputList:
            socket.enable()

    def disable(self):
        for socket in self.inputList + self.outputList:
            socket.disable()

    def setupBind(self):
        """Setup the mousebutton actions for drag and drop feature"""
        self.frame.bind(DGG.B1PRESS, self._dragStart, [self.frame])
        self.frame.bind(DGG.B1RELEASE, self._dragStop)

    def select(self, select):
        """Set this node as selected or deselected"""
        if self.selected == select: return
        self.selected = select
        self.setColor()

    def setColor(self):
        if self.selected and not self.hasError:
            self.frame["frameColor"] = self.highlightColor
        elif self.selected and self.hasError:
            self.frame["frameColor"] = self.errorHighlightColor
        elif self.hasError:
            self.frame["frameColor"] = self.errorColor
        else:
            self.frame["frameColor"] = self.normalColor

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
        base.messenger.send("NodeEditor_set_dirty")

    def getLeftEdge(self):
        """Get the left edge of the frame as seen from the frame"""
        return self.frame["frameSize"][0]

    def getRightEdge(self):
        """Get the right edge of the frame as seen from the frame"""
        return self.frame["frameSize"][1]

    def getBottomEdge(self):
        """Get the bottom edge of the frame as seen from the frame"""
        return self.frame["frameSize"][2]

    def getTopEdge(self):
        """Get the top edge of the frame as seen from the frame"""
        return self.frame["frameSize"][3]

    def getLeft(self, np=None):
        """Get left edge of the frame with respect to it's position as seen from the given np"""
        if np is None:
            np = render2d
        return self.getPos(np).getX() + self.frame["frameSize"][0]

    def getRight(self, np=None):
        """Get right edge of the frame with respect to it's position as seen from the given np"""
        if np is None:
            np = render2d
        return self.getPos(np).getX() + self.frame["frameSize"][1]

    def getBottom(self, np=None):
        """Get bottom edge of the frame with respect to it's position as seen from the given np"""
        if np is None:
            np = render2d
        return self.getPos(np).getZ() + self.frame["frameSize"][2]

    def getTop(self, np=None):
        """Get top edge of the frame with respect to it's position as seen from the given np"""
        if np is None:
            np = render2d
        return self.getPos(np).getZ() + self.frame["frameSize"][3]
