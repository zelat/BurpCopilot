#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

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
from thread import start_new_thread

from prompts.prompt_class import ANALYSIS_PROMPT
from table import Table, LogEntry
from utils.logger import Logger
from utils.taskprocess import SingleTaskListStorage, TaskProcess, openai_embedding_call, openai_call
from utils.pinecone_storage import use_pinecone


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
        autonomousPentest = JMenuItem("Generate payload with AI")
        autonomousPentest.addActionListener(AutonomousPentest(self._extender, self._extender._callbacks, self._extender._helpers))

        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(DeleteSelectedRequest(self._extender))

        self._extender.menu = JPopupMenu("Popup")
        self._extender.menu.add(sendRequestMenu)
        self._extender.menu.add(sendRequestMenu2)
        self._extender.menu.add(sendResponseMenu)
        self._extender.menu.add(copyURLitem)
        self._extender.menu.add(send2ChatGPT)
        self._extender.menu.add(autonomousPentest)
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
        start_new_thread(self.async_analysisOrgRequest, (messageInfo,))

    def async_analysisOrgRequest(self, messageInfo):
        conversation_history = {}
        extender = self._extender
        # print("BurpCopilotPrompt.init_session = ", BurpCopilotPrompt.init_session)
        # init_content = sendMessageOpenAI(extender, BurpCopilotPrompt.init_session)
        # 将响应添加到历史记录
        # conversation_history[0] = init_content
        # 将历史记录组合成新的提示
        request = messageInfo.getRequest()
        response = messageInfo.getResponse()
        # 打印请求
        request_info = self._helpers.analyzeRequest(request)
        headers_list = request_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        request_body_bytes = bytearray(request[request_info.getBodyOffset():])
        request_str = headers_str + '\n' + request_body_bytes.decode('utf-8')
        # 打印响应
        response_info = self._helpers.analyzeResponse(response)
        headers_list = response_info.getHeaders()
        headers_str = '\n'.join(headers_list)
        response_body_bytes = bytearray(response[response_info.getBodyOffset():])
        response_str = headers_str # + '\n' + response_body_bytes.decode('utf-8')
        prompt_json = {
                "Question": ANALYSIS_PROMPT,
                "Request": request_str,
                "Response": response_str,
                "Answer": ""
        }
        conversation_history[0] = prompt_json
        conversation_history_string = json.dumps(conversation_history)
        print("conversation_history: ", conversation_history_string)
        content = openai_call(extender, conversation_history_string)
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
                                              requestResponse=messageInfo, aicomments=content,
                                              modifiedRequest=self._extender._airequestViewer.getMessage()))


class AutonomousPentest(ActionListener):
    def __init__(self, extender, callbacks, helpers):
        self._extender = extender
        self._callbacks = callbacks
        self._helpers = helpers

    def actionPerformed(self, e):
        messageInfo = self._extender._currentlyDisplayedItem._requestResponse
        start_new_thread(self.async_autonomousPentest, (messageInfo,))

    def async_autonomousPentest(self, messageInfo):
        extender = self._extender
        helpers = self._helpers
        logger = Logger()
        openai_key = extender.KEYTRType.getText()

        objective = "I want to test web application" # 任务目标
        # content = openai_embedding_call(openai_key, objective)
        # dict2string = json.dumps(content)
        # logger.debug(content)

        # Initialize tasks storage
        tasks_storage = SingleTaskListStorage()
        loop = True
        # 所欲偶的测试结果都存入向量存储
        results_storage = use_pinecone(extender, objective)
        taskprocess = TaskProcess(extender, results_storage, objective)
        while loop:
            # As long as there are tasks in the storage...
            if not tasks_storage.is_empty():
                # Print the task list
                logger.debug("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
                for t in tasks_storage.get_task_names():
                    logger.debug(" • " + str(t))

                # task = tasks_storage.popleft()
                # logger.debug("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
                # logger.debug(str(task["task_name"]))
                #
                # result = taskprocess.execution_agent(objective, str(task["task_name"]))
                # logger.debug("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
                # logger.debug(result)
                #
                # enriched_result = {
                #     "data": result
                # }
                #
                # result_id = "result_{}".format(task['task_id'])
                # results_storage.add(task, result, result_id)
                # new_tasks = taskprocess.task_creation_agent(
                #     objective,
                #     enriched_result,
                #     task["task_name"],
                #     tasks_storage.get_task_names(),
                # )
                #
                # logger.debug('Adding new tasks to task_storage')
                # for new_task in new_tasks:
                #     new_task.update({"task_id": tasks_storage.next_task_id()})
                #     logger.debug(str(new_task))
                #     tasks_storage.append(new_task)
                #
                # prioritized_tasks = taskprocess.prioritization_agent()
                # if prioritized_tasks:
                #     tasks_storage.replace(prioritized_tasks)
                # time.sleep(5)
            else:
                print('Done.')
                loop = False

        # 更新到控件中
        # self._extender._airequestViewer.setMessage(dict2string, True)
        # 更新到LogEntry
        # row = self._extender.logTable.getSelectedRow()
        # self._extender._log.set(row, LogEntry(id=self._extender.tableModel.getValueAt(row, 0),
        #                                       method=self._extender.tableModel.getValueAt(row, 1),
        #                                       url=self._extender.tableModel.getValueAt(row, 2),
        #                                       status=self._extender.tableModel.getValueAt(row, 3),
        #                                       length=self._extender.tableModel.getValueAt(row, 4),
        #                                       mime_type=self._extender.tableModel.getValueAt(row, 5),
        #                                       cookies=self._extender.tableModel.getValueAt(row, 6),
        #                                       requestResponse=messageInfo,
        #                                       aicomments=self._extender.aicommentsTextArea.getText(),
        #                                       modifiedRequest=content))


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
