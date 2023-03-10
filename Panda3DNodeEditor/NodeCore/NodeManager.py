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
    def __init__(self, nodeViewNP=None, defaultNodeMap=None, customNodeMap=None):
        # Node Management
        self.nodeList = []

        # Socket connection Management
        self.connections = []
        self.startSocket = None
        self.endSocket = None

        # Drag and Drop feature
        self.selectedNodes = []

        self.nodeViewNP = nodeViewNP

        self.defaultNodeMap = defaultNodeMap
        self.customNodeMap = customNodeMap

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
            print("CREATE:", nodeType)
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
                        self.updateSocketNodeLogic(connector.socketB)
                    else:
                        self.updateSocketNodeLogic(connector.socketA)
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

        self.updateAllLeaveNodes()

        base.messenger.send("NodeEditor_set_dirty")

    #-------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    #-------------------------------------------------------------------
    def setStartPlug(self, socket):
        """Set the start socket for a possible connection"""
        self.startSocket = socket

    def setEndPlug(self, socket):
        """Set the end socket for a possible connection"""
        self.endSocket = socket

    def cancelPlug(self):
        """A possible connection between two sockets has been canceled"""
        self.startSocket = None
        self.endSocket = None

    def connectPlugs(self, startSocket=None, endSocket=None):
        """Create a line connection between the sockets set in
        self.startSocket and self.endSocket if a connection is possible

        This function will not allow a connection with only one socket
        set, if both sockets are of the same type or on the same node."""

        if startSocket is not None:
            self.startSocket = startSocket
        if endSocket is not None:
            self.endSocket = endSocket

        # only do something if we actually have two sockets
        if self.startSocket is None or self.endSocket is None:
            return

        # check if the "IN" socket has no connections otherwise we can't connect
        if (self.startSocket.type == INSOCKET and self.startSocket.connected) \
        or (self.endSocket.type == INSOCKET and self.endSocket.connected):
            # check if this is our connection. If so, we want to disconnect
            for connector in self.connections[:]:
                if connector.connects(self.startSocket, self.endSocket):
                    connector.disconnect()
                    self.connections.remove(connector)

                    # Update logic of the sockets' nodes
                    self.updateDisconnectedNodesLogic(self.startSocket, self.endSocket)

                    self.startSocket = None
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
            connector = NodeConnector(self.startSocket, self.endSocket)
            self.connections.append(connector)
            self.startSocket.setConnected(True)
            self.endSocket.setConnected(True)
            outSocketNode = self.startSocket.node if self.startSocket.type is OUTSOCKET else self.endSocket.node
            self.updateConnectedNodes(outSocketNode)
            self.startSocket = None
            self.endSocket = None
            base.messenger.send("NodeEditor_set_dirty")
            return connector

    def showConnections(self):
        for connector in self.connections:
            connector.show()

    def hideConnections(self):
        for connector in self.connections:
            connector.hide()

    def updateAllLeaveNodes(self):
        leaves = []
        for node in self.nodeList:
            if node.isLeaveNode():
                leaves.append(node)

        for leave in leaves:
            leave.logic()
            self.updateConnectedNodes(leave)

    def updateDisconnectedNodesLogic(self, socketA, socketB):
        """
        Updates the logic of the nodes of socket A and socket B.
        The respective input plug type sockets value will be set to None.
        """
        # Update logic of out socket node
        outSocketNode = socketA.node if socketA.type is OUTSOCKET else socketB.node
        outSocketNode.logic()
        self.updateConnectedNodes(outSocketNode)

        # Update logic of in socket node
        inSocketNode = socketA.node if socketA.type is INSOCKET else socketB.node
        inSocket = socketA if socketA.type is INSOCKET else socketB
        inSocket.setValue(None)
        inSocketNode.logic()
        self.updateConnectedNodes(inSocketNode)

    def updateSocketNodeLogic(self, socket):
        """Update the logic of the given node and all nodes connected
        down the given"""
        if socket.type is INSOCKET:
            socket.setValue(None)
        socket.node.logic()
        self.updateConnectedNodes(socket.node)

    def updateConnectedNodes(self, leaveNode):
        self.processedConnections = []
        self.startNode = leaveNode
        self.__updateConnectedNodes(leaveNode)

    def __updateConnectedNodes(self, leaveNode):
        """Update logic of all nodes connected the leave nodes
        out sockets recursively down to the last connected node."""
        for connector in self.connections:
            for outSocket in leaveNode.outputList:
                outSock = None
                inSock = None

                if connector.socketA is outSocket:
                    inSock = connector.socketB
                    outSock = connector.socketA
                elif connector.socketB is outSocket:
                    inSock = connector.socketA
                    outSock = connector.socketB
                else:
                    continue

                connector.setChecked()
                outSock.node.logic()
                inSock.setValue(outSock.getValue())
                inSock.node.logic()

                if connector in self.processedConnections:
                    # this connector is leading to a recursion
                    connector.setError(True)
                    continue
                self.processedConnections.append(connector)

                self.__updateConnectedNodes(inSock.node)

                self.processedConnections.remove(connector)

    def updateConnections(self, args=None):
        """Update line positions of all connections"""
        for connector in self.connections:
            connector.update()
