#!/usr/bin/env python
# -*- coding: utf-8 -*-

from burp import IBurpExtender, IHttpListener, ITab, IContextMenuInvocation, IContextMenuFactory
from helpers.initiator import Initiator
from utils.util import handle_message


class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("BurpCopliot")
        initiator = Initiator(self)
        initiator.init_constants()
        initiator.draw_all()
        initiator.implement_all()
        initiator.init_ui()
        return

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        handle_message(self, toolFlag, messageIsRequest, messageInfo)
