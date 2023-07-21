#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""
from uuid import uuid4
from direct.showbase import ShowBaseGlobal
from direct.directtools.DirectGeometry import LineNodePath

class NodeConnector:
    def __init__(self, plugA, plugB):
        self.connectorID = uuid4()
        self.plugA = plugA
        self.socketA = plugA.socket
        self.plugB = plugB
        self.socketB = plugB.socket
        self.line = LineNodePath(ShowBaseGlobal.aspect2d, thickness=2, colorVec=(0.8,0.8,0.8,1))
        self.draw()

        self.show = self.line.show
        self.hide = self.line.hide

    def update(self):
        self.line.reset()
        self.draw()

    def draw(self):
        self.line.moveTo(self.plugA.getPos(ShowBaseGlobal.aspect2d))
        self.line.drawTo(self.plugB.getPos(ShowBaseGlobal.aspect2d))
        self.line.create()
        self.line.setBin("fixed", 1)

    def has(self, socket):
        """Returns True if one of the sockets this connector connects is
        the given socket"""
        return socket == self.socketA or socket == self.socketB

    def hasPlug(self, plug):
        return plug == self.plugA or plug == self.plugB

    def connects(self, a, b):
        """Returns True if this connector connects socket a and b"""
        return (a == self.socketA or a == self.socketB) and (b == self.socketA or b == self.socketB)

    def connectsPlugs(self, a, b):
        """Returns True if this connector connects plug a and b"""
        return (a == self.plugA or a == self.plugB) and (b == self.plugA or b == self.plugB)

    def disconnect(self):
        self.line.reset()
        self.socketA.setConnected(False, self.plugA)
        self.socketB.setConnected(False, self.plugB)

    def setChecked(self):
        self.line.setColor(0,1,0,1)
        self.update()

    def setError(self, hasError):
        self.line.setColor(1,0,0,1)
        self.update()

    def __str__(self):
        return f"Connection {self.socketA.name} to {self.socketB.name}"
