.. _ui_colors:

================
Taurus colors
================

Taurus uses color codes on many of its widgets. Colors are used to represent two
main things: the state of a device and the quality level of an attribute.
The state represents the summary condition of a certain device. For example, a
power supply, maybe report to be *On* if it is working properly, *Off* if it is
shutdown or *Fault* if there is a communication problem between the software and
the physical device. Taurus allows for a reduced set of these states, each of which
has a specified color. The table below shows all possible values for the state
and their corresponding colors.

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
    <tr class="state_row"><td>On</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="ON">ON</td></tr>
    <tr class="state_row"><td>Off</td><td>White (255,255,255)</td><td>Black (0,0,0)</td><td class="OFF">OFF</td></tr>
    <tr class="state_row"><td>Close</td><td>White (255,255,255)</td><td>Green (0,128,0)</td><td class="CLOSE">CLOSE</td></tr>
    <tr class="state_row"><td>Open</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="OPEN">OPEN</td></tr>
    <tr class="state_row"><td>Insert</td><td>White (255,255,255)</td><td>Black (0,0,0)</td><td class="INSERT">INSERT</td></tr>
    <tr class="state_row"><td>Extract</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="EXTRACT">EXTRACT</td></tr>
    <tr class="state_row"><td>Moving</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="MOVING">MOVING</td></tr>
    <tr class="state_row"><td>Standby</td><td>Yellow (255,255,0)</td><td>Black (0,0,0)</td><td class="STANDBY">STANDBY</td></tr>
    <tr class="state_row"><td>Fault</td><td>Red (255,0,0)</td><td>Black (0,0,0)</td><td class="FAULT">FAULT</td></tr>
    <tr class="state_row"><td>Init</td><td>Grenoble (204,204,122)</td><td>Black (0,0,0)</td><td class="INIT">INIT</td></tr>
    <tr class="state_row"><td>Running</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="RUNNING">RUNNING</td></tr>
    <tr class="state_row"><td>Alarm</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="ALARM">ALARM</td></tr>
    <tr class="state_row"><td>Disable</td><td>Magenta (255,0,255)</td><td>Black (0,0,0)</td><td class="DISABLE">DISABLE</td></tr>
    <tr class="state_row"><td>Unknown</td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="UNKNOWN">UNKNOWN</td></tr>
    <tr class="state_row"><td><empty></td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="NONE">-----</td></tr>
    </table>
    </body>
    </html>


The quality of an attribute (example, voltage of a power supply) defines it's 
"state". If the value of an attribute can be read then its quality is *valid*.
If for some reason there is a problem when trying to read the attribute value
from the equipement and it cannot be displayed, then the quality is set to
*invalid*. If the value is below or above the warning or alarm thresolds, then
the quality is set to *alarm*.
The quality is set to *changing* when the value is being changed over time
(example, the position of a motor is changing during a motion).
      
.. raw:: html

    <html>
    <head>
    <title>Taurus color guide</title>
    <style type="text/css">
    .ATTR_INVALID  { background: rgb(128, 128, 128); color: rgb(255, 255, 255); text-align: right; }
    .ATTR_VALID    { background: rgb(0,   255,   0); color: rgb(  0,   0,   0); text-align: right; }
    .ATTR_ALARM    { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: right; }
    .ATTR_WARNING  { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: right; }
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
    <tr class="quality_row"><td>Invalid</td><td>Gray (128,128,128)</td><td>White (255,255,255)</td><td class="ATTR_INVALID">-----</td></tr>
    <tr class="quality_row"><td>Valid</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="ATTR_VALID">10.89 mV</td></tr>
    <tr class="quality_row"><td>Alarm</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="ATTR_ALARM">76.54 mV</td></tr>
    <tr class="quality_row"><td>Warning</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="ATTR_WARNING">64.23 mV</td></tr>
    <tr class="quality_row"><td>Changing</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="ATTR_CHANGING">20.45 mV</td></tr>
    <tr class="quality_row"><td><empty></td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="ATTR_NONE">-----</td></tr>
    </table>
    </body>
    </html>

