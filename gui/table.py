#!/usr/bin/env python
# -*- coding: utf-8 -*-

from javax.swing.table import AbstractTableModel
from java.awt.event import MouseAdapter
from java.awt.event import ItemListener
from javax.swing import RowFilter
from javax.swing import JCheckBox
from javax.swing import JTable
from javax.swing import JLabel
from javax.swing import JPanel
from java.lang import Runnable
from java.lang import Integer
from java.lang import String
from java.awt import Color

class TableFilter():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """
        init show tab
        """

        filterLModified = JLabel("Modified:")
        filterLModified.setBounds(10, 10, 100, 30)

        filterLUnauthenticated = JLabel("Unauthenticated:")
        filterLUnauthenticated.setBounds(250, 10, 100, 30)

        self._extender.showAuthBypassModified = JCheckBox(self._extender.BYPASSSED_STR)
        self._extender.showAuthBypassModified.setBounds(10, 35, 200, 30)
        self._extender.showAuthBypassModified.setSelected(True)
        self._extender.showAuthBypassModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthPotentiallyEnforcedModified = JCheckBox("Is enforced???")
        self._extender.showAuthPotentiallyEnforcedModified.setBounds(10, 60, 200, 30)
        self._extender.showAuthPotentiallyEnforcedModified.setSelected(True)
        self._extender.showAuthPotentiallyEnforcedModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthEnforcedModified = JCheckBox(self._extender.ENFORCED_STR)
        self._extender.showAuthEnforcedModified.setBounds(10, 85, 200, 30)
        self._extender.showAuthEnforcedModified.setSelected(True)
        self._extender.showAuthEnforcedModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthBypassUnauthenticated = JCheckBox(self._extender.BYPASSSED_STR)
        self._extender.showAuthBypassUnauthenticated.setBounds(250, 35, 200, 30)
        self._extender.showAuthBypassUnauthenticated.setSelected(True)
        self._extender.showAuthBypassUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthPotentiallyEnforcedUnauthenticated = JCheckBox("Is enforced???")
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.setBounds(250, 60, 200, 30)
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.setSelected(True)
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthEnforcedUnauthenticated = JCheckBox(self._extender.ENFORCED_STR)
        self._extender.showAuthEnforcedUnauthenticated.setBounds(250, 85, 200, 30)
        self._extender.showAuthEnforcedUnauthenticated.setSelected(True)
        self._extender.showAuthEnforcedUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showDisabledUnauthenticated = JCheckBox("Disabled")
        self._extender.showDisabledUnauthenticated.setBounds(250, 110, 200, 30)
        self._extender.showDisabledUnauthenticated.setSelected(True)
        self._extender.showDisabledUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.filterPnl = JPanel()
        self._extender.filterPnl.setLayout(None)
        self._extender.filterPnl.setBounds(0, 0, 1000, 1000)

        self._extender.filterPnl.add(filterLModified)
        self._extender.filterPnl.add(filterLUnauthenticated)
        self._extender.filterPnl.add(self._extender.showAuthBypassModified)
        self._extender.filterPnl.add(self._extender.showAuthPotentiallyEnforcedModified)
        self._extender.filterPnl.add(self._extender.showAuthEnforcedModified)
        self._extender.filterPnl.add(self._extender.showAuthBypassUnauthenticated)
        self._extender.filterPnl.add(self._extender.showAuthPotentiallyEnforcedUnauthenticated)
        self._extender.filterPnl.add(self._extender.showAuthEnforcedUnauthenticated)
        self._extender.filterPnl.add(self._extender.showDisabledUnauthenticated)


