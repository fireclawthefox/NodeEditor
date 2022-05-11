#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from direct.gui import DirectGuiGlobals as DGG
#DGG.BELOW = "below"

from direct.gui.DirectFrame import DirectFrame
from DirectGuiExtension.DirectMenuItem import DirectMenuItem, DirectMenuItemEntry, DirectMenuItemSubMenu, DirectMenuSeparator
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer


class MenuBar():
    def __init__(self, customNodeMap, customExporterMap):
        screenWidthPx = base.getSize()[0]

        #
        # Menubar
        #
        self.menu_bar = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,screenWidthPx,-12, 12),
            autoUpdateFrameSize=False,
            pos=(0, 0, 0),
            itemMargin=(2,2,2,2),
            parent=base.pixel2d)

        customExporters = []
        if len(customExporterMap) > 0:
            for entry, action in customExporterMap.items():
                customExporters.append(
                    DirectMenuItemEntry(entry, base.messenger.send, ["NodeEditor_customSave", [action]]))
            customExporters.append(DirectMenuSeparator())

        self.file_entries = [
            DirectMenuItemEntry("New", base.messenger.send, ["NodeEditor_new"]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Open", base.messenger.send, ["NodeEditor_load"]),
            DirectMenuItemEntry("Save", base.messenger.send, ["NodeEditor_save"]),
            DirectMenuSeparator(),
            *customExporters,
            DirectMenuItemEntry("Quit", base.messenger.send, ["quit_app"]),
            ]
        self.file = self.__create_menu_item("File", self.file_entries)

        self.view_entries = [
            DirectMenuItemEntry("Zoom In", base.messenger.send, ["NodeEditor_zoom", [True]]),
            DirectMenuItemEntry("Zoom Out", base.messenger.send, ["NodeEditor_zoom", [False]]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Reset Zoom", base.messenger.send, ["NodeEditor_zoom_reset"]),
            ]
        self.view = self.__create_menu_item("View", self.view_entries)

        self.tool_entries = [
            DirectMenuItemEntry("Refresh", base.messenger.send, ["NodeEditor_refreshNodes"]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Copy Nodes", taskMgr.doMethodLater, [0.2, base.messenger.send, "delayedCopyFromMenu", ["NodeEditor_copyNodes"]]),
            DirectMenuItemEntry("Delete Nodes", base.messenger.send, ["NodeEditor_removeNode"]),
            ]
        self.tool = self.__create_menu_item("Tools", self.tool_entries)

        self.node_map = {
            "Math Nodes >":{
                "Numeric Input":"NumericNode",
                "Addition":"AddNode",
                "Divide":"DivideNode",
                "Multiply":"MultiplyNode"},
            "Boolean Nodes >":{
                "Boolean Value":"BoolNode",
                "Boolean And":"BoolAnd",
                "Boolean Or":"BoolOr"},
            "Simple Output":"TestOutNode"
        }
        self.node_map.update(customNodeMap)

        self.nodes_entries = []
        for node_name, node in self.node_map.items():
            if type(node) == str:
                self.nodes_entries.append(
                    DirectMenuItemEntry(
                        node_name, base.messenger.send, ["addNode", [node]]))
            elif type(node) == list:
                self.nodes_entries.append(
                    DirectMenuItemEntry(
                        node_name, base.messenger.send, ["addNode", [node[1]]]))
            elif type(node) == dict:
                sub_entries = []
                for sub_node_name, sub_node in node.items():
                    if type(sub_node) == list:
                        sub_entries.append(
                            DirectMenuItemEntry(
                                sub_node_name,
                                base.messenger.send,
                                ["addNode", [sub_node[1]]]))
                    else:
                        sub_entries.append(
                            DirectMenuItemEntry(
                                sub_node_name,
                                base.messenger.send,
                                ["addNode", [sub_node]]))
                self.nodes_entries.append(
                    DirectMenuItemSubMenu(
                        node_name, sub_entries))

        self.nodes = self.__create_menu_item("Nodes", self.nodes_entries)

        self.menu_bar.addItem(self.file, skipRefresh=True)
        self.menu_bar.addItem(self.view, skipRefresh=True)
        self.menu_bar.addItem(self.tool, skipRefresh=True)
        self.menu_bar.addItem(self.nodes)

    def __create_menu_item(self, text, entries):
        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        sepColor = (0.7, 0.7, 0.7, 1)

        return DirectMenuItem(
            text=text,
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=entries,
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            item_relief=DGG.FLAT,
            item_pad=(0.2, 0.2),
            itemFrameColor=color,
            separatorFrameColor=sepColor,
            popupMenu_frameColor=color,
            highlightColor=color[2])
