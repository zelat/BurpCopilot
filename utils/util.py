#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from javax.swing import SwingUtilities
from gui.table import UpdateTableEDT, LogEntry
from helpers.http import makeMessage, makeRequest, get_cookie_header_from_message, \
    get_authorization_header_from_message, isStatusCodesReturned

reload(sys)

sys.setdefaultencoding('utf8')
sys.path.append("..")


def tool_needs_to_be_ignored(self, toolFlag):
    for i in range(0, self.IFList.getModel().getSize()):
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore spider requests":
            if (toolFlag == self._callbacks.TOOL_SPIDER):
                return True
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore proxy requests":
            if (toolFlag == self._callbacks.TOOL_PROXY):
                return True
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore target requests":
            if (toolFlag == self._callbacks.TOOL_TARGET):
                return True
    return False


def capture_last_cookie_header(self, messageInfo):
    cookies = get_cookie_header_from_message(self, messageInfo)
    if cookies:
        self.lastCookiesHeader = cookies
        # self.fetchCookiesHeaderButton.setEnabled(True)


def capture_last_authorization_header(self, messageInfo):
    authorization = get_authorization_header_from_message(self, messageInfo)
    if authorization:
        self.lastAuthorizationHeader = authorization
        self.fetchAuthorizationHeaderButton.setEnabled(True)


def valid_tool(self, toolFlag):
    return (toolFlag == self._callbacks.TOOL_PROXY or
            (toolFlag == self._callbacks.TOOL_REPEATER and
             self.interceptRequestsfromRepeater.isSelected()))


def handle_304_status_code_prevention(self, messageIsRequest, messageInfo):
    should_prevent = False
    if self.prevent304.isSelected():
        if messageIsRequest:
            requestHeaders = list(self._helpers.analyzeRequest(messageInfo).getHeaders())
            newHeaders = list()
            for header in requestHeaders:
                if not "If-None-Match:" in header and not "If-Modified-Since:" in header:
                    newHeaders.append(header)
                    should_prevent = True
        if should_prevent:
            requestInfo = self._helpers.analyzeRequest(messageInfo)
            bodyBytes = messageInfo.getRequest()[requestInfo.getBodyOffset():]
            bodyStr = self._helpers.bytesToString(bodyBytes)
            messageInfo.setRequest(self._helpers.buildHttpMessage(newHeaders, bodyStr))


def message_not_from_autorize(self, messageInfo):
    return not self.replaceString.getText() in self._helpers.analyzeRequest(messageInfo).getHeaders()


def no_filters_defined(self):
    return self.IFList.getModel().getSize() == 0


def handle_message(self, toolFlag, messageIsRequest, messageInfo):
    if (self.intercept and valid_tool(self, toolFlag) or toolFlag == "BurpCopilot"):
        handle_304_status_code_prevention(self, messageIsRequest, messageInfo)

        if not messageIsRequest:
            if message_not_from_autorize(self, messageInfo):
                if self.ignore304.isSelected():
                    if isStatusCodesReturned(self, messageInfo, ["304", "204"]):
                        return
                checkwithAI(self, messageInfo)


def send_request_to_burpcopilot(self, messageInfo):
    message = makeMessage(self, messageInfo)
    requestResponse = makeRequest(self, messageInfo, message)
    checkwithAI(self, requestResponse)


def checkwithAI(self, messageInfo):
    self.messageInfo = messageInfo
    message = makeMessage(self, messageInfo)
    requestResponse = makeRequest(self, messageInfo, message)

    responseInfo = self._helpers.analyzeResponse(requestResponse.getResponse())
    self._lock.acquire()
    row = self._log.size()
    self.method = self._helpers.analyzeRequest(messageInfo.getRequest()).getMethod()
    self.url = self._helpers.analyzeRequest(requestResponse).getUrl()
    self.status = responseInfo.getStatusCode()
    self.length = len(requestResponse.getResponse())
    self.headers = self._helpers.analyzeRequest(requestResponse).getHeaders()
    self.cookies = [header.split(": ")[1] for header in self.headers if header.startswith("Cookie")]
    self.mimetypes = responseInfo.getInferredMimeType()
    print("currentRequestNumber:", self.currentRequestNumber)
    print("method:", self.method)
    print("url:", self.url)
    print("status:", self.status)
    print("length:", self.length)
    print("MIME type:", self.mimetypes)
    print("cookies:", self.cookies)
    self._log.add(LogEntry(self.currentRequestNumber, self.method, self.url, self.status, self.length, self.mimetypes,
                           self.cookies, self.messageInfo, None, None))

    SwingUtilities.invokeLater(UpdateTableEDT(self, "insert", row, row))
    self.currentRequestNumber = self.currentRequestNumber + 1
    self._lock.release()


def retestAllRequests(self):
    for i in range(self.tableModel.getRowCount()):
        logEntry = self._log.get(self.logTable.convertRowIndexToModel(i))
        handle_message(self, "BURPCOPILOT", False, logEntry._originalrequestResponse)
