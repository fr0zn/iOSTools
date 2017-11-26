from collections import OrderedDict
import struct
import xml2dict
import math
import json

file = '''
<dict>                          <!-- dict, level 0 | END! -->
    <string>AAA</string>        <!-- string, level 1 -->
    <boolean>1</boolean>        <!-- bool, level 1 -->

    <string>BBB</string>        <!-- string, level 1 -->
    <boolean>1</boolean>        <!-- bool, level 1 -->

    <dict>                      <!-- dict, level 1 -->
        <string>CCC</string>    <!-- string, level 2 -->
        <boolean>1</boolean>    <!-- bool, level 2 | END! -->
    </dict>

    <string>DDD</string>        <!-- string, level 1 -->
    <boolean>1</boolean>        <!-- bool, level 1 | END! -->
</dict>

'''

class OSSerializeBinary_h():
    kOSSerializeDictionary   = 0x01000000
    kOSSerializeArray        = 0x02000000
    kOSSerializeSet          = 0x03000000
    kOSSerializeNumber       = 0x04000000
    kOSSerializeSymbol       = 0x08000000
    kOSSerializeString       = 0x09000000
    kOSSerializeData         = 0x0a000000
    kOSSerializeBoolean      = 0x0b000000
    kOSSerializeObject       = 0x0c000000
    kOSSerializeTypeMask     = 0x7F000000
    kOSSerializeDataMask     = 0x00FFFFFF
    kOSSerializeEndCollecton = 0x80000000
    # defined
    kOSSerializeBinarySignature = 0x000000d3

class Serialize():
    def __init__(self):
        self.d = [OSSerializeBinary_h.kOSSerializeBinarySignature]
    def parse(self, key, data, end):
        if 'dict' in key:
            self.do(self.dictionary, data, end)
        if 'string' in key:
            self.do(self.string, data, end)
        if 'boolean' in key:
            self.do(self.boolean, data, end)

    def do(self, function, data, end):
        function(data, end)

    def dictionary(self, data, end):
        h = OSSerializeBinary_h.kOSSerializeDictionary
        h ^= OSSerializeBinary_h.kOSSerializeEndCollecton if end else 0x0
        self.d.append(h)

    def string(self, data, end):
        if type(data) == dict or type(data) == OrderedDict:
            try:
                len_s = int(data['@size'],0)
                text  = data['#text']
            except:
                pass
        else:
            len_s = len(data) + 1 # null byte
            text = data
        h = OSSerializeBinary_h.kOSSerializeString
        h ^= len_s
        h ^= OSSerializeBinary_h.kOSSerializeEndCollecton if end else 0x0
        self.d.append(h)
        # Fill the data with nulls, divisible by uint32_t size
        len_fill = int(math.ceil(len(text) / 8.0))
        def nfill(d,l):
            d_m = d
            while len(d_m) != l:
                d_m = d_m + '\x00'
            return d_m
        self.d += list(struct.unpack('<{}I'.format(len_fill),nfill(text, len_fill*4)))

    def boolean(self, data, end):
        h = OSSerializeBinary_h.kOSSerializeBoolean
        h ^= 0x1 if data == "1" else 0x0
        h ^= OSSerializeBinary_h.kOSSerializeEndCollecton if end else 0x0
        self.d.append(h)

    def binary(self):
        return self.d

def pprint(data):
    print json.dumps(data, indent=1)

def _OSSerializeBinary(s,level_data):
    '''Recursion of the parsed dictionary'''
    for index,element in enumerate(level_data):
        # is end if we are in the last element of the list
        is_end = True if index == len(level_data) - 1 else False 
        s.parse(element, level_data[element], end=is_end)
        try:
            _OSSerializeBinary(s, level_data[element])
        except:
            # This is a leaf
            pass

def OSSerializeBinary(xml_content):
    parsed = xml2dict.parse(file)
    s = Serialize()
    _OSSerializeBinary(s, parsed)
    return s.binary()

print file
s = OSSerializeBinary(file)
for i in s:
    print hex(i),

