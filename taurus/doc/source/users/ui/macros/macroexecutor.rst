.. _macroexecutor_ui:

==========================================
MacroExecutor User's Interface
==========================================


.. contents::


*MacroExecutor* provides an user-friendly graphical interface to macro execution.
It is divided into 3 main areas: `actions bar`, `parameters editor` and `favourites list`. 
Their functionalities are supported by `Spock command line` and `macro progress bar`.
User has full control over macros thanks to action buttons: Start(Resume), Stop, Pause located in `actions bar`     
Graphical `parameters editor` provides a clear way to set and modify macro execution settings (parameters).
Macros which are more frequently used can be permanently stored in `favourites list`. 
Once macro was started Door's state led and `macro progress bar` informs user about its status. 
Current macro settings (parameters) are translated to spock syntax, and represented in non editable
`spock command line`.

.. figure:: /_static/macros/macroexecutor01.png
  :align: center


.. _macroexecutor_stand-alone:


MacroExecutor as a stand-alone application
------------------------------------------

You may also use *MacroExcutor* as a stand-alone application. In this case it appears embedded
in window and some extra functionalities are provided. 
You can launch the stand-alone *MacroExecutor* with the following command::

    macroexecutor [options] [<macro_executor_dev_name> <door_dev_name>]
	
Options::
 
  --taurus-log-level=LEVEL
                        taurus log level. Allowed values are (case
                        insensitive): critical, error, warning/warn, info,
                        debug, trace
                        
  --taurus-polling-period=MILLISEC
                        taurus global polling period in milliseconds
                        
  --taurus-serialization-mode=SERIAL
                        taurus serialization mode. Allowed values are (case
                        insensitive): serial, concurrent (default)
  
  --tango-host=TANGO_HOST
                        Tango host name

    
The model list is optional and is a space-separated list of two device names: macro server and door.
If not provided at the application startup, models can be later on changed in configuration dialog.   
   
Extra functionalities:

- Changing macro configuration

.. todo:: 
	This chapter is not ready... Sorry for inconvenience.
	
- Configuring custom editors
 
.. todo:: 
	This chapter is not ready... Sorry for inconvenience.

	
.. _editing_macro_parameters:

Editing macro parameters
------------------------

.. _editing_macro_parameters_standard:

Using standard editor
'''''''''''''''''''''

If no custom parameter editor is assigned to macro, default editor is used to configure execution settings (parameters).
Parameters are represented in form of tree (with hidden root node) - every parameter is a separate branch with two columns: 
parameter name and parameter value.
Editor is populated with default values of parameters, if this in not a case 'None' values are used. (If macro execution settings 
were restored e.g. from favourites list, editor is populated with stored values). Values become editable either by double-clicking on them, 
or by pressing F2 button when value is selected. This action opens default parameter editor (combobox with predefined values, spin box etc.). 

In case of macros with single parameters only, tree has only a one level branch, and then tree representation looks more like a list 
(because of hidden root node)

.. figure:: /_static/macros/macroparameterseditor01.png
  :align: center

In case of macros which contain repeat parameters, concept of tree is more visible.  
 
.. figure:: /_static/macros/macroparameterseditor02.png
  :align: center
  
- adding new parameter repetition

First select parameter node and if its maximum number of repetition is not exceeded, button with '+' sign appears enabled. 
After pressing this button child branch with new repetition appears in tree editor.   

.. figure:: /_static/macros/macroparameterseditor03.png
  :align: center
  
- modifying repetition order

First select repetition node (with #<number> text), and buttons with arrows becomes enable (if it is feasible to change order)

.. figure:: /_static/macros/macroparameterseditor04.png
  :align: center

- removing parameter repetition

First select repetition node (with #<number> text), and if it's minimum number of repetition is not reached, button with '-' sign appears enabled. 
After pressing this button child branch disappears from tree editor. (see previous picture)

.. figure:: /_static/macros/macroparameterseditor05.png
  :align: center

.. _editing_macro_parameters_custom:

Using custom editors
''''''''''''''''''''

.. todo:: 
	This chapter is not ready... Sorry for inconvenince. 

.. _editing_favourites_list:

Editing favourites list
-----------------------
  
Once macro parameters are configured they can be easily stored in favourites list for later reuse.   

- adding a favourite 

Clicking in Add to favourites button (the one with yellow star), adds a new entry in favourite list, 
with current macro and its current settings.

- restoring a favourite

To restore macro from favourites list just select it in the list and macro parameters editor will immediately populate with stored settings.

- modifying favouites list

First select favourite macro and buttons with arrows becomes enable (if it is feasible to change order)

- removing a favourite

First select favourite macro, button with '-' sign appears enabled. After pressing this button, previously selected macro disappears from the list.