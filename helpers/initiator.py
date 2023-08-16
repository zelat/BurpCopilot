#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from gui.configuration_tab import ConfigurationTab
from gui.tabs import Tabs, ITabImpl
from gui.menu import MenuImpl
from java.util import ArrayList
from threading import Lock

class Initiator():
    def __init__(self, extender):
        self._extender = extender
    
    def init_constants(self):
        self.contributors = ["Federico Dotta", "mgeeky", "Marcin Woloszyn", "jpginc"]
        self._extender.version = 1.5
        self._extender._log = ArrayList()
        self._extender._lock = Lock()

        self._extender.BYPASSSED_STR = "Failed"
        self._extender.IS_ENFORCED_STR = "Not Sure(please configure enforcement detector)"
        self._extender.ENFORCED_STR = "Passed"
        
        self._extender.intercept = 0
        self._extender.lastCookiesHeader = ""
        self._extender.lastAuthorizationHeader = ""

        self._extender.currentRequestNumber = 1
        self._extender.expanded_requests = 0


    def draw_all(self):
        cfg_tab = ConfigurationTab(self._extender)
        cfg_tab.draw()

        tabs = Tabs(self._extender)
        tabs.draw()
    
    def implement_all(self):
        itab = ITabImpl(self._extender)
        menu = MenuImpl(self._extender)

        self._extender._callbacks.registerContextMenuFactory(menu)
        self._extender._callbacks.addSuiteTab(itab)
        self._extender._callbacks.registerHttpListener(self._extender)

    def init_ui(self):
        self._extender._callbacks.customizeUiComponent(self._extender._splitpane)
        self._extender._callbacks.customizeUiComponent(self._extender.logTable)
        self._extender._callbacks.customizeUiComponent(self._extender.scrollPane)
        self._extender._callbacks.customizeUiComponent(self._extender.tabs)
