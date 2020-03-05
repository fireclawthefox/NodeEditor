#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from direct.showbase import ShowBaseGlobal
from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.directtools.DirectGeometry import LineNodePath

class NodeConnector:
    def __init__(self, socketA, socketB):
        self.socketA = socketA
        self.socketB = socketB
        self.line = LineNodePath(ShowBaseGlobal.aspect2d, thickness=2, colorVec=(0.8,0.8,0.8,1))
        self.draw()

    def update(self):
        self.line.reset()
        self.draw()

    def draw(self):
        self.line.moveTo(self.socketA.plug.getPos(ShowBaseGlobal.aspect2d))
        self.line.drawTo(self.socketB.plug.getPos(ShowBaseGlobal.aspect2d))
        self.line.create()

    def has(self, socket):
        return socket == self.socketA or socket == self.socketB

    def connects(self, a, b):
        return (a == self.socketA or a == self.socketB) and (b == self.socketA or b == self.socketB)

    def disconnect(self):
        self.line.reset()
        self.socketA.setConnected(False)
        self.socketB.setConnected(False)
