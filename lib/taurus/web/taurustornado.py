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

"""
"""

from __future__ import print_function

__docformat__ = "restructuredtext"

import os.path

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode

from taurus import Database, Device, Attribute, Configuration, Object
from taurus.core.taurusdatabase import TaurusDatabase
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusconfiguration import TaurusConfiguration
from taurus.core.taurusbasetypes import AttrQuality, TaurusEventType
from taurus.core.taurusvalidator import AttributeNameValidator, ConfigurationNameValidator
from taurus.core.util.colors import ATTRIBUTE_QUALITY_PALETTE


class TaurusWebAttribute(object):

    def __init__(self, ws, name):
        self.name = name
        self.ws = ws
        self.attribute.addListener(self)
    
    @property
    def attribute(self):
        return Attribute(self.name)
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        modelObj = evt_src
        data = {}
        if evt_type == TaurusEventType.Error:
            data['css'] = {'color':'white', 'background-color' : 'red'}
            
            data['html'] = str(evt_value)
        else:
            if evt_type == TaurusEventType.Config:
                modelObj = evt_src.getParentObj()
                data['title'] = evt_src.description
            valueObj = modelObj.getValueObj()
            value = valueObj.value
            quality = valueObj.quality
            bg, fg = ATTRIBUTE_QUALITY_PALETTE.rgb_pair(quality)
            bg, fg = "rgb{0}".format(bg), "rgb{0}".format(fg)
            data['css'] = {'color': fg, 'background-color' : bg}
            data['html'] = modelObj.displayValue(value).replace('\n', r'<br/>')
            #data['value'] = value
        data['model'] = modelObj.getNormalName()
        json_data = json_encode(data)
        self.write_message(json_data)

    def write_message(self, message):
        return self.ws.write_message(message)

    def clear(self):
        self.attribute.removeListener(self)

class TaurusWebConfiguration(object):

    def __init__(self, ws, name):
        self.name = name
        self.param = ConfigurationNameValidator().getParams(name)['configparam']
        self.ws = ws
        self.configuration.addListener(self)
    
    @property
    def configuration(self):
        return Configuration(self.name)
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        modelObj = evt_src
        data = {}
        if evt_type == TaurusEventType.Error:
            data['css'] = {'color':'white', 'background-color' : 'red'}
            data['html'] = str(evt_value)
        else:
            data['css'] = {}
            data['html'] = getattr(modelObj, self.param)
            data['title'] = modelObj.description
            
 #       data['css']['font-size'] = "24pt";  
        data['model'] = self.name
        json_data = json_encode(data)
        self.write_message(json_data)

    def write_message(self, message):
        return self.ws.write_message(message)
    
    def clear(self):
        self.configuration.removeListener(self)


class TaurusSocket(WebSocketHandler):

    def open(self):
        self.models = set()
        
    def on_message(self, json_data):
        data = json_decode(json_data)
        if 'models' in data:
            self.clear_models()
            model_names = set(data['models'])
            for model_name in model_names:
                model_name = str(model_name)
                if AttributeNameValidator().isValid(model_name):
                    web_model = TaurusWebAttribute(self, model_name)
                elif ConfigurationNameValidator().isValid(model_name):
                    web_model = TaurusWebConfiguration(self, model_name)
                else:
                    continue
                self.models.add(web_model)
            
    def on_close(self):
        self.clear_models()

    def clear_models(self):
        for model in self.models:
            model.clear()
        self.models.clear()

def get_taurus_tornado_static_path():
    local_path = os.path.dirname(__file__)
    static_path = os.path.join(local_path, 'static')
    return static_path

def get_default_handlers():
    return [
        (r"/taurus", TaurusSocket),
        (r"/taurus/(.*)", StaticFileHandler, {"path": get_taurus_tornado_static_path() }),
    ]

def start(handlers=None, static_path=None, port=8888, **kwargs):
    if static_path is None:
        local_path = os.path.dirname(__file__)
        static_path= os.path.join(local_path, 'static')
    if handlers is None:
        handlers = [ (r"/", MainHandler), 
                     (r"/taurus", TaurusSocket), ]
    application = Application(handlers, static_path=static_path, **kwargs)
    application.listen(port)
    print("Starting...")
    try:
        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().start()
        print("Finished")
    except KeyboardInterrupt:
        print("Finished by Keyboard interrupt (Ctrl+C)")

if __name__ == "__main__":
    start()
