#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
import os
from panda3d.core import (
    LPoint2f,
    Point2,
    Point3,
    CardMaker,
    Vec3,
    TransparencyAttrib,
    loadPrcFileData,
    Filename)

# We need showbase to make this script directly runnable
from direct.showbase.DirectObject import DirectObject
from direct.directtools.DirectGeometry import LineNodePath

from Panda3DNodeEditor.SaveScripts.SaveJSON import Save
from Panda3DNodeEditor.LoadScripts.LoadJSON import Load
from Panda3DNodeEditor.GUI.MainView import MainView
from Panda3DNodeEditor.NodeCore.NodeManager import NodeManager

class NodeEditor(DirectObject):
    def __init__(self, parent, customNodeMap={}, customExporterMap={}):

        DirectObject.__init__(self)

        fn = Filename.fromOsSpecific(os.path.dirname(__file__))
        fn.makeTrueCase()
        self.icon_dir = str(fn) + "/"
        loadPrcFileData("", f"model-path {self.icon_dir}")

        #
        # NODE VIEW
        #
        self.viewNP = aspect2d.attachNewNode("viewNP")
        self.viewNP.setScale(0.5)

        #
        # NODE MANAGER
        #
        self.nodeMgr = NodeManager(self.viewNP, customNodeMap)

        # Drag view
        self.mouseSpeed = 1
        self.mousePos = None
        self.startCameraMovement = False

        # Box select
        # variables to store the start and current pos of the mousepointer
        self.startPos = LPoint2f(0,0)
        self.lastPos = LPoint2f(0,0)
        # variables for the to be drawn box
        self.boxCardMaker = CardMaker("SelectionBox")
        self.boxCardMaker.setColor(1,1,1,0.25)
        self.box = None

        #
        # MENU BAR
        #
        self.mainView = MainView(parent, customNodeMap, customExporterMap)

        self.enable_editor()

    # ------------------------------------------------------------------
    # FRAME COMPATIBILITY FUNCTIONS
    # ------------------------------------------------------------------
    def is_dirty(self):
        """
        This method returns True if an unsaved state of the editor is given
        """
        return len(self.nodeMgr.getAllNodes()) > 0

    def enable_editor(self):
        """
        Enable the editor.
        """
        self.enable_events()

        # Task for handling dragging of the camera/view
        taskMgr.add(self.updateCam, "NodeEditor_task_camActualisation", priority=-4)

        self.viewNP.show()

    def disable_editor(self):
        """
        Disable the editor.
        """
        self.ignore_all()
        taskMgr.remove("NodeEditor_task_camActualisation")

        self.viewNP.hide()

    def do_exception_save(self):
        """
        Save content of editor if the application crashes
        """
        Save(self.nodeMgr.nodeList, self.nodeMgr.connections, True)

    # ------------------------------------------------------------------
    # NODE EDITOR RELATED EVENTS
    # ------------------------------------------------------------------
    def enable_events(self):
        # Add nodes
        self.accept("addNode", self.nodeMgr.addNode)
        # Remove nodes
        self.accept("NodeEditor_removeNode", self.nodeMgr.removeNode)
        self.accept("x", self.nodeMgr.removeNode)
        self.accept("delete", self.nodeMgr.removeNode)
        # Selecting
        self.accept("selectNode", self.nodeMgr.selectNode)
        # Deselecting
        self.accept("mouse3", self.nodeMgr.deselectAll)
        # Node Drag and Drop
        self.accept("dragNodeStart", self.setDraggedNode)
        self.accept("dragNodeMove", self.updateNodeMove)
        self.accept("dragNodeStop", self.updateNodeStop)
        # Duplicate/Copy nodes
        self.accept("shift-d", self.nodeMgr.copyNodes)
        self.accept("NodeEditor_copyNodes", self.nodeMgr.copyNodes)
        # Refresh node logics
        self.accept("ctlr-r", self.nodeMgr.updateAllLeaveNodes)
        self.accept("NodeEditor_refreshNodes", self.nodeMgr.updateAllLeaveNodes)

        #
        # SOCKET RELATED EVENTS
        #
        self.accept("updateConnectedNodes", self.nodeMgr.updateConnectedNodes)
        # Socket connection with drag and drop
        self.accept("startPlug", self.nodeMgr.setStartPlug)
        self.accept("endPlug", self.nodeMgr.setEndPlug)
        self.accept("connectPlugs", self.nodeMgr.connectPlugs)
        self.accept("cancelPlug", self.nodeMgr.cancelPlug)
        # Draw line while connecting sockets
        self.accept("startLineDrawing", self.startLineDrawing)
        self.accept("stopLineDrawing", self.stopLineDrawing)

        #
        # CONNECTION RELATED EVENTS
        #
        self.accept("NodeEditor_updateConnections", self.nodeMgr.updateConnections)

        #
        # PROJECT MANAGEMENT
        #
        self.accept("NodeEditor_new", self.newProject)
        self.accept("NodeEditor_save", self.saveProject)
        self.accept("NodeEditor_load", self.loadProject)
        self.accept("quit_app", exit)

        #
        # EXPORTERS
        #
        self.accept("NodeEditor_customSave", self.customExport)

        #
        # EDITOR VIEW
        #
        # Zooming
        self.accept("NodeEditor_zoom", self.zoom)
        self.accept("NodeEditor_zoom_reset", self.zoomReset)
        self.accept("wheel_up", self.zoom, [True])
        self.accept("wheel_down", self.zoom, [False])

        # Drag view
        self.accept("mouse2", self.setMoveCamera, [True])
        self.accept("mouse2-up", self.setMoveCamera, [False])

        # Box select
        # accept the 1st mouse button events to start and stop the draw
        self.accept("mouse1", self.startBoxDraw)
        self.accept("mouse1-up", self.stopBoxDraw)

    # ------------------------------------------------------------------
    # PROJECT FUNCTIONS
    # ------------------------------------------------------------------
    def newProject(self):
        self.nodeMgr.cleanup()

    def saveProject(self):
        Save(self.nodeMgr.nodeList, self.nodeMgr.connections)

    def loadProject(self):
        self.nodeMgr.cleanup()
        Load(self.nodeMgr)

    def customExport(self, exporter):
        exporter(self.nodeMgr.nodeList, self.nodeMgr.connections)

    # ------------------------------------------------------------------
    # CAMERA SPECIFIC FUNCTIONS
    # ------------------------------------------------------------------
    def setMoveCamera(self, moveCamera):
        """Start dragging around the editor area/camera"""
        # store the mouse position if weh have a mouse
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            self.mousePos = Point2(x, y)
        # set the variable according to if we want to move the camera or not
        self.startCameraMovement = moveCamera

    def updateCam(self, task):
        """Task that will move the editor area/camera around according
        to mouse movements"""
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
            wp = base.win.getProperties()
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

            self.nodeMgr.updateConnections()

        # continue the task until it got manually stopped
        return task.cont

    def zoom(self, zoomIn):
        """Zoom the editor in or out dependent on the value in zoomIn"""
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
        self.nodeMgr.updateConnections()

    def zoomReset(self):
        """Set the zoom level back to the default"""
        self.viewNP.setScale(0.5)
        self.nodeMgr.updateConnections()

    # ------------------------------------------------------------------
    # DRAG LINE
    # ------------------------------------------------------------------
    def startLineDrawing(self, startPos):
        """Start a task that will draw a line from the given start
        position to the cursor"""
        self.line = LineNodePath(render2d, thickness=2, colorVec=(0.8,0.8,0.8,1))
        self.line.moveTo(startPos)
        t = taskMgr.add(self.drawLineTask, "drawLineTask")
        t.startPos = startPos

    def drawLineTask(self, task):
        """Draws a line from a given start position to the cursor"""
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            pos = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])

            self.line.reset()
            self.line.moveTo(task.startPos)
            self.line.drawTo(pos)
            self.line.create()
        return task.cont

    def stopLineDrawing(self):
        """Stop the task that draws a line to the cursor"""
        taskMgr.remove("drawLineTask")
        if self.line is not None:
            self.line.reset()
            self.line = None

    # ------------------------------------------------------------------
    # EDITOR NODE DRAGGING UPDATE
    # ------------------------------------------------------------------
    def setDraggedNode(self, node):
        """This will set the node that is currently dragged around
        as well as update other selected nodes which will be moved
        in addition to the main dragged node"""
        self.draggedNode = node
        self.draggedNode.disable()
        self.tempNodePositions = {}
        for node in self.nodeMgr.selectedNodes:
            self.tempNodePositions[node] = node.frame.getPos(render2d)

    def updateNodeMove(self, mouseA, mouseB):
        """Will be called as long as a node is beeing dragged around"""
        for node in self.nodeMgr.selectedNodes:
            if node is not self.draggedNode and node in self.tempNodePositions.keys():
                editVec = Vec3(self.tempNodePositions[node] - mouseA)
                newPos = mouseB + editVec
                node.frame.setPos(render2d, newPos)
        self.nodeMgr.updateConnections()

    def updateNodeStop(self, node=None):
        """Will be called when a node dragging stopped"""
        self.draggedNode.enable()
        self.draggedNode = None
        self.tempNodePositions = {}
        self.nodeMgr.updateConnections()

    # ------------------------------------------------------------------
    # SELECTION BOX
    # ------------------------------------------------------------------
    def startBoxDraw(self):
        """Start drawing the box"""
        if base.mouseWatcherNode.hasMouse():
            # get the mouse position
            self.startPos = LPoint2f(base.mouseWatcherNode.getMouse())
        taskMgr.add(self.dragBoxDrawTask, "dragBoxDrawTask")

    def stopBoxDraw(self):
        """Stop the draw box task and remove the box"""
        if not taskMgr.hasTaskNamed("dragBoxDrawTask"): return
        taskMgr.remove("dragBoxDrawTask")
        if self.startPos is None or self.lastPos is None: return
        self.nodeMgr.deselectAll()
        if self.box is not None:
            for node in self.nodeMgr.getAllNodes():
                # store some view scales for calculations
                viewXScale = self.viewNP.getScale().getX()
                viewZScale = self.viewNP.getScale().getZ()

                # calculate the node edges
                nodeLeft = node.getLeft() * viewXScale
                nodeRight = node.getRight() * viewXScale
                nodeBottom = node.getBottom() * viewZScale
                nodeTop = node.getTop() * viewZScale

                # calculate bounding box edges
                left = min(self.lastPos.getX(), self.startPos.getX())
                right = max(self.lastPos.getX(), self.startPos.getX())
                top = max(self.lastPos.getY(), self.startPos.getY())
                bottom = min(self.lastPos.getY(), self.startPos.getY())

                # check for hits
                xGood = yGood = False
                if left < nodeLeft and right > nodeLeft:
                    xGood = True
                elif left < nodeRight and right > nodeRight:
                    xGood = True
                if top > nodeTop and bottom < nodeTop:
                    yGood = True
                elif top > nodeBottom and bottom < nodeBottom:
                    yGood = True

                # check if we have any hits
                if xGood and yGood:
                    self.nodeMgr.selectNode(node, True, True)

            # Cleanup the selection box
            self.box.removeNode()
            self.startPos = None
            self.lastPos = None

    def dragBoxDrawTask(self, task):
        """This task will track the mouse position and actualize the box's size
        according to the first click position of the mouse"""
        if base.mouseWatcherNode.hasMouse():
            if self.startPos is None:
                self.startPos = LPoint2f(base.mouseWatcherNode.getMouse())
            # get the current mouse position
            self.lastPos = LPoint2f(base.mouseWatcherNode.getMouse())
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
