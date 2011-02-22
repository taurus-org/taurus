#!/usr/bin/env python

import sys, os
import PyTango

from PyQt4 import QtGui, QtCore, Qt

import upgrade_utils

def get_default_tango_host():
    tg = os.environ.get('TANGO_HOST')
    if tg is None: return '', ''
    return tg.split(':')

class BaseUpgradePage(QtGui.QWizardPage):
    
    host_key = 'tango_host'
    port_key = 'tango_port'
    p_instance_key = 'pool_instance'
    p_version_key = 'pool_version'
    
    def __init__(self, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/logo.jpg"))
    
    def db(self):
        return self.wizard().db()
    
    def pool(self):
        return self.wizard().pool()
        
    def version(self):
        return self.wizard().version()
    
    
class IntroPage(QtGui.QWizardPage):
    
    def __init__(self, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
    
        self.setTitle('Introduction')
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        
        label = QtGui.QLabel('This wizard will upgrade your device pool to ' \
                             'the desired version. You simply need to specify ' \
                             'the tango host, the pool instance and the new ' \
                             'version you which to upgrade to')
        label.setWordWrap(True)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    
class SelectTangoHostPage(BaseUpgradePage):
    
    def __init__(self, parent = None):
        BaseUpgradePage.__init__(self, parent)
        self.setTitle('Tango Host')
        self.setSubTitle('Please select the Tango Host')
        
        #panel = QtGui.QWidget(self)
        panel = self
        layout = QtGui.QGridLayout(panel)
        
        hostEdit = QtGui.QLineEdit(panel)
        portEdit = QtGui.QLineEdit(panel)

        self.registerField(self.host_key, hostEdit)
        self.registerField(self.port_key, portEdit)

        host, port = get_default_tango_host()

        hostEdit.setText(host)
        portEdit.setText(port)

        self.connect(hostEdit, 
                     QtCore.SIGNAL('textEdited(const QString &)'), 
                     QtCore.SIGNAL('completeChanged()'))
        self.connect(portEdit, 
                     QtCore.SIGNAL('textEdited(const QString &)'), 
                     QtCore.SIGNAL('completeChanged()'))
        
        hostLabel = QtGui.QLabel('&Host:', panel)
        portLabel = QtGui.QLabel('&Port:', panel)
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.statusLabel = QtGui.QLabel(panel)
        
        self.statusLabel.setAutoFillBackground(True)
        palette = self.statusLabel.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(Qt.QColor.fromRgb(200,200,200)))
        
        hostLabel.setBuddy(hostEdit)
        portLabel.setBuddy(portEdit)
    
        layout.addWidget(hostLabel, 0, 0, Qt.Qt.AlignRight)
        layout.addWidget(portLabel, 1, 0, Qt.Qt.AlignRight)
        layout.addWidget(hostEdit, 0, 1, Qt.Qt.AlignLeft)
        layout.addWidget(portEdit, 1, 1, Qt.Qt.AlignLeft)
        layout.addWidget(portEdit, 1, 1, Qt.Qt.AlignLeft)
        layout.addItem(spacer, 2, 0, 1, 2)
        layout.addWidget(self.statusLabel, 3, 0, 1, 2)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
    
    def initializePage(self):
        BaseUpgradePage.initializePage(self)

    def isComplete(self):
        try:
            db = self.db()
            self.statusLabel.setText('')
            return True
        except PyTango.DevFailed, df:
            txt = str(df.args[-1].desc)
            self.statusLabel.setText(txt)
            return False

class SelectInstancePage(BaseUpgradePage):
    
    def __init__(self, parent = None):
        BaseUpgradePage.__init__(self, parent)
        self.setTitle('Pool Instance')
        self.setSubTitle('Please select the Pool Server instance')
        
        #panel = QtGui.QWidget(self)
        panel = self
        
        self.instanceCB = QtGui.QComboBox(panel)
        self.instanceCB.setDuplicatesEnabled(False)
        self.instanceCB.setEditable(False)
        self.registerField(self.p_instance_key, self.instanceCB)
        
        layout = QtGui.QGridLayout(panel)
        instanceLabel = QtGui.QLabel('instance:', panel)
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.statusLabel = QtGui.QLabel(panel)

        self.statusLabel.setAutoFillBackground(True)
        palette = self.statusLabel.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(Qt.QColor.fromRgb(200,200,200)))

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.addWidget(instanceLabel, 0, 0, Qt.Qt.AlignRight)
        layout.addWidget(self.instanceCB, 0, 1, Qt.Qt.AlignLeft)
        layout.addItem(spacer, 1, 0, 1, 2)

        layout.addWidget(self.statusLabel, 2, 0, 1, 2)
        
        self.connect(self.instanceCB, 
                     QtCore.SIGNAL('currentIndexChanged(int)'), 
                     QtCore.SIGNAL('completeChanged()'))

    def isComplete(self):
        idx = self.instanceCB.currentIndex()
        if idx >= 0:
            db = self.db()
            serv = str(self.instanceCB.currentText())
            curr_vers = upgrade_utils.get_pool_server_version(serv, db=db)
            txt = 'Current version is %s' % curr_vers
            possible_upgrades = upgrade_utils.get_possible_upgrades(serv, db=db)
            if not possible_upgrades:
                txt += ". There are no possible upgrades for this version"
            self.statusLabel.setText(txt)
            return len(possible_upgrades)
        else:
            self.statusLabel.setText('No instance selected')
            return False
            
    def initializePage(self):
        BaseUpgradePage.initializePage(self)
        db = self.db()
        self.instanceCB.clear()
        self.instanceCB.addItems(upgrade_utils.get_server_list(db=db))

