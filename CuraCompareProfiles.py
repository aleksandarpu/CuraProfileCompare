# -*- coding: utf-8 -*-

#######################################################
#  CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
#
# Free to use
#######################################################

from PyQt5 import QtWidgets
from Ui_MainWindow import Ui_MainWindow
import sys
import json

from CuraCompareData import CuraData, CuraDataMerge, CuraDataValue
from CuraCompareData import getAllKeys

version = '0.2.0'


# read *.curaprofile
def loadCuraProfile(fileName):
    zf = zipfile.ZipFile(fileName)
    ziplist = zf.infolist()
    dictX = {}
    fileSections = set() #
    for info in ziplist:
        datastr = "".join( chr(x) for x in zf.read(info.filename))

        fileSections = *fileSections, info.filename
        dictX[info.filename] = CuraData()
        dictX[info.filename].set(datastr)
    return fileSections, dictX




if __name__ == "__main__":
    #infoJson = {}
    #with open('fdmprinter.def.json') as f:
    #    infoJson = json.load(f)


    #sections, data = loadGCodeProfile('CFFFP_LCD_dcdc_Ground.gcode')
    #sections, data = loadGCodeSettings('CFFFP_LCD_dcdc_Ground.gcode')
    #sections, data = loadGCodeSettings('CFFFP_Case_Bottom_7.5h.gcode')

    #with open('settings-formated.json') as json_file:
    #    data = json.load(json_file)
    #    print(json.dumps(data, indent=4))
    #    for key in data:
    #        g = data[key]
    #        print(g)

    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow(version)
    app.exec_()