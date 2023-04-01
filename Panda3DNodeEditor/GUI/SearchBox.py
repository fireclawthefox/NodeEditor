import math
from dataclasses import dataclass, field
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension import DirectGuiHelper as DGH
from panda3d.core import TextNode
from typing import Callable

@dataclass
class SearchBoxEntryData:
    name: str = ""
    tags: list = field(default_factory=list)
    command: Callable = None
    extraArgs: list = field(default_factory=list)


class SearchBoxEntry(DirectButton):
    def __init__(self, parent = None, **kw):
        optiondefs = (
            ('entryData',       None,             None),
           )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        # Initialize superclasses
        DirectButton.__init__(self, parent, **kw)
        # Call option initialization functions
        self.initialiseoptions(SearchBoxEntry)
        if self["entryData"] is not None:
            entryData = self["entryData"]
            self["text"] = f"{entryData.name} - {','.join(entryData.tags)}"
            if entryData.command is not None:
                self["command"] = entryData.command
                self["extraArgs"] = entryData.extraArgs
        self.resetFrameSize()

class SearchBox(DirectObject):
    def __init__(self, numEntriesPerPage=50):
        self.numEntriesPerPage = numEntriesPerPage
        self.allEntries = []
        self.entries = []

        self.baseFrame = DirectFrame(
            frameSize=[-0.5,0.5,-0.5,0.5])
        self.baseBoxSizer = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=False,
            frameColor=(1,0,1,1))
        self.baseAutoSizer = DirectAutoSizer(
            self.baseFrame,
            self.baseBoxSizer)

        entrySize = 0.05
        self.searchEntry = DirectEntry(
            scale=entrySize,
            width=1/entrySize-0.4,
            borderWidth=[0.2,0.2],
            command=self.filter)
        self.baseBoxSizer.addItem(self.searchEntry)
        self.accept(self.searchEntry.guiItem.getTypeEvent(), self.filter)
        self.accept(self.searchEntry.guiItem.getEraseEvent(), self.filter)

        fs = self.baseFrame["frameSize"]
        remSize = self.baseBoxSizer.getRemainingSpace() - 0.1
        self.scrollFrame = DirectScrolledFrame(
            frameSize=[fs[0],fs[1],-remSize,0],
            scrollBarWidth=0.04,
        )
        pos = (0,0,DGH.getRealHeight(self.scrollFrame)/2.0 - 0.04)
        self.scrollFrame.setPos(pos)
        self.nodesBoxSizer = DirectBoxSizer(
            self.scrollFrame.canvas,
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=True,
            frameColor=(0,0,1,1))
        self.baseBoxSizer.addItem(self.scrollFrame)

        self.controlsBoxSizer = DirectBoxSizer(
            orientation=DGG.HORIZONTAL,
            frameColor=(1,0,1,1))
        self.btnPrev = DirectButton(
            text="<",
            text_scale=0.1,
            text_pos=(0,-0.02),
            frameSize = (-0.15, 0.15, -0.05, 0.05),
            borderWidth = (0.01, 0.01),
            command=self.turnPage,
            extraArgs=[-1])
        self.btnNext = DirectButton(
            text=">",
            text_scale=0.1,
            text_pos=(0,-0.02),
            frameSize = (-0.15, 0.15, -0.05, 0.05),
            borderWidth = (0.01, 0.01),
            command=self.turnPage,
            extraArgs=[1])
        self.lblPages = DirectLabel(
            text="0/0",
            text_scale=0.05,
            frameSize = (-0.2, 0.2, -0.04, 0.06))
        self.controlsBoxSizer.addItem(self.btnPrev)
        self.controlsBoxSizer.addItem(self.lblPages)
        self.controlsBoxSizer.addItem(self.btnNext)
        self.baseBoxSizer.addItem(self.controlsBoxSizer)

        self.destroy = self.baseFrame.destroy
        self.show = self.baseFrame.show
        self.hide = self.baseFrame.hide

    def __filterFunc(self, entry):
        fullMatch = True
        for searchText in self.searchTextEntriesLower:
            match = False
            if searchText in entry.name.lower():
                match = True
            for tag in entry.tags:
                if searchText in tag.lower():
                    match = True
            fullMatch = fullMatch and match
        return fullMatch

    def filter(self, args):
        searchTextRaw = self.searchEntry.get()
        searchTextEntries = searchTextRaw.split(" ")
        self.searchTextEntriesLower = []
        for searchTextUpper in searchTextEntries:
            self.searchTextEntriesLower.append(searchTextUpper.lower())
        self.entries = list(filter(self.__filterFunc, self.allEntries))
        self.numPages = math.ceil(len(self.entries) / self.numEntriesPerPage)
        self.currentPage = 0
        self.showEntriesPage(self.currentPage)
        self.lblPages["text"] = f"{self.currentPage+1} / {self.numPages}"

    def setEntries(self, entries=[]):
        self.currentPage = 0
        self.allEntries = entries
        self.entries = entries
        self.numPages = math.ceil(len(self.entries) / self.numEntriesPerPage)
        self.showEntriesPage(self.currentPage)
        self.updatePageCounter()

    def showEntriesPage(self, pageNr):
        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        nbfs = self.baseFrame["frameSize"]
        self.nodesBoxSizer.removeAllItems(removeNodes=True)
        maxWidth = 0
        buttons = []
        s = base.win.getSize()
        aspect = s[1]/s[0]
        for entry in self.entries[pageNr*self.numEntriesPerPage:pageNr*self.numEntriesPerPage+self.numEntriesPerPage]:
            entryWidget = SearchBoxEntry(
                scale=.05,
                frameColor=color,
                frameSize=(nbfs[0]/0.05, nbfs[1]/0.05, -0.5, 1),
                text="Unknown",
                text_align=TextNode.A_left,
                text_fg=(1,1,1,1),
                text_pos=(nbfs[0]/0.05, 0, 0),
                entryData=entry
            )
            textWidth = entryWidget.component("text0").textNode.get_width()
            maxWidth = max(maxWidth, textWidth)
            buttons.append(entryWidget)

        maxWidth = max(nbfs[1]/0.05, maxWidth)
        for button in buttons:
            button["frameSize"] = (nbfs[0]/0.05, maxWidth, -0.5, 1)
            self.nodesBoxSizer.addItem(button, skipRefresh=True)
        self.nodesBoxSizer.refresh()
        self.scrollFrame["canvasSize"] = self.nodesBoxSizer["frameSize"]

    def turnPage(self, direction):
        self.currentPage += direction
        if self.currentPage < 0:
            self.currentPage = 0
        elif self.currentPage > self.numPages-1:
            self.currentPage = self.numPages-1

        self.showEntriesPage(self.currentPage)
        self.updatePageCounter()

    def updatePageCounter(self):
        self.lblPages["text"] = f"{self.currentPage+1} / {self.numPages}"

'''
import random
from direct.showbase.ShowBase import ShowBase
app = ShowBase()
sb = SearchBox()
entries = []
for i in range(200):
    entries.append(SearchBoxEntryData(
        name=f"Node-{i}",
        tags=["P3D", random.choice(["Direct", "Core"])] + [random.choice(["Base", "Header", "Main"])],
        command=sb.destroy
        )
    )
sb.setEntries(entries)
app.run()
'''
