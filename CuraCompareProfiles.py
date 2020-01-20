# -*- coding: utf-8 -*-

# CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
#
# Free to use

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import zipfile

from CuraCompareData import CuraData, CuraDataMerge, CuraDataValue

version = '0.1.0'

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('CuraCompareProfiles.ui', self)
        self.dictA = {}  # loaded curaprofile
        self.dictB = {}

        self.setupTableWidget(self.tableWidget_1)
        self.setupTableWidget(self.tableWidget_2)

        self.curaDataMergeUp = CuraDataMerge()      # merged data for upper table
        self.curaDataMergeDown = CuraDataMerge()    # merged data for lower table
        self.aFileSections = set() # names of files in curaprofile
        self.bFileSections = set() 

        self.setupMessages()
        self.show()

    # Prepare QTableWidgets
    def setupTableWidget(self, tableWidget):
        tableWidget.setRowCount(4)
        tableWidget.setColumnCount(5)
        tableWidget.setColumnWidth(0, 8)
        tableWidget.setColumnWidth(1, 100)
        tableWidget.setColumnWidth(2, 200)
        tableWidget.setColumnWidth(3, 230)
        tableWidget.setColumnWidth(4, 230)
        
        tableWidget.setHorizontalHeaderLabels(("ID", "Section", "Name", "A value", "B value"))
        # set Name column to be resized
        tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    # Message handling
    def setupMessages(self):
        self.pushButtonLoadA.clicked.connect(self.pushButtonLoadAClicked)
        self.pushButtonLoadB.clicked.connect(self.pushButtonLoadBClicked)
        self.pushButtonReloadB.clicked.connect(self.pushButtonReloadBClicked)
        self.pushButtonSwapSections.clicked.connect(self.pushButtonSwapClicked)
        self.actionAbout.triggered.connect(self.showAbout)

    def showAbout(self):
        QMessageBox.about(self, "Simple Cure Profile compare",
                          "Freeeware tool to compare two curaprofile files    \n"
                          "Version " + version+ "\n\n"
                          "Autor: Aleksandar Putic (c) 2020\n\naleksandarpu@gmail.com\n"
                          )

    # handle Shap button
    # swap section names and re-populate tables
    def pushButtonSwapClicked(self):
        if len(self.bFileSections) > 1:
            self.bFileSections = self.bFileSections[1],self.bFileSections[0]
            self.labelFileBSection1.setText(self.bFileSections[0])
            self.labelFileBSection2.setText(self.bFileSections[1])
            self.labelFileBSection1.setToolTip(self.bFileSections[0])
            self.labelFileBSection2.setToolTip(self.bFileSections[1])

        self.showData(self.dictA, self.dictB)

    # select A file
    # enable B file loading when done
    def pushButtonLoadAClicked(self):
        fileName = self.selectCuraProfileFile() # select file
        self.dictA = {}
        if fileName:
            zf = zipfile.ZipFile(fileName) # open as zip archive
            ziplist = zf.infolist()
            self.aFileSections = set()
            # curaprofile contains 2 files
            for info in ziplist:
                # binary to string
                datastr = "".join( chr(x) for x in zf.read(info.filename))
                # add filename to typle
                self.aFileSections = *self.aFileSections, info.filename
                self.dictA[info.filename] = CuraData(datastr) # parse into CuraData class

            # display curaprofile files (sections)
            self.labelFileASection1.setText(self.aFileSections[0])
            self.labelFileASection2.setText(self.aFileSections[1])
            self.labelFileASection1.setToolTip(self.aFileSections[0])
            self.labelFileASection2.setToolTip(self.aFileSections[1])

        self.labelFileNameA.setText(fileName) # display curaprofile file name
        self.labelFileNameA.setToolTip(fileName) # display curaprofile file name
        self.showData(self.dictA, None)
        # enable loading for B file
        self.pushButtonLoadB.setEnabled(True)

    def pushButtonReloadBClicked(self):
        fileName = self.labelFileNameA.getText()
        self.dictB = {}
        self.loadBFile(fileName)

    def pushButtonLoadBClicked(self):
        fileName = self.selectCuraProfileFile()
        self.dictB = {}
        if fileName:
            self.loadBFile(fileName)

    def loadBFile(self, fileName):
        zf = zipfile.ZipFile(fileName)
        ziplist = zf.infolist()
        self.dictB = {}
        self.bFileSections = set() #
        for info in ziplist:
            datastr = "".join( chr(x) for x in zf.read(info.filename))

            self.bFileSections = *self.bFileSections, info.filename
            self.dictB[info.filename] = CuraData(datastr)

        self.labelFileBSection1.setText(self.bFileSections[0])
        self.labelFileBSection2.setText(self.bFileSections[1])
        self.labelFileBSection1.setToolTip(self.bFileSections[0])
        self.labelFileBSection2.setToolTip(self.bFileSections[1])

        self.labelFileNameB.setText(fileName)
        self.labelFileNameB.setToolTip(fileName)
        self.showData(self.dictA, self.dictB)

        # enable Swap button
        self.pushButtonReloadB.setEnabled(True)
        self.pushButtonSwapSections.setEnabled(True)

    def showData(self, adata, bdata):
        # merge data from 2 profiles into CuraDataMerge class
        self.curaDataMergeUp = CuraDataMerge()
        self.curaDataMergeDown = CuraDataMerge()
        if bdata is not None:
            self.curaDataMergeUp.set(adata[self.aFileSections[0]], bdata[self.bFileSections[0]])
            self.curaDataMergeDown.set(adata[self.aFileSections[1]], bdata[self.bFileSections[1]])
        else: # only a file is loaded
            aside = adata[self.aFileSections[0]]
            self.curaDataMergeUp.set(aside, None)
            bside = adata[self.aFileSections[1]]
            self.curaDataMergeDown.set(bside, None)

        # display merged data in tables
        self.fillTable(self.tableWidget_1, self.curaDataMergeUp)
        self.fillTable(self.tableWidget_2, self.curaDataMergeDown)

    # populate QTableWidget from CuraMergeData object
    def fillTable(self, tableWidget, curaDataMerge):
        row = 0
        no = curaDataMerge.getSize()
        tableWidget.setRowCount(no)
        for k, section in curaDataMerge.sections.items():
            for key in sorted(section.keys()):
                v1 = section[key]
            #for k1, v1 in section.items():
                tableWidget.setItem(row, 0, QTableWidgetItem(""))
                tableWidget.setItem(row, 1, QTableWidgetItem("[{}]".format(k)))

                item = QTableWidgetItem(key)
                item.setToolTip(key)
                tableWidget.setItem(row, 2, item)
                if hasattr(v1, 'avalue'):
                    if v1.avalue is not None:
                        item = QTableWidgetItem(v1.avalue)
                        item.setToolTip(v1.avalue)
                        tableWidget.setItem(row, 3, item)
                    else:
                        tableWidget.setItem(row, 3, QTableWidgetItem(""))
                else:
                    tableWidget.setItem(row, 3, QTableWidgetItem(""))
                if hasattr(v1, 'bvalue'):
                    if v1.bvalue is not None:
                        item = QTableWidgetItem(v1.bvalue)
                        item.setToolTip(v1.bvalue)
                        tableWidget.setItem(row, 4, item)
                    else:
                        tableWidget.setItem(row, 4, QTableWidgetItem(""))
                else:
                    tableWidget.setItem(row, 4, QTableWidgetItem(""))

                if k == 'metadata': # separate section by color
                    self.colorRowBackground(tableWidget, row, QtGui.QColor(225,225,153))

                row = row + 1

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
        fd.setNameFilter(("Cura profile files (*.curaprofile)"))
        if fd.exec_() == QtWidgets.QDialog.Accepted:
            filenames = fd.selectedFiles()
            if len(filenames) > 0:
                return filenames[0]
        return None

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    app.exec_()