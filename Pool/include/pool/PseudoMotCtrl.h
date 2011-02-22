#ifndef PSEUDOMOTCTRL_H_
#define PSEUDOMOTCTRL_H_

#include <vector>
#include <map>
#include <tango.h>
#include <pool/PseudoCtrl.h>

/**
 * The pseudo motor controller base class
 */
class PseudoMotorController:public PseudoController
{
public:
	PseudoMotorController(const char *inst): PseudoController(inst) {}
	virtual ~PseudoMotorController() {}
	
	virtual double CalcPhysical(int32_t, std::vector<double> &) = 0;
	virtual double CalcPseudo(int32_t, std::vector<double> &) = 0;
	
	/**
	 * Default implementation: go through CalcPhysical for all motors involved
	 * 
	 * @param	pseudo_pos		[in]	list of pseudo motor positions
	 * @param	physical_pos	[out]	list of physical motor positions
	 * 
	 * @warning It is crucial that this method is called with physical_pos 
	 *           vector containning the correct number of elements.
	 */ 
	virtual void CalcAllPhysical(std::vector<double> &pseudo_pos, std::vector<double> &physical_pos)
	{
		// The physical_pos vector passed as argument should already
		// be initialized with the correct size.
		std::vector<double>::size_type m_nb = physical_pos.size();
		assert(m_nb > 0);
		
		for(std::vector<double>::size_type axis = 0; axis < m_nb ; axis++)
			physical_pos[axis] = CalcPhysical(axis+1, pseudo_pos);
	}

	/**
	 * Default implementation: go through CalcPseudo for all pseudo motors 
	 * involved
	 * 
	 * @param	physical_pos	[in]	list of physical motor positions
	 * @param	pseudo_pos		[out]	list of pseudo motor positions
	 * 
	 * @warning It is crucial that this method is called with pseudo_pos 
	 *           vector containning the correct number of elements.
	 */ 
	virtual void CalcAllPseudo(std::vector<double> &physical_pos, std::vector<double> &pseudo_pos)
	{
		// The physical_pos vector passed as argument should already
		// be initialized with the correct size.
		std::vector<double>::size_type pm_nb = pseudo_pos.size();
		assert(pm_nb > 0);
		
		for(std::vector<double>::size_type axis = 0; axis < pm_nb ; axis++)
			pseudo_pos[axis] = CalcPseudo(axis+1, physical_pos);	
	}
	
};

#endif /*PSEUDOMOTCTRL_H_*/
