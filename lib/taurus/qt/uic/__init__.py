#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""The taurus.qt.uic submodule. It contains uic tools"""

__all__ = ["tau2taurus", "resolve_inheritance"]

__docformat__ = 'restructuredtext'

import os
import sys
import optparse
import lxml.etree

import taurus.qt.qtgui.util
from taurus.qt import Qt

import tau2taurus_map

def print_tau2taurus_map(class_map):
    """
    Prints the dictionary assuming it was built by reading a tau2taurus CSV file
    
    :param class_map: the dictionary containing tau2taurus information
    :type class_map: dict
    """
    for old_mod, v in class_map.items():
        for old_class, data in v.items():
            new_mod, new_class = data
            print "%s.%s -> %s.%s" % (old_mod,old_class,new_mod,new_class) 

def tau2taurus(xml_source):
    """
    Replaces tau occurences with taurus using a CSV table file.
    
    :param xml_source: xml object
    :type xml_source: lxml.etree.Element
    :return: the xml object transformed
    :rtype: lxml.etree.Element
    """
    
    class_map = tau2taurus_map.TAU_2_TAURUS_MAP
    custom_widgets = xml_source.findall(".//customwidget")
    widget_factory = taurus.qt.qtgui.util.TaurusWidgetFactory()
    widget_klasses = widget_factory.getWidgets()
    
    new_custom_widget_name_list = []
    new_custom_widget_node_list = []
    
    for custom_widget in custom_widgets:
        header_node = custom_widget.find("header")
        class_node = custom_widget.find("class")
        extends_node = custom_widget.find("extends")
        header_name = header_node.text
        class_name = class_node.text
        extends_name = extends_node.text
        
        # non tau widget... do nothing
        if not header_name.startswith("tau."):
            new_custom_widget_name_list.append(class_name)
            new_custom_widget_node_list.append(custom_widget)
            continue
        
        mod_dict = class_map.get(header_name)
        if mod_dict is None:
            print("tau module '%s' not found in map_file. Aborting..." % header_name)
            sys.exit(1)
        
        class_info = mod_dict.get(class_name)
        if class_info is None:
            print("tau class '%s' in module '%s' not found in map_file. Aborting..." % (class_name,
                header_name))
            sys.exit(2)
        
        new_class_name = class_info[1]
        new_widget_info = widget_klasses[new_class_name]
        new_mod_name, widget_klass = new_widget_info
        new_super_name = widget_klass.__base__.__name__
        
        print("replacing reference to %s.%s(%s) with %s.%s(%s)" % (header_name, 
            class_name, extends_name, new_mod_name, new_class_name, new_super_name))
    
        if class_name != new_class_name:
            widgets = xml_source.findall(".//widget[@class='%s']" % class_name)
            for widget in widgets:
                print("\treplacing widget %s (%s) with %s" % (class_name, 
                    widget.get("name"), new_class_name))
                widget.set("class", new_class_name)
        
        if new_class_name in new_custom_widget_name_list:
            continue
        
        print("\treplacing customWidget node %s.%s with %s.%s" % (header_name,
            class_name, new_mod_name, new_class_name))
    
        new_custom_widget_node = lxml.etree.Element("customwidget")
        class_node = lxml.etree.SubElement(new_custom_widget_node, "class")
        extends_node = lxml.etree.SubElement(new_custom_widget_node, "extends")
        header_node = lxml.etree.SubElement(new_custom_widget_node, "header")

        header_node.text = new_mod_name
        class_node.text = new_class_name
        extends_node.text = new_super_name
        new_custom_widget_name_list.append(new_class_name)
        new_custom_widget_node_list.append(new_custom_widget_node)

    if len(new_custom_widget_node_list) > 0:
        custom_widgets_node = xml_source.find(".//customwidgets")
        if custom_widgets_node is None:
            ui_node = xml_source.getroot()
            custom_widgets_node = lxml.etree.SubElement(ui_node, "customwidgets")
        custom_widgets_node.clear() # remove all children
        custom_widgets_node.extend(new_custom_widget_node_list)

    return xml_source

def resolve_inheritance(xml_source):
    """
    Resolves custom widget inheritance.
    
    :param xml_source: xml object
    :type xml_source: lxml.etree.Element
    :return: the xml object transformed
    :rtype: lxml.etree.Element
    """
    
    custom_widgets = xml_source.findall(".//customwidget")
    widget_factory = taurus.qt.qtgui.util.TaurusWidgetFactory()
    widget_klasses = widget_factory.getWidgets()
    custom_widget_list = xml_source.xpath(".//customwidget/class/text()")
    
    new_custom_widgets = []
    for custom_widget in custom_widgets:
        class_node = custom_widget.find("class")
        class_name = class_node.text
        if not class_name in widget_klasses:
            continue
        extends_node = custom_widget.find("extends")
        super_name = extends_node.text
        if super_name in custom_widget_list:
            continue
        if super_name in dir(Qt):
            continue
        if super_name not in widget_klasses:
            xml = _build_plain_widget(super_name)
        else:
            module_name, widget_klass = widget_klasses[super_name]
            xml = _build_widget(module_name, widget_klass, widget_klasses, custom_widget_list)
        new_custom_widgets.extend(xml)
    
    if len(new_custom_widgets) > 0:
        custom_widgets_node = xml_source.find(".//customwidgets")
        if custom_widgets_node is None:
            ui_node = xml_source.getroot()
            custom_widgets_node = lxml.etree.SubElement(ui_node, "customwidgets")
        custom_widgets_node.extend(new_custom_widgets)
    return xml_source

def _build_plain_widget(widget_klass_name):
    custom_widget_node = lxml.etree.Element("customwidget")
    ret = [ custom_widget_node ]
    class_node = lxml.etree.SubElement(custom_widget_node, "class")
    header_node = lxml.etree.SubElement(custom_widget_node, "header")
    
    class_node.text = widget_klass_name
    header_node.text = ""
    return ret

def _build_widget(module_name, widget_klass, widget_klasses, existing_widgets):
    """Builds a set of "customwidget" xml nodes necessary for the given widget"""
    
    custom_widget_node = lxml.etree.Element("customwidget")
    ret = [ custom_widget_node ]
    class_node = lxml.etree.SubElement(custom_widget_node, "class")
    extends_node = lxml.etree.SubElement(custom_widget_node, "extends")
    header_node = lxml.etree.SubElement(custom_widget_node, "header")

    widget_klass_name = widget_klass.__name__
    widget_super_klass = widget_klass.__base__
    widget_super_klass_name = widget_super_klass.__name__
    
    header_node.text = module_name
    class_node.text = widget_klass_name
    extends_node.text = widget_super_klass_name
    
    existing_widgets.append(widget_klass_name)
    
    if widget_super_klass_name not in widget_klasses and widget_super_klass_name not in dir(Qt):
        new_custom_widget_nodes = _build_plain_widget(widget_super_klass_name)
        ret.extend(new_custom_widget_nodes)
    else:
        if widget_super_klass_name in widget_klasses and widget_super_klass_name not in existing_widgets:
            super_module_name, super_klass = widget_klasses[widget_super_klass_name]
            new_custom_widget_nodes = _build_widget(super_module_name, super_klass, widget_klasses, existing_widgets)
            ret.extend(new_custom_widget_nodes)
    
    return ret