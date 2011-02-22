#include "CPoolElementContainer.h"
#include <algorithm>
#include <functional>
#include <assert.h>

namespace Pool_ns
{

PoolElementContainer::PoolElementContainer(PoolThrower *t)
{
    thrower = (t == NULL) ? new PoolThrower() : t;
}

PoolElementContainer::~PoolElementContainer()
{
    SAFE_DELETE(thrower);
}

void PoolElementContainer::add_controller_class(CtrlFiCa *ctrl_class)
{
    // TODO
}

CtrlFiCa* PoolElementContainer::get_controller_class(const std::string &name)
{
    if (name.find('/') != std::string::npos)
    {
        std::ostringstream o;
        o << "Invalid controller class name: " << name << "." 
          << "Must be a simple class name (case sensitive)" << std::ends;
        thrower->throw_exception("PoolElementContainer_InvalidCtrlClass", o.str(),
                                 "PoolElementContainer::get_controller_class");
    }
    
    CtrlClassNameMapIt it = ctrl_class_names.find(name);

    if (it == ctrl_class_names.end())
    {
        std::ostringstream o;
        o << "No controller class named " << name << " found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownCtrlClass", o.str(),
                                 "PoolElementContainer::get_controller_class");
    }
    return ctrl_class_ids[it->second];
}

void PoolElementContainer::add_element(PoolElement *pe)
{
    ElementId id = pe->get_id();
    ElementType type = pe->get_type();
    const std::string &name = pe->get_name();
    
    assert(id != InvalidId);
    assert(name.size() > 0);
    
    PoolElement *old_pe = NULL;
    
    try { old_pe = get_element(id); }
    catch(...) {}

    if (old_pe != NULL)
    {
        std::ostringstream o;
        o << "element with id '" << id << "' already exists as "
          << old_pe->get_name() << ". Impossible to add " << name << std::ends;
       
        thrower->throw_exception("PoolElementContainer_RepeatedElementId", 
                                 o.str(), "PoolElementContainer::add_element");
    }
    
    try { old_pe = get_element(name); }
    catch(...) {}

    if (old_pe != NULL)
    {
        std::ostringstream o;
        o << "element with name '" << name << "' already exists with id "
          << old_pe->get_id() << ". Impossible to add " << name << std::ends;
       
        thrower->throw_exception("PoolElementContainer_RepeatedElementName",
                                 o.str(), "PoolElementContainer::add_element");
    }
    
    element_ids[id] = pe;
    element_names[name] = id;
    element_types.insert(ElemTypeMultiMapVT(type, id));

    assert(element_ids.size() == element_names.size());
    assert(element_names.size() == element_types.size());
}

PoolElement* PoolElementContainer::rename_element(const std::string &old_name,
                                                  const std::string &new_name,
                                                  ElemSet &deps)
{
    PoolElement *pe = get_element(old_name);
    
    PoolElement *exists_element = NULL;
    try
    {
        exists_element = get_element(new_name);
    }
    catch(...)
    {}

    if (exists_element)
    {
        std::ostringstream o;
        o << "element '" << old_name << "' cannot be renamed to '" << new_name
          << "' because there is already a " 
          << FullElementTypeStr[exists_element->get_type()] << " with that name";
       
        thrower->throw_exception("PoolElementContainer_ElementExists",
                                 o.str(), "PoolElementContainer::rename_element");
    }
    
    // update internal maps
    element_names.erase(old_name);
    element_names[new_name] = pe->get_id();

    // update the element
    pe->set_name(new_name);
    
    // find which elements use this 
    deps.insert(pe);
    get_element_users(pe->get_id(), deps);
    
    for_each(deps.begin(), deps.end(), std::mem_fun(&PoolElement::update_info));
    
    return pe;
}

bool PoolElementContainer::remove_element(ElementId id)
{
    ElemIdMapIt id_it = element_ids.find(id);
    if(id_it == element_ids.end())
        return false;

    for(ElemNameMapIt it_str = element_names.begin(); 
        it_str != element_names.end(); ++it_str)
    {
        if(it_str->second == id)
        {
            element_names.erase(it_str);
            break;
        }
    }
    
    for(ElemTypeMultiMapIt it_type = element_types.begin(); 
        it_type != element_types.end(); ++it_type)
    {
        if(it_type->second == id)
        {
            element_types.erase(it_type);
            break;
        }
    } 

    delete id_it->second;
    element_ids.erase(id);

    assert(element_ids.size() == element_names.size());
    assert(element_names.size() == element_types.size());
    
    return true;
}

void PoolElementContainer::remove_all_elements(ElementType type)
{
    element_types.erase(type);
    
    for(ElemNameMapIt str_it = element_names.begin(); str_it != element_names.end();)
    {
        if(get_element(str_it->second)->get_type() == type)
            element_names.erase(str_it++);
        else
            ++str_it;
    }
    
    for(ElemIdMapIt id_it = element_ids.begin(); id_it != element_ids.end();)
    {
        if(id_it->second->get_type() == type)
        {
            delete id_it->second;
            element_ids.erase(id_it++);
        }
        else
            ++id_it;
    }

    assert(element_ids.size() == element_names.size());
    assert(element_names.size() == element_types.size());
}

PoolElement* PoolElementContainer::get_element(const std::string &name,
                                               bool any_name /*= false*/)
{
    ElemNameMapIt it_str = element_names.find(name);
    if (it_str == element_names.end() && (any_name == false)) 
    {
        std::ostringstream o;
        o << "No element with name '" << name << "' found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownElement", o.str(),
                                 "PoolElementContainer::get_element");
    }
    else if(it_str != element_names.end())
        return get_element(it_str->second);
    
    return get_element_by_full_name(name);
}

