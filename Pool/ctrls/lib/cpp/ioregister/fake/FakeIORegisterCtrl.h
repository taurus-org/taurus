#ifndef _FAKEIOREGISTERCTRL_H_
#define _FAKEIOREGISTERCTRL_H_

#include <tango.h>
#include <pool/IORegisterCtrl.h>

extern "C"
{
	/**
	 * The create controller method for the DummyCom controller.
	 */	
	Controller *_create_FakeIORegisterController(const char *,vector<Controller::Properties> &);
}

/**
 * @brief A IORegister controller that fakes send and receive operations
 */
class FakeIORegisterController:public IORegisterController
{
	double CppComCh_extra_2;	///< dummy property value. Means nothing. For test purposes
	
public:
	/// Constructor
	FakeIORegisterController(const char *,vector<Controller::Properties> &);
	/// Destructor
	virtual ~FakeIORegisterController();

	/**
	 *	@name Management
	 *	Controller add/remove devices related methods
	 */
	//@{
	
	/**
	 * @brief adds (activates) a device in the controller given by the index.
	 * 
	 * @param idx the device index to be added (starts with 1).
	 */
	virtual void AddDevice(int32_t idx);
	
	/**
	 * @brief removes a device in the controller given by the index.
	 * 
	 * @param idx the device index to be removed (starts with 1).
	 */
	virtual void DeleteDevice(int32_t idx);
	//@}
	
	/**
	 * Atempts to read data into the given buffer. 
	 * The length of the data can be checked by inspecting the buffer.
	 * 
	 * @param idx - ioregister id
	 * @param max_read_len - max length of buff to read.
	 *                        0 empties the read_buff and returns 0.
	 *                       -1 (default value) to read all available data from the channel.
	 */
	virtual string &ReadOne(int32_t, int32_t max_read_len = -1); 
	

		
	/**
	 * @param idx - ioregister id
	 * @param write_buff - buffer which contains data to be written
	 * @param write_len - length of buffer to write.
	 *                    0 will not write anything
	 *                    -1 (default value) will atempt to write the entire contents of the write_buff
	 * @return the length of the data actually written
	 */
	virtual int32_t WriteOne(int32_t, string &, int32_t write_len = -1); 
	

	/**
	 *	@name State
	 *	Controller state related methods.
	 */
	//@{
	/**
	 * @brief StateOne.
	 * 
	 * @param idx         [in] device index (starts with 1).
	 * @param ctrl_state [out] pointer to the state object that will contain the
	 *                         controller state.  
	 */	
	virtual void StateOne(int32_t, Controller::CtrlState *);
	//@}
	
	/**
	 *	@name Extra Attributes
	 *	Extra attributes related methods.
	 */
	//@{
	/** 
	 * @brief Sets the given extra attribute parameter with the given value on
	 *        the given device index.
	 * 
	 * @param idx       [in] device index (starts at 1)
	 * @param attr_name [in] extra attribute name
	 * @param ctrl_data [in] new value reference object
	 */	
	virtual void SetExtraAttributePar(int32_t, string &, Controller::CtrlData &);
	
	/** 
	 * @brief Get the given extra attribute parameter value for the given device
	 *        index.
	 * 
	 * @param idx       [in] device index (starts at 1)
	 * @param attr_name [in] extra attribute name
	 * 
	 * @return a CtrlData object containning the extra attribute value
	 */	
	virtual Controller::CtrlData GetExtraAttributePar(int32_t, string &);
	
	//@}

	/**
	 * @brief Sends the given string to the controller.
	 * 
	 * @param the_str the string to be sent.
	 * 
	 * @return a string with the controller response.
	 */
	virtual string SendToCtrl(string &);
					
protected:
	void bad_data_type(string &);
	
	int32_t read_nb;          ///< number of reads invoked on this object
	int32_t write_nb;         ///< number of writes invoked on this object
};

#endif /*_DUMMYCOMCHCTRL_H_*/
