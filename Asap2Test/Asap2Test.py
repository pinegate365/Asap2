#!/usr/bin/env python
# -*- coding: UTF-8 -*- 
import os
import sys
import clr
import codecs
from Python.Runtime import PyObjectConversions
from Python.Runtime.Codecs import RawProxyEncoder
from System.IO import (MemoryStream,StreamWriter,StreamReader)
from System.Text import UTF8Encoding
file_path,_ = os.path.split(os.path.realpath(__file__))
clr.AddReference(os.path.join(file_path,'../Asap2/bin/Debug/Asap2.dll'))

from Asap2 import *

source_file = "../testFile.a2l"

# https://github.com/pythonnet/pythonnet/issues/514
class ListAsRawEncoder(RawProxyEncoder):
    __namespace__ = "MyNameSpace"
    def CanEncode(self, clr_type):
        return clr_type.Name == "List`1" and clr_type.Namespace == "System.Collections.Generic"

class ErrorHandler(IErrorReporter):
    __namespace__ = "MyNameSpace"

    def __init__(self):
        self.informations = 0
        self.warnings = 0
        self.errors = 0

    def reportError(self,message):
        self.errors+=1
        print(message)

    def reportWarning(self,message):
        self.warnings+=1
        print(message)

    def reportInformation(self,message):
        self.informations+=1
        print(message)

def main(source_file, dest_file = None):
    list_raw_encoder = ListAsRawEncoder()
    PyObjectConversions.RegisterEncoder(list_raw_encoder)

    errorHandler = ErrorHandler()
    parser = Parser(source_file, errorHandler)
    comment = FileComment(os.linesep + "A2l file for testing ASAP2 parser." + os.linesep, True)
    tree = parser.DoParse()

    if tree is not None:
            if (errorHandler.warnings == 0):
                print("Parsed file with no warnings.")
            else:
                print("Parsed file with {} warnings.".format(errorHandler.warnings))

            errorHandler = ErrorHandler()
            tree.Validate(errorHandler)
            
            if (errorHandler.warnings == 0):
                print("Validated parsed data with no warnings.")
            else:
                print("Validated parsed data with {} warnings.".format(errorHandler.warnings))

            input("Press enter to serialise data.")

            tree.elements.Insert(0, comment)
            ms = MemoryStream()
            stream = StreamWriter(ms, UTF8Encoding(True))
            parser.Serialise(tree, stream)
            ms.Position = 0
            sr = StreamReader(ms)
            myStr = sr.ReadToEnd()
            print(myStr)

            if dest_file is not None:
                # output to the file
                f = codecs.open(dest_file, 'w+', 'utf-8')
                f.write(myStr)
                f.close()

            input("Press enter to close...")
    else:
        print("Parsing failed!")


if __name__ == "__main__":
    dest_file = None
    if len(sys.argv) > 1:
        source_file = sys.argv[1]
    if len(sys.argv) > 2:
        dest_file = sys.argv[2]
    main(source_file, dest_file)