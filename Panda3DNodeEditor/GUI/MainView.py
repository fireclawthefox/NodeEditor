import logging

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame

from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer

from Panda3DNodeEditor.GUI.MenuBar import MenuBar


class MainView():
    def __init__(self, parent, customNodeMap, customExporterMap):
        logging.debug("Setup GUI")

        self.menuBarHeight = 24

        #
        # LAYOUT SETUP
        #

        # the box everything get's added to
        self.main_box = DirectBoxSizer(
            frameColor=(0,0,0,0),
            state=DGG.DISABLED,
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=False)
        # our root element for the main box
        self.main_sizer = DirectAutoSizer(
            frameColor=(0,0,0,0),
            parent=parent,
            child=self.main_box,
            childUpdateSizeFunc=self.main_box.refresh
            )

        # our menu bar
        self.menu_bar_sizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.main_box,
            extendVertical=False)

        # CONNECT THE UI ELEMENTS
        self.main_box.addItem(
            self.menu_bar_sizer,
            updateFunc=self.menu_bar_sizer.refresh,
            skipRefresh=True)

        #
        # CONTENT SETUP
        #
        self.menu_bar = MenuBar(customNodeMap, customExporterMap)
        self.menu_bar_sizer.setChild(self.menu_bar.menu_bar)
        self.menu_bar_sizer["childUpdateSizeFunc"] = self.menu_bar.menu_bar.refresh

        self.main_box.refresh()
