#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""


from FileBrowser import FileBrowser

class Load:
    def __init__(self, nodeEditor):
        self.nodeEditor = nodeEditor
        self.browser = FileBrowser(self.load, True, defaultFilename="project.json")

    def load(self, doLoad):
        if doLoad:
            self.newProjectCall()
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            self.__executeLoad(path)

        self.browser.destroy()
        del self.browser

    def __executeLoad(self, jsonFile)
        try:
            fileContent = json.load(jsonFile)
        except Exception as e:
            print("Couldn't load project file {}".format(jsonFile))
            print(e)
            return



