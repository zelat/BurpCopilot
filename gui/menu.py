#!/usr/bin/env python
# -*- coding: utf-8 -*-

from burp import IContextMenuFactory
from java.util import LinkedList
from javax.swing import JMenuItem
from java.awt.event import ActionListener
from thread import start_new_thread
from utils.util import send_request_to_burpcopilot


class MenuImpl(IContextMenuFactory):
    def __init__(self, extender):
        self._extender = extender
        self._log = extender._log

    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages()
        if responses > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request&response to BurpCopliot")
            for response in responses:
                requestMenuItem.addActionListener(HandleMenuItems(self._extender, response, "request"))
            ret.add(requestMenuItem)
            return ret
        return None

class HandleMenuItems(ActionListener):
    def __init__(self, extender, messageInfo, menuName):
        self._extender = extender
        self._log = extender._log
        self._menuName = menuName
        self._messageInfo = messageInfo

    def actionPerformed(self, e):
        if self._menuName == "request":
            start_new_thread(send_request_to_burpcopilot, (self._extender, self._messageInfo))
