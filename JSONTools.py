#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
class JSONTools:
    def get(self, nodes, connections):
        jsonElements = {}
        jsonElements["ProjectVersion"] = "0.1"
        jsonElements["Nodes"] = []
        jsonElements["Connections"] = []

        for node in nodes:
            jsonElements["Nodes"].append(
                {
                    "id":str(node.nodeID),
                    "type":node.__module__,
                    "pos":str(node.frame.getPos()),
                    "inSockets":self.__getSockets(node.inputList),
                    "outSockets":self.__getSockets(node.outputList)
                }
            )

        for connector in connections:
            jsonElements["Connections"].append(
                {
                    "id":str(connector.connectorID),
                    "nodeA_ID":str(connector.socketA.node.nodeID),
                    "nodeB_ID":str(connector.socketB.node.nodeID),
                    "socketA_ID":str(connector.socketA.socketID),
                    "socketB_ID":str(connector.socketB.socketID),
                }
            )
        return jsonElements

    def __getSockets(self, socketList):
        sockets = []
        for socket in socketList:
            if not socket.connected:
                # only store values entered by the user, not by other
                # sockets as they should be recalculated on load
                sockets.append({
                    "id":str(socket.socketID),
                    "value":str(socket.getValue())
                })
            else:
                sockets.append({
                    "id":str(socket.socketID),
                })
        return sockets