class SelectVersionPage(BaseUpgradePage):
    
    def __init__(self, parent = None):
        BaseUpgradePage.__init__(self, parent)
        self.setTitle('Version')
        self.setSubTitle('Please select the version to upgrade to')
        
        panel = self
        
        self.versionCB = QtGui.QComboBox(panel)
        self.versionCB.setDuplicatesEnabled(False)
        self.versionCB.setEditable(False)
        self.registerField(self.p_version_key, self.versionCB)
        
        layout = QtGui.QGridLayout(panel)
        versionLabel = QtGui.QLabel('version:', panel)
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.statusLabel = QtGui.QLabel(panel)

        self.statusLabel.setAutoFillBackground(True)
        palette = self.statusLabel.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(Qt.QColor.fromRgb(200,200,200)))

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.addWidget(versionLabel, 0, 0, Qt.Qt.AlignRight)
        layout.addWidget(self.versionCB, 0, 1, Qt.Qt.AlignLeft)
        layout.addItem(spacer, 1, 0, 1, 2)

        layout.addWidget(self.statusLabel, 2, 0, 1, 2)

    def initializePage(self):
        serv = self.pool()
        db = self.db()
        self.setSubTitle('Please select to which version you want to upgrade %s to' % serv)
        self.versionCB.clear()
        curr_vers = upgrade_utils.get_pool_server_version(serv, db=db)
        possible_new_vers = upgrade_utils.get_possible_upgrades(serv, db=db)
        
        if not possible_new_vers:
            self.statusLabel.setText('There are no suitable upgrades for version %s' % curr_vers)
        else:
            self.versionCB.addItems(possible_new_vers)

class ConclusionPage(BaseUpgradePage):

    def __init__(self, parent = None):
        BaseUpgradePage.__init__(self, parent)
        self.setTitle('Upgrade')
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        layout = QtGui.QVBoxLayout(self)
        self.label = QtGui.QLabel(self)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

    def initializePage(self):
        finishText = self.wizard().buttonText(QtGui.QWizard.FinishButton)
        finishText.remove('&')
        txt = "You are now ready to upgrade '%s' to version '%s'. Click on " \
              "'%s' to proceed with the upgrade" % (self.pool(), self.version(), finishText)
        self.label.setText(txt)
        
class SardanaUpgradeWizard(QtGui.QWizard):
    
    host_key = 'tango_host'
    port_key = 'tango_port'
    p_instance_key = 'pool_instance'
    p_version_key = 'pool_version'
    
        
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        self._db = None
        self.setWindowTitle("Sardana Upgrade Tool")
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.addPage(IntroPage())
        self.addPage(SelectTangoHostPage())
        self.pool_page_idx = self.addPage(SelectInstancePage())
        self.version_page_idx = self.addPage(SelectVersionPage())
        self.addPage(ConclusionPage())
        
    def pool(self):
        pool_instance_idx = int(self.pool_index())
        p = self.page(self.pool_page_idx).instanceCB.itemText(pool_instance_idx)
        return str(p)

    def pool_index(self):
        return str(self.field(self.p_instance_key).toString())

    def version(self):
        pool_version_idx = int(self.pool_version_index())
        v = self.page(self.version_page_idx).versionCB.itemText(pool_version_idx)
        return str(v)
    
    def pool_version_index(self):
        return str(self.field(self.p_version_key).toString())
    
    def db(self):
        host = str(self.field(self.host_key).toString()).lower()
        port = str(self.field(self.port_key).toString()).lower()
        if not self._db or self._db.get_db_host().lower() != host or \
           self._db.get_db_port().lower() != port:
            try:
                self._db = PyTango.Database(host, port)
            except PyTango.DevFailed, df:
                self._db = None
                raise df
        return self._db
        
    def accept(self):
        pool = self.pool()
        new_version = self.version()
        res = self.upgrade(pool, new_version)
        if res:
            self.setStartId(1)
            self.restart()
        else:
            QtGui.QWizard.accept(self)
            

    def upgrade(self, serv, new_vers):
        db = self.db()
        old_vers = upgrade_utils.get_pool_server_version(serv, db=db)
        u_kcls = upgrade_utils.get_suitable_upgrade(old_vers, new_vers)
        u_obj = u_kcls()
        
        dialog = QtGui.QProgressDialog("Upgrading %s to %s..." % (serv, new_vers), "Abort", 0, 100, self)
        dialog.setAutoClose(True)
        dialog.setMinimumDuration(0)

        import time
        for msg, percentage in u_obj.upgrade(db, serv, old_vers, new_vers):
            dialog.setLabelText(msg)
            dialog.setValue(percentage)
            time.sleep(0.1)
        
        dialog = QtGui.QMessageBox()
        dialog.setWindowTitle("Success!!!")
        dialog.setText("Do you wish to upgrade another Sardana?")
        dialog.setInformativeText("Selecting No will exit this wizard")
        dialog.setIcon(QtGui.QMessageBox.Question)
        dialog.addButton(QtGui.QMessageBox.Yes)
        dialog.addButton(QtGui.QMessageBox.No)
        dialog.setDefaultButton(QtGui.QMessageBox.Yes)
        return dialog.exec_() == QtGui.QMessageBox.Yes

def main():
    app = QtGui.QApplication([])
    res_fname = os.path.abspath(__file__)
    res_fname = res_fname[:res_fname.rfind('.')] + '.rcc'
    QtCore.QResource.registerResource(res_fname)
    wizard = SardanaUpgradeWizard()
    wizard.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()