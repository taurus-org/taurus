import os.path

from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode

from taurus import Database, Device, Attribute, Configuration, Object
from taurus.core import TaurusDatabase, TaurusDevice, TaurusAttribute, TaurusConfiguration
from taurus.core import AttrQuality, TaurusEventType
from taurus.core import AttributeNameValidator, ConfigurationNameValidator
from taurus.core.util.colors import ATTRIBUTE_QUALITY_PALETTE

class MainHandler(RequestHandler):
    def get(self):
        self.render("countclient.html")


class TestHandler(RequestHandler):
    def get(self):
        self.render("test.html")


class TaurusWebAttribute(object):

    TemplateDiv = """<div style="font-size: 24pt;{style}">{value}</div>"""
    
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
            data['html'] = modelObj.displayValue(value)
            data['value'] = value
#        data['css']['font-size'] = "24pt";  
        data['model'] = modelObj.getNormalName()
        json_data = json_encode(data)
        self.write_message(json_data)

    def write_message(self, message):
        return self.ws.write_message(message)

    def clear(self):
        self.attribute.removeListener(self)


class TaurusWebConfiguration(object):

    TemplateDiv = """<div style="font-size: 24pt;{style}">{value}</div>"""
    
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
        
def main():
    local_path = os.path.dirname(__file__)
    static_path= os.path.join(local_path, 'static')
    handlers = [ (r"/", MainHandler), 
                 (r"/test", TestHandler), 
                 (r"/taurus", TaurusSocket), ]
    application = Application(handlers, static_path=static_path)
    application.listen(8888)
    print "Starting..."
    try:
        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().start()
        print "Finished"
    except KeyboardInterrupt:
        print "Finished by Keyboard interrupt (Ctrl+C)"

if __name__ == "__main__":
    main()
