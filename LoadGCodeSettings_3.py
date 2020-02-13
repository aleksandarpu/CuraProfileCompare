#######################################################
#  CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
#
# Read parameters added to end of gcode file by Cura
# Rows start with ';SETTINGS_3'
# This can be transformad into json string
#
# Free to use
#######################################################

import json
import configparser
from CuraCompareData import CuraData

# read cura settings from ';SETTINGS_3; block at end of gcode file
def loadGCodeSettings_3(fileName):
    # ;SETTING_3
    data = CuraData()
    data.sections['general'] = {}
    data.sections['metadata'] = {}
    data.sections["values"] = {}

    with open(fileName) as file:
        line = file.readline()
        while line.find(';SETTING_3') == -1:
            line = file.readline()
            if len(line) == 0:
                return data

        jsonstr = ''
        while len(line) > 0:
            if line.find(';SETTING_3') != 0:
                break;
            jsonstr = jsonstr + line[len(';SETTING_3 '):].strip()
            line = file.readline()

        #jsonstr = jsonstr.replace('\\\\n', '\\\n')
        #print(jsonstr)
        jsondata = json.loads(jsonstr)
        print(json.dumps(jsondata, indent=4))
        for key, val in jsondata.items():
            if isinstance(val, list):
                for v in val:
                    v1 = v.replace('\\n', '\n')
                    v2 = v1.replace('\\', '')
                    data.set(v2)
            else:
                v = val.replace('\\n', '\n')

                v1 = v.replace('\\', '')
                data.set(v)
    print(data)

    return data
