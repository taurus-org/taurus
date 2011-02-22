#include <pool/ComCtrl.h>
#include <sstream>
#include <stdint.h>

ComController::ComController(const char *inst):Controller(inst),meth_not_impl("Pool_meth_not_implemented")
{
	//cout << "In the ComController class ctor" << endl;

	comCh_Overflow = INT_MAX;
}

ComController::~ComController ( )
{
	//cout << "In the ComController class dtor" << endl;
}

string &ComController::ReadOne(int32_t, int32_t /*max_read_len = -1*/)
{
	//cout << "Default ReadOne method returning 0" << endl;
	read_buff.clear();
	return read_buff;
}

string &ComController::ReadLineOne(int32_t )
{
	//cout << "Default ReadOne method returning 0" << endl;
	read_buff.clear();
	return read_buff;
}

int32_t ComController::WriteOne(int32_t, string &, int32_t /*write_len = -1*/)
{
	//cout << "Default WriteOne method returning 0" << endl;
	return 0;
}

string &ComController::WriteReadOne(int32_t, string &ostr, int32_t /*write_len = -1*/, int32_t /*max_read_len = -1*/)
{
	//cout << "Default WriteReadOne method returning 0" << endl;
	read_buff.clear();
	return read_buff;
}
