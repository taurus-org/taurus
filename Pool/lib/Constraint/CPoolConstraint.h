#ifndef _CPOOL_CONSTRAINT_H_
#define _CPOOL_CONSTRAINT_H_

namespace Pool_ns
{

/**
 * The constraint pool object
 */
struct ConstraintPool : public ControllerPool
{
	/** List of elements connected to the constraint. */
	vector<IConstraintable*>			elements;

	/**
	 * Returns the type of element this object represents.
	 * @see ElementType
	 *
	 * @return This element type
	 */
	virtual ElementType get_type()				{ return CONSTRAINT_ELEM; }
};

} 

#endif // _CPOOL_H_
