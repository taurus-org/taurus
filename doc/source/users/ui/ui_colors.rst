.. _ui_colors:

================
Taurus colors
================

Taurus uses color codes on many of its widgets. Colors are used to represent two
main things: 

- the state of a taurus device 
- the quality of (the reading of) an attribute.


Taurus Device state colors
---------------------------

Taurus Device states, as defined in :class:`taurus.core.TaurusDevState` are
represented by the following colors:


.. raw:: html

    <html>
    <head>
    <title>Taurus color guide</title>
    <style type="text/css">
    .Ready      { background: rgb(  0, 255,   0); color: rgb(  0,   0,   0); text-align: center; }
    .NotReady   { background: rgb(255,   0,   0); color: rgb(  0,   0,   0); text-align: center; }
    .Undefined  { background: rgb(128, 128, 128); color: rgb(  0,   0,   0); text-align: center; }
    tr.state_row   { height: 40px; }
    </style>
    </head>
    <body align="center">
    <table width="100%" border="1" cellspacing="0" cellpadding="2">
    <caption>Colors for the Taurus Device States (scheme-agnostic)</caption>
    <tr><th>State</th><th>Background</th><th>Foreground</th><th width="80">Preview</th></tr>
    <tr class="state_row"><td>Ready</td><td>Green (0,255,0)</td><td>Black (0,0,0)</td><td class="Ready">Ready</td></tr>
    <tr class="state_row"><td>NotReady</td><td>Red (255,0,0)</td><td>Black (0,0,0)</td><td class="NotReady">NotReady</td></tr>
    <tr class="state_row"><td>Undefined</td><td>Gray (128,128,128)</td><td>Black (0,0,0)</td><td class="Undefined">Undefined</td></tr>
    </table>
    </body>
    </html>


Taurus Attribute Value Quality colors
-------------------------------------

The quality of an attribute measures the reliability of the current read value for
that attribute. The meanings of the qualities are:

- *Invalid*: there was some problem when trying to read the attribute (the value should not be trusted)
- *Valid*: the attribute was read correctly (no reason to suspect its value validity)
- *Alarm*: the value is valid, but it exceeded its defined alarm limits
- *Warning*: like *Alarm* but for the warning limits
- *Changing*: the attribute was read correctly but it is being changed at the time of reading (so its value is
  likely to differ if re-read)

Taurus Attribute value qualities are represented by the following colors:
      
.. raw:: html

    <html>
    <head>
    <title>Taurus color guide</title>
    <style type="text/css">
    .Invalid  { background: rgb(128, 128, 128); color: rgb(255, 255, 255); text-align: right; }
    .Valid    { background: rgb(0,   255,   0); color: rgb(  0,   0,   0); text-align: right; }
    .Alarm    { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: right; }
    .Warning  { background: rgb(255, 140,   0); color: rgb(255, 255, 255); text-align: right; }
    .Changing { background: rgb(128, 160, 255); color: rgb(  0,   0,   0); text-align: right; }
    tr.quality_row { height: 40px; }
    </style>
    </head>
    <body>
    <table width="100%" border="1" cellspacing="0" cellpadding="2">
    <caption>Colors for Taurus Attribute quality</caption>
    <tr><th>Quality</th><th>Background</th><th>Foreground</th><th width="80">Preview</th></tr>
    <tr class="quality_row"><td>Invalid</td><td>Gray (128,128,128)</td><td>White (255,255,255)</td><td class="Invalid">-----</td></tr>
    <tr class="quality_row"><td>Valid</td><td>Dead Frog Green (0,255,0)</td><td>Black (0,0,0)</td><td class="Valid">10.89 mV</td></tr>
    <tr class="quality_row"><td>Alarm</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="Alarm">76.54 mV</td></tr>
    <tr class="quality_row"><td>Warning</td><td>Orange (255,140,0)</td><td>White (255,255,255)</td><td class="Warning">64.23 mV</td></tr>
    <tr class="quality_row"><td>Changing</td><td>Light Blue (128,160,255)</td><td>Black (0,0,0)</td><td class="Changing">20.45 mV</td></tr>
    </table>
    </body>
    </html>


Tango-specific Device state colors
----------------------------------

Tango Device states are richer than the generic ones. The following is a table of 
the colors used to represent Tango-specific device states handled by the :mod:`taurus.core.tango`
scheme:

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


