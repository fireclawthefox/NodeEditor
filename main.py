#!/usr/bin/env python
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    loadPrcFileData,
    WindowProperties,
    AntialiasAttrib)
from editorLogHandler import setupLog
from Panda3DNodeEditor.NodeEditor import NodeEditor

loadPrcFileData(
    "",
    """
    sync-video #t
    textures-power-2 none
    window-title Node Editor
    maximized #t
    win-size 1280 720
    """)

setupLog("NodeEditor")

base = ShowBase()

def set_dirty_name():
    wp = WindowProperties()
    wp.setTitle("*Node Editor")
    base.win.requestProperties(wp)

def set_clean_name():
    wp = WindowProperties()
    wp.setTitle("Node Editor")
    base.win.requestProperties(wp)

base.accept("request_dirty_name", set_dirty_name)
base.accept("request_clean_name", set_clean_name)


# Disable the default camera movements
base.disableMouse()

#
# VIEW SETTINGS
#
base.win.setClearColor((0.16, 0.16, 0.16, 1))
render.setAntialias(AntialiasAttrib.MAuto)
render2d.setAntialias(AntialiasAttrib.MAuto)

NodeEditor(base.pixel2d)

base.run()
