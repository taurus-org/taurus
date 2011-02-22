//+=============================================================================
//
// file :         Utils.cpp
//
// description :
//
// project :      TANGO Device Server
//
// $Author: tcoutinho $
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//+=============================================================================
#include <math.h>
#include "Utils.h"
#include "CPoolElement.h"

namespace Pool_ns
{
    
bool doubleEqual(double a, double b)
{
    return (fabs(a - b) <= EPSILON * fabs(a));
}

AutoPoolMonitor::AutoPoolMonitor(PoolMonitor *mon): monitor(mon) 
{
    if (monitor)
        monitor->get_monitor();
}
    
AutoPoolMonitor::AutoPoolMonitor(PoolElement *elem)
{
    if (elem && (monitor = elem->get_serialization_monitor()))
    {
        monitor->get_monitor();
    }
}
    
AutoPoolMonitor::~AutoPoolMonitor()
{
    if (monitor)
        monitor->rel_monitor();
}

}
