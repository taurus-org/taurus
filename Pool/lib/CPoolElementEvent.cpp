#include <assert.h>

#include <Utils.h>
#include <CPoolElementEvent.h>
#include <CPoolElement.h>

namespace Pool_ns 
{

//------------------------------------------------------------------------------
// PoolElementEvent::PoolElementEvent
//
PoolElementEvent::PoolElementEvent(PoolEventType evt_type, PoolElement* src_elem)
:type(evt_type), src(src_elem), priority(false)
{}

//------------------------------------------------------------------------------
// PoolElementEvent::PoolElementEvent
//
PoolElementEvent::PoolElementEvent(const PoolElementEvent &rhs)
:type(rhs.type), src(rhs.src), dim(rhs.dim), priority(rhs.priority)
{
  	if(type == StateChange)
  	{
  		old.state = rhs.old.state;
  		curr.state = rhs.curr.state;
  	}
  	else if(type == PositionChange)
  	{
  		old.position = rhs.old.position;
  		curr.position = rhs.curr.position;
  	}
  	else if(type == PositionArrayChange)
  	{
  		old.position_array = rhs.old.position_array;
  		curr.position_array = rhs.curr.position_array;
  	}
  	else if(type == CTValueChange ||
  			type == ZeroDValueChange ||
  			type == OneDValueChange ||
  			type == PseudoCoValueChange)
  	{
  		old.value = rhs.old.value;
  		curr.value = rhs.curr.value;
  	}

  	else if(type == MotionEnded)
  	{

  	}
}

std::ostream & PoolElementEvent::printToStream(std::ostream & flux, int indent) const
{
	indentToStream(flux, indent);
	flux << "{ PoolElementEvent: ";
	if(priority) flux << "Priority " << type;
	if(type == StateChange)
  	{
		flux << "State Event [src=" << src->name << ", previous="
		     << PoolStateName[old.state] << ", current="
		     << PoolStateName[curr.state] << "]";
  	}
  	else if(type == PositionChange)
  	{
		flux << "Position Event [src=" << src->name << ", previous="
		     << old.position << ", current="
		     << curr.position << "]";
  	}
  	else if(type == PositionArrayChange)
  	{
		flux << "PositionArray Event [src=" << src->name << ", dim=" << dim
		     << ", current=(";
		for(int32_t l=0;l<dim;++l)
			flux << curr.position_array[l] << ", ";
		flux << curr.position << ")]";
  	}
  	else if(type == CTValueChange ||
  			type == ZeroDValueChange ||
  			type == PseudoCoValueChange)
  	{
		flux << "Value Event [src=" << src->name << ", previous="
		     << old.value << ", current="
		     << curr.value << "]";
  	}
  	else if(type == MotionEnded)
  	{
		flux << "MotionEnded [src=" << src->name << "]";
  	}
  	else if(type == ElementStructureChange)
  	{
		flux << "ElementStructureChange Event [src=" << src->name << "]";
  	}
  	else if(type == ElementListChange)
  	{
		flux << "ElementListChange Event [src=" << src->name << "]";
  	}
  	else
  	{
  		flux << std::endl;
  		assert(false);
  	}
	flux << "}" << std::endl;
    return flux;
}

}
