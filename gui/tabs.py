#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from java.awt.datatransfer import StringSelection
from javax.swing.table import TableRowSorter
from java.awt.event import AdjustmentListener
from java.awt.event import ActionListener
from java.awt.event import MouseAdapter
from javax.swing import JSplitPane
from javax.swing import JMenuItem
from javax.swing import JScrollPane
from javax.swing import JPopupMenu
from javax.swing import JTabbedPane
from javax.swing import JPanel
from java.awt import GridLayout
from java.awt import Toolkit
from java.lang import Math
from javax.swing import JTextArea
from burp import ITab
from burp import IMessageEditorController
from java.net import URL
from thread import start_new_thread

from table import Table, LogEntry


class ITabImpl(ITab):
    def __init__(self, extender):
        self._extender = extender
        self._log = extender._log

    def getTabCaption(self):
        return "BurpCopilot"

    def getUiComponent(self):
        return self._extender._splitpane


class Tabs():
    def __init__(self, extender):
        self._extender = extender
        self._log = extender._log

    def draw(self):
        """  init autorize tabs
        """

        self._extender.logTable = Table(self._extender)

        tableWidth = self._extender.logTable.getPreferredSize().width
        self._extender.logTable.getColumn("ID").setPreferredWidth(Math.round(tableWidth / 25 * 1))
        self._extender.logTable.getColumn("Method").setPreferredWidth(Math.round(tableWidth / 25 * 2))
        self._extender.logTable.getColumn("URL").setPreferredWidth(Math.round(tableWidth / 25 * 12))
        self._extender.logTable.getColumn("Status").setPreferredWidth(Math.round(tableWidth / 25 * 2))
        self._extender.logTable.getColumn("Length").setPreferredWidth(Math.round(tableWidth / 25 * 2))
        self._extender.logTable.getColumn("MIME type").setPreferredWidth(Math.round(tableWidth / 25 * 2))
        self._extender.logTable.getColumn("Cookies").setPreferredWidth(Math.round(tableWidth / 25 * 4))
        self._extender.tableSorter = TableRowSorter(self._extender.tableModel)
        self._extender.logTable.setRowSorter(self._extender.tableSorter)
        self._extender._splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        self._extender._splitpane.setResizeWeight(1)
        self._extender.scrollPane = JScrollPane(self._extender.logTable)
        self._extender._splitpane.setLeftComponent(self._extender.scrollPane)
        self._extender.scrollPane.getVerticalScrollBar().addAdjustmentListener(AutoScrollListener(self._extender))
        self._extender.aicommentsTextArea = JTextArea("", 5, 30)
        self._extender.aicomment_pane = JScrollPane(self._extender.aicommentsTextArea)

        copyURLitem = JMenuItem("Copy URL")
        copyURLitem.addActionListener(CopySelectedURL(self._extender))

        sendRequestMenu = JMenuItem("Send Original Request to Repeater")
        sendRequestMenu.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, True))

        sendRequestMenu2 = JMenuItem("Send Modified Request to Repeater")
        sendRequestMenu2.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, False))

        sendResponseMenu = JMenuItem("Send Responses to Comparer")
        sendResponseMenu.addActionListener(SendResponseComparer(self._extender, self._extender._callbacks))

        # 发送给openai
        send2ChatGPT = JMenuItem("Analysis vulnerability with AI")
        send2ChatGPT.addActionListener(Send2ChatGPT(self._extender, self._extender._callbacks, self._extender._helpers))

        # openai生成payload
        generateRequestByChatGPT = JMenuItem("Generate payload with AI")
        generateRequestByChatGPT.addActionListener(
            GenerateRequestByOpenAI(self._extender, self._extender._callbacks, self._extender._helpers))

        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(DeleteSelectedRequest(self._extender))

        self._extender.menu = JPopupMenu("Popup")
        self._extender.menu.add(sendRequestMenu)
        self._extender.menu.add(sendRequestMenu2)
        self._extender.menu.add(sendResponseMenu)
        self._extender.menu.add(copyURLitem)
        self._extender.menu.add(send2ChatGPT)
        self._extender.menu.add(generateRequestByChatGPT)
        message_editor = MessageEditor(self._extender)

        self._extender.tabs = JTabbedPane()
        self._extender._requestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._responseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._airequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._airesponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender.original_requests_tabs = JTabbedPane()
        self._extender.original_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.original_requests_tabs.addTab("AI Modified Request",
                                                     self._extender._airequestViewer.getComponent())
        # self._extender.original_requests_tabs.addTab("AI Modified Response",
        #                                              self._extender._airesponseViewer.getComponent())
        # self._extender.original_requests_tabs.addTab("AI Comments", None)
        self._extender.original_requests_tabs.setSelectedIndex(0)

        self._extender.modified_requests_tabs = JTabbedPane()
        self._extender.modified_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.modified_requests_tabs.addTab("Request", self._extender._requestViewer.getComponent())
        self._extender.modified_requests_tabs.addTab("Response", self._extender._responseViewer.getComponent())
        self._extender.modified_requests_tabs.addTab("AI Comments", self._extender.aicomment_pane)
        self._extender.modified_requests_tabs.setSelectedIndex(0)

        self._extender.requests_panel = JPanel(GridLayout(2, 0))
        self._extender.requests_panel.add(self._extender.modified_requests_tabs)
        self._extender.requests_panel.add(self._extender.original_requests_tabs)

        self._extender.tabs.addTab("Request/Response Viewers", self._extender.requests_panel)

        self._extender.tabs.addTab("Configuration", self._extender._cfg_splitpane)
        self._extender.tabs.setSelectedIndex(1)
        self._extender._splitpane.setRightComponent(self._extender.tabs)


