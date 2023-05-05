from panda3d.core import TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.gui import DirectGuiGlobals as DGG

class SocketPlug():
    def __init__(self, parent):
        self.plugWidget = DirectFrame(
            state = DGG.NORMAL,
            image="icons/Plug.png",
            image_scale=.05,
            frameColor=(0, 0, 0, 0),
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            parent=parent,
        )
        self.plugWidget.setTransparency(TransparencyAttrib.M_multisample)
        self.setupBind()

    def setupBind(self):
        self.plugWidget.bind(DGG.B1PRESS, self.startPlug)
        self.plugWidget.bind(DGG.B1RELEASE, self.releasePlug)
        self.plugWidget.bind(DGG.ENTER, self.endPlug)

    def startPlug(self, event):
        base.messenger.send("startPlug", [self])
        base.messenger.send("startLineDrawing", [self.plugWidget.getPos(render2d)])

    def endPlug(self, event):
        taskMgr.remove("delayedPlugRelease")
        base.messenger.send("endPlug", [self])
        base.messenger.send("connectPlugs")

    def releasePlug(self, event):
        base.messenger.send("stopLineDrawing")
        taskMgr.doMethodLater(0.2, base.messenger.send, "delayedPlugRelease", extraArgs=["cancelPlug"])

    def setConnected(self, connected):
        self.connected = connected
        if self.connected:
            self.plugWidget["image"] = "icons/PlugConnectedGood.png"
        else:
            self.plugWidget["image"] = "icons/Plug.png"
