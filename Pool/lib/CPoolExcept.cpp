#include "PyUtils.h"
#include <iostream>
#include "CPoolExcept.h"

namespace Pool_ns
{

void Except::print_exception(const PoolFailed &pf)
{
    std::vector<PoolError>::const_iterator it = pf.errors.begin();
    
    for(; it != pf.errors.end(); ++it)
    {
        std::cerr << "Pool exception" << std::endl;
        std::cerr << "Error : " << it->reason << std::endl;
        std::cerr << "Desc : " << it->desc << std::endl;
        std::cerr << "Origin : " << it->origin << std::endl;
        std::cerr << std::endl;
    }
}

void Except::throw_python_exception(const char *reason,
                                    const char *desc,
                                    const char *origin)
    {
        std::string r,d,o;
        PythonUtils::instance()->translate_exception(r,d,o);

        PoolError err(reason, desc, origin);
        PoolFailed pf(err);
        pf.errors.push_back(PoolError(r,d,o));
        throw pf;
    }

}
