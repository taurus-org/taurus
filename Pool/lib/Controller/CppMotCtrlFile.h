#ifndef CPPMOTCTRLFILE_H_
#define CPPMOTCTRLFILE_H_

#include "CppCtrlFile.h"

namespace Pool_ns
{

/** 
 * The CppUndefCtrlFile class declaration 
 */
class CppUndefCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppUndefCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppUndefCtrlFile(const std::string &);
    
    /// Destructor for CppUndefCtrlFile class
    ~CppUndefCtrlFile();
};


/** 
 * The CppMotCtrlFile class declaration 
 */
class CppMotCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppMotCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppMotCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppMotCtrlFile class from the CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppMotCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppMotCtrlFile();
};


/** 
 * The CppPseudoMotCtrlFile class declaration 
 */
class CppPseudoMotCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppPseudoMotCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppPseudoMotCtrlFile(const std::string &);
    
    /**
     * "Copy" constructor for CppPseudoMotCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */	
    CppPseudoMotCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppPseudoMotCtrlFile();

protected:

    /**
     * Obtains particular pseudo motor information of a controller class that 
     * resides in the file represented by this class. 
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.
     */
    virtual void get_particular_info(const std::string &, vector<string> &);

    /**
     * Obtains particular pseudo motor information of a controller instance of
     * a class that resides in the file represented by this class.
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param ctrl_inst_name [in]  The controller instance name.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.
     */	
    virtual void get_particular_info(const std::string &ctrl_class_name, 
                                     const std::string &ctrl_inst_name, 
                                     vector<string> &info)
    { get_particular_info(ctrl_class_name,info); }
};


/**
 * The CppCoTiCtrlFile class declaration
 */
class CppCoTiCtrlFile : public CppCtrlFile
{
public:
    
    /**
     * constructor for CppCoTiCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppCoTiCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppCoTiCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppCoTiCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppCoTiCtrlFile();		
};


/**
 * The CppZeroDCtrlFile class declaration
 */
class CppZeroDCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppZeroDCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppZeroDCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppZeroDCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppZeroDCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppZeroDCtrlFile();		
};

/**
 * The CppOneDCtrlFile class declaration
 */
class CppOneDCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppOneDCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppOneDCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppOneDCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppOneDCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppOneDCtrlFile();		
};

/**
 * The CppTwoDCtrlFile class declaration
 */
class CppTwoDCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppTwoDCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppTwoDCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppTwoDCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppTwoDCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppTwoDCtrlFile();		
};

/**
 * The CppPseudoCoCtrlFile class declaration
 */
class CppPseudoCoCtrlFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppPseudoCoCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppPseudoCoCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppPseudoCoCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference
     * @param dev        Pointer to the Pool object.
     */
    CppPseudoCoCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppPseudoCoCtrlFile();	
    
protected:
    
    /**
     * Obtains particular pseudo counter information of a controller class that 
     * resides in the file represented by this class. 
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.
     */
    virtual void get_particular_info(const std::string &, vector<string> &);

    /**
     * Obtains particular pseudo counter information of a controller instance of
     * a class that resides in the file represented by this class.
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param ctrl_inst_name [in]  The controller instance name.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.

     */	
    virtual void get_particular_info(const std::string &ctrl_class_name, 
                                     const std::string &ctrl_inst_name, 
                                     vector<string> &info)
    { get_particular_info(ctrl_class_name,info); }
};


/**
 *  The CppComCtrlFile class declaration
 */
class CppComCtrlFile : public CppCtrlFile
{
public:
    
    /**
     * constructor for CppComCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppComCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppComCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppComCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppComCtrlFile();
};


/**
 *  The CppIORegisterCtrlFile class declaration
 */
class CppIORegisterCtrlFile : public CppCtrlFile
{
public:
    
    /**
     * constructor for CppIORegisterCtrlFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppIORegisterCtrlFile(const std::string &);

    /**
     * "Copy" constructor for CppIORegisterCtrlFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppIORegisterCtrlFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppIORegisterCtrlFile();

protected:

    /**
     * Obtains particular input/output register information of a controller class that 
     * resides in the file represented by this class. 
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.
     */
    virtual void get_particular_info(const std::string &, vector<string> &);

    /**
     * Obtains particular input/output information of a controller instance of
     * a class that resides in the file represented by this class.
     * 
     * @param ctrl_class_name [in] The controller class for which to retrieve 
     *                             the information.
     * @param ctrl_inst_name [in]  The controller instance name.
     * @param info [out]           The controller information related to the
     *                             given controller class. The particular
     *                             information is appended to the vector.
     */	
    virtual void get_particular_info(const std::string &ctrl_class_name, 
                                     const std::string &ctrl_inst_name, 
                                     vector<string> &info)
    { get_particular_info(ctrl_class_name,info); }

        
};

/**
 * The CppConstraintFile class declaration
 */
class CppConstraintFile : public CppCtrlFile
{
public:

    /**
     * constructor for CppConstraintFile class
     * 
     * @param f_name     The controller class file name (cpp lib or python module)
     * @param dev        Pointer to the Pool object.
     */
    CppConstraintFile(const std::string &);

    /**
     * "Copy" constructor for CppConstraintFile class from the 
     * CppUndefCtrlFile class
     * 
     * @param undef_ctrl The original CppUndefCtrlFile object reference 
     * @param dev        Pointer to the Pool object.
     */
    CppConstraintFile(CppUndefCtrlFile &);
    
    /// Destructor
    ~CppConstraintFile();		
};

} // End of Pool_ns namespace

#endif /*CPPMOTCTRLFILE_H_*/
