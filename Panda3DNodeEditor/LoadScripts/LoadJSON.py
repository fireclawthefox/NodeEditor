#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
import logging

# NOTE: LPoint3f is required for loading the position from json using eval
from panda3d.core import LPoint3f

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser
from uuid import UUID

class Load:
    def __init__(self, nodeMgr):
        self.nodeMgr = nodeMgr
        self.browser = DirectFolderBrowser(self.load, True, defaultFilename="project.logic")

    def load(self, doLoad):
        if doLoad:
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            self.__executeLoad(path)

        self.browser.destroy()
        del self.browser

    def __executeLoad(self, path):
        fileContent = None
        try:
            with open(path, 'r') as infile:
                fileContent = json.load(infile)
        except Exception as e:
            logging.exception(f"Couldn't load project file {path}")
            return

        if fileContent is None:
            logging.error(f"Problems reading file: {infile}")
            return

        # 1. Create all nodes
        jsonNodes = fileContent["Nodes"]
        newNodes = []
        hasUnknownNodes = False
        for jsonNode in jsonNodes:
            node = self.nodeMgr.createNode(jsonNode["type"], jsonNode["typeName"])
            if node is None:
                logging.error(f"Couldn't load node of type: {jsonNode['type']} {jsonNode['typeName']}")
                hasUnknownNodes = True
                continue
            node.nodeID = UUID(jsonNode["id"])
            node.setPos(eval(jsonNode["pos"]))
            for i in range(len(jsonNode["inSockets"])):
                # Create all input sockets of this node
                inSocket = jsonNode["inSockets"][i]

                if len(node.inputList) <= i:
                    node.addIn(
                        inSocket["name"],
                        self.nodeMgr.socketMap[inSocket["socketType"]],
                        inSocket["allowMultiConnect"],
                        inSocket["extraArgs"])
                curSocket = node.inputList[i]
                # create sockets' plugs and set their IDs
                for plugIdx in range(inSocket["plugs"]):
                    if plugIdx >= len(curSocket.plugs):
                        # we need to add a plug
                        curSocket.createPlug(curSocket.frame)
                    curSocket.plugs[plugIdx].plugID = inSocket["plugs"][plugIdx]["id"]
                # set the sockets value if it has any
                if "value" in inSocket:
                    curSocket.setValue(inSocket["value"])
                # set the sockets ID
                curSocket.socketID = UUID(inSocket["id"])
            for i in range(len(jsonNode["outSockets"])):
                outSocket = jsonNode["outSockets"][i]
                if len(node.outputList) == i:
                    node.addOut(outSocket["name"])
                node.outputList[i].plugs[0].plugID = outSocket["plugs"][0]["id"]
                node.outputList[i].socketID = UUID(outSocket["id"])
            node.show()
            newNodes.append(node)

        if hasUnknownNodes:
            logging.info("Some nodes could not be loaded. Make sure all node extensions are available.")

        # 2. Connect all nodes
        jsonConnections = fileContent["Connections"]
        for jsonConnection in jsonConnections:
            # we have a connection of one of the to be copied nodes
            nodeA = None
            nodeB = None

            for node in newNodes:
                if node.nodeID == UUID(jsonConnection["nodeA_ID"]):
                    nodeA = node
                elif node.nodeID == UUID(jsonConnection["nodeB_ID"]):
                    nodeB = node

            if nodeA is None or nodeB is None:
                logging.error(f"could not connect nodes: {nodeA} - {nodeB}")
                continue

            socketA = None
            socketB = None
            for socket in nodeA.inputList + nodeA.outputList + nodeB.inputList + nodeB.outputList:
                if socket.socketID == UUID(jsonConnection["socketA_ID"]):
                    socketA = socket
                elif socket.socketID == UUID(jsonConnection["socketB_ID"]):
                    socketB = socket
            self.nodeMgr.connectPlugs(socketA, socketB)

        # 3. Run logic from all leave nodes down to the end
        self.nodeMgr.updateAllLeaveNodes()

        base.messenger.send("NodeEditor_set_clean")

        base.messenger.send("setLastPath", [path])

