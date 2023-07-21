from panda3d.core import TransparencyAttrib
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui import DirectGuiGlobals as DGG
from uuid import uuid4

class SocketPlug():
    def __init__(self, socket, parent, prefixes=[], idOverwrite=None, removable=False):
        self.socket = socket
        self.plugID = ":".join(prefixes) + (":" if len(prefixes) > 0 else "") + f"{uuid4()}"
        self.value = None
        self.connected = False
        if idOverwrite:
            # This is used to give this plug a specific ID. For example
            # if we load plugs that already have an ID defined.
            self.plugID = idOverwrite
        self.plugWidget = DirectFrame(
            state = DGG.NORMAL,
            image="icons/Plug.png",
            image_scale=.05,
            frameColor=(0, 0, 0, 0),
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            parent=parent,
        )
        self.btnRemovePlug = None
        if removable:
            self.btnRemovePlug = DirectButton(
                text="-",
                scale=0.1,
                text_fg=(1, 1, 1, 1),
                text_bg=(0, 0, 0, 0),
                frameColor=(0.7, 0.1, 0.1, 1),
                pos=(0.04,0,0.04),
                pad=(0.2, 0.2),
                parent=self.plugWidget,
                relief=DGG.FLAT,
                command=self.socket.removeEntry,
                extraArgs=[self],
            )
        self.plugWidget.setTransparency(TransparencyAttrib.M_multisample)
        self.setupBind()

        self.getPos = self.plugWidget.getPos

    def removePlug(self):
        base.messenger.send("disconnectPlug", [self])
        if self.btnRemovePlug:
            self.btnRemovePlug.removeNode()
        self.plugWidget.removeNode()

    def setValue(self, value):
        self.value = value
        self.socket.update()

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

        # update our socket that our connection value has changed
        self.socket.update()
