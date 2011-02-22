#!/usr/bin/env python

import sys,os,imp,time
import PyTango

try:
    from PyQt4 import QtGui, QtCore
    try:
        import tau
        mode = 2
    except:
        mode = 1
except:
    mode = 0

from simuConfig import Simulation
from simuConfigGUI_ui import Ui_simuConfigDialog

def format_DevFailed(df):
    """Alternative print of PyTango.DevFailed. The original 
    PyTango.Except.print_exception seems not to work at shutdown so this 
    ensures a good print in that case"""
    
    desc = df.message['desc'].rstrip('\n').replace('\n',"              \n")
    
    ret=  40*'-' + '\n'
    ret+= "   Severety = %s\n" % df.message['severity']
    ret+= "     Reason = %s\n" % df.message['reason']
    ret+= "Description = %s\n" % desc
    ret+= "     Origin = %s\n" % df.message['origin']
    return ret
    
class NewSystemDialog(QtGui.QDialog):
    
    def __init__(self, db, parent = None):
       QtGui.QDialog.__init__(self, parent)
       
       self.simulation = Simulation(db)
       self.mode = mode
       self.cfg = Ui_simuConfigDialog()
       self.cfg.setupUi(self)
       self.update()
       
       apply = self.cfg.buttonBox.button(QtGui.QDialogButtonBox.Apply)    
       QtCore.QObject.connect(apply, QtCore.SIGNAL("clicked()"), self.create)
       
    def update(self):
       db = self.simulation.db
       self.setWindowTitle("New Sardana Simulation on %s:%s" % (db.get_db_host(), db.get_db_port()))
       self.cfg.motorServerNameLineEdit.setText(self.simulation.motor_server_name)
       self.cfg.motorControllerNameLineEdit.setText(self.simulation.motor_ctrl_alias)
       self.cfg.motorNumberSpinBox.setValue(self.simulation.motor_nb)
       
       self.cfg.counterServerNameLineEdit.setText(self.simulation.counter_server_name)
       self.cfg.counterControllerNameLineEdit.setText(self.simulation.counter_ctrl_alias)
       self.cfg.counterNumberSpinBox.setValue(self.simulation.counter_nb)
       
       self.cfg.zeroDNumberSpinBox.setValue(self.simulation.zerod_nb)
       
       self.cfg.poolServerNameLineEdit.setText(self.simulation.pool_server_name)
       self.cfg.poolNameLineEdit.setText(self.simulation.pool_alias)
       self.cfg.poolPathTextEdit.clear()
       for pool_path_item in self.simulation.pool_path:
           self.cfg.poolPathTextEdit.append(QtCore.QString(pool_path_item))
       
       self.cfg.msServerNameLineEdit.setText(self.simulation.ms_server_name)
       self.cfg.msNameLineEdit.setText(self.simulation.ms_alias)
       self.cfg.macroPathTextEdit.clear()
       for ms_path_item in self.simulation.ms_path:
           self.cfg.macroPathTextEdit.append(QtCore.QString(ms_path_item))
       
       self.cfg.doorNameLineEdit.setText(self.simulation.door_alias)

    def reload(self):
        host, port = self.simulation.db.get_db_host(),self.simulation.db.get_db_port_num()
        self.simulation = Simulation(host,port)
        self.update()
    
    @QtCore.pyqtSignature("triggered()")
    def create(self):
        self.simulation.motor_ctrl_alias = str(self.cfg.motorControllerNameLineEdit.text())
        self.simulation.motor_nb = self.cfg.motorNumberSpinBox.value()
        
        self.simulation.counter_ctrl_alias = str(self.cfg.counterControllerNameLineEdit.text())
        self.simulation.counter_nb = self.cfg.counterNumberSpinBox.value()
        
        self.simulation.zerod_nb = self.cfg.zeroDNumberSpinBox.value()
        
        self.simulation.pool_alias = str(self.cfg.poolNameLineEdit.text())
        self.simulation.pool_path = str(self.cfg.poolPathTextEdit.toPlainText()).split()
        
        self.simulation.ms_alias = str(self.cfg.msServerNameLineEdit.text())
        self.simulation.ms_path = str(self.cfg.macroPathTextEdit.toPlainText()).split()
        self.simulation.door_alias = str(self.cfg.doorNameLineEdit.text())
        
        self.simulation.create_motor_simulator()
        self.simulation.create_counter_simulator()
        self.simulation.create_pool()
        
        inst_name = self.simulation.pool_server_name.split("/")[1]

        mot_proc, co_proc, pool_proc = self.__start_servers(inst_name)

        try:
            # wait a little for things to stabilize
            # (pool may take some seconds)
            QtCore.QThread.sleep(3)
            ret = self.simulation.check_pool_ctrl_classes()
    
            if not ret:
                QtGui.QMessageBox.warning(self, "Invalid PoolPath",
                                          """The current PoolPath does not contain the necessary controller classes.\n
                                             Some pool elements may not be properly created.""")
            self.simulation.fill_pool()
            self.simulation.create_ms()
            self.simulation.create_door()        
            
            QtGui.QMessageBox.information(self, "Success!",
                                          "Simulation environment successfuly created")
            
            self.reload()
            
        finally:
            pass
            if mot_proc:
                mot_proc.terminate()
                ret = mot_proc.waitForFinished(3000)
                if not ret:
                    mot_proc.kill()
            if co_proc:
                co_proc.terminate()
                ret = co_proc.waitForFinished(3000)
                if not ret:
                    co_proc.kill()
            if pool_proc:
                pool_proc.terminate()
                ret = pool_proc.waitForFinished(3000)
                if not ret:
                    pool_proc.kill()
    
    def __start_python_server(self, cls, id):
        
        _proc = QtCore.QProcess()
        
        try:
            f,name,attr = imp.find_module(cls) 
            f.close()
            _file = os.path.realpath(name)
            _dir = os.path.dirname(_file)
            _proc.setWorkingDirectory(_dir)
            _proc.setStandardOutputFile('/dev/null')
            _proc.setStandardErrorFile('/dev/null')
            _proc.start("python",[_file, id])
            _proc.waitForStarted()
            s = _proc.state()
            if s != QtCore.QProcess.Running:
                _proc = None  
        except:
            _proc = None
        
        return _proc
    
    def __start_cpp_server(self, cls, id):
        
        _proc = QtCore.QProcess()
        
        try:
            _proc.setWorkingDirectory(os.path.realpath(os.path.curdir))
            _proc.start(cls,[id])
            _proc.waitForStarted()
            s = _proc.state()
            if s != QtCore.QProcess.Running:
                _proc = None  
        except:
            _proc = None
            
        return _proc
        
        
    def __start_servers(self, id):

        mot_proc = self.__start_python_server('SimuMotorCtrl', id)
        if not mot_proc:
            QtGui.QMessageBox.information(self, "Start motor simulator",
                                          "Motor simulator could not be found.\nPlease start the simulator by typing: 'python SimuMotorCtrl.py %s'" % id)
        yield mot_proc    
        
        co_proc = self.__start_python_server('SimuCoTiCtrl', id)
        if not co_proc:
            QtGui.QMessageBox.information(self, "Start counter simulator",
                                          "Counter simulator could not be found.\nPlease start the simulator by typing: 'python SimuCoTiCtrl.py %s'" % id)
        yield co_proc
        
        pool_proc = self.__start_cpp_server('Pool', id)
        if not pool_proc:
            QtGui.QMessageBox.information(self, "Start device pool",
                                          "Device pool could not be found.\nPlease start the device pool by typing: 'Pool %s'" % id)
        yield pool_proc

        ms_proc = self.__start_python_server('MacroServer', id)
        if not ms_proc:
            QtGui.QMessageBox.information(self, "Start macro server",
                                          "Macro server could not be found.\nPlease start the macro server by typing: 'MacroServer %s'" % id)
        yield ms_proc
        
    
def startGUI():
    if mode == 2:
        # reduce the amount of logging
        tau.core.utils.Logger.setLogLevel(tau.core.utils.Logger.Info)
    app = QtGui.QApplication(sys.argv)
    wnd = NewSystemDialog()
    wnd.show()
    res = app.exec_()
    print "Application finished"
    sys.exit(res)
        
def startConsole():
    try:
        console = Console(Simulation())
        console.go()
    except KeyboardInterrupt, e:
        print
        print "Canceled..."
        sys.exit(0)
    
if __name__ == "__main__":

    if mode > 0:
        startGUI()
    else:
        print "Qt4 is not available. Starting console mode..."
        startConsole()
    
    