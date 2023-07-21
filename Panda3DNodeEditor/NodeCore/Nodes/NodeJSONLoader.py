#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging
import ast
import json
from dataclasses import dataclass
from Panda3DNodeEditor.NodeCore.Nodes.NodeBase import NodeBase
from Panda3DNodeEditor.NodeCore.Sockets.BoolSocket import BoolSocket
from Panda3DNodeEditor.NodeCore.Sockets.InSocket import InSocket
from Panda3DNodeEditor.NodeCore.Sockets.NumericSocket import NumericSocket
from Panda3DNodeEditor.NodeCore.Sockets.OptionSelectSocket import OptionSelectSocket
from Panda3DNodeEditor.NodeCore.Sockets.TextSocket import TextSocket
from Panda3DNodeEditor.NodeCore.Sockets.ArgumentsSocket import ArgumentsSocket
from Panda3DNodeEditor.NodeCore.Sockets.ListSocket import ListSocket
from Panda3DNodeEditor.NodeCore.Sockets.DictionarySocket import DictionarySocket
from Panda3DNodeEditor.NodeCore.Sockets.OutSocket import OutSocket
from Panda3DNodeEditor.NodeCore.Sockets.OutListSocket import OutListSocket

@dataclass
class NodeMetadata:
    name: str = ""
    category: str = ""
    node: NodeBase = None

class NodeJSONLoader():
    def __init__(self, nodeDefinitionJSONs, socketMap):
        self.nodeMetas = {}
        self.socketMap = socketMap
        self.jsonContent = {}
        for nodeDefinitionJSON in nodeDefinitionJSONs:
            try:
                with open(nodeDefinitionJSON, 'r') as jsonFileContent:
                    jsonFileDict = json.load(jsonFileContent)
                    self.jsonContent["Nodes"] = {
                        **(self.jsonContent["Nodes"] if "Nodes" in self.jsonContent else {}),
                        **(jsonFileDict["Nodes"] if "Nodes" in jsonFileDict else {})}
            except Exception as e:
                logging.exception(
                    "Couldn't load Node definition file {}".format(nodeDefinitionJSON))

        if len(self.jsonContent.keys()) <= 0:
            logging.error("Problems reading definition file(s)")
            return

        for nodeID, definition in self.jsonContent["Nodes"].items():
            self.nodeMetas[nodeID] = NodeMetadata()
            self.nodeMetas[nodeID].name = definition["name"]
            self.nodeMetas[nodeID].category = definition["cat"]

    def __categoryMap(self, category, categoryList, nodeName, nodeDef):
        """Create a new category map part"""
        if len(categoryList) == 0:
            return {category: {nodeName: nodeDef}}
        retMap = {}
        retMap[category] = self.__categoryMap(
            categoryList[0],
            categoryList[1:],
            nodeName,
            nodeDef)
        return retMap

    def __updateMap(self, category, categoryList, nodeMapPart, nodeName, nodeDef):
        """Update the category map part"""
        if len(categoryList) == 0:
            if category in nodeMapPart:
                nodeMapPart[category][nodeName] = nodeDef
            else:
                nodeMapPart[category] = {nodeName: nodeDef}
            return nodeMapPart
        if category in nodeMapPart:
            nodeMapPart[category] = self.__updateMap(
                categoryList[0],
                categoryList[1:],
                nodeMapPart[category],
                nodeName,
                nodeDef
            )
        else:
            nodeMapPart[category] = self.__categoryMap(
                categoryList[0],
                categoryList[1:],
                nodeName,
                nodeDef
            )
        return nodeMapPart

    def getNodeMap(self):
        nodeMap = {}
        for nodeID, meta in self.nodeMetas.items():
            categoryList = meta.category.split(",")

            if categoryList[0] == "" and len(categoryList) == 1:
                # no hierarchy
                nodeMap[meta.name] = [nodeID, [self.loadNode, nodeID]]
            elif categoryList[0] not in nodeMap.keys() and len(categoryList) > 1:
                # deep hierarchy
                nodeMap[categoryList[0]] = self.__categoryMap(
                    categoryList[1],
                    categoryList[2:],
                    meta.name,
                    [nodeID, [self.loadNode, nodeID]]
                )
            elif categoryList[0] not in nodeMap.keys():
                # flat hierarchy
                nodeMap[categoryList[0]] = {meta.name: [nodeID, [self.loadNode, nodeID]]}
            elif len(categoryList) > 1:
                # update deep hierarchy
                nodeMap[categoryList[0]] = self.__updateMap(
                    categoryList[1],
                    categoryList[2:],
                    nodeMap[categoryList[0]],
                    meta.name,
                    [nodeID, [self.loadNode, nodeID]]
                )
            else:
                # update flat hierarchy
                nodeMap[categoryList[0]][meta.name] = [nodeID, [self.loadNode, nodeID]]
        return nodeMap

    def loadNode(self, nodeID, parent):
        for nodeIDInFile, definition in self.jsonContent["Nodes"].items():
            if nodeIDInFile != nodeID:
                continue
            nodeMeta = self.nodeMetas[nodeID]
            nodeMeta.node = NodeBase(nodeMeta.name, parent)
            nodeMeta.node.typeName = nodeID
            if "extraAttr" in definition:
                nodeMeta.node.customAttributes = definition["extraAttr"]

            for outSocket in definition["out"]:
                if type(outSocket) == dict:
                    # out socket type
                    ost = outSocket["type"]
                    if ost == "list":
                        nodeMeta.node.addOut(outSocket["name"], OutListSocket)
                else:
                    nodeMeta.node.addOut(outSocket, OutSocket)

            for inSocket in definition["in"]:
                st = inSocket["type"].lower()
                socketType = None
                extraArgs = None
                if st == "bool":
                    socketType = BoolSocket
                elif st == "in":
                    socketType = InSocket
                elif st == "num":
                    socketType = NumericSocket
                elif st == "option":
                    socketType = OptionSelectSocket
                    extraArgs = [inSocket["options"]]
                elif st == "text":
                    socketType = TextSocket
                elif st == "arguments":
                    socketType = ArgumentsSocket
                    if "argNames" in inSocket:
                        extraArgs = [inSocket["argNames"]]
                elif st == "list":
                    socketType = ListSocket
                elif st == "dict":
                    socketType = DictionarySocket
                elif st in self.socketMap.keys():
                    socketType = self.socketMap[st]
                    if "extraArgs" in inSocket:
                        extraArgs = inSocket["extraArgs"]
                else:
                    logging.error(f"Unknown socket type {st} in {nodeMeta.name}!")
                    continue

                nodeMeta.node.addIn(
                    inSocket["name"],
                    socketType,
                    inSocket["allowMultiConnect"] if "allowMultiConnect" in inSocket else False,
                    extraArgs
                    )
            return nodeMeta.node
