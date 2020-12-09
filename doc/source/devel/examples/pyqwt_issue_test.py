'''
This code checks if a known bug in some PyQwt versions affects your installation.
Simply run this script and see the diagnosis in the std output.

If you are affected, the solution is to install/compile a newer version of PyQwt/SIP

Notably, the python-qwt5-qt4 package originally shipped with
Ubuntu 10.10 and Debian 6 is affected

In some systems, the bug produces a segfault while in some others it
produces an Assertion error similar to the following:
python: /build/buildd/sip4-qt3-4.10.5/siplib/siplib.c:2600: sip_api_parse_result: Assertion `assign_helper != ((void *)0)' failed.

See also:
https://bugs.launchpad.net/ubuntu/+source/pyqwt5/+bug/672509
http://www.esrf.eu/mail_archives/tango/archive/msg04025.html
'''

from PyQt4 import Qt, Qwt5


class MyScaleDrawSafe(Qwt5.QwtScaleDraw):

    def __init__(self):
        Qwt5.QwtScaleDraw.__init__(self)


class MyScaleDrawDanger(Qwt5.QwtScaleDraw):

    def __init__(self):
        Qwt5.QwtScaleDraw.__init__(self)

    def label(self, val):
        return Qwt5.QwtScaleDraw.label(self, val)


class MyPlot(Qwt5.QwtPlot):

    def __init__(self, parent=None):
        Qwt5.QwtPlot.__init__(self, parent)
        self.setAxisScaleDraw(Qwt5.QwtPlot.xBottom, MyScaleDrawSafe())
        print("Replotting with MyScaleDrawSafe:...")
        self.replot()
        print("ok")
        self.setAxisScaleDraw(Qwt5.QwtPlot.xBottom, MyScaleDrawDanger())
        print("Replotting with MyScaleDrawDanger (if it crashes now you are affected by the bug) :...")
        self.replot()
        print("SAFE!!!")
        print("if this is printed, the sip/PyQwt bug does not affect you")

app = Qt.QApplication([])
p = MyPlot()
p.show()
