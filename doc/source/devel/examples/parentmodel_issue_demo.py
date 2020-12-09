'''
This code exposes a limitation in the useParentModel architecture of Taurus and
explains how to avoid/work-around it.

Note that the conditions for hitting this limitation are quite special and that
in most situations you will not hit it. But unfortunately it may happen with
designer-generated files, and then the recheckTaurusParent() workaround is useful:
call recheckTaurusParent for all designer created widgets that use TaurusParentModel.
You can do it right after calling the setupUi method.
'''
from __future__ import print_function
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
import sys
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None)

# The problem arises in some situations when the Taurus parenting is not the same
# as the Qt parenting. For demonstration we use 3 widgets:
# p <-- m <--c (the arrows indicate the *Qt* parent)
# note that "m" not being a Taurus widget, implies that the *Taurus* parent of c is p
# also note that we are not giving the parent in the constructor, but we rely on
# doing it later on when adding to layout

p = TaurusWidget()  # Taurus parent
m = Qt.QWidget()  # midle widget (non Taurus)
c = TaurusLabel()  # Taurus child

# here we call setUseParentModel before the parent is known!

c.setUseParentModel(True)

# we prepare the layouts

m.setLayout(Qt.QVBoxLayout())
p.setLayout(Qt.QVBoxLayout())

# Now, by adding the widgets to the layout we are actually reparenting them.
# The order in which we reparent determines success/failure:
# if we do m-->p and then c-->m, it works, but if we do it in the opposite
# order, we trigger the error.
# (i.e., if we had called "p.layout().addWidget(m)" it would work work)
m.layout().addWidget(c)
p.layout().addWidget(m)

# the problem arises because the Taurus ancestry of c is only checked when:
# a) c.setUseParentModel() is called (and it effectively changes something) or
# b) when c is Qt-reparented
##
# In this example, c is reparented before m, so when it checks for a Taurus
# ancestor, none is found. Then m is reparented and c now would find its right
# Taurus ancestor (p)... but c never gets notified!

# Manually calling c.recheckTaurusParent() after the parenting has changed is
# another way to work around this issue (you can test by uncommenting
# the following line):

# c.recheckTaurusParent()

p.setModel('sys/tg_test/1/state')
print('p model:', p.getModelName())
print('c model:', c.getModelName())


p.show()
sys.exit(app.exec_())
