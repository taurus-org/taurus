.. _color-guide:

===================
Taurus color guide
===================

Taurus follows the ATK_ color scheme. The colors correspond to the tango DEV_STATE 
data type and to the tango attibute quality.

.. _state-color-guide:

State
-------

.. raw:: html

    <html>
    <head>
    <title>Taurus color guide</title>
    <style type="text/css">
    .ON      { background: rgb(  0, 255,   0); color: rgb(  0,   0,   0); text-align: center; }
    .OFF     { background: rgb(255, 255, 255); color: rgb(  0,   0,   0); text-align: center; }
    .CLOSE   { background: rgb(255, 255, 255); color: rgb(  0, 128,   0); text-align: center; }
    .OPEN    { background: rgb(  0, 255,   0); color: rgb(  0,   0,   0); text-align: center; }
    .INSERT  { background: rgb(255, 255, 255); color: rgb(  0,   0,   0); text-align: center; }
    .EXTRACT { background: rgb(  0, 255,   0); color: rgb(  0,   0,   0); text-align: center; }
    .MOVING  { background: rgb(128, 160, 255); color: rgb(  0,   0,   0); text-align: center; }
    .STANDBY { background: rgb(255, 255,   0); color: rgb(  0,   0,   0); text-align: center; }
    .FAULT   { background: rgb(255,   0,   0); color: rgb(  0,   0,   0); text-align: center; }
    .INIT    { background: rgb(204, 204, 122); color: rgb(  0,   0,   0); text-align: center; }
    .RUNNING { background: rgb(128, 160, 255); color: rgb(  0,   0,   0); text-align: center; }
    .ALARM   { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: center; }
    .DISABLE { background: rgb(255,   0, 255); color: rgb(  0,   0,   0); text-align: center; }
    .UNKNOWN { background: rgb(128, 128, 128); color: rgb(  0,   0,   0); text-align: center; }
    .NONE    { background: rgb(128, 128, 128); color: rgb(  0,   0,   0); text-align: center; }
    tr.state_row   { height: 40px; }
    </style>
    </head>
    <body align="center">
    <table width="100%" border="1" cellspacing="0" cellpadding="2">
    <caption>color scheme for the State</caption>
    <tr><th>State</th><th>Background</th><th>Foreground</th><th width="80">Preview</th></tr>
    <tr class="state_row"><td>ON</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="ON">ON</td></tr>
    <tr class="state_row"><td>OFF</td><td>White (255,255,255)</td><td>Black (0,0,0)</td><td class="OFF">OFF</td></tr>
    <tr class="state_row"><td>CLOSE</td><td>White (255,255,255)</td><td>Green (0,128,0)</td><td class="CLOSE">CLOSE</td></tr>
    <tr class="state_row"><td>OPEN</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="OPEN">OPEN</td></tr>
    <tr class="state_row"><td>INSERT</td><td>White (255,255,255)</td><td>Black (0,0,0)</td><td class="INSERT">INSERT</td></tr>
    <tr class="state_row"><td>EXTRACT</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="EXTRACT">EXTRACT</td></tr>
    <tr class="state_row"><td>MOVING</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="MOVING">MOVING</td></tr>
    <tr class="state_row"><td>STANDBY</td><td>Yellow (255,255,0)</td><td>Black (0,0,0)</td><td class="STANDBY">STANDBY</td></tr>
    <tr class="state_row"><td>FAULT</td><td>Red (255,0,0)</td><td>Black (0,0,0)</td><td class="FAULT">FAULT</td></tr>
    <tr class="state_row"><td>INIT</td><td>Grenoble (204,204,122)</td><td>Black (0,0,0)</td><td class="INIT">INIT</td></tr>
    <tr class="state_row"><td>RUNNING</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="RUNNING">RUNNING</td></tr>
    <tr class="state_row"><td>ALARM</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="ALARM">ALARM</td></tr>
    <tr class="state_row"><td>DISABLE</td><td>Magenta (255,0,255)</td><td>Black (0,0,0)</td><td class="DISABLE">DISABLE</td></tr>
    <tr class="state_row"><td>UNKNOWN</td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="UNKNOWN">UNKNOWN</td></tr>
    <tr class="state_row"><td>None</td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="NONE">-----</td></tr>
    </table>
    </body>
    </html>

.. _quality-color-guide:

Attribute quality
-----------------

.. raw:: html

    <html>
    <head>
    <title>Taurus color guide</title>
    <style type="text/css">
    .ATTR_INVALID  { background: rgb(128, 128, 128); color: rgb(255, 255, 255); text-align: right; }
    .ATTR_VALID    { background: rgb(0,   255,   0); color: rgb(  0,   0,   0); text-align: right; }
    .ATTR_ALARM    { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: right; }
    .ATTR_WARNING  { background: rgb(255, 140,   0); color: rgb(  0,   0,   0); text-align: right; }
    .ATTR_CHANGING { background: rgb(128, 160, 255); color: rgb(  0,   0,   0); text-align: right; }
    .ATTR_UNKNOWN  { background: rgb(128, 128, 128); color: rgb(  0,   0,   0); text-align: right; }
    .ATTR_NONE     { background: rgb(128, 128, 128); color: rgb(  0,   0,   0); text-align: right; }
    tr.quality_row { height: 40px; }
    </style>
    </head>
    <body>
    <table width="100%" border="1" cellspacing="0" cellpadding="2">
    <caption>color scheme for the quality</caption>
    <tr><th>Quality</th><th>Background</th><th>Foreground</th><th width="80">Preview</th></tr>
    <tr class="quality_row"><td>ATTR_INVALID</td><td>Gray (128,128,128)</td><td>White (255,255,255)</td><td class="ATTR_INVALID">-----</td></tr>
    <tr class="quality_row"><td>ATTR_VALID</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="ATTR_VALID">10.89 mV</td></tr>
    <tr class="quality_row"><td>ATTR_ALARM</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="ATTR_ALARM">76.54 mV</td></tr>
    <tr class="quality_row"><td>ATTR_WARNING</td><td>Orange (255,140,0)</td><td>Black (0,0,0)</td><td class="ATTR_WARNING">64.23 mV</td></tr>
    <tr class="quality_row"><td>ATTR_CHANGING</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="ATTR_CHANGING">20.45 mV</td></tr>
    <tr class="quality_row"><td>None</td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="ATTR_NONE">-----</td></tr>
    </table>
    </body>
    </html>
    

.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _ESRF: http://www.esrf.eu/
