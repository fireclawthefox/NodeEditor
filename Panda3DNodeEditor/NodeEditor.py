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
from Panda3DNodeEditor.GUI.SearchBox import SearchBox
from Panda3DNodeEditor.GUI.SearchBox import SearchBoxEntryData
from Panda3DNodeEditor.NodeCore.NodeManager import NodeManager
from Panda3DNodeEditor.NodeCore.Nodes.NodeJSONLoader import NodeJSONLoader


from Panda3DNodeEditor.NodeCore.Sockets.BoolSocket import BoolSocket
from Panda3DNodeEditor.NodeCore.Sockets.InSocket import InSocket
from Panda3DNodeEditor.NodeCore.Sockets.NumericSocket import NumericSocket
from Panda3DNodeEditor.NodeCore.Sockets.OptionSelectSocket import OptionSelectSocket
from Panda3DNodeEditor.NodeCore.Sockets.TextSocket import TextSocket
from Panda3DNodeEditor.NodeCore.Sockets.ArgumentsSocket import ArgumentsSocket
from Panda3DNodeEditor.NodeCore.Sockets.ListSocket import ListSocket

class NodeEditor(DirectObject):
    def __init__(self,
            parent,
            defaultNodeMap={},
            defaultNodeJSONFiles=[],
            customNodeMap={},
            customExporterMap={},
            customSocketMap={},
            customNodeJSONFiles=[]):

        DirectObject.__init__(self)

        fn = Filename.fromOsSpecific(os.path.dirname(__file__))
        fn.makeTrueCase()
        self.icon_dir = str(fn) + "/"
        loadPrcFileData("", f"model-path {self.icon_dir}")

        #
        # PROJECT RELATED
        #
        self.lastSavePath = None
        self.dirty = False

        #
        # NODE VIEW
        #
        self.viewNP = aspect2d.attachNewNode("viewNP")
        self.viewNP.setScale(0.5)

        #
        # NODE LOADING
        #
        self.nodeJSONLoader = NodeJSONLoader(
            defaultNodeJSONFiles,
            customSocketMap)
        defaultNodeMap = {
            **defaultNodeMap,
            **self.nodeJSONLoader.getNodeMap()
        }
        defaultSocketMap = {
            BoolSocket.__name__: BoolSocket,
            InSocket.__name__: InSocket,
            NumericSocket.__name__: NumericSocket,
            OptionSelectSocket.__name__: OptionSelectSocket,
            TextSocket.__name__: TextSocket,
            ArgumentsSocket.__name__: ArgumentsSocket,
            ListSocket.__name__: ListSocket
        }

        self.customNodeJSONLoader = NodeJSONLoader(
            customNodeJSONFiles,
            customSocketMap)
        customJsonNodeMap = self.customNodeJSONLoader.getNodeMap()
        customNodeMap = {
            **customNodeMap,
            **customJsonNodeMap}

        #
        # NODE MANAGER
        #
        self.nodeMgr = NodeManager(
            self.viewNP,
            defaultNodeMap,
            defaultSocketMap,
            customNodeMap,
            customSocketMap)

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
        self.mainView = MainView(parent, defaultNodeMap, customNodeMap, customExporterMap)

        #
        # SEARCH BOX
        #
        self.searchBox = SearchBox(50, self.searchBoxClose)
        self.searchBox.hide()

        # Search Box content
        node_map = defaultNodeMap
        node_map.update(customNodeMap)
        nodes_entries = []
        for node_name, node in node_map.items():
            if type(node) == str:
                nodes_entries.append(
                    SearchBoxEntryData(
                        name=node_name,
                        tags=[],
                        command=self.searchBoxSelect,
                        extraArgs=[node]
                    ))
            elif type(node) == list:
                nodes_entries.append(
                    SearchBoxEntryData(
                        name=node_name,
                        tags=[],
                        command=self.searchBoxSelect,
                        extraArgs=[node[1]]
                    ))
            elif type(node) == dict:
                tags = [node_name]
                sub_entries = self.__addSubEntries(tags, node)
                nodes_entries += sub_entries
        self.searchBox.setEntries(nodes_entries)

        #
        # START EDITOR
        #
        self.enable_editor()

    def __addSubEntries(self, tags, node):
        sub_entries = []
        for sub_node_name, sub_node in node.items():
            added_node = None
            if type(sub_node) == list:
                added_node = sub_node[1]
            elif type(sub_node) == str:
                added_node = sub_node
            elif type(sub_node) == dict:
                sub_tags = tags + [sub_node_name]
                sub_sub_entries = self.__addSubEntries(sub_tags, sub_node)
                sub_entries += sub_sub_entries
                continue
            else:
                logging.error(f"Unknown type for sub-node: {type(sub_node)}")
                continue
            sub_entries.append(
                SearchBoxEntryData(
                        name=sub_node_name,
                        tags=tags,
                        command=self.searchBoxSelect,
                        extraArgs=[added_node]
                    ))
        return sub_entries

    # ------------------------------------------------------------------
    # FRAME COMPATIBILITY FUNCTIONS
    # ------------------------------------------------------------------
    def is_dirty(self):
        """
        This method returns True if an unsaved state of the editor is given
        """
        return self.dirty

    def enable_editor(self):
        """
        Enable the editor.
        """
        self.enable_events()

        # Task for handling dragging of the camera/view
        taskMgr.add(self.updateCam, "NodeEditor_task_camActualisation", priority=-4)

        self.viewNP.show()
        self.nodeMgr.showConnections()

    def disable_editor(self):
        """
        Disable the editor.
        """
        self.ignore_all()
        taskMgr.remove("NodeEditor_task_camActualisation")

        self.viewNP.hide()
        self.nodeMgr.hideConnections()

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
        self.accept("ShowNodeSearch", self.searchBox.show)
        self.accept("f3", self.searchBox.show)
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
        self.accept("NodeEditor_run_logic", self.nodeMgr.run_logic)

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
        self.accept("NodeEditor_save_as", self.saveAsProject)
        self.accept("NodeEditor_load", self.loadProject)
        self.accept("quit_app", exit)

        self.accept("NodeEditor_set_dirty", self.set_dirty)
        self.accept("NodeEditor_set_clean", self.set_clean)

        self.accept("setLastPath", self.setLastPath)

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
        self.lastSavePath = None

    def saveProject(self):
        Save(self.nodeMgr.nodeList, self.nodeMgr.connections, filepath=self.lastSavePath)

    def saveAsProject(self):
        Save(self.nodeMgr.nodeList, self.nodeMgr.connections)

    def loadProject(self):
        self.nodeMgr.cleanup()
        Load(self.nodeMgr)

    def customExport(self, exporter):
        exporter(self.nodeMgr.nodeList, self.nodeMgr.connections)

    def setLastPath(self, path):
        self.lastSavePath = path

    def set_dirty(self):
        base.messenger.send("request_dirty_name")
        self.dirty = True

    def set_clean(self):
        base.messenger.send("request_clean_name")
        self.dirty = False
        self.hasSaved = True

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
        if self.draggedNode is None: return
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
                p = node.frame.get_parent()
                nodeLeft = node.getLeft(p) * viewXScale / base.a2dRight
                nodeRight = node.getRight(p) * viewXScale / base.a2dRight
                nodeBottom = node.getBottom(p) * viewZScale / base.a2dTop
                nodeTop = node.getTop(p) * viewZScale / base.a2dTop

                # calculate bounding box edges
                left = min(self.lastPos.getX(), self.startPos.getX())
                right = max(self.lastPos.getX(), self.startPos.getX())
                top = max(self.lastPos.getY(), self.startPos.getY())
                bottom = min(self.lastPos.getY(), self.startPos.getY())

                l_in_l = left > nodeLeft
                r_in_r = right < nodeRight
                b_in_t = bottom < nodeTop
                t_in_b = top > nodeBottom

                r_in_l = right > nodeLeft
                l_in_r = left < nodeRight
                t_in_t = top < nodeTop
                b_in_b = bottom > nodeBottom

                l_out_l = left < nodeLeft
                r_out_r = right > nodeRight
                b_out_b = bottom < nodeBottom
                t_out_t = top > nodeTop

                nodeHit = False

                #
                # Side checks
                #
                if l_in_l and r_in_r and t_in_b and t_in_t:
                    # Box hits middle from below
                    nodeHit = True
                elif l_in_l and r_in_r and b_in_t and b_in_b:
                    # Box hits middle from above
                    nodeHit = True
                elif t_in_t and b_in_b and r_in_l and r_in_r:
                    # Box hits middle from left
                    nodeHit = True
                elif t_in_t and b_in_b and l_in_r and l_in_l:
                    # Box hits middle from right
                    nodeHit = True

                #
                # Corner checks
                #
                elif r_in_l and r_in_r and b_in_t and b_in_b:
                    # Box hits top left corner
                    nodeHit = True
                elif l_in_r and l_in_l and b_in_t and b_in_b:
                    # Box hits top right corner
                    nodeHit = True
                elif l_in_r and l_in_l and t_in_b and t_in_t:
                    # Box hits bottom right corner
                    nodeHit = True
                elif r_in_l and r_in_r and t_in_b and t_in_t:
                    # Box hits bottom left corner
                    nodeHit = True

                #
                # surrounding checks
                #
                elif l_in_r and l_in_l and t_out_t and b_out_b:
                    # box encases the left of the node
                    nodeHit = True
                elif r_in_l and r_in_r and t_out_t and b_out_b:
                    # box encases the right of the node
                    nodeHit = True
                elif t_in_b and t_in_t and r_out_r and l_out_l:
                    # box encases the bottom of the node
                    nodeHit = True
                elif b_in_t and b_in_b and r_out_r and l_out_l:
                    # box encases the top of the node
                    nodeHit = True

                #
                # Node fully encased
                #
                elif l_out_l and r_out_r and b_out_b and t_out_t:
                    # box encased fully
                    nodeHit = True

                if nodeHit:
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

    # ------------------------------------------------------------------
    # SEARCH BOX
    # ------------------------------------------------------------------
    def searchBoxSelect(self, node):
        self.searchBox.hide()
        base.messenger.send("addNode", [node])

    def searchBoxClose(self):
        self.searchBox.hide()
