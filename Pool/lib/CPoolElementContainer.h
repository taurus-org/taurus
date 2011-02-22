#ifndef _CPOOL_ELEMENTCONTAINER_H_
#define _CPOOL_ELEMENTCONTAINER_H_

#include "PyUtils.h"
#include "CtrlFiCa.h"
#include "CtrlFile.h"
#include "CPoolDefs.h"
#include "CPoolElement.h"
#include <map>
#include <set>

namespace Pool_ns
{

class PoolElementContainer
{
protected:
    
    typedef ElemIdMap::value_type                     ElemIdMapVT;
    typedef ElemNameMap::value_type                   ElemNameMapVT;
    typedef ElemTypeMultiMap::value_type              ElemTypeMultiMapVT;

    typedef std::pair<ElemTypeMultiMapIt, ElemTypeMultiMapIt> PairElemTypeMultiMapIt;
    
    virtual void add_element(PoolElement *);
    
    virtual PoolElement* rename_element(const std::string &, const std::string &, ElemSet &);
    
    virtual bool remove_element(ElementId );
    
    inline bool remove_element(const std::string &, bool any_name = false);
    
    virtual void remove_all_elements(ElementType );

    virtual void add_controller_class(CtrlFiCa *);
    
    /** Exception thrower object */
    PoolThrower                                   *thrower;
    
    /** map of all elements */
    ElemIdMap                                     element_ids;
    
    /** map of all elements by name */
    ElemNameMap                                   element_names;
    
    /** multimap of all elements by type */
    ElemTypeMultiMap                              element_types;

    /** map of all known controller classes */
    CtrlClassIdMap                                ctrl_class_ids;

    /**
     * map of all known controller classes by name 
     * name is: <class name> (case sensitive)
     */
    CtrlClassNameMap                              ctrl_class_names;
    
    /** map of all known controller files */
    CtrlFileIdMap                                 ctrl_file_ids;

    /** map of all known controller files by simple name */
    CtrlFileNameMultiMap                          ctrl_file_names;

    /** map of all known controller files by full path name */
    CtrlFileNameMap                               ctrl_absolute_file_names;
    
public:

    typedef ElemTypeMultiMapIt                    PoolElementTypeIt;

    /**
     * Constructor
     * 
     * @param[in] t thrower class. If NULL is given (default), a PoolThrower is
     *               created and used
     */
    PoolElementContainer(PoolThrower *t = NULL);
    
    /**
     * Destructor
     */
    virtual ~PoolElementContainer();

    inline PoolThrower* get_thrower();

    /**
     * Get the Controller Class object pointer for the given ID
     *
     * @param[in] name controller class name. This name must be 
     *                  <absolute path filename>/<class name> 
     *
     * @return a pointer to the controller class object
     */
    inline CtrlFiCa *get_controller_class(ElementId );
    
    /**
     * Get the Controller Class object pointer
     *
     * @param[in] name controller class name. This name must be 
     *                  <absolute path filename>/<class name> 
     *
     * @return a pointer to the controller class object
     *
     * @throws PoolElementContainer_UnknownCtrlClass, PoolElementContainer_InvalidCtrlClass
     */
    CtrlFiCa* get_controller_class(const std::string &);
    
    /**
     * Get the Controller File object pointer for the given ID
     *
     * @param[in] name controller file name. This name must be 
     *                  <absolute path filename>
     *
     * @return a pointer to the controller class object
     */
    inline CtrlFile *get_controller_file(ElementId );

    ////////////////////////////////////////////////////////////////////////////

    /**
     * Get the pool element object pointer
     *
     * @param[in] id element id
     *
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement
     */
    inline PoolElement *get_element(ElementId );
    
    /**
     * Get the pool element object pointer filtering for a certain type of element
     *
     * @param[in] id element id
     * @param[in] type the type of element to filter by
     *
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement, PoolElementContainer_WrongElementType
     */
    inline PoolElement *get_element(ElementId , ElementType );
    
    /**
     * Get the pool element object pointer
     *
     * @param[in] name element name. If any_name is false then this must be the
     *                  the 'simple' element name. Otherwise it can be the simple
     *                  name or the full name
     * @param[in] any_name if true also search by full name. Otherwise search
                            only by 'simple' name
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement
     */
    PoolElement *get_element(const std::string &, bool any_name = false);
    
    /**
     * Get the pool element object pointer filtering for a certain type of element
     *
     * @param[in] name element name. If any_name is false then this must be the
     *                  the 'simple' element name. Otherwise it can be the simple
     *                  name or the full name
     * @param[in] type the type of element to filter by
     * @param[in] any_name if true also search by full name. Otherwise search
                            only by 'simple' name
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement, PoolElementContainer_WrongElementType
     */
    PoolElement *get_element(const std::string &, ElementType, bool any_name = false);
    
    /**
     * Get the pool element ID
     *
     * @param[in] name element name. If any_name is false then this must be the
     *                  the 'simple' element name. Otherwise it can be the simple
     *                  name or the full name
     * @param[in] any_name if true also search by full name. Otherwise search
                            only by 'simple' name
     * @return the element ID
     *
     * @throws PoolElementContainer_UnknownElement
     */
    ElementId get_element_id(const std::string &, bool any_name = false);

    /**
     * Get the pool element object pointer
     *
     * @param[in] full_name full element name.
     *
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement
     */
    PoolElement *get_element_by_full_name(const std::string &);

