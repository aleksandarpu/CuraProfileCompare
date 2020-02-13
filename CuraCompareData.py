#######################################################
#  CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
#
# CuraData contains dictionary with 3 entries: general, metadata and values
# Each entry is dictionary too
#
# Free to use
#######################################################

import configparser

# after loadinf 2 curaprofile files
# merge values into this object:
# avalue from A file, and bvalue from B file
# isSame is set to True only when both values are same
class CuraDataValue(object):
    def __init__(self):
        self.isSame = False
        self.avalue = None
        self.bvalue = None

    def __init__(self, val, side):
        self.set(val, side)


    def set(self, val, side):
        self.isSame = False
        if side == 'a':
            self.avalue = val
        else:
            self.bvalue = val
        self.setSame()

    # check avalue vs bvalue
    def setSame(self):
        if hasattr(self, 'avalue') and hasattr(self, 'bvalue'):
            if self.avalue is not None and self.bvalue is not None:
                if self.avalue == self.bvalue:
                    self.isSame = True
                    return
        isSame = False

# merge data from 2 curaprofile files
# key point to CuraDataValue object which hold both A and B side values
class CuraDataMerge(object):
    def __init__(self):
        # curaprofile has 'general', 'metadata' and 'values' section
        self.sections = { 'general' : {}, 'metadata' : {}, 'values' : {} }

    def hasData(self): # sanity check. don't use object with no data in it
        if len(self.sections) > 0:
            return True
        return False

    def getSectionsNumber(self):
        return len(self.sections)

    # count all key/value pairs in all sections
    # used to determine QTableWidget row count
    def getSize(self):
        c = 0
        for k in self.sections:
            c = c + len(self.sections[k])
        return c

    # actual data merge
    # adata is dictionary from A file bdata is from B file
    def set(self, adata, bdata):
        # First, insert all data from adata, for all sections
        for key in adata.sections:
            self.setSection(key, adata.sections[key])
        if bdata is None:
            return
        # Second, update exsisting keys with data from B file
        # insert new key/value if key is not exist
        for key in bdata.sections:
            self.updateSection(key, bdata.sections[key])

    # key is section name
    # data is dictionary
    def setSection(self, key, data):
        self.sections[key] = {}
        for k, v in data.items(): # copy key/values - store in CuraDataValue object as avalue
            self.sections[key][k] = CuraDataValue(v, 'a')


    # key is section name
    # data is dictionary
    def updateSection(self, key, data): # data is dictionary, data is B side
        for k, v in data.items():
            if k in self.sections[key]:
                x = self.sections[key][k]
                x.set(v, 'b')
                self.sections[key][k] = x # add bvalue
            else:
                self.sections[key][k] = CuraDataValue(v, 'b') # new key/value

# data is in ini e.g. config foramt stored in string d
# convert this into dictionary gor each section in Config
def configToDict(d):
    Config = configparser.ConfigParser()
    Config.read_string(d)
    result = dict()
    result['general'] = dict();
    result['metadata'] = dict();
    result['values'] = dict();
    if Config.has_section('general'):
        result['general'] = {}
        for x in Config.items('general'):
            result['general'][x[0]] = x[1]
    if Config.has_section('metadata'):
        result['metadata'] = {}
        for x in Config.items('metadata'):
            result['metadata'][x[0]] = x[1]
    if Config.has_section('values'):
        result['values'] = {}
        for x in Config.items('values'):
            result['values'][x[0]] = x[1]

    return result

# store data loaded from curaprofile internal file
# curaprofile has 3 sections
class CuraData(object):
    def __init__(self):
        self.sections = { 'general' : {}, 'metadata' : {}, 'values' : {}}
        self.loaded = False

    def Merge(selfself, dict1, dict2):
        if isinstance(dict1, dict):
            res = { **dict1, **dict2 }
        else:
            res = dict2
        return res

    # parse string as ini file (config file)
    # store key/value dictionary for each section in 'ini file'
    def set(self, str):
        res = configToDict(str)
        self.sections['general'] = res['general']
        self.sections['metadata'] = res['metadata']
        self.sections['values'] = self.Merge(self.sections['values'], res['values'])


    def hasData(self): # for sanity check
        for key in self.sections:
            if len(self.sections[key]) > 0:
                return True
        return False

def findInDict(d, key):
    if key in d:
        return d[key]
    for k in d.keys():
        if isinstance(d[k], dict):
            ret = findInDict(d[k], key)
            if ret is not None:
                return ret

    return None

def findKeyInfo(jsonData, key):
    for k in jsonData['settings'].keys():
        ret = findInDict(jsonData['settings'][k], key)
        if ret is not None:
            return ret;
    return None


def getSubKeys(d):
    keylist = []
    for k in d.keys():
        if isinstance(d[k], dict):
            if k != 'children' and k != 'options':
                keylist.append(k)
            if k != 'options':
                ret = getSubKeys(d[k])
                if ret is not None:
                    if len(ret) > 0:
                        keylist = [*keylist, *ret]

    return keylist

def getAllKeys(jsonData):
    keylist = {}
    for k in jsonData['settings'].keys():
        ret = getSubKeys(jsonData['settings'][k])
        keylist[k] = ret
    return keylist