class Send2ChatGPT(ActionListener):
    def __init__(self, extender, callbacks, helpers):
        self._extender = extender
        self._callbacks = callbacks
        self._helpers = helpers

    def actionPerformed(self, e):
        messageInfo = self._extender._currentlyDisplayedItem._requestResponse
        start_new_thread(self.async_send_to_openai, (messageInfo,))

    def async_send_to_openai(self, message_info):
        # 获取OPENAI配置
        OPENAI_KEY = self._extender.KEYTRType.getText()
        MODEL = self._extender.IFType.getSelectedItem()
        TEMP = self._extender.TEMTRType.getSelectedItem()

        request = message_info.getRequest()
        response = message_info.getResponse()
        # 打印请求
        request_info = self._helpers.analyzeRequest(request)
        headers_list = request_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        request_body_bytes = bytearray(request[request_info.getBodyOffset():])
        request_str = headers_str + '\n' + request_body_bytes.decode('utf-8')
        print("Request:")
        print(request_str)

        # 打印响应
        response_info = self._helpers.analyzeResponse(response)
        headers_list = response_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        response_body_bytes = bytearray(response[response_info.getBodyOffset():])
        response_str = headers_str + '\n' + response_body_bytes.decode('utf-8')
        print("Response:")
        print(response_str)
        prompt_template = (
            '请分析以下HTTP请求和响应的潜在安全漏洞，特别关注OWASP十大漏洞，如SQL注入、XSS、CSRF等常见的web应用程序安全威胁,\n'
            '将你的回答格式为一个项目列表，每个点列出一个漏洞名称和简要描述，格式如下::\n'
            '-- 漏洞名称:对漏洞的简要描述,排除无关信息\n'
            '=== Request ===\n'
            '```{request_str}```\n'
            '=== Response ===\n'
            '```{response_str}```\n'
        )

        prompt = prompt_template.format(request_str=request_str, response_str=response_str)

        # 设置OpenAI API的URL
        OPENAI_URL = 'https://api.openai.com/v1/chat/completions'

        # 设置所需的认证令牌
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + OPENAI_KEY
        }

        # 构建发送到OpenAI API所需的数据
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": MODEL,
            "temperature": TEMP
        }

        java_url = URL(OPENAI_URL)
        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.write(json.dumps(payload).encode('utf-8'))
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        input_stream = connection.getInputStream()
        response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
        jsonresult = json.loads(response_body)
        content = jsonresult["choices"][0]["message"]["content"]
        # 更新到控件中
        self._extender.aicommentsTextArea.setText(content)
        # 更新到LogEntry
        row = self._extender.logTable.getSelectedRow()
        self._extender._log.set(row, LogEntry(id=self._extender.tableModel.getValueAt(row, 0),
                                              method=self._extender.tableModel.getValueAt(row, 1),
                                              url=self._extender.tableModel.getValueAt(row, 2),
                                              status=self._extender.tableModel.getValueAt(row, 3),
                                              length=self._extender.tableModel.getValueAt(row, 4),
                                              mime_type=self._extender.tableModel.getValueAt(row, 5),
                                              cookies=self._extender.tableModel.getValueAt(row, 6),
                                              requestResponse=message_info, aicomments=content,
                                              modifiedRequest=self._extender._airequestViewer.getMessage()))


