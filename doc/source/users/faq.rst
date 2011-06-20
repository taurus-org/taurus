
===
FAQ
===

What is the Sardana SCADA system and how do I get an overview over the different components?
--------------------------------------------------------------------------------------------
An overview over the different Sardana components can be found here <LINK>. The basic Sardana SCADA philosophy can be found here <LINK>

How do I install Sardana?
-------------------------
The Sardana SCADA system consists of different components which have to be installed:
TANGO: The control system middleware and tools  <LINK>
PyTango: The Python language binding for TANGO <LINK>
Taurus: The GUI toolkit which is part of Sardana SCADA <LINK>
The Sardana device pool, macro server and tools  <LINK>

How to work with Taurus GUI?
----------------------------
A user documentation for the Taurus GUI application can be found here <LINK>

How to produce your own Taurus GUI panel?
-----------------------------------------
The basic philosophy of Taurus GUI is to provide automatic GUIs which are automatically replaced by more and more specific GUIs if these are found.  
The documentation how to create a generic panel which can be filled via selection and cut and paste can be found here <LINK>. 
A more advanced usage is to create a Taurus widget and ingrate it into the application. Documentation for this approach can be found here <LINK>

How to call procedures?
-----------------------
The central idea of the Sardana SCADA system is to execute procedures centrally. The execution can be started from either:
SPOCK offers a command line interface with commands very similar to SPEC. It is documented here <LINK>
Procedures can also be executed with a GUI interface the macro executor. This GUI interface offering input from the keyboard and the generic widgets is documented here <LINK>. A macro can be associated with a specific GUI interface. This mechanism is documented here <LINK>
Procedures can also be executed in specific GUIs and specific Taurus widgets. The API to execute macros from this python code is documented here <LINK>

How to write procedures?
------------------------
User written procedures are central to the Sardana SCADA system. Documentation how to write macros can be found here <LINK>. Macro writers might also find the following documentation interesting:
Documentation on how to debug macros  can be found here <LINK>
In addition of the strength of the python language macro writers can interface with common elements (motors, counters) , call other macros and use many utilities provided. The API is documented here <LINK>
Documentation how to document your macros can be found here <LINK>

How to write scan procedures?
-----------------------------
A very common type of procedure is the “scan” where some quantity is varied while recording some other quantities. Many common types of general-purpose scans procedures are already available in Sardana <LINK>, and a simple API is provided for writing more specific ones.

How to adapt SARDANA to your own hardware?
------------------------------------------
Sardana is meant to be interfaced to all types of different hardware with all types of control systems. For every new hardware item the specific behavior has to be programmed by writing a controller code. The documentation how to write Sardana controllers and pseudo controllers can be found here <LINK>.  This documentation also includes the API which can be used to interface to the specific hardware item.

How to add your own file format?
--------------------------------
Documentation how to add your own file format can be found here <LINK>

How to use the standard macros?
-------------------------------
The list of all standard macros and their usage can be found here <LINK>.

How to add conditions in macros?
--------------------------------
Executing macros and moving elements can be subject to external conditions (for example an interlock). New types of software interlocks can be easily added to the system and are documented here <LINK>

How to write your own Taurus application?
-----------------------------------------
You have basically two possibilities to write your own Taurus application
Start from get General TaurusGUI and create a configuration file. This approach is documented here <LINK>
Start to write your own Qt application in python starting from the Taurus main window. This approach is documented here <LINK>

Which are the standard Taurus graphical GUI components?
-------------------------------------------------------
A list of all standard Taurus GUI components together with screen shots and example code can be found here <LINK>

How to write your own Taurus widget?
------------------------------------

A tutorial of how to write your own Taurus widget can be found here <LINK>

How to work with the graphical GUI editor?
------------------------------------------
Taurus uses the Qt Designer as a graphical editor. Documentation about the designer can be found here <LINK> and the Taurus specific parts here <LINK>

 
