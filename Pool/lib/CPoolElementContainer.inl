#include <sstream>

namespace Pool_ns
{

inline PoolThrower* PoolElementContainer::get_thrower()
{
    return thrower;
}

inline CtrlFiCa* PoolElementContainer::get_controller_class(ElementId id)
{
    CtrlClassIdMapIt it = ctrl_class_ids.find(id);

    if (it == ctrl_class_ids.end())
    {
        std::ostringstream o;
        o << "No controller class with ID " << id << " found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownCtrlClass", o.str(),
                                 "PoolElementContainer::get_controller_class");
    }
    return it->second;
}

inline CtrlFile* PoolElementContainer::get_controller_file(ElementId id)
{
    CtrlFileIdMapIt it = ctrl_file_ids.find(id);

    if (it == ctrl_file_ids.end())
    {
        std::ostringstream o;
        o << "No controller file with ID " << id << " found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownCtrlFile", o.str(),
                                 "PoolElementContainer::get_controller_file");
    }
    return it->second;
}

inline bool PoolElementContainer::remove_element(const std::string &name, 
                                          bool any_name /*= false*/)
{
    try
    {
        return remove_element(get_element(name, any_name)->get_id());
    }
    catch(...)
    {
        return false;
    }
}

inline PoolElement *PoolElementContainer::get_element(ElementId id)
{ 
    ElemIdMapIt it = element_ids.find(id);

    if (it == element_ids.end())
    {
        std::ostringstream o;
        o << "No element with ID " << id << " found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownElement", o.str(),
                                 "PoolElementContainer::get_element");
    }
    return it->second;
}

inline PoolElement *PoolElementContainer::get_element(ElementId id,
                                                      ElementType type)
{
    PoolElement *pe = get_element(id);
                                
    if (pe->get_type() != type)
    {
        std::ostringstream o;
        o << "No " << ElementTypeStr[type] << " with ID " << id << " found."
          << " A " << ElementTypeStr[pe->get_type()] << " named '" << pe->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("PoolElementContainer_WrongElementType", o.str(),
                                 "PoolElementContainer::get_element");
    }
    return pe;
}

inline int32_t PoolElementContainer::get_element_nb(ElementType type)
{
    return (int32_t)element_types.count(type);
}

inline void PoolElementContainer::get_all_elements(ElementType type, 
                                                   PoolElementTypeIt &beg,
                                                   PoolElementTypeIt &end)
{
    PairElemTypeMultiMapIt p;
    get_range(type, p);
    beg = p.first; 
    end = p.second;
}

inline void PoolElementContainer::get_range(ElementType type,
                                            PairElemTypeMultiMapIt &p)
{
    p = element_types.equal_range(type);
}

inline bool PoolElementContainer::element_exists(const std::string &name,
                                                 bool any_name /*=false*/)
{
    try { get_element(name, any_name); return true; }
    catch(...) { return false; }
}

inline bool PoolElementContainer::element_exists(const std::string &name, 
                                                 ElementType type,
                                                 bool any_name /*=false*/)
{
    try { get_element(name, type, any_name); return true; }
    catch(...) { return false; }
}

}
