#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
from ast import *
import astor
import ast
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
                        self.updateSocketNodeLogic(connector.socketB, connector.plugB)
                    else:
                        self.updateSocketNodeLogic(connector.socketA, connector.plugA)
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

        self.updateAllLeaveNodes()

        base.messenger.send("NodeEditor_set_dirty")

    #-------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    #-------------------------------------------------------------------
    def setStartPlug(self, plug):
        """Set the start socket for a possible connection"""
        print("SET START!", plug)
        self.startPlug = plug
        self.startSocket = plug.socket

    def setEndPlug(self, plug):
        """Set the end socket for a possible connection"""
        print("SET END!", plug)
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

                # Update logic of the sockets' nodes
                self.updateDisconnectedNodesLogic(self.startPlug, self.endPlug)
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

                    # Update logic of the sockets' nodes
                    self.updateDisconnectedNodesLogic(self.startPlug, self.endPlug)

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
            self.updateConnectedNodes(outSocketNode)
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

    def updateAllLeaveNodes(self):
        leaves = []
        for node in self.nodeList:
            if node.isLeaveNode():
                leaves.append(node)

        for leave in leaves:
            leave.logic()
            self.updateConnectedNodes(leave)

    def updateDisconnectedNodesLogic(self, plugA, plugB):
        """
        Updates the logic of the nodes of socket A and socket B.
        The respective input plug type sockets value will be set to None.
        """
        # Update logic of out socket node
        outSocketNode = plugA.socket.node if plugA.socket.type is OUTSOCKET else plugB.socket.node
        outSocketNode.logic()
        self.updateConnectedNodes(outSocketNode)

        # Update logic of in socket node
        inSocketNode = plugA.socket.node if plugA.socket.type is INSOCKET else plugB.socket.node
        inPlug = plugA if plugA.socket.type is INSOCKET else plugB
        print(inPlug.socket)
        print("CALL setValue of SOCKET?")
        inPlug.socket.setValue(inPlug, None)
        inSocketNode.logic()
        self.updateConnectedNodes(inSocketNode)

    def updateSocketNodeLogic(self, socket, plug):
        """Update the logic of the given node and all nodes connected
        down the given"""
        print("UPDATE LOGIC")
        if socket.type is INSOCKET:
            plug.setValue(None)
        socket.node.logic()
        self.updateConnectedNodes(socket.node)

    def updateConnectedNodes(self, leaveNode):
        self.processedConnections = []
        self.startNode = leaveNode
        self.__updateConnectedNodes(leaveNode)

    def __updateConnectedNodes(self, leaveNode):
        """Update logic of all nodes connected the leave nodes
        out sockets recursively down to the last connected node."""
        print("Update leave node")
        for connector in self.connections:
            for outSocket in leaveNode.outputList:
                outSock = None
                outPlug = None
                inSock = None
                inPlug = None

                if connector.socketA is outSocket:
                    inSock = connector.socketB
                    inPlug = connector.plugB
                    outSock = connector.socketA
                    outPlug = connector.plugA
                elif connector.socketB is outSocket:
                    inSock = connector.socketA
                    inPlug = connector.plugA
                    outSock = connector.socketB
                    outPlug = connector.plugB
                else:
                    continue

                connector.setChecked()
                outSock.node.logic()
                print("SETTING VALUE OF PLUG NOE!")
                print("out", outSock.getValue())
                print("in", inSock.getValue())
                print("out sock:", outSock)
                print("in sock:", inSock)
                print("out plug:", outPlug)
                print("in plug:", inPlug)
                inSock.setValue(inPlug, outSock.getValue())
                inSock.node.logic()

                if connector in self.processedConnections:
                    # this connector is leading to a recursion
                    connector.setError(True)
                    continue
                self.processedConnections.append(connector)

                self.__updateConnectedNodes(inSock.node)

                self.processedConnections.remove(connector)

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

    def run_logic(self, args=None):
        print("PYTHON:")

        """
        FunctionDef(
            name='myFunc',
            args=arguments(
                posonlyargs=[],
                args=[arg(arg='a'), arg(arg='b')],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),


            arguments(
                posonlyargs=[],
                args=[arg(arg='a'), arg(arg='b')],
                vararg=arg(arg='kw'),
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=arg(arg='kwargs')


            body=[
                Expr(value=Constant(value=Ellipsis))],
            decorator_list=[])


        Module(
            body=[
                Expr(
                    value=Call(
                        func=Name(
                            id='print',
                            ctx=Load()
                        ),
                        args=[
                            Constant(value='Test')
                        ],
                        keywords=[]
                    )
                )
            ],
        type_ignores=[])


        Call(func=Name(id='print', ctx=Load()),args={Arguments}, keywords=[])
        """
        """
        Module([
            FunctionDef(
                name="MyFunc",
                args=arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]),
                body=[
                    Call(
                        func=Name(
                            id='print',
                            ctx=Load()
                        ),
                        args=[arg("Test")],
                        keywords=[]
                    )],
                decorator_list=[],
                returns=None,
                type_comment="")], [])
        """

        #astString = ast.dump(ast.parse("def myFunc(a, /, b, c:d, e=f, *g, **h):\n\tprint('Test')"))
        astString = self.getASTEval()
        print(astString)
        if astString is None:
            logging.error("No Entry Node found!")
            return
        astTree = eval(astString)
        print(astString)
        print(astTree)
        print(ast.dump(astTree, indent=4))
        ast.fix_missing_locations(astTree)
        print(ast.unparse(astTree))
        #print(self.getPythonScript())
        code = astor.to_source(astTree)
        print("PYTHON CODE:")
        print("")
        print(code)

    def replacePlaceholders(self, node, text):
        self.visitedNodes.append(node)
        print("PLACEHOLDERS ON NODE: ", node)
        print("MY TEXT: ", text)
        for socket in node.inputList:
            placeholderTypes = ["arguments:", "*", "?"]
            placeholders = [f"{socket.name}"]
            for pt in placeholderTypes:
                for placeholder in placeholders[:]:
                    placeholders.append(f"{pt}{placeholder}")
            for i in range(len(placeholders)):
                placeholders[i] = f"{{{placeholders[i]}}}"

            print("SOCKET: ", socket.name)
            print(placeholders)

            socketValue = socket.getValue()
            replText = str(socketValue)
            if type(socketValue) == str:
                replText = f"\"{replText}\""
            isStarred = False
            isOptional = False
            isArguments = False
            for placeholder in placeholders:
                if "*" in placeholder:
                    placeholder.replace("*", "")
                    isStarred = True
                if "?" in placeholder:
                    placeholder.replace("?", "")
                    isOptional = True

                if "arguments:" in placeholder:
                    placeholder.replace("arguments:", "")
                    isArguments = True

                if placeholder not in text:
                    continue

                if isOptional \
                and socket.getValue() == None:
                    replText = ""
                elif isArguments:
                    strValues = []
                    socketValue = socket.getValue()
                    if socketValue is not None:
                        if type(socketValue) == list:
                            for value in socketValue:
                                strValues.append(f"arg(\"{value}\")")
                            replText = ",".join(strValues)
                        else:
                            replText = f"arg(\"{socketValue}\")"
                elif isStarred:
                    strValues = []
                    if socket.getValue() is not None:
                        for value in socket.getValue():
                            strValues.append(str(value))
                    replText = ",".join(strValues)

                print("Replacing '", placeholder, "' with '", replText, "'")
                text = text.replace(placeholder, replText)
                break

        for socket in node.outputList:
            placeholder = f"{{{socket.name}}}"
            connections = self.getConnectionsOfSocket(socket)
            if len(connections) == 0: continue
            # since we only allow one connection per socket on those
            # nodes, we can savely take the first
            connector = connections[0]
            otherSocket = None
            if connector.socketA is socket:
                otherNode = connector.socketB.node
            else:
                otherNode = connector.socketA.node
            #if otherNode not in self.visitedNodes:
            template = self.replacePlaceholders(otherNode, otherNode.customAttributes["py"])
            #else:
            #    template = otherNode.customAttributes["py"]
            text = text.replace(placeholder, template)
        return text

    def getASTEval(self):
        self.visitedNodes = []
        for node in self.nodeList:
            if "isRoot" in node.customAttributes \
            and node.customAttributes["isRoot"]:
                print("FOUND ROOT")
                return self.replacePlaceholders(node, node.customAttributes["py"])

    def getAst(self):
        """Returns the Abstract Syntax Tree representation of this node"""

        pyScript = self.getPythonScript()
        try:
            print(f"pasre:\n{pyScript}")
            self.astRepr = ast.parse(pyScript, type_comments=True)
        except:
            pass

        return self.astRepr
