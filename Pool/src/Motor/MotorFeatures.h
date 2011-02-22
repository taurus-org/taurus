//=============================================================================
//
// file :        MotorFeatures.h
//
// description : Include for the Motor features.
//
// project :	Motor generic client class
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2006/12/18 11:35:29  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.1  2006/10/05 08:00:16  etaurel
// - Controller now supports dynamic features
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//==============================================================================

#ifndef _MOTORFEATURES_H
#define _MOTORFEATURES_H

//==================================================================================
//
//  Motor features list
//	-------------------
//
//
// A motor extra attribute is defined by three informations which are:
// 	1 - The extra attribute name
//	2 - The extra attribute data type
//	3 - The extra attribute write type
//
// Four data types are supported. They are:
// 	- BOOLEAN
//	- LONG
//	- DOUBLE
//	- STRING
//
// Two write types are supported for each of the data type. They are:
//	- READ
//	- READ_WRITE
//
//==================================================================================

namespace Motor_ns
{

#define		BACKLASH_FEATURE_NAME			"CanDoBacklash"
#define		ROUNDING_FEATURE_NAME			"WantRounding"

const char *MotorFeaturesList[] = {
	BACKLASH_FEATURE_NAME,
	ROUNDING_FEATURE_NAME,
	"Encoder",
	"Home_speed",
	"Home_acceleration",
	NULL
};

//==================================================================================
//
// End of motor features list
//
//==================================================================================

}

#endif /* _MOTORFEATURES_H */
