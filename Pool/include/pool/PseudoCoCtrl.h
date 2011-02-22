#ifndef PSEUDOCOCTRL_H_
#define PSEUDOCOCTRL_H_

#include <pool/PseudoCtrl.h>

/**
  * class PseudoCounterController
  */

class PseudoCounterController : public PseudoController
{
public:
	PseudoCounterController(const char *inst): PseudoController(inst) {}
	virtual ~PseudoCounterController() {}

	virtual double Calc(int32_t, std::vector<double> &) = 0;
};

#endif /*PSEUDOCOCTRL_H_*/