class GenerateRequestByOpenAI(ActionListener):
    def __init__(self, extender, callbacks, helpers):
        self._extender = extender
        self._callbacks = callbacks
        self._helpers = helpers

    def actionPerformed(self, e):
        messageInfo = self._extender._currentlyDisplayedItem._requestResponse
        start_new_thread(self.async_generate_request, (messageInfo,))

    def async_generate_request(self, message_info):
        # 获取OPENAI配置
        OPENAI_KEY = self._extender.KEYTRType.getText()
        MODEL = self._extender.IFType.getSelectedItem()
        TEMP = self._extender.TEMTRType.getSelectedItem()

        request = message_info.getRequest()
        response = message_info.getResponse()
        # 打印请求
        request_info = self._helpers.analyzeRequest(request)
        headers_list = request_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        request_body_bytes = bytearray(request[request_info.getBodyOffset():])
        request_str = headers_str + '\n' + request_body_bytes.decode('utf-8')
        print("Request:")
        print(request_str)

        # 打印响应
        response_info = self._helpers.analyzeResponse(response)
        headers_list = response_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        response_body_bytes = bytearray(response[response_info.getBodyOffset():])
        response_str = headers_str  # + '\n' + response_body_bytes.decode('utf-8')
        print("Response:")
        print(response_str)
        prompt_template = (
            '请分析以下HTTP请求和响应的潜在安全漏洞，特别关注OWASP十大漏洞，如SQL注入、XSS、CSRF等常见的web应用程序安全威胁,\n'
            '请根据以下的Request生成一个新的Reqest来测试是否存在安全漏洞, 你的输出为新的Request,该输出将直接在BurpSuite中发送, 且输出中不能带有中文.\n'
            '=== Request ===\n'
            '{request_str}\n'
        )

        prompt = prompt_template.format(request_str=request_str, response_str=response_str)

        # 设置OpenAI API的URL
        OPENAI_URL = 'https://api.openai.com/v1/chat/completions'

        # 设置所需的认证令牌
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + OPENAI_KEY
        }

        # 构建发送到OpenAI API所需的数据
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": MODEL,
            "temperature": TEMP
        }

        java_url = URL(OPENAI_URL)
        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.write(json.dumps(payload).encode('utf-8'))
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        input_stream = connection.getInputStream()
        response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
        jsonresult = json.loads(response_body)
        content = jsonresult["choices"][0]["message"]["content"]
        # 更新到控件中
        self._extender._airequestViewer.setMessage(content, True)
        # 更新到LogEntry
        row = self._extender.logTable.getSelectedRow()
        self._extender._log.set(row, LogEntry(id=self._extender.tableModel.getValueAt(row, 0),
                                              method=self._extender.tableModel.getValueAt(row, 1),
                                              url=self._extender.tableModel.getValueAt(row, 2),
                                              status=self._extender.tableModel.getValueAt(row, 3),
                                              length=self._extender.tableModel.getValueAt(row, 4),
                                              mime_type=self._extender.tableModel.getValueAt(row, 5),
                                              cookies=self._extender.tableModel.getValueAt(row, 6),
                                              requestResponse=message_info, aicomments=self._extender.aicommentsTextArea.getText(),
                                              modifiedRequest=content))

class SendRequestRepeater(ActionListener):
    def __init__(self, extender, callbacks, original):
        self._extender = extender
        self._callbacks = callbacks
        self.original = original

    def actionPerformed(self, e):
        if self.original:
            request = self._extender._currentlyDisplayedItem._originalrequestResponse
        else:
            request = self._extender._currentlyDisplayedItem._requestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize")

class SendResponseComparer(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        originalResponse = self._extender._currentlyDisplayedItem._originalrequestResponse
        modifiedResponse = self._extender._currentlyDisplayedItem._requestResponse
        unauthorizedResponse = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse

        self._callbacks.sendToComparer(originalResponse.getResponse())
        self._callbacks.sendToComparer(modifiedResponse.getResponse())
        self._callbacks.sendToComparer(unauthorizedResponse.getResponse())

class DeleteSelectedRequest(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        # TODO: Implement this function.
        pass

class CopySelectedURL(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(
            self._extender._currentlyDisplayedItem._requestResponse).getUrl()))
        clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
        clpbrd.setContents(stringSelection, None)

class AutoScrollListener(AdjustmentListener):
    def __init__(self, extender):
        self._extender = extender

    def adjustmentValueChanged(self, e):
        if self._extender.autoScroll.isSelected():
            e.getAdjustable().setValue(e.getAdjustable().getMaximum())

class MessageEditor(IMessageEditorController):
    def __init__(self, extender):
        self._extender = extender

    def getHttpService(self):
        return self._extender._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._extender._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._extender._currentlyDisplayedItem.getResponse()

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.getComponent().getSelectedIndex() == 2:
            if self._extender.expanded_requests == 0:
                print("==========================")