import PyTango

class A:

	def push_event(self,e):
		print e.attr_value.value

def delete(pool):

	m_list = pool.read_attribute("MotorList").value
	for m in m_list:
		m_name = m.split()[0]
		print "Deleting motor %s..." % m_name,
		try:
			pool.DeleteMotor(m_name)
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])
			print e

	ct_list = pool.read_attribute("ExpChannelList").value
	for ct in ct_list:
		ct_name = ct.split()[0]
		print "Deleting counter %s..." % ct_name,
		try:
			pool.DeleteExpChannel(ct_name)
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])
			print e

	ctrl_list = pool.read_attribute("ControllerList").value
	for ctrl in ctrl_list:
		ctrl_name = ctrl.split()[0]
		print "Deleting controller %s..." % ctrl_name,
		try:
			pool.DeleteController(ctrl_name)
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])


def load_with_dummy_ct(pool,start_idx,nb):
	ctrl_name = "DummyCTStressCtrl"
	pool.CreateController(["CounterTimer","DummyCounterTimerController.py","DummyCounterTimerController",ctrl_name])

	for i in xrange(nb):
		ct_name = "ct_stress_%d" % (start_idx + i)
		print "Creating counter/timer %s..." % ct_name,
		try:
			pool.CreateExpChannel([[i+1],[ct_name,ctrl_name]])
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])


def load_with_simu_motor(pool,start_idx,nb):
	ctrl_name = "SimuMotStressCtrl"
	pool.CreateController(["Motor","SimuMotorCtrl.la","SimuMotorController",ctrl_name,"DevName","tcoutinho/simulator/motctrl2"])

	for i in xrange(nb):
		m_name = "mot_stress_%d" % (start_idx + i)
		print "Creating motor %s..." % m_name,
		try:
			pool.CreateMotor([[i+1],[m_name,ctrl_name]])
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])


def load_with_dummy_motor(pool,start_idx,nb):
	ctrl_name = "DummyMotStressCtrl"
	pool.CreateController(["Motor","DummyMotorController.py","DummyMotorController",ctrl_name])

	for i in xrange(nb):
		m_name = "mot_stress_%d" % (start_idx + i)
		print "Creating motor %s..." % m_name,
		try:
			pool.CreateMotor([[i+1],[m_name,ctrl_name]])
			print "[DONE]"
		except PyTango.DevFailed, e:
			print "%s [FAILED!]" % str(e.args[0]['reason'])

def main():
	pool = PyTango.DeviceProxy("tcoutinho/pool/05")

	delete(pool)

	sim_mot_nb = 64
	dummy_mot_nb = 512
	dummy_ct_nb = 150
	
	load_with_simu_motor(pool,1,sim_mot_nb)
	load_with_dummy_motor(pool,sim_mot_nb+1,dummy_mot_nb)

#	load_with_dummy_ct(pool,1,dummy_ct_nb)


if __name__ == "__main__":
	main()
