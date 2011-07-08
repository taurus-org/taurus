import os
import xml.dom.minidom

from sardana.macroserver.macro import *

TAG_MACRO       = 'macro'
TAG_PARAM       = 'param' 
TAG_PARAMREPEAT = 'paramrepeat'
TAG_REPEAT      = 'repeat'
TAG_PARAMS      = 'params'
TAG_SEQUENCE    = 'sequence'

ATTRIBUTE_NAME          = 'name'
ATTRIBUTE_VALUE         = 'value'
ATTRIBUTE_INDEX         = 'nr'
ATTRIBUTE_DESCRIPTION   = 'description'
ATTRIBUTE_DEFVALUE      = 'defvalue'
ATTRIBUTE_TYPE          = 'type'
ATTRIBUTE_ALLOWEDHOOKS  = 'allowedHooks'
ATTRIBUTE_HASPARAMS     = 'hasParams'
ATTRIBUTE_MIN           = 'min'

class sequence(Macro):
    """This macro executes a sequence of macros. As a parameter 
    it receives a string which is a xml structure. These macros which allow
    hooks can nest another sequence (xml structure). In such a case, 
    this macro is executed recursively."""
    
    param_def = [
       ['xml',   Type.String,   None, 'Xml string representing a sequence']
    ]
        
    def run(self, *pars):       
        xmlDoc = xml.dom.minidom.parseString(pars[0])
        macros = self.parseXml(xmlDoc)
        for macro in macros:
            self.runMacro(macro)
#            self.pausePoint()
            
    def parseXml(self, xmlDoc):
        macros = []
        sequenceElement = xmlDoc.getElementsByTagName(TAG_SEQUENCE)[0]
        childElement = sequenceElement.firstChild
        while childElement:
            if childElement.localName == TAG_MACRO:
                params, hookElement = self.parseMacro(childElement)
                macro = self.createMacro(params)
                if hookElement is not None:
                    hook = self.createExecMacroHook([self.__class__.__name__,
                                                    hookElement.toxml()])
                    macro.hooks = [hook]
                macros.append(macro)
            childElement = childElement.nextSibling
        return macros
            
    def parseMacro(self, xmlElement):
        name = str(xmlElement.getAttribute(ATTRIBUTE_NAME))
        params = (name,)
        hookElement = None
        childElement = xmlElement.firstChild
        while childElement:
            if childElement.localName == TAG_PARAM:
                params += self.parseParam(childElement)
            elif childElement.localName == TAG_PARAMREPEAT:
                params += self.parseParamRepeat(childElement)
            elif childElement.localName == TAG_SEQUENCE:
                hookElement = childElement
            childElement = childElement.nextSibling
        return (params,hookElement)
            
    def parseParam(self, xmlElement):
        return (str(xmlElement.getAttribute(ATTRIBUTE_VALUE)),)
        
    def parseParamRepeat(self, xmlElement):
        params = ()
        childElement = xmlElement.firstChild
        while childElement:
            if childElement.localName == TAG_REPEAT:
                params += self.parseRepeat(childElement)
            childElement = childElement.nextSibling
        return params
    
    def parseRepeat(self, xmlElement):
        params = ()
        childElement = xmlElement.firstChild
        while childElement:
            if childElement.localName == TAG_PARAM:
                params += self.parseParam(childElement)
            elif childElement.localName == TAG_PARAMREPEAT:
                params += self.parseParamRepeat(childElement)
            childElement = childElement.nextSibling
        return params
