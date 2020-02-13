#######################################################
#  CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
#
# Read parameters added to end of gcode file
# as described in CuraSettingsInjector
# source: https://github.com/tjjfvi/CuraSettingsInjector
#
# Free to use
#######################################################

from CuraCompareData import CuraData


def loadGCodeInjected(fileName):
    # ;****Current settings used*****
    # ;******End of current settings*****
    dict1 = {}
    data = CuraData()

    data.sections['general'] = {}
    data.sections['metadata'] = {}
    data.sections["values"] = {}

    with open(fileName) as file:
        line = file.readline()
        while line.find(';****Current settings used*****') == -1:
            line = file.readline()
            if len(line) == 0:
                return data

        while len(line) > 0:
            line = file.readline()
            if line.find(';******End of current settings*****') != -1:
                break;
            if line.find('; ') == 0:
                line = line[2:]
                key, val = line.split('=')
                dict1[key.strip()] = val.strip()

    data.sections["values"] = dict1

    return data