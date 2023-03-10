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

@dataclass
class NodeMetadata:
    name: str = ""
    category: str = ""
    node: NodeBase = None

class NodeJSONLoader(NodeBase):
    def __init__(self, nodeDefinitionJSON):
        self.nodeMetas = {}
        self.jsonContent = None
        try:
            with open(nodeDefinitionJSON, 'r') as jsonFileContent:
                self.jsonContent = json.load(jsonFileContent)
        except Exception as e:
            print("Couldn't load Node definition file {}".format(nodeDefinitionJSON))
            print(e)
            return

        if self.jsonContent is None:
            print("Problems reading file: {}".format(infile))
            return

        for nodeID, definition in self.jsonContent["Nodes"].items():
            self.nodeMetas[nodeID] = NodeMetadata()
            self.nodeMetas[nodeID].name = definition["name"]
            self.nodeMetas[nodeID].category = definition["category"]

    def getNodeMap(self):
        nodeMap = {}
        for nodeID, meta in self.nodeMetas.items():
            if meta.category in nodeMap:
                nodeMap[meta.category][meta.name] = [nodeID, [self.loadNode, nodeID]]
            else:
                nodeMap[meta.category] = {meta.name: [nodeID, [self.loadNode, nodeID]]}
        return nodeMap

    def loadNode(self, nodeID, parent):
        for nodeIDInFile, definition in self.jsonContent["Nodes"].items():
            if nodeIDInFile != nodeID:
                continue
            nodeMeta = self.nodeMetas[nodeID]
            nodeMeta.node = NodeBase(nodeMeta.name, parent)
            nodeMeta.node.typeName = nodeID
            nodeMeta.node.pyTemplate = definition["astRepresentation"]

            for outSocket in definition["outSockets"]:
                nodeMeta.node.addOut(outSocket)

            for inSocket in definition["inSockets"]:
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

    #def logic(self):
    #    self.outputList[0].value = self.inputList[0].getValue()

    #def getAst(self):
    #    return ast.Constant(self.inputList[0].getValue())
