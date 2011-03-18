

.. currentmodule:: settings_widget

Settings Widget
======================

Settings Widget - the widget to setting up the different types of properties. 
The user variable modifications are stored inside the internal stack and can be cancelled.
(undo()/redo()). 

The Settings Widget returns:  (properties, name, values)

types:

- string
- integer
- boolean
- float

dimensions:

- 0D
- 1D
- 2D

Example::

    app = QtGui.QApplication(sys.argv)
    properties = []
    properties.append(PropertyInfo("name", "string", "0D", "deviceName"))
    properties.append(PropertyInfo("number0", "integer", "0D", 5))
    properties.append(PropertyInfo("boollll0", "boolean", "0D", False))    
    properties.append(PropertyInfo("number1", "float", "0D", 3.5))
    properties.append(PropertyInfo("string2", "string", "0D", "hehe"))
    properties.append(PropertyInfo("table0", "integer", "1D", [1,2,3]))
    properties.append(PropertyInfo("tablestringD1", "float", "1D", [1.5]))
    properties.append(PropertyInfo("tablestringD1", "string", "1D", ["aaaa","bbb","ccc"]))
    properties.append(PropertyInfo("tablefloatD1", "float", "1D", [1.0,2.5,3.6]))
    properties.append(PropertyInfo("tablebooleanD1", "boolean", "1D", [True,False,True]))
    properties.append(PropertyInfo("tableboointD1", "integer", "1D", [1,2,3]))
    properties.append(PropertyInfo("tablestringD2", "string", "2D",[ ["aaaa","bbb","ccc"],["aaaa2","bbb2","ccc2"],["aaaa3","bbb3","ccc3"] ]))
    
    
    nds=SettingsWidget()
    nds.setProperties(properties)
    nds.show()
    sys.exit(app.exec_())




.. automodule:: settings_widget
    :members:
    :undoc-members: