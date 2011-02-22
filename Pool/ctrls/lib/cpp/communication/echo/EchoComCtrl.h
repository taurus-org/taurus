#ifndef _DUMMYCOMCTRL_H_
#define _DUMMYCOMCTRL_H_

#include <pool/ComCtrl.h>

extern "C"
{
	Controller *_create_EchoCommunicationController(
			const char *,
			std::vector<Controller::Properties> &);
}

/**
 * Current channel state 
 */
enum ChState { ChDisabled = 0, ChOpen, ChClosed };

/**
 * An 'echo like' communication controller class
 */
class EchoCommunicationController:public ComController
{
	
public:
	EchoCommunicationController(const char *,vector<Controller::Properties> &);
	virtual ~EchoCommunicationController();

	virtual void AddDevice(int32_t idx);
	virtual void DeleteDevice(int32_t idx);

	/**
	 * Atempts to read data into the given buffer. 
	 * The length of the data can be checked by inspecting the buffer.
	 * 
	 * @param[in] idx communication channel id
	 * @param[in] max_read_len max length of buff to read.
	 *                         0 empties the read_buff and returns 0.
	 *                         -1 (default value) to read all available data
	 *                         from the channel.
	 */
	virtual string &ReadOne(int32_t, int32_t max_read_len = -1); 
	
	/**
	 * Atempts to read data into the given buffer up to a new line character. 
	 * The length of the data can be checked by inspecting the buffer.
	 * 
	 * @param[in] idx communication channel id
	 */
	virtual string &ReadLineOne(int32_t); 
		
	/**
	 * @param idx - communication channel id
	 * @param write_buff - buffer which contains data to be written
	 * @param write_len - length of buffer to write.
	 *                    0 will not write anything
	 *                    -1 (default value) will atempt to write the entire contents of the write_buff
	 * @return the length of the data actually written
	 */
	virtual int32_t WriteOne(int32_t, string &, int32_t write_len = -1); 
	
	/**
	 * @param idx - communication channel id
	 * @param write_buff - buffer which contains data to be written
	 * @param write_len - length of buffer to write.
	 *                    0 will not write anything
	 *                    -1 will atempt to write the entire contents of the write_buff
	 * @param max_read_len - max length of buff to read.
	 *                        0 empties the read_buff and returns 0.
	 *                       -1 to read all available data from the channel.
	 * @return the length of the data actually written
	 */
	virtual string &WriteReadOne(int32_t, string &, int32_t write_len = -1, int32_t max_read_len = -1); 
	
	virtual void StateOne(int32_t, Controller::CtrlState *);
	
	virtual Controller::CtrlData GetExtraAttributePar(int32_t, string &);
	virtual void SetExtraAttributePar(int32_t, string &, Controller::CtrlData &);
	
	virtual string SendToCtrl(string &);
					
protected:
	void bad_data_type(string &);
	
	int32_t read_nb;
	int32_t write_nb;

	vector<ChState> state;
	vector<string> last_write;
};

#endif /*_DUMMYCOMCHCTRL_H_*/
