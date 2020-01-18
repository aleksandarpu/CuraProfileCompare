import configparser

# CURA (Ultimaker Cura) profile file compare tool
#
# Created by: Aleksandar Putic, 2020
# aleksandarpu@gmali.com
#
# Part of Cura Profile Compare project
# Free to use

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
        self.sections = {} # curaprofile has 'general', 'metadata' and 'values' section

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

# store data loaded from curaprofile internal file
# curaprofile has 3 sections
class CuraData(object):
    def __init__(self):
        self.sections = {}

    def __init__(self, str):
        self.sections = {}
        self.set(str)

    # parse string as ini file (config file)
    # store key/value dictionary for each section in 'ini file'
    def set(self, str):
        Config = configparser.ConfigParser()
        Config.read_string(str)
        if Config.has_section('general'):
            self.sections['general'] = {}
            for x in Config.items('general'):
                self.sections['general'][x[0]] = x[1]
        if Config.has_section('metadata'):
            self.sections['metadata'] = {}
            for x in Config.items('metadata'):
                self.sections['metadata'][x[0]] = x[1]
        if Config.has_section('values'):
            self.sections['values'] = {}
            for x in Config.items('values'):
                self.sections['values'][x[0]] = x[1]

    def hasData(self): # for sanity check
        for key in self.sections:
            if len(self.sections[key]) > 0:
                return True
        return False
