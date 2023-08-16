#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import DefaultComboBoxModel
from java.awt.event import ActionListener
from javax.swing import SwingUtilities
from javax.swing import JOptionPane
from javax.swing import JSplitPane
from javax.swing import JComboBox
from javax.swing import JTextArea
from javax.swing import JCheckBox
from javax.swing import JButton
from javax.swing import JPanel
from javax.swing import JLabel

from table import UpdateTableEDT


class ConfigurationTab():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init configuration tab
        """
        AIModels = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613"]
        Temperature = [0.7, 0.8, 0.9, 1.0]
        self._extender.autoScroll = JCheckBox("Auto Scroll")
        self._extender.autoScroll.setBounds(145, 80, 130, 30)

        self._extender.IFLType = JLabel("Models:")
        self._extender.IFLType.setBounds(10, 10, 140, 30)
        self._extender.IFType = JComboBox(AIModels)
        self._extender.IFType.setBounds(110, 10, 430, 30)

        self._extender.KEYLType = JLabel("OpenAI KEY:")
        self._extender.KEYLType.setBounds(10, 50, 140, 30)
        self._extender.KEYTRType = JTextArea("Input OpenAI KEY", 1, 20)
        self._extender.KEYTRType.setBounds(110, 50, 430, 30)

        self._extender.TEMLType = JLabel("Temperature:")
        self._extender.TEMLType.setBounds(10, 90, 140, 30)
        self._extender.TEMTRType = JComboBox(Temperature)
        self._extender.TEMTRType.setBounds(110, 90, 80, 30)

        self.config_pnl = JPanel()
        self.config_pnl.setBounds(0, 0, 1000, 1000)
        self.config_pnl.setLayout(None)
        self.config_pnl.add(self._extender.IFLType)
        self.config_pnl.add(self._extender.IFType)
        self.config_pnl.add(self._extender.KEYLType)
        self.config_pnl.add(self._extender.KEYTRType)
        self.config_pnl.add(self._extender.TEMLType)
        self.config_pnl.add(self._extender.TEMTRType)

        self._extender._cfg_splitpane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        self._extender._cfg_splitpane.setResizeWeight(0.5)
        self._extender._cfg_splitpane.setBounds(0, 0, 1000, 1000)
        self._extender._cfg_splitpane.setLeftComponent(self.config_pnl)

    def startOrStop(self, event):
        if self._extender.startButton.getText() == "Autorize is off":
            self._extender.startButton.setText("Autorize is on")
            self._extender.startButton.setSelected(True)
            self._extender.intercept = 1
        else:
            self._extender.startButton.setText("Autorize is off")
            self._extender.startButton.setSelected(False)
            self._extender.intercept = 0

    def clearList(self, event):
        self._extender._lock.acquire()
        oldSize = self._extender._log.size()
        self._extender._log.clear()
        SwingUtilities.invokeLater(UpdateTableEDT(self._extender, "delete", 0, oldSize - 1))
        self._extender._lock.release()

    def replaceQueryHanlder(self, event):
        if self._extender.replaceQueryParam.isSelected():
            self._extender.replaceString.setText("paramName=paramValue")
        else:
            self._extender.replaceString.setText(self.DEFUALT_REPLACE_TEXT)

    def saveHeaders(self, event):
        savedHeadersTitle = JOptionPane.showInputDialog("Please provide saved headers title:")
        self._extender.savedHeaders.append(
            {'title': savedHeadersTitle, 'headers': self._extender.replaceString.getText()})
        self._extender.savedHeadersTitlesCombo.setModel(DefaultComboBoxModel(self.getSavedHeadersTitles()))
        self._extender.savedHeadersTitlesCombo.getModel().setSelectedItem(savedHeadersTitle)

    def removeHeaders(self, event):
        model = self._extender.savedHeadersTitlesCombo.getModel()
        selectedItem = model.getSelectedItem()
        if selectedItem == "Temporary headers":
            return

        delObject = None
        for savedHeaderObj in self._extender.savedHeaders:
            if selectedItem == savedHeaderObj['title']:
                delObject = savedHeaderObj
        self._extender.savedHeaders.remove(delObject)
        model.removeElement(selectedItem)

    def getSavedHeadersTitles(self):
        titles = []
        for savedHeaderObj in self._extender.savedHeaders:
            titles.append(savedHeaderObj['title'])
        return titles

    def fetchCookiesHeader(self, event):
        if self._extender.lastCookiesHeader:
            self._extender.replaceString.setText(self._extender.lastCookiesHeader)

    def fetchAuthorizationHeader(self, event):
        if self._extender.lastAuthorizationHeader:
            self._extender.replaceString.setText(self._extender.lastAuthorizationHeader)


class SavedHeaderChange(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        selectedTitle = self._extender.savedHeadersTitlesCombo.getSelectedItem()
        headers = [x for x in self._extender.savedHeaders if x['title'] == selectedTitle]
        self._extender.replaceString.setText(headers[0]['headers'])
