#ifndef _CPOOL_EXCEPT_H_
#define _CPOOL_EXCEPT_H_

#include <string>
#include <vector>

namespace Pool_ns
{

struct PoolError
{
    std::string     reason;
    std::string     desc;
    std::string     origin;
    
    PoolError() 
    {}

    PoolError(const std::string& r, const std::string& d, const std::string& o):
    reason(r), desc(d), origin(o)
    {}
    
    PoolError(const char *r, const char *d, const char *o):
    reason(r), desc(d), origin(o)
    {}

    PoolError(const char *r, const std::string &d, const char *o):
    reason(r), desc(d), origin(o)
    {}
};

struct PoolFailed
{
    std::vector<PoolError> errors;
    
    PoolFailed()
    {}
    
    PoolFailed(PoolError &e)
    { errors.push_back(e); }
};

class Except
{
public:

    static inline void throw_exception(const char *reason,
                                       const char *desc,
                                       const char *origin)
    {
        PoolError err(reason, desc, origin);
        throw PoolFailed(err);
    }
    
    static inline void throw_exception(const char *reason,
                                       const std::string &desc,
                                       const char *origin)
    {
        PoolError err(reason, desc, origin);
        throw PoolFailed(err);
    }
    
    static void throw_python_exception(const char *reason,
                                       const char *desc,
                                       const char *origin);
    
    static void print_exception(const PoolFailed &pf);
    
};

class PoolThrower
{
public:
    virtual ~PoolThrower() 
    { }

    virtual inline void throw_exception(const char *reason,
                                        const char *desc,
                                        const char *origin)
    { Except::throw_exception(reason, desc, origin); }
    
    virtual inline void throw_exception(const char *reason,
                                        const std::string &desc,
                                        const char *origin)
    { Except::throw_exception(reason, desc, origin); }
    
    virtual inline void throw_python_exception(const char *reason,
                                               const char *desc,
                                               const char *origin)
    { Except::throw_python_exception(reason, desc, origin); }
    
    static inline void print_exception(const PoolFailed &pf)
    { Except::print_exception(pf); }
};

} 

#endif // _CPOOL_EXCEPT_H_
