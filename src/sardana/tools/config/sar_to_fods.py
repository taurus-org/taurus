#!/usr/bin/env python

import sys,types
from lxml import etree

def transform(f):
    t = etree.XSLT(etree.parse("SAR_TO_FODS.xslt"))
    if type(f) in types.StringTypes:
        doc = etree.parse(f)
    else:
        doc = f
    return t(doc)

def main():
    filename = sys.argv[1]
    t = transform(filename)
    print etree.tostring(t, pretty_print=True)

if __name__ == "__main__":
    main()
