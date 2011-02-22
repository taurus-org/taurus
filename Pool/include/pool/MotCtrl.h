#ifndef MOTCTRL_H_
#define MOTCTRL_H_

#include <vector>
#include <pool/Ctrl.h>

#define		HOME				0x1
#define		UPPER_SWITCH		0x2
#define		LOWER_SWITCH		0x4

/**
 * The motor controller base class
 */
class MotorController:public Controller
{
public:
    
    /** 
     * Constructor
     * 
     * @param inst [in] the controller instance name.
     */	
    MotorController(const char *);
    
    /// Destructor
    virtual ~MotorController();
    
    /**
     * Motor Controller state structure
     */
    struct MotorState: public Controller::CtrlState
    {
        int32_t    switches;
    };
        
//
// Methods to move motor(s)
//

    /**
     * @name Start motion
     * The group of methods that relate to a motion
     */
    //@{
    /**
     * @brief PreStartAll. Default implementation does nothing.
     */
    virtual void PreStartAll() {}
    
    /**
     * @brief PreStartOne. Default implementation returns <code>true</code>.
     */	
    virtual bool PreStartOne(int32_t, double) {return true;}
    
    /**
     * @brief StartOne. Default implementation does nothing.
     */	
    virtual void StartOne(int32_t, double) {}
    
    /**
     * @brief StartAll. Default implementation does nothing.
     */	
    virtual void StartAll() {}
    //@}
    
    
    /**
     * @name Position methods
     * The group of methods to read motor(s) position
     */
    //@{

    /**
     * @brief PreReadAll. Default implementation does nothing.
     */	
    virtual void PreReadAll() {}

    /**
     * @brief PreReadOne. Default implementation does nothing.
     */	
    virtual void PreReadOne(int32_t ) {}

    /**
     * @brief ReadAll. Default implementation does nothing.
     */	
    virtual void ReadAll() {}

    /**
     * @brief ReadOne. Default implementation does nothing.
     */	
    virtual double ReadOne(int32_t );
    
    /**
     * @brief AbortOne. Default implementation does nothing.
     */	
    virtual void AbortOne(int32_t ) {}
    
    /**
     * @brief DefinePosition. Default implementation does nothing.
     */	
    virtual void DefinePosition(int32_t, double) {}
    
    //@}
    
    /**
     * @name Par methods
     * Methods to Get/Set motor parameters
     */
    //@{
    
    /**
     * @brief GetPar. Default implementation returns a double with 'NaN'
     * @param[in] idx        motor index (starts with 1)
     * @param[in] param_name parameter name
     * @return motor parameter value
     */	
    virtual Controller::CtrlData GetPar(int32_t, std::string &);

    /**
     * @brief GetPar. Default implementation does nothing
     * @param[in] idx         motor index (starts with 1)
     * @param[in] param_name  parameter name
     * @param[in] param_value parameter value
     */	
    virtual void SetPar(int32_t, std::string &, Controller::CtrlData &) {}
    
protected:
    /** parameter for NaN */
    double			mot_NaN;
    
    /** default string for method not implemented */
    std::string		meth_not_impl;
};

        
#endif /*MOTCTRL_H_*/
