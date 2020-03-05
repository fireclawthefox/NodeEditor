#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time
import configparser
import importlib
import copy

from direct.showbase import ShowBaseGlobal
from panda3d.core import (
    loadPrcFileData,
    LPoint2f,
    Point2,
    Point3,
    NodePath,
    CardMaker,
    Vec3,
    AntialiasAttrib,
    TransparencyAttrib)
loadPrcFileData("", """
""")

# We need showbase to make this script directly runnable
from direct.showbase.ShowBase import ShowBase

from direct.directtools.DirectGeometry import LineNodePath

from direct.gui import DirectGuiGlobals as DGG

from MenuBar import MenuBar

from NodeCore.NodeBase import NodeBase
from NodeCore.Nodes import *
from NodeCore.Sockets.SocketBase import OUTSOCKET, INSOCKET
from NodeCore.NodeConnector import NodeConnector

class main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        self.win.setClearColor((0.16, 0.16, 0.16, 1))
        render.setAntialias(AntialiasAttrib.MAuto)
        render2d.setAntialias(AntialiasAttrib.MAuto)

        self.startSocket = None
        self.endSocket = None

        self.nodeList = []
        self.connections = []
        self.selectedNodes = []

        self.accept("space", self.addNode)
        self.accept("startPlug", self.setStartPlug)
        self.accept("endPlug", self.setEndPlug)
        self.accept("connectPlugs", self.connectPlugs)
        self.accept("cancelPlug", self.cancelPlug)
        self.accept("startLineDrawing", self.startLineDrawing)
        self.accept("stopLineDrawing", self.stopLineDrawing)
        self.accept("dragNodeStart", self.setDraggedNode)
        self.accept("dragNodeMove", self.updateNodeMove)
        self.accept("dragNodeStop", self.updateNodeStop)
        self.accept("updateConnectedNodes", self.updateConnectedNodes)
        self.accept("selectNode", self.selectNode)
        self.accept("shift-d", self.copyNodes)

        self.accept("addNode", self.addNode)
        self.accept("removeNode", self.removeNode)
        self.accept("x", self.removeNode)

        self.accept("new", self.newProject)
        self.accept("save", self.saveProject)
        self.accept("load", self.loadProject)
        self.accept("quit", exit)

        self.accept("zoom", self.zoom)
        self.accept("zoom_reset", self.zoomReset)

        self.accept("wheel_up", self.zoom, [True])
        self.accept("wheel_down", self.zoom, [False])

        self.mouseSpeed = 1
        self.mousePos = None
        self.startCameraMovement = False
        self.accept("mouse2", self.setMoveCamera, [True])
        self.accept("mouse2-up", self.setMoveCamera, [False])

        self.accept("mouse3", self.deselectAll)

        # accept the 1st mouse button events to start and stop the draw
        self.accept("mouse1", self.startBoxDraw)
        self.accept("mouse1-up", self.stopBoxDraw)
        # variables to store the start and current pos of the mousepointer
        self.startPos = LPoint2f(0,0)
        self.lastPos = LPoint2f(0,0)
        # variables for the to be drawn box
        self.boxCardMaker = CardMaker("SelectionBox")
        self.boxCardMaker.setColor(1,0,0,0.25)
        self.box = None


        self.screenSize = base.getSize()
        self.accept("window-event", self.windowEventHandler)

        self.menuBar = MenuBar()

        self.viewNP = aspect2d.attachNewNode("viewNP")
        self.viewNP.setScale(0.5)

        # add the cameras update task so it will be updated every frame
        self.taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

    def newProject(self):
        self.cleanup()

    def cleanup(self):
        self.deselectAll()
        self.removeAllNodes()

        self.startSocket = None
        self.endSocket = None

        self.nodeList = []
        self.connections = []
        self.selectedNodes = []

    def saveProject(self):
        pass

    def loadProject(self):
        pass

    #
    # CAMERA SPECIFIC FUNCTIONS
    #
    def setMoveCamera(self, moveCamera):
        # store the mouse position if weh have a mouse
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            self.mousePos = Point2(x, y)
        # set the variable according to if we want to move the camera or not
        self.startCameraMovement = moveCamera

    def updateCam(self, task):
        # variables to store the mouses current x and y position
        x = 0.0
        y = 0.0
        if base.mouseWatcherNode.hasMouse():
            # get the mouse position
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
        if base.mouseWatcherNode.hasMouse() \
        and self.mousePos is not None \
        and self.startCameraMovement:
            # Move the viewer node aspect independent
            wp = self.win.getProperties()
            aspX = 1.0
            aspY = 1.0
            wpXSize = wp.getXSize()
            wpYSize = wp.getYSize()
            if wpXSize > wpYSize:
                aspX = wpXSize / float(wpYSize)
            else:
                aspY = wpYSize / float(wpXSize)
            mouseMoveX = (self.mousePos.getX() - x) / self.viewNP.getScale().getX() * self.mouseSpeed * aspX
            mouseMoveY = (self.mousePos.getY() - y) / self.viewNP.getScale().getZ() * self.mouseSpeed * aspY
            self.mousePos = Point2(x, y)

            self.viewNP.setX(self.viewNP, -mouseMoveX)
            self.viewNP.setZ(self.viewNP, -mouseMoveY)

            self.updateConnections()

        # continue the task until it got manually stopped
        return task.cont

    def zoom(self, zoomIn):
        zoomFactor = 0.05
        maxZoomIn = 2
        maxZoomOut = 0.1
        if zoomIn:
            s = self.viewNP.getScale()
            if s.getX()-zoomFactor < maxZoomIn and s.getY()-zoomFactor < maxZoomIn and s.getZ()-zoomFactor < maxZoomIn:
                self.viewNP.setScale(s.getX()+zoomFactor,s.getY()+zoomFactor,s.getZ()+zoomFactor)
        else:
            s = self.viewNP.getScale()
            if s.getX()-zoomFactor > maxZoomOut and s.getY()-zoomFactor > maxZoomOut and s.getZ()-zoomFactor > maxZoomOut:
                self.viewNP.setScale(s.getX()-zoomFactor,s.getY()-zoomFactor,s.getZ()-zoomFactor)
        self.updateConnections()

    def zoomReset(self):
        self.viewNP.setScale(0.5)
        self.updateConnections()

    def addNode(self, nodeType=None):
        self.deselectAll()
        if nodeType is None:
            node = NodeBase("Test", self.viewNP)
            node.addOut("Out 1")
            node.addOut("Out 2")
            node.addIn("In 1")
            node.addIn("In 2")
        else:
            node = eval(nodeType + ".Node")(self.viewNP)
        node.create()
        self.nodeList.append(node)

    def removeNode(self):
        for node in self.selectedNodes:
            for connector in self.connections[:]:
                if connector.socketA.node is node or connector.socketB.node is node:
                    connector.disconnect()
                    self.connections.remove(connector)
            self.nodeList.remove(node)
            node.destroy()
            del node

    def removeAllNodes(self):
        # Remove all connections
        for connector in self.connections[:]:
            connector.disconnect()
            self.connections.remove(connector)

        # Remove all nodes
        for node in self.nodeList[:]:
            self.nodeList.remove(node)
            node.destroy()
            del node

    def copyNodes(self):
        newNodeList = []
        for node in self.selectedNodes:
            newNode = type(node)(self.viewNP)
            #newNode = copy.deepcopy(node)
            #newNode = testValueNode.Node(self.viewNP)
            newNode.show()
            newNode.frame.setPos(node.frame.getPos())
            newNodeList.append(newNode)
            self.nodeList.append(newNode)

        self.deselectAll()
        for node in newNodeList:
            node.select(True)
            self.selectedNodes.append(node)
        dragNode = newNodeList[0]
        dragNode.accept("mouse1-up", dragNode._dragStop)
        dragNode._dragStart(dragNode.frame, None)

    def startLineDrawing(self, startPos):
        self.line = LineNodePath(render2d, thickness=2, colorVec=(0.8,0.8,0.8,1))
        self.line.moveTo(startPos)
        t = self.taskMgr.add(self.drawLineTask, "drawLineTask")
        t.startPos = startPos

    def drawLineTask(self, task):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            pos = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])

            self.line.reset()
            self.line.moveTo(task.startPos)
            self.line.drawTo(pos)
            self.line.create()
        return task.cont

    def stopLineDrawing(self):
        taskMgr.remove("drawLineTask")
        if self.line is not None:
            self.line.reset()
            self.line = None

    def setStartPlug(self, socket):
        self.startSocket = socket

    def setEndPlug(self, socket):
        self.endSocket = socket

    def cancelPlug(self):
        self.startSocket = None
        self.endSocket = None

    def connectPlugs(self):
        # only do something if we actually have two sockets
        if self.startSocket is None or self.endSocket is None:
            return

        # check if the "IN" socket has no connections otherwise we can't connect
        if (self.startSocket.type == INSOCKET and self.startSocket.connected) \
        or (self.endSocket.type == INSOCKET and self.endSocket.connected):
            for connector in self.connections[:]:
                if connector.connects(self.startSocket, self.endSocket):
                    connector.disconnect()
                    self.connections.remove(connector)
                    outSocketNode = self.startSocket.node if self.startSocket.type is OUTSOCKET else self.endSocket.node
                    self.updateConnectedNodes(outSocketNode)
                    self.startSocket = None
                    self.endSocket = None
                    return
            return

        # check if the nodes and types are different, we can't connect
        # a node with itself or an "OUT" type with another "OUT" type.
        # The same applies to "IN" type sockets
        if self.startSocket.node is not self.endSocket.node \
        and self.startSocket.type != self.endSocket.type:
            connector = NodeConnector(self.startSocket, self.endSocket)
            self.connections.append(connector)
            self.startSocket.setConnected(True)
            self.endSocket.setConnected(True)
            outSocketNode = self.startSocket.node if self.startSocket.type is OUTSOCKET else self.endSocket.node
            self.updateConnectedNodes(outSocketNode)
            self.startSocket = None
            self.endSocket = None

    def updateConnectedNodes(self, leaveNode):
        for connector in self.connections:
            for outSocket in leaveNode.outputList:
                if connector.socketA is outSocket:
                    connector.socketA.node.logic()
                    connector.socketB.setValue(connector.socketA.getValue())
                    connector.socketB.node.logic()
                    self.updateConnectedNodes(connector.socketB.node)
                elif connector.socketB is outSocket:
                    connector.socketB.node.logic()
                    connector.socketA.setValue(connector.socketB.getValue())
                    connector.socketA.node.logic()
                    self.updateConnectedNodes(connector.socketA.node)

    def setDraggedNode(self, node):
        self.draggedNode = node
        self.tempNodePositions = {}
        for node in self.selectedNodes:
            self.tempNodePositions[node] = node.frame.getPos(render2d)

    def updateNodeMove(self, mouseA, mouseB):
        for node in self.selectedNodes:
            if node is not self.draggedNode and node in self.tempNodePositions.keys():
                editVec = Vec3(self.tempNodePositions[node] - mouseA)
                newPos = mouseB + editVec
                node.frame.setPos(render2d, newPos)
        self.updateConnections()

    def updateNodeStop(self, node=None):
        self.draggedNode = None
        self.tempNodePositions = {}
        self.updateConnections()

    def updateConnections(self, args=None):
        for connector in self.connections:
            connector.update()

    def windowEventHandler(self, window=None):
        # call showBase windowEvent which would otherwise get overridden and breaking the app
        self.windowEvent(window)

        if window != self.win:
            # This event isn't about our window.
            return

        if window is not None: # window is none if panda3d is not started
            if self.screenSize == base.getSize():
                return
            self.screenSize = base.getSize()

            # Resize all editor frames
            self.menuBar.resizeFrame()

    def selectNode(self, node, selected, addToSelection=False, deselectOthersIfUnselected=False):
        if not addToSelection:
            if deselectOthersIfUnselected:
                if not node.selected:
                    self.deselectAll(node)
            else:
                self.deselectAll(node)
        if selected:
            if node not in self.selectedNodes:
                node.select(True)
                self.selectedNodes.append(node)
        else:
            node.select(False)
            self.selectedNodes.remove(node)

    def deselectAll(self, excludedNode=None):
        for node in self.nodeList:
            if node is excludedNode: continue
            node.select(False)
        self.selectedNodes = []

    def startBoxDraw(self):
        """Start drawing the box"""
        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            self.startPos = LPoint2f(self.mouseWatcherNode.getMouse())
        taskMgr.add(self.dragBoxDrawTask, "dragBoxDrawTask")

    def stopBoxDraw(self):
        """Stop the draw box task and remove the box"""
        if not taskMgr.hasTaskNamed("dragBoxDrawTask"): return
        taskMgr.remove("dragBoxDrawTask")
        if self.startPos is None or self.lastPos is None: return
        self.deselectAll()
        if self.box is not None:
            for node in self.nodeList:
                pos = node.frame.getPos(render2d)

                nodeLeft = pos.getX() + node.frame["frameSize"][0] * self.viewNP.getScale().getX()
                nodeRight = pos.getX() + node.frame["frameSize"][1] * self.viewNP.getScale().getX()
                nodeBottom = pos.getZ() + node.frame["frameSize"][2] * self.viewNP.getScale().getZ()
                nodeTop = pos.getZ() + node.frame["frameSize"][3] * self.viewNP.getScale().getZ()

                left = min(self.lastPos.getX(), self.startPos.getX())
                right = max(self.lastPos.getX(), self.startPos.getX())
                top = max(self.lastPos.getY(), self.startPos.getY())
                bottom = min(self.lastPos.getY(), self.startPos.getY())

                xGood = yGood = False
                if left < nodeLeft and right > nodeLeft:
                    xGood = True
                elif left < nodeRight and right > nodeRight:
                    xGood = True
                if top > nodeTop and bottom < nodeTop:
                    yGood = True
                elif top > nodeBottom and bottom < nodeBottom:
                    yGood = True

                if xGood and yGood:
                    self.selectNode(node, True, True)
                    #node.select(True)
            self.box.removeNode()
            self.startPos = None
            self.lastPos = None

    def dragBoxDrawTask(self, task):
        """This task will track the mouse position and actualize the box's size
        according to the first click position of the mouse"""
        if self.mouseWatcherNode.hasMouse():
            if self.startPos is None:
                self.startPos = LPoint2f(self.mouseWatcherNode.getMouse())
            # get the current mouse position
            self.lastPos = LPoint2f(self.mouseWatcherNode.getMouse())
        else:
            return task.cont

        # check if we already have a box
        if self.box != None:
            # if so, remove that old box
            self.box.removeNode()
        # set the box's size
        self.boxCardMaker.setFrame(
        	self.lastPos.getX(),
        	self.startPos.getX(),
        	self.startPos.getY(),
        	self.lastPos.getY())
        # generate, setup and draw the box
        node = self.boxCardMaker.generate()
        self.box = render2d.attachNewNode(node)
        self.box.setBin("gui-popup", 25)
        self.box.setTransparency(TransparencyAttrib.M_alpha)

        # run until the task is manually stopped
        return task.cont

# Create a ShowBase instance to make this gui directly runnable
app = main()
app.run()
