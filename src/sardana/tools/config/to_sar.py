#!/usr/bin/env python

import sys, types
from lxml import etree

SAR_NS = 'http://sardana.cells.es/client/framework/config'

def transform(f):
    if type(f) in types.StringTypes:
        doc = etree.parse(f)
    else:
        doc = f
    
    root = doc.getroot()
    
    if (root.nsmap.get(None) == SAR_NS) or root.tag.endswith("Sardana"):
        return doc
    
    # it is either a EXCEL XML or a Flat ODS
    if root.nsmap.get('ss'):
        import xls_to_sar
        t = xls_to_sar.transform
    else:
        import fods_to_sar
        t = fods_to_sar.transform
    return t(doc)

def main():
    filename = sys.argv[1]
    t = transform(filename)
    print etree.tostring(t, pretty_print=True)

if __name__ == "__main__":
    main()