    /**
     * Get the pool element object pointer filtering for a certain type of element
     *
     * @param[in] full_name full element name.
     * @param[in] type the type of element to filter by
     *
     * @return a pointer to the element object
     *
     * @throws PoolElementContainer_UnknownElement, PoolElementContainer_WrongElementType
     */
    PoolElement *get_element_by_full_name(const std::string &, ElementType);
    
    /**
     * Obtains the number of existing elements for the given type
     *
     * @param[in] type filter for the type of element
     *
     * @return the number of elements for the given type
     */
    inline int32_t get_element_nb(ElementType );
    
    /**
     * Obtains an imutable reference to the map of element IDs
     *
     * @return an imutable reference to the map of element IDs
     */
    inline const ElemIdMap &get_element_id_map() const
    { return element_ids; }

    /**
     * Obtains a reference to the map of element IDs
     *
     * Warning: Use with care outside this class. Make sure you don't modify
     * the map inadvertedly. Whenever possible use the const variant.
     *
     * @return a reference to the map of element IDs
     */
    inline ElemIdMap &get_element_id_map()
    { return element_ids; }

    /**
     * Obtains an imutable reference to the map of element names
     *
     * @return an imutable reference to the map of element names
     */
    inline const ElemNameMap &get_element_name_map() const
    { return element_names; }

    /**
     * Obtains a reference to the map of element names
     *
     * Warning: Use with care outside this class. Make sure you don't modify
     * the map inadvertedly. Whenever possible use the const variant.
     *
     * @return a reference to the map of element names
     */
    inline ElemNameMap &get_element_name_map()
    { return element_names; }
    
    /**
     * Obtains an imutable reference to the multimap of element types
     *
     * @return an imutable reference to the multimap of element types
     */
    inline const ElemTypeMultiMap &get_element_type_map() const
    { return element_types; }

    /**
     * Obtains a reference to the multimap of element types
     *
     * Warning: Use with care outside this class. Make sure you don't modify
     * the map inadvertedly. Whenever possible use the const variant.
     *
     * @return a reference to the multimap of element types
     */
    inline ElemTypeMultiMap &get_element_type_map()
    { return element_types; }

    /**
     * Obtains the start and stop iterator for the given element type
     *
     * @param[in]  type the type of element to filter
     * @param[out] beg the iterator which will contain the beginning
     * @param[out] end the iterator which will contain the end
     */
    inline void get_all_elements(ElementType , PoolElementTypeIt &, 
                                 PoolElementTypeIt &);

    /**
     * Obtains the range iterator for the given element type
     *
     * @param[in]  type the type of element to filter
     * @param[out] pair the range iterator which will contain the grange
     */
    inline void get_range(ElementType , PairElemTypeMultiMapIt &);

    /**
     * Determines if the given element name exists
     *
     * @param[in] name element name. If any_name is false then this must be the
     *                  the 'simple' element name. Otherwise it can be the simple
     *                  name or the full name
     * @param[in] any_name if true also search by full name. Otherwise search
                            only by 'simple' name
     * @return true if the element exists or false otherwise
     *
     */
    inline bool element_exists(const std::string &, bool any_name = false);
    
    /**
     * Determines if the given element name exists for the given type
     *
     * @param[in] name element name. If any_name is false then this must be the
     *                  the 'simple' element name. Otherwise it can be the simple
     *                  name or the full name
     * @param[in]  type the type of element to filter
     * @param[in] any_name if true also search by full name. Otherwise search
                            only by 'simple' name
     * @return true if the element exists or false otherwise
     *
     */
    inline bool element_exists(const std::string &, ElementType, bool any_name = false);

    /**
     * Determine the elements which use the element identified by the ID
     * 
     * @param[in] elem_id element to be searched
     * @param[out] elems array of elements to be filled with the elements
     */
    void get_element_users(ElementId, ElemIdVector &);

    /**
     * Determine the elements which use the element identified by the ID
     * 
     * @param[in] elem_id element to be searched
     * @param[out] elems array of elements to be filled with the elements
     */
    void get_element_users(ElementId, ElemVector &);

    /**
     * Determine the elements which use the element identified by the ID
     * 
     * @param[in] elem_id element to be searched
     * @param[out] elems set of elements to be filled with the elements
     */
    void get_element_users(ElementId, ElemIdSet &);

    /**
     * Determine the elements which use the element identified by the ID
     * 
     * @param[in] elem_id element to be searched
     * @param[out] elems set of elements to be filled with the elements
     */
    void get_element_users(ElementId, ElemSet &);

    /**
     * Determine all the different element types in the given list of elements
     * 
     * @param[in] elems list of element IDs
     * @param[out] elem_types list of element types to be filled
     */
    void get_element_types(ElemIdVector &, ElemTypeSet &);
    
    /**
     * Determine all the different element types in the given list of elements
     * 
     * @param[in] elems list of elements
     * @param[out] elem_types list of element types to be filled
     */
    void get_element_types(ElemVector &, ElemTypeSet &);

    /**
     * Determine all the different element types in the given list of elements
     * 
     * @param[in] elems set of element IDs
     * @param[out] elem_types list of element types to be filled
     */
    void get_element_types(ElemIdSet &, ElemTypeSet &);
    
    /**
     * Determine all the different element types in the given list of elements
     * 
     * @param[in] elems set of elements
     * @param[out] elem_types list of element types to be filled
     */
    void get_element_types(ElemSet &, ElemTypeSet &);
};

}

#include "CPoolElementContainer.inl"

#endif  // _CPOOL_ELEMENTCONTAINER_H_
