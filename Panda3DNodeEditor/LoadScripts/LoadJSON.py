#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json

# NOTE: LPoint3f is required for loading the position from json using eval
from panda3d.core import LPoint3f

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser
from uuid import UUID

class Load:
    def __init__(self, nodeMgr):
        self.nodeMgr = nodeMgr
        self.browser = DirectFolderBrowser(self.load, True, defaultFilename="project.json")

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
            print("Couldn't load project file {}".format(path))
            print(e)
            return

        if fileContent is None:
            print("Problems reading file: {}".format(infile))
            return

        # 1. Create all nodes
        jsonNodes = fileContent["Nodes"]
        newNodes = []
        for jsonNode in jsonNodes:
            node = self.nodeMgr.createNode(jsonNode["type"])
            node.nodeID = UUID(jsonNode["id"])
            node.setPos(eval(jsonNode["pos"]))
            for i in range(len(jsonNode["inSockets"])):
                inSocket = jsonNode["inSockets"][i]
                node.inputList[i].socketID = UUID(inSocket["id"])
                if "value" in inSocket:
                    node.inputList[i].setValue(inSocket["value"])
            for i in range(len(jsonNode["outSockets"])):
                outSocket = jsonNode["outSockets"][i]
                node.outputList[i].socketID = UUID(outSocket["id"])
            node.show()
            newNodes.append(node)

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