class TabTableFilter(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        self._extender.tableSorter.sort()


class TableModel(AbstractTableModel):
    def __init__(self, extender):
        self._extender = extender
        self._log = extender._log

    def getRowCount(self):
        try:
            return self._extender._log.size()
        except:
            return 0

    def getColumnCount(self):
        return 7

    def getColumnName(self, columnIndex):
        data = ['ID', 'Method', 'URL', 'Status', 'Length', "MIME type","Cookies"]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getColumnClass(self, columnIndex):
        data = [Integer, String, String, Integer, Integer, String, String]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._extender._log.get(rowIndex)
        if columnIndex == 0:
            return logEntry._id
        if columnIndex == 1:
            return logEntry._method
        if columnIndex == 2:
            return logEntry._url
        if columnIndex == 3:
            return logEntry._status
        if columnIndex == 4:
            return logEntry._length
        if columnIndex == 5:
            return logEntry._mime_type
        if columnIndex == 6:
            return logEntry._cookies
        return ""


class Table(JTable):
    def __init__(self, extender):
        self._extender = extender
        self._log = extender._log
        self._extender.tableModel = TableModel(extender)
        self.setModel(self._extender.tableModel)
        self.addMouseListener(Mouseclick(self._extender))
        self.getColumnModel().getColumn(0).setPreferredWidth(450)
        self.setRowSelectionAllowed(True)

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        value = self._extender.tableModel.getValueAt(self._extender.logTable.convertRowIndexToModel(row), col)

        if col == 6 or col == 7:
            if value == self._extender.BYPASSSED_STR:
                comp.setBackground(Color(255, 153, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.IS_ENFORCED_STR:
                comp.setBackground(Color(255, 204, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.ENFORCED_STR:
                comp.setBackground(Color(204, 255, 153))
                comp.setForeground(Color.BLACK)
        else:
            comp.setForeground(Color.BLACK)
            comp.setBackground(Color.WHITE)

        selectedRow = self._extender.logTable.getSelectedRow()
        if selectedRow == row:
            comp.setBackground(Color(201, 215, 255))
            comp.setForeground(Color.BLACK)

        return comp

    def changeSelection(self, row, col, toggle, extend):
        # show the log entry for the selected row
        logEntry = self._extender._log.get(self._extender.logTable.convertRowIndexToModel(row))
        self._extender._requestViewer.setMessage(logEntry._requestResponse.getRequest(), True)
        self._extender._responseViewer.setMessage(logEntry._requestResponse.getResponse(), False)
        self._extender._currentlyDisplayedItem = logEntry

        print("ai comment: ", logEntry._aicomments)
        self._extender.aicommentsTextArea.setText(logEntry._aicomments)
        JTable.changeSelection(self, row, col, toggle, extend)

        self._extender._airequestViewer.setMessage(logEntry._modifiedRequest, True)
        JTable.changeSelection(self, row, col, toggle, extend)
        return


class LogEntry:
    def __init__(self, id, method, url, status, length, mime_type, cookies, requestResponse, aicomments, modifiedRequest):
        self._id = id
        self._requestResponse = requestResponse
        self._method = method
        self._url = url
        self._status = status
        self._length = length
        self._mime_type = mime_type
        self._cookies = cookies
        self._aicomments = aicomments
        self._modifiedRequest = modifiedRequest
        return


class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.button == 3:
            self._extender.menu.show(evt.getComponent(), evt.getX(), evt.getY())


class TableRowFilter(RowFilter):
    def __init__(self, extender):
        self._extender = extender


class UpdateTableEDT(Runnable):
    def __init__(self, extender, action, firstRow, lastRow):
        self._extender = extender
        self._action = action
        self._firstRow = firstRow
        self._lastRow = lastRow

    def run(self):
        if self._action == "insert":
            self._extender.tableModel.fireTableRowsInserted(self._firstRow, self._lastRow)
        elif self._action == "update":
            self._extender.tableModel.fireTableRowsUpdated(self._firstRow, self._lastRow)
        elif self._action == "delete":
            self._extender.tableModel.fireTableRowsDeleted(self._firstRow, self._lastRow)
        else:
            print("Invalid action in UpdateTableEDT")