PoolElement* PoolElementContainer::get_element_by_full_name(const std::string &full_name)
{
    std::string full_name_lower(full_name);
    std::transform(full_name_lower.begin(), full_name_lower.end(), 
                   full_name_lower.begin(), ::tolower);
    
    for (ElemIdMapIt ite = element_ids.begin(); ite != element_ids.end(); ++ite)
    {
        PoolElement *pe = ite->second;
        std::string curr_full_name_lower(pe->full_name);
        std::transform(curr_full_name_lower.begin(), curr_full_name_lower.end(),
                       curr_full_name_lower.begin(), ::tolower);

        if (curr_full_name_lower == full_name_lower)
        {
            return pe;
        }
    }
    
    std::ostringstream o;
    o << "No element with name '" << full_name << "' found" << std::ends;
    thrower->throw_exception("PoolElementContainer_UnknownElement", o.str(),
                             "PoolElementContainer::get_element_by_full_name");
    return NULL;
}

ElementId PoolElementContainer::get_element_id(const std::string &name,
                                               bool any_name /*= false*/)
{
    // this method does not call get_element(<name>, <any name>) for efficiency
    // reasons
    ElemNameMapIt it_str = element_names.find(name);
    if (it_str == element_names.end() && (any_name == false)) 
    {
        std::ostringstream o;
        o << "No element with name '" << name << "' found" << std::ends;
        thrower->throw_exception("PoolElementContainer_UnknownElement", o.str(),
                                 "PoolElementContainer::get_element");
    }
    else if(it_str != element_names.end())
        return it_str->second;
    
    std::string name_lower(name);
    std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
    
    for (ElemIdMapIt ite = element_ids.begin(); ite != element_ids.end(); ++ite)
    {
        PoolElement *pe = ite->second;
        std::string full_name_lower(pe->full_name);
        std::transform(full_name_lower.begin(), full_name_lower.end(),
                       full_name_lower.begin(), ::tolower);

        if (full_name_lower == name_lower)
        {
            return ite->first;
        }
    }
    
    std::ostringstream o;
    o << "No element with name '" << name << "' found" << std::ends;
    thrower->throw_exception("PoolElementContainer_UnknownElement", o.str(),
                             "PoolElementContainer::get_element");
    return InvalidId;
}

PoolElement* PoolElementContainer::get_element(const std::string &name, 
                                               ElementType type,
                                               bool any_name /*= false*/)
{
    PoolElement *pe = get_element(name, any_name);
    ElementType pe_type = pe->get_type();
    
    if (pe_type != type)
    {
        std::ostringstream o;
        o << "No " << FullElementTypeStr[type] << " with name '" << name << "' found."
          << " A " << FullElementTypeStr[pe_type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("PoolElementContainer_WrongElementType", o.str(), 
                                 "PoolElementContainer::get_element");
    }    
    return pe;
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_users
//
void PoolElementContainer::get_element_users(ElementId elem_id, ElemIdVector &elems)
{
    ElemIdMap &all_elems = get_element_id_map();
    for(ElemIdMapIt it = all_elems.begin(); it != all_elems.end(); ++it)
    {
        if (it->second->is_member(elem_id))
            elems.push_back(elem_id);
    }
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_users
//
void PoolElementContainer::get_element_users(ElementId elem_id, ElemVector &elems)
{
    ElemIdMap &all_elems = get_element_id_map();
    for(ElemIdMapIt it = all_elems.begin(); it != all_elems.end(); ++it)
    {
        PoolElement *pe = it->second;
        if (pe->is_member(elem_id))
            elems.push_back(pe);
    }
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_users
//
void PoolElementContainer::get_element_users(ElementId elem_id, ElemIdSet &elems)
{
    ElemIdMap &all_elems = get_element_id_map();
    for(ElemIdMapIt it = all_elems.begin(); it != all_elems.end(); ++it)
    {
        if (it->second->is_member(elem_id))
            elems.insert(elem_id);
    }
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_users
//
void PoolElementContainer::get_element_users(ElementId elem_id, ElemSet &elems)
{
    ElemIdMap &all_elems = get_element_id_map();
    for(ElemIdMapIt it = all_elems.begin(); it != all_elems.end(); ++it)
    {
        PoolElement *pe = it->second;
        if (pe->is_member(elem_id))
            elems.insert(pe);
    }
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_types
//
void PoolElementContainer::get_element_types(ElemIdVector &elems, ElemTypeSet &elem_types)
{
    for(ElemIdVectorIt it = elems.begin(); it != elems.end(); ++it)
        elem_types.insert(get_element(*it)->get_type());
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_types
//
void PoolElementContainer::get_element_types(ElemVector &elems, ElemTypeSet &elem_types)
{
    for(ElemVectorIt it = elems.begin(); it != elems.end(); ++it)
        elem_types.insert((*it)->get_type());
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_types
//
void PoolElementContainer::get_element_types(ElemIdSet &elems, ElemTypeSet &elem_types)
{
    for(ElemIdSetIt it = elems.begin(); it != elems.end(); ++it)
        elem_types.insert(get_element(*it)->get_type());
}

//------------------------------------------------------------------------------
// PoolElementContainer::get_element_types
//
void PoolElementContainer::get_element_types(ElemSet &elems, ElemTypeSet &elem_types)
{
    for(ElemSetIt it = elems.begin(); it != elems.end(); ++it)
        elem_types.insert((*it)->get_type());
}


} // namespace
