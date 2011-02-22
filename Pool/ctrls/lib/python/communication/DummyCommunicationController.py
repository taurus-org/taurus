from pool import CommunicationController
import PyTango
import time

class ChState:
	ChStateDisabled = 0
	ChStateOpen = 1
	ChStateClosed = 2
	
class DummyCommunicationController(CommunicationController):
	"""This class is the Tango Sardana Echo like communication controller in Python"""

	ctrl_extra_attributes = {}
	
	gender = "Echo"
	model  = "Simplest Echo"
	organization = "CELLS - ALBA"
	MaxDevice = 256
	
	def __init__(self,inst,props):
		CommunicationController.__init__(self,inst,props)
		print "[DummyCommunicationController] ctor for instance",inst
		self.state = 256*[ChState.ChStateDisabled,]
		self.last_write = 256*["",]
		
	def OpenOne(self,ind):
		if self.state[ind - 1] != ChState.ChStateDisabled:
			self.state[ind - 1] = ChState.ChStateOpen
		else:
			raise "Trying to open an invalid channel"
	
	def CloseOne(self,ind):
		if self.state[ind - 1] != ChState.ChStateDisabled:
			self.state[ind - 1] = ChState.ChStateClosed
		else:
			raise "Trying to close an invalid channel"
		
	def AddDevice(self,ind):
		print "[DummyCommunicationController]",self.inst_name,": In AddDevice method for index",ind
		self.state[ind - 1] = ChState.ChStateOpen
		self.last_write[ind - 1] = ""
		
	def DeleteDevice(self,ind):
		print "[DummyCommunicationController]",self.inst_name,": In DeleteDevice method for index",ind
		self.state[ind - 1] = ChState.ChStateDisabled
		self.last_write[ind - 1] = ""
		
	def StateOne(self,ind):
		print "[DummyCommunicationController]",self.inst_name,": In StateOne method for index",ind
		return (PyTango.DevState.ON, "I am Ok!")

	def ReadOne(self,ind,max_read_len):
		print "[DummyCommunicationController]",self.inst_name,": In ReadOne method for index",ind
		if self.state[ind - 1] == ChState.ChStateDisabled:
			raise "Trying to read in an invalid channel"
		if self.state[ind - 1] == ChState.ChStateClosed:
			raise "Trying to read in a closed channel"
				
		if max_read_len >= 0:
			return self.last_write[ind-1][:max_read_len]
		else:
			return self.last_write[ind-1]

	def ReadLineOne(self,ind):
		print "[DummyCommunicationController]",self.inst_name,": In ReadLineOne method for index",ind
		if self.state[ind - 1] == ChState.ChStateDisabled:
			raise "Trying to read line in an invalid channel"
		if self.state[ind - 1] == ChState.ChStateClosed:
			raise "Trying to read line in a closed channel"
		
		try:
			idx = self.last_write[ind-1].index('\n')
			return self.last_write[ind-1][:idx+1]
		except:
			return self.last_write[ind-1]
		
	def WriteOne(self,ind,buf,write_len):
		print "[DummyCommunicationController]",self.inst_name,": In WriteOne method for index",ind
		print "          with data = ",buf, " write_len = ", write_len
		if self.state[ind - 1] == ChState.ChStateDisabled:
			raise "Trying to write in an invalid channel"
		if self.state[ind - 1] == ChState.ChStateClosed:
			raise "Trying to write in a closed channel"
		
		self.last_write[ind-1] = buf
		return write_len

	def WriteReadOne(self,ind,buff,write_len,max_read_len):
		print "[DummyCommunicationController]",self.inst_name,": In WriteReadOne method for index",ind
		print "          with data = ",buf, " write_len = ", write_len, " max_read_len = ", max_read_len
		if self.state[ind - 1] == ChState.ChStateDisabled:
			raise "Trying to writeread in an invalid channel"
		if self.state[ind - 1] == ChState.ChStateClosed:
			raise "Trying to writeread in a closed channel"
				
		self.last_write[ind-1] = buf
		
		if max_read_len >= 0:
			return self.last_write[ind-1][:max_read_len]
		else:
			return self.last_write[ind-1]		
	
	def GetExtraAttributePar(self,ind,name):
		pass

	def SetExtraAttributePar(self,ind,name,value):
		pass
		
	def SendToCtrl(self,in_data):
		print "Received value =",in_data
		return in_data
	
	def __del__(self):
		print "[DummyCommunicationController]",self.inst_name,": Aarrrrrg, I am dying"

		
if __name__ == "__main__":
	obj = DummyCommunicationController('test')
