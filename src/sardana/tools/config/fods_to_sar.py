#!/usr/bin/env python

""" The sardana transformation tool.
    Syntax:
        python fods_to_sar.py <file.fods>
        
    This tool outputs a sardana XML file from an FODS XML file.
    
    file.xml must be a valid XML file comming from an OpenOffice spreadsheet in FODS format.
"""


import sys, os, types
from lxml import etree

def transform(f):
    directory = os.path.dirname(os.path.abspath(__file__))
    xslt_filename = os.path.join(directory, "FODS_TO_SAR.xslt")
    
    t = etree.XSLT(etree.parse(xslt_filename))
    if type(f) in types.StringTypes:
        doc = etree.parse(f)
    else:
        doc = f
    return t(doc)

def main():
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
        
    filename = sys.argv[1]
    t = transform(filename)
    print etree.tostring(t, pretty_print=True)

if __name__ == "__main__":
    main()
