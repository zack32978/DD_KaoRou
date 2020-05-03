#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, copy
from PySide2.QtWidgets import QWidget, QMainWindow, QGridLayout, QFileDialog, QToolBar,\
        QAction, QDialog, QStyle, QSlider, QLabel, QPushButton, QStackedWidget, QHBoxLayout,\
        QLineEdit, QTableWidget, QAbstractItemView, QTableWidgetItem, QGraphicsTextItem, QMenu,\
        QGraphicsScene, QGraphicsView, QGraphicsDropShadowEffect, QComboBox, QMessageBox, QColorDialog
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QGraphicsVideoItem
from PySide2.QtGui import QIcon, QKeySequence, QFont, QBrush, QColor
from PySide2.QtCore import Qt, QTimer, QEvent, QPoint, Signal, QSizeF, QUrl, QThread
        

def cnt2Time(cnt, interval, value=0):
    '''
    receive int
    return str
    count of interval times -> m:s.ms
    '''
    labels = []
    for i in range(value, cnt + value):
        m, s = divmod(i * interval, 60000)
        s, ms = divmod(s, 1000)
        labels.append(('%s:%02d.%03d' % (m, s, ms))[:-1])
    return labels


class refillVerticalLabel(QThread):
    def __init__(self, value, globalInterval, subtitle, parent=None):
        super(refillVerticalLabel, self).__init__(parent)
        self.value = value - 1
        self.globalInterval = globalInterval
        self.oldInterval = self.globalInterval
        self.subtitle = subtitle

    def setGlobalInterval(self, globalInterval):
        self.globalInterval = globalInterval

    def run(self):
        while 1:
            try:
                scrollValue = self.subtitle.verticalScrollBar().value()
                if scrollValue != self.oldInterval or scrollValue == 0:
                    self.oldInterval = scrollValue
                    refillToken = False
                    for y in range(scrollValue - 3, scrollValue + 47):
                        if not self.subtitle.verticalHeaderItem(y):
                            refillToken = True
                            break
                    if refillToken:
                        for cnt, label in enumerate(cnt2Time(50, self.globalInterval, y)):
                            self.subtitle.setVerticalHeaderItem(y + cnt, QTableWidgetItem(label))
                            time.sleep(0.000001)
            except:
                pass
            time.sleep(0.01)
    

class asyncTable(QThread):
    reconnect = Signal()

    def __init__(self, subtitleDict, globalInterval, duration, subtitle, autoSub, tablePreset, position=0, parent=None):
        super(asyncTable, self).__init__(parent)
        self.subtitleDict = copy.deepcopy(subtitleDict)
        self.globalInterval = globalInterval
        self.duration = duration
        self.subtitle = subtitle
        self.autoSub = autoSub
        self.tablePreset = tablePreset
        self.position = position

    def initSubtitle(self):
#         for x in range(5):
#             for y in range(self.subtitle.rowCount()):
#                 if self.subtitle.rowSpan(y, x) > 1:
#                     self.subtitle.setSpan(y, x, 1, 1)
#                 self.subtitle.setItem(y, x, QTableWidgetItem(''))
#                 self.subtitle.item(y, x).setBackground(QBrush(QColor('#232629')))
#                 time.sleep(0.0001)
        self.subtitle.clearSpans()
        self.subtitle.clear()  # 这两个清空命令 辣鸡！辣鸡！辣鸡！格子多了一调用就崩溃！
        self.subtitle.setRowCount(self.duration // self.globalInterval + 1)  # 重置表格行数

#         for t in self.autoSub:  # 重新标记AI识别位置
#             start, delta = t
#             startRow = start // self.globalInterval
#             endRow = startRow + delta // self.globalInterval
#             if self.tablePreset[1]:
#                 for y in range(startRow, endRow):
#                     self.subtitle.setItem(y, 0, QTableWidgetItem(self.tablePreset[0]))
#                 try:
#                     self.subtitle.item(startRow, 0).setBackground(QBrush(QColor('#35545d')))
#                 except:
#                     pass
#                 self.subtitle.setSpan(startRow, 0, endRow - startRow, 1)
#                 if self.tablePreset[0]:
#                     self.subtitleDict[0][start] = [delta, self.tablePreset[0]]
#             else:
#                 for y in range(startRow, endRow):
#                     self.subtitle.setItem(y, 0, QTableWidgetItem(self.tablePreset[0]))
#                     self.subtitle.item(y, 0).setBackground(QBrush(QColor('#35545d')))
#                     if self.tablePreset[0]:
#                         self.subtitleDict[0][y * self.globalInterval] = [self.globalInterval, self.tablePreset[0]]

    def run(self):
        self.initSubtitle()
        for index, subData in self.subtitleDict.items():
            for start, rowData in subData.items():
                startRow = start // self.globalInterval
                deltaRow = rowData[0] // self.globalInterval
                if deltaRow:
                    for row in range(startRow, startRow + deltaRow):
                        if row >= 0:
                            try:
                                self.subtitle.setItem(row, index, QTableWidgetItem(rowData[1]))
                                self.subtitle.item(row, index).setBackground(QBrush(QColor('#35545d')))
                            except:
                                pass
                    if deltaRow > 1:
                        self.subtitle.setSpan(startRow, index, deltaRow, 1)
        time.sleep(0.015)
        row = self.position // self.globalInterval
        self.subtitle.selectRow(row)
        self.subtitle.verticalScrollBar().setValue(row - 10)
        self.reconnect.emit()
