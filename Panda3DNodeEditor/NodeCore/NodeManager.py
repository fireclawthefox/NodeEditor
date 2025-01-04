#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
import logging

import Panda3DNodeEditor
from Panda3DNodeEditor import NodeCore
from Panda3DNodeEditor.NodeCore.Nodes import *
from Panda3DNodeEditor.NodeCore.Nodes.NodeBase import NodeBase
from Panda3DNodeEditor.NodeCore.Sockets.SocketBase import OUTSOCKET, INSOCKET
from Panda3DNodeEditor.NodeCore.NodeConnector import NodeConnector

class NodeManager:
    def __init__(self, nodeViewNP=None, defaultNodeMap={}, defaultSocketMap={}, customNodeMap={}, customSocketMap={}):
        # Node Management
        self.nodeList = []

        # Socket connection Management
        self.connections = []
        self.startPlug = None
        self.startSocket = None
        self.endPlug = None
        self.endSocket = None

        # Drag and Drop feature
        self.selectedNodes = []

        self.nodeViewNP = nodeViewNP

        self.defaultNodeMap = defaultNodeMap
        self.defaultSocketMap = defaultSocketMap

        self.customNodeMap = customNodeMap
        self.customSocketMap = customSocketMap

        self.socketMap = {
            **self.defaultSocketMap,
            **self.customSocketMap
        }

    def cleanup(self):
        self.deselectAll()
        self.removeAllNodes()

        self.startSocket = None
        self.endSocket = None

        self.nodeList = []
        self.connections = []
        self.selectedNodes = []

        base.messenger.send("NodeEditor_set_clean")

    #-------------------------------------------------------------------
    # NODE MANAGEMENT
    #-------------------------------------------------------------------
    def getAllNodes(self):
        return self.nodeList

    def createNode(self, nodeType, typeName):
        """Creates a node of the given type and returns it. Returns None
        if the node could not be created.
        nodeType can be either a node class type or a string representing such a type"""
        node = None
        nodeClassName = nodeType.split(".")[-1]
        if nodeClassName == "NodeBase":
            try:
                nodeInfo = self.findInNodeMap(typeName, self.defaultNodeMap)[1]
                node = nodeInfo[0](nodeInfo[1], self.nodeViewNP)
                node.recreation = [nodeInfo[0], nodeInfo[1]]
            except Exception as e:
                logging.error("Failed to load node type", exc_info=True)
                return None
        else:
            logging.debug("loading custom node")
            # try for the custom nodes
            for entry, customNodeType in self.customNodeMap.items():
                if type(customNodeType) == dict:
                    for sub_entry, sub_customNodeType in customNodeType.items():
                        if sub_customNodeType[0] == nodeClassName:
                            nodeType = sub_customNodeType[1]
                else:
                    if customNodeType[0] == nodeClassName:
                        nodeType = customNodeType[1]
            if nodeType is None:
                logging.error(f"couldn't add unknown node type: {nodeType}")
            else:
                logging.debug(f"found Node type: {nodeType}")
            try:
                node = nodeType(self.nodeViewNP)
            except Exception as e:
                logging.error("Failed to load node type", exc_info=True)
                return None

        self.nodeList.append(node)
        base.messenger.send("NodeEditor_set_dirty")
        return node

    def findInNodeMap(self, typeName, nodemap):
        for nodeName, nodeInfo in nodemap.items():
            if type(nodeInfo) == dict:
                ni = self.findInNodeMap(typeName, nodeInfo)
                if ni is not None:
                    return ni
            elif nodeInfo[0] == typeName:
                return nodeInfo
        return None

    def addNode(self, nodeType):
        """Create a node of the given type"""
        self.deselectAll()
        node = None
        if isinstance(nodeType, list):
            node = nodeType[0](nodeType[1], self.nodeViewNP)
            node.typeName = node.typeName
            node.recreation = [nodeType[0], nodeType[1]]
        elif isinstance(nodeType, str):
            node = eval(nodeType + ".Node")(self.nodeViewNP)
        else:
            node = nodeType(self.nodeViewNP)
        node.create()
        self.nodeList.append(node)
        base.messenger.send("NodeEditor_set_dirty")
        return node

    def removeNode(self, selectedNodes=[]):
        """Remove all selected nodes"""
        if selectedNodes == []:
            selectedNodes = self.selectedNodes
        for node in selectedNodes:
            for connector in self.connections[:]:
                if connector.socketA.node is node or connector.socketB.node is node:
                    connector.disconnect()
                    self.connections.remove(connector)
                    # Update logic of the disconnected existing socket node
                    if connector.socketA.node is node:
                        connector.socketB.node.logic()
                    else:
                        connector.socketA.node.logic()
            self.nodeList.remove(node)
            node.destroy()
            del node

    def removeAllNodes(self):
        """Remove all nodes and connections that are currently in the editor"""
        # Remove all connections
        for connector in self.connections[:]:
            connector.disconnect()
            self.connections.remove(connector)

        # Remove all nodes
        for node in self.nodeList[:]:
            self.nodeList.remove(node)
            node.destroy()
            del node

        base.messenger.send("NodeEditor_set_clean")

    def selectNode(self, node, selected, addToSelection=False, deselectOthersIfUnselected=False):
        """Select or deselect the given node according to the boolean value in selected.
        If addToSelection is set, other nodes currently selected are not deselected.
        If deselectOthersIfUnselected is set, other nodes will be deselected if the given node
        is not yet selected"""
        # check if we want to add to the current selection
        if not addToSelection:
            if deselectOthersIfUnselected:
                if not node.selected:
                    self.deselectAll(node)
            else:
                self.deselectAll(node)

        # check if we want to select or deselect the node
        if selected:
            # Select
            # Only select if it's not already selected
            if node not in self.selectedNodes:
                node.select(True)
                self.selectedNodes.append(node)
        else:
            # Deselect
            node.select(False)
            self.selectedNodes.remove(node)

    def deselectAll(self, excludedNode=None):
        """Deselect all nodes"""
        for node in self.nodeList:
            if node is excludedNode: continue
            node.select(False)
        self.selectedNodes = []

    def copyNodes(self):
        """Copy all selected nodes (light copies) and start dragging
        with the mouse cursor"""

        if self.selectedNodes == []: return

        # a mapping of old to new nodes
        nodeMapping = {}
        socketMapping = {}

        # create shallow copies of all nodes
        newNodeList = []
        for node in self.selectedNodes:
            if type(node) == NodeBase:
                print(node.recreation)
                newNode = node.recreation[0](node.recreation[1], self.nodeViewNP)
                newNode.recreation = node.recreation
                print(newNode)
            else:
                newNode = type(node)(self.nodeViewNP)
            newNode.show()
            newNode.frame.setPos(node.frame.getPos())
            newNodeList.append(newNode)
            self.nodeList.append(newNode)
            nodeMapping[node] = newNode
            for i in range(len(node.inputList)):
                socketMapping[node.inputList[i]] = newNode.inputList[i]
            for i in range(len(node.outputList)):
                socketMapping[node.outputList[i]] = newNode.outputList[i]

        #TODO: This needs to be extended to connect plugs, also plugs may need to be created!
        # get connections of to be copied nodes
        for connector in self.connections:
            if connector.socketA.node in self.selectedNodes and connector.socketB.node in self.selectedNodes:
                # we have a connection of one of the to be copied nodes
                newNodeA = nodeMapping[connector.socketA.node]
                newNodeB = nodeMapping[connector.socketB.node]

                newSocketA = socketMapping[connector.socketA]
                newSocketB = socketMapping[connector.socketB]

                self.connectPlugs()
                connector = NodeConnector(newSocketA, newSocketB)
                self.connections.append(connector)
                newSocketA.setConnected(True)
                newSocketB.setConnected(True)

        # deselect all nodes
        self.deselectAll()

        # now only select the newly created ones
        for node in newNodeList:
            node.select(True)
            self.selectedNodes.append(node)

        # start the dragging of the new nodes
        dragNode = newNodeList[0]
        dragNode.accept("mouse1-up", dragNode._dragStop)
        dragNode._dragStart(dragNode.frame, None)

        base.messenger.send("NodeEditor_set_dirty")

    #-------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    #-------------------------------------------------------------------
    def setStartPlug(self, plug):
        """Set the start socket for a possible connection"""
        self.startPlug = plug
        self.startSocket = plug.socket

    def setEndPlug(self, plug):
        """Set the end socket for a possible connection"""
        self.endPlug = plug
        self.endSocket = plug.socket

    def cancelPlug(self):
        """A possible connection between two sockets has been canceled"""
        self.startPlug = None
        self.startSocket = None
        self.endPlug = None
        self.endSocket = None

    def disconnectPlug(self, plug):
        for connector in self.connections[:]:
            if connector.hasPlug(plug):
                connector.disconnect()
                self.connections.remove(connector)
                base.messenger.send("NodeEditor_set_dirty")
                return

    def connectPlugs(self, startPlug=None, endPlug=None):
        """Create a line connection between the sockets set in
        self.startSocket and self.endPlug if a connection is possible

        This function will not allow a connection with only one socket
        set, if both sockets are of the same type or on the same node."""

        if startPlug is not None:
            self.startPlug = startPlug
            self.startSocket = startPlug.socket
        if endPlug is not None:
            self.endPlug = endPlug
            self.endSocket = endPlug.socket

        # only do something if we actually have two sockets
        if self.startPlug is None or self.endPlug is None:
            return

        # check if the "IN" socket has no connections otherwise we can't connect
        if (self.startSocket.type == INSOCKET and self.startPlug.connected) \
        or (self.endSocket.type == INSOCKET and self.endPlug.connected):
            # check if this is our connection. If so, we want to disconnect
            for connector in self.connections[:]:
                if connector.connectsPlugs(self.startPlug, self.endPlug):
                    connector.disconnect()
                    self.connections.remove(connector)
                    self.startPlug = None
                    self.startSocket = None
                    self.endPlug = None
                    self.endSocket = None
                    base.messenger.send("NodeEditor_set_dirty")
                    return
            if (self.startSocket.type == INSOCKET and not self.startSocket.allowMultiConnect) \
            or (self.endSocket.type == INSOCKET and not self.endSocket.allowMultiConnect):
                return

        # check if the nodes and types are different, we can't connect
        # a node with itself or an "OUT" type with another "OUT" type.
        # The same applies to "IN" type sockets
        if self.startSocket.node is not self.endSocket.node \
        and self.startSocket.type != self.endSocket.type:
            connector = NodeConnector(self.startPlug, self.endPlug)
            self.connections.append(connector)
            self.startSocket.setConnected(True, self.startPlug)
            self.endSocket.setConnected(True, self.endPlug)
            outSocketNode = self.startSocket.node if self.startSocket.type is OUTSOCKET else self.endSocket.node
            self.startPlug = None
            self.startSocket = None
            self.endPlug = None
            self.endSocket = None
            base.messenger.send("NodeEditor_set_dirty")
            return connector

    def showConnections(self):
        for connector in self.connections:
            connector.show()

    def hideConnections(self):
        for connector in self.connections:
            connector.hide()

    def getConnectionsOfNode(self, node):
        """Returns a list of connections that are connected with the
        given node"""
        connections = []
        for connector in self.connections:
            for socket in node.inputList + node.outputList:
                if connector.socketA is socket \
                or connector.socketB is socket:
                    connections.append(connector)
        return connections

    def getConnectionsOfSocket(self, socket):
        """Returns a list of connections that the given socket is a part
        of"""
        connections = []
        for connector in self.connections:
            if connector.socketA is socket \
            or connector.socketB is socket:
                connections.append(connector)
        return connections

    def updateConnections(self, args=None):
        """Update line positions of all connections"""
        for connector in self.connections:
            connector.update()
