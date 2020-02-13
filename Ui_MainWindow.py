from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import *
from PyQt5 import uic
from CuraCompareData import CuraDataMerge, CuraData, getAllKeys, findKeyInfo
from LoadGCodeSettings_3 import loadGCodeSettings_3
from LoadGCodeInjected import loadGCodeInjected
import zipfile
import json


groupColumn = 0
nameColumn  = 1
keyColumn   = 2
avalColumn  = 3
bvalColumn  = 4

InfoJsonFileName='fdmprinter.def.json'

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, ver):
        self.version = ver
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('CuraCompareProfiles.ui', self)
        self.CuradataA = CuraData()  # loaded curaprofile
        self.CuradataB = CuraData()
        self.loadInfo(InfoJsonFileName)
        self.AllKeys = getAllKeys(self.infoJson)
        self.showGrouped = False
        self.setupTableWidget(self.tableWidget_1)

        self.curaDataMerge = CuraDataMerge()  # merged data for upper table

        self.setupMessages()
        self.show()

    # Prepare QTableWidgets
    def setupTableWidget(self, tableWidget):
        tableWidget.setRowCount(12)
        tableWidget.setColumnCount(5)
        tableWidget.setColumnWidth(groupColumn, 150)
        tableWidget.setColumnWidth(nameColumn, 200)
        tableWidget.setColumnWidth(keyColumn, 120)
        tableWidget.setColumnWidth(avalColumn, 150)
        tableWidget.setColumnWidth(bvalColumn, 150)

        tableWidget.setHorizontalHeaderLabels(("Group", "Name", "Key", "A value", "B value"))
        # set Name column to be resized
        tableWidget.horizontalHeader().setSectionResizeMode(nameColumn, QtWidgets.QHeaderView.Stretch)

    def loadInfo(self, fileName):
        with open(fileName) as f:
            self.infoJson = json.load(f)
    #        keys = self.infoJson['settings'].keys()
    #        self.infoGroups=[*keys]

    # Message handling
    def setupMessages(self):
        self.pushButtonLoadA.clicked.connect(self.pushButtonLoadAClicked)
        self.pushButtonLoadB.clicked.connect(self.pushButtonLoadBClicked)
        self.pushButtonReloadA.clicked.connect(self.pushButtonReloadAClicked)
        self.pushButtonReloadB.clicked.connect(self.pushButtonReloadBClicked)
        self.actionAbout.triggered.connect(self.showAbout)
        self.radioButton_2.toggled.connect(self.radioButtonClicked)
        self.radioButton.toggled.connect(self.radioButtonClicked)

    def showAbout(self):
        QMessageBox.about(self, "Simple Cure Profile compare",
                          "Freeeware tool to compare two curaprofile files    \n"
                          "Version " + self.version + "\n\n"
                                                 "Autor: Aleksandar Putic (c) 2020\n\naleksandarpu@gmail.com\n"
                          )

    def radioButtonClicked(self):
        radioButton = self.sender()
        if radioButton == self.radioButton_2 :
            if radioButton.isChecked():
                self.showGroupped = True
            else:
                self.showGroupped = False
            self.showData()

    # select A file
    # enable B file loading when done
    def pushButtonLoadAClicked(self):
        fileName, filter = self.selectCuraProfileFile()  # select file
        self.CuradataA = CuraData()
        if fileName:
            self.loadAFile(fileName, filter)

    def pushButtonLoadBClicked(self):
        fileName, filter = self.selectCuraProfileFile()
        self.CuradataB = CuraData()
        if fileName:
            self.loadBFile(fileName, filter)

    def pushButtonReloadAClicked(self):
        fileName = self.labelFileNameA.getText()
        self.CuradataA = CuraData()
        self.loadAFile(fileName)

    def pushButtonReloadBClicked(self):
        fileName = self.labelFileNameB.getText()
        self.CuradataB = CuraData()
        self.loadBFile(fileName)

    def loadAFile(self, fileName, filter):

        if filter.find("CuraSettingsInjector") >= 0:
            curaData = loadGCodeInjected(fileName)
        else:
            if filter.find("Cura gcode settings") >= 0 :
                curaData = loadGCodeSettings_3(fileName)
            else:
                zf = zipfile.ZipFile(fileName)  # open as zip archive
                ziplist = zf.infolist()
                #self.aFileSections = set()

                curaData = CuraData()
                for info in ziplist:    # curaprofile contains 2 files
                    datastr = "".join(chr(x) for x in zf.read(info.filename))   # binary to string
                    curaData.set(datastr)

        self.CuradataA = curaData               # parse into CuraData class

        self.labelFileNameA.setText(fileName)  # display curaprofile file name
        self.labelFileNameA.setToolTip(fileName)  # display curaprofile file name
        self.showData()

        self.pushButtonReloadA.setEnabled(True) # enable reload button
        self.pushButtonLoadB.setEnabled(True)   # enable loading for B file

    def loadBFile(self, fileName, filter):
        if filter.find("CuraSettingsInjector") >= 0:
            curaData = loadGCodeInjected(fileName)
        else:
            if filter.find("Cura gcode settings") >= 0 :
                curaData = loadGCodeSettings_3(fileName)
            else:
                zf = zipfile.ZipFile(fileName)
                ziplist = zf.infolist()
                self.CuradataB = CuraData()
                #self.bFileSections = set()  #
                curaData = CuraData()
                for info in ziplist:
                    datastr = "".join(chr(x) for x in zf.read(info.filename))
                    curaData.set(datastr)

        self.CuradataB = curaData

        self.labelFileNameB.setText(fileName)
        self.labelFileNameB.setToolTip(fileName)
        self.showData()

        self.pushButtonReloadB.setEnabled(True) # enable reload button

    def showData(self):
        # merge data from 2 profiles into CuraDataMerge class
        self.curaDataMerge = CuraDataMerge()
        if self.CuradataB.hasData():
            self.curaDataMerge.set(self.CuradataA, self.CuradataB)
        else:  # only a file is loaded
            self.curaDataMerge.set(self.CuradataA, None)

        # display merged data in tables
        if self.radioButton_2.isChecked():
            self.fillTableGrouped(self.tableWidget_1, self.curaDataMerge)
        else:
            self.fillTable(self.tableWidget_1, self.curaDataMerge)

    # populate QTableWidget from CuraMergeData object
    def fillTable(self, tableWidget, curaDataMerge):
        row = 0
        no = curaDataMerge.getSize()
        tableWidget.setRowCount(no)
        if 'values' in curaDataMerge.sections:
            d = curaDataMerge.sections['values']
            for key in d.keys():
                for gkey in self.AllKeys:
                    if key in self.AllKeys[gkey]:
                        item = QTableWidgetItem(gkey.capitalize())
                        tableWidget.setItem(row, groupColumn, item)
                        break

                # for k1, v1 in section.items():
                info = findKeyInfo(self.infoJson, key)
                if info is not None:
                    item = QTableWidgetItem(info['label'])
                    desc = info['description'].replace('.', '.\n')

                    item.setToolTip(desc.strip())
                    tableWidget.setItem(row, nameColumn, item)
                else:
                    tableWidget.setItem(row, nameColumn, QTableWidgetItem(""))

                self.fillTableValues(row, d, key, tableWidget)
                row = row + 1

    # populate QTableWidget from CuraMergeData object
    def fillTableGrouped(self, tableWidget, curaDataMerge):
        row = 0
        no = curaDataMerge.getSize()
        tableWidget.setRowCount(no)
        if 'values' in curaDataMerge.sections:
            d = curaDataMerge.sections['values']
            for gkey in self.AllKeys:
                for key in self.AllKeys[gkey]:
                    if key not in d:
                        continue

                    item = QTableWidgetItem(gkey.capitalize())
                    tableWidget.setItem(row, groupColumn, item)
                    # for k1, v1 in section.items():
                    info = findKeyInfo(self.infoJson, key)
                    if info is not None:
                        item = QTableWidgetItem(info['label'])
                        desc = info['description'].replace('.', '.\n')

                        item.setToolTip(desc.strip())
                        tableWidget.setItem(row, nameColumn, item)
                    else:
                        tableWidget.setItem(row, nameColumn, QTableWidgetItem(""))

                    self.fillTableValues(row, d, key, tableWidget)

                    row = row + 1

    def fillTableValues(self, row, d, key, tableWidget):
        item = QTableWidgetItem(key)
        item.setToolTip(key)
        tableWidget.setItem(row, keyColumn, item)
        v1 = d[key]
        aval = ''
        bval = ''
        if hasattr(v1, 'avalue'):
            if v1.avalue is not None:
                aval = v1.avalue
                item = QTableWidgetItem(v1.avalue)
                item.setToolTip(v1.avalue)
                item.setTextAlignment(QtCore.Qt.AlignRight)
                tableWidget.setItem(row, avalColumn, item)
            else:
                tableWidget.setItem(row, avalColumn, QTableWidgetItem(""))
        else:
            tableWidget.setItem(row, avalColumn, QTableWidgetItem(""))
        if hasattr(v1, 'bvalue'):
            if v1.bvalue is not None:
                bval = v1.bvalue
                item = QTableWidgetItem(v1.bvalue)
                item.setToolTip(v1.bvalue)
                item.setTextAlignment(QtCore.Qt.AlignRight)
                tableWidget.setItem(row, bvalColumn, item)
            else:
                tableWidget.setItem(row, bvalColumn, QTableWidgetItem(""))
        else:
            tableWidget.setItem(row, bvalColumn, QTableWidgetItem(""))

        if len(aval) == 0 or len(bval) == 0:
            self.colorRowBackground(tableWidget, row, QtGui.QColor(255, 255, 255))
        else:
            if len(aval) > 0 and len(bval) > 0:
                self.colorRowBackground(tableWidget, row, QtGui.QColor(153, 225, 153))
            else:
                self.colorRowBackground(tableWidget, row, QtGui.QColor(153, 0, 0))

        #if k == 'metadata':  # separate section by color
        #    self.colorRowBackground(tableWidget, row, QtGui.QColor(225, 225, 153))

    # set background color for row in QTableWidget
    def colorRowBackground(self, tableWidget, row, color):
        for j in range(tableWidget.columnCount()):
            ti = tableWidget.item(row, j)
            if ti is not None:
                ti.setBackground(color)

    # show FileOpen dialog
    def selectCuraProfileFile(self):
        fd = QtWidgets.QFileDialog()
        fd.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        fd.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        l = "Cura profile files (*.curaprofile);;Cura gcode settings (*.gcode);;CuraSettingsInjector (*.gcode)"

        fd.setNameFilter(l)
        if fd.exec_() == QtWidgets.QDialog.Accepted:
            filenames = fd.selectedFiles()
            filter = fd.selectedNameFilter()
            if len(filenames) > 0:
                return filenames[0], filter
        return None
