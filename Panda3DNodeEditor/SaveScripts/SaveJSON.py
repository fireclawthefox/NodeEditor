#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
import logging
import tempfile

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser
from Panda3DNodeEditor.Tools.JSONTools import JSONTools

class Save:
    def __init__(self, nodes, connections, exceptionSave=False, filepath=None):
        self.dlgOverwrite = None
        self.dlgOverwriteShadow = None
        self.jsonElements = JSONTools().get(nodes, connections)

        if exceptionSave:
            tmpPath = os.path.join(tempfile.gettempdir(), "NEExceptionSave.logic")
            self.__executeSave(tmpPath)
            logging.info("Wrote crash session file to {}".format(tmpPath))
        else:
            if filepath is None:
                self.browser = DirectFolderBrowser(
                    command=self.save,
                    fileBrowser=True,
                    askForOverwrite=True,
                    defaultFilename="project.logic")
            else:
                self.__executeSave(filepath)

    def save(self, doSave):
        if doSave:
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            self.__executeSave(path)
            base.messenger.send("setLastPath", [path])
        self.browser.destroy()
        del self.browser

    def __executeSave(self, path):
        if self.dlgOverwrite is not None: self.dlgOverwrite.destroy()
        if self.dlgOverwriteShadow is not None: self.dlgOverwriteShadow.destroy()

        with open(path, 'w') as outfile:
            json.dump(self.jsonElements, outfile, indent=2)

        base.messenger.send("NodeEditor_set_clean")
