#ifndef _COMCONTROLLER_H
#define _COMCONTROLLER_H

#include <pool/Ctrl.h>

/**
  * class ComController
  */

class ComController : public Controller
{
public:
	std::string read_buff;

	ComController(const char *);
	virtual ~ComController();

	/**
	 * @param idx - communication channel id
	 */
	virtual void OpenOne(int32_t ) {}

	/**
	 * @param idx - communication channel id
	 */
	virtual void CloseOne(int32_t) {}

	/**
	 * Atempts to read data into the given buffer.
	 * The length of the data can be checked by inspecting the buffer.
	 *
	 * @param idx - communication channel id
	 * @param max_read_len - max length of buff to read.
	 *                        0 empties the read_buff and returns 0.
	 *                       -1 to read all available data from the channel.
	 */
	virtual std::string &ReadOne(int32_t, int32_t max_read_len = -1);

	/**
	 * Atempts to read data into the given buffer up to a new line character.
	 * The length of the data can be checked by inspecting the buffer.
	 *
	 * @param idx - communication channel id
	 */
	virtual std::string &ReadLineOne(int32_t );

	/**
	 * @param idx - communication channel id
	 * @param write_buff - buffer which contains data to be written
	 * @param write_len - length of buffer to write.
	 *                    0 will not write anything
	 *                    -1 (default value) will atempt to write the entire contents of the write_buff
	 * @return the length of the data actually written
	 */
	virtual int32_t WriteOne(int32_t, std::string &, int32_t write_len = -1);

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
	virtual std::string &WriteReadOne(int32_t, std::string &, int32_t write_len = -1, int32_t max_read_len = -1);

protected:
	std::string		meth_not_impl;
	int32_t			comCh_Overflow;
};

#endif // COMCHCONTROLLER_H
