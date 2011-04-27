# Sardana device pool tango system
# Adapted from Jens Meyer Makefile.am

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

lib_LTLIBRARIES = libPool.la

bin_PROGRAMS = Pool

libPool_la_CPPFLAGS = \
    -I@TANGO_ROOT@/include \
    -I@TANGO_ROOT@/include/tango \
    -I@OMNI_ROOT@/include \
    $(PYTHON_CPPFLAGS) \
    -I$(srcdir)/../include \
    -I$(srcdir)/Motor \
    -I$(srcdir)/MotorGroup \
    -I$(srcdir)/PseudoMotor \
    -I$(srcdir)/CTExpChannel \
    -I$(srcdir)/ZeroDExpChannel \
    -I$(srcdir)/OneDExpChannel \
    -I$(srcdir)/TwoDExpChannel \
    -I$(srcdir)/MeasurementGroup \
    -I$(srcdir)/CommunicationChannel \
    -I$(srcdir)/IORegister \
    -I$(srcdir)/PoolBaseDev \
    -I$(srcdir)/PoolIndBaseDev \
    -I$(srcdir)/PoolGroupBaseDev \
    -I$(srcdir)/PseudoCounter \
    -I$(srcdir)/../lib \
    -I$(srcdir)/../lib/Ctrl \
    -I$(srcdir)/../lib/Controller \
    -I$(srcdir)/../lib/Motor \
    -I$(srcdir)/../lib/MotorGroup \
    -I$(srcdir)/../lib/PseudoMotor \
    -I$(srcdir)/../lib/PseudoCounter \
    -I$(srcdir)/../lib/CTExpChannel \
    -I$(srcdir)/../lib/ZeroDExpChannel \
    -I$(srcdir)/../lib/OneDExpChannel \
    -I$(srcdir)/../lib/TwoDExpChannel \
    -I$(srcdir)/../lib/MeasurementGroup \
    -I$(srcdir)/../lib/CommunicationChannel \
    -I$(srcdir)/../lib/IORegister \
    -I$(srcdir)/../lib/Instrument

Pool_CPPFLAGS = \
    -I@TANGO_ROOT@/include \
    -I@TANGO_ROOT@/include/tango \
    -I@OMNI_ROOT@/include \
    $(PYTHON_CPPFLAGS) \
    -I$(srcdir)/../include \
    -I$(srcdir)/Motor \
    -I$(srcdir)/MotorGroup \
    -I$(srcdir)/PseudoMotor \
    -I$(srcdir)/CTExpChannel \
    -I$(srcdir)/ZeroDExpChannel \
    -I$(srcdir)/OneDExpChannel \
    -I$(srcdir)/TwoDExpChannel \
    -I$(srcdir)/MeasurementGroup \
    -I$(srcdir)/CommunicationChannel \
    -I$(srcdir)/IORegister \
    -I$(srcdir)/PoolBaseDev \
    -I$(srcdir)/PoolIndBaseDev \
    -I$(srcdir)/PoolGroupBaseDev \
    -I$(srcdir)/PseudoCounter \
    -I$(srcdir)/../lib \
    -I$(srcdir)/../lib/Ctrl \
    -I$(srcdir)/../lib/Controller \
    -I$(srcdir)/../lib/Motor \
    -I$(srcdir)/../lib/MotorGroup \
    -I$(srcdir)/../lib/PseudoMotor \
    -I$(srcdir)/../lib/PseudoCounter \
    -I$(srcdir)/../lib/CTExpChannel \
    -I$(srcdir)/../lib/ZeroDExpChannel \
    -I$(srcdir)/../lib/OneDExpChannel \
    -I$(srcdir)/../lib/TwoDExpChannel \
    -I$(srcdir)/../lib/MeasurementGroup \
    -I$(srcdir)/../lib/CommunicationChannel \
    -I$(srcdir)/../lib/IORegister \
    -I$(srcdir)/../lib/Instrument

Pool_LDADD = -lPool

libPool_la_LIBADD = -L../lib -L../lib/sandbox \
    -L@TANGO_ROOT@/lib \
    -L@OMNI_ROOT@/lib \
    $(PYTHON_LDFLAGS) \
    -ltango \
    -llog4tango \
    -lomniORB4 \
    -lomniDynamic4 \
    -lomnithread \
    -lCOS4 \
    -lltdl \
    -lpthread \
    -lrt \
    -lpypool \
    -lpool

libPool_la_CXXFLAGS = -D_REENTRANT -Wall -ansi 
Pool_CXXFLAGS = -D_REENTRANT -Wall -ansi 

libPool_la_LDFLAGS = -export-dynamic
Pool_LDFLAGS = -export-dynamic

Pool_SOURCES = $(srcdir)/main.cpp \
    $(srcdir)/ClassFactory.cpp

libPool_la_SOURCES = $(srcdir)/PoolFactory.h \
    $(srcdir)/PoolClass.h \
    $(srcdir)/Pool.h \
    $(srcdir)/PoolUtil.h \
    $(srcdir)/Profile.h \
    $(srcdir)/Motor/Motor.h \
    $(srcdir)/Motor/MotorClass.h \
    $(srcdir)/Motor/MotorFeatures.h \
    $(srcdir)/Motor/MotorUtil.h \
    $(srcdir)/MotorGroup/MotorGroup.h \
    $(srcdir)/MotorGroup/MotorGroupClass.h \
    $(srcdir)/MotorGroup/MotorGroupUtil.h \
    $(srcdir)/PseudoMotor/PseudoMotor.h \
    $(srcdir)/PseudoMotor/PseudoMotorClass.h \
    $(srcdir)/PseudoMotor/PseudoMotorUtil.h \
    $(srcdir)/CTExpChannel/CTExpChannel.h \
    $(srcdir)/CTExpChannel/CTExpChannelClass.h \
    $(srcdir)/CTExpChannel/CTExpChannelUtil.h \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannel.h \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannelClass.h \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannelUtil.h \
    $(srcdir)/OneDExpChannel/OneDExpChannel.h \
    $(srcdir)/OneDExpChannel/OneDExpChannelClass.h \
    $(srcdir)/OneDExpChannel/OneDExpChannelUtil.h \
    $(srcdir)/TwoDExpChannel/TwoDExpChannel.h \
    $(srcdir)/TwoDExpChannel/TwoDExpChannelClass.h \
    $(srcdir)/TwoDExpChannel/TwoDExpChannelUtil.h \
    $(srcdir)/PseudoCounter/PseudoCounter.h \
    $(srcdir)/PseudoCounter/PseudoCounterClass.h \
    $(srcdir)/PseudoCounter/PseudoCounterUtil.h \
    $(srcdir)/MeasurementGroup/MeasurementGroup.h \
    $(srcdir)/MeasurementGroup/MeasurementGroupClass.h \
    $(srcdir)/MeasurementGroup/MeasurementGroupUtil.h \
    $(srcdir)/PoolBaseDev/PoolBaseUtil.h \
    $(srcdir)/PoolBaseDev/PoolBaseDev.h \
    $(srcdir)/PoolIndBaseDev/PoolIndBaseDev.h \
    $(srcdir)/PoolIndBaseDev/PoolIndBaseUtil.h \
    $(srcdir)/PoolIndBaseDev/PoolDynAttr.h \
    $(srcdir)/PoolGroupBaseDev/PoolGroupBaseUtil.h \
    $(srcdir)/PoolGroupBaseDev/PoolGroupBaseDev.h \
    $(srcdir)/CommunicationChannel/CommunicationChannel.h \
    $(srcdir)/CommunicationChannel/CommunicationChannelClass.h \
    $(srcdir)/CommunicationChannel/CommunicationChannelUtil.h \
    $(srcdir)/IORegister/IORegister.h \
    $(srcdir)/IORegister/IORegisterClass.h \
    $(srcdir)/IORegister/IORegisterUtil.h \
    $(srcdir)/Profile.cpp \
    $(srcdir)/PoolFactory.cpp \
    $(srcdir)/PoolClass.cpp \
    $(srcdir)/PoolStateMachine.cpp	\
    $(srcdir)/Pool.cpp \
    $(srcdir)/PoolUtilMeth.cpp \
    $(srcdir)/Pool_AddRemove.cpp \
    $(srcdir)/Pool_GetFind.cpp \
    $(srcdir)/PoolUtil.cpp \
    $(srcdir)/Motor/MotorClass.cpp \
    $(srcdir)/Motor/Motor.cpp \
    $(srcdir)/Motor/MotorStateMachine.cpp \
    $(srcdir)/Motor/MotorUtil.cpp \
    $(srcdir)/MotorGroup/MotorGroupClass.cpp \
    $(srcdir)/MotorGroup/MotorGroup.cpp \
    $(srcdir)/MotorGroup/MotorGroupStateMachine.cpp \
    $(srcdir)/MotorGroup/MotorGroupUtil.cpp \
    $(srcdir)/PseudoMotor/PseudoMotorClass.cpp \
    $(srcdir)/PseudoMotor/PseudoMotorUtil.cpp \
    $(srcdir)/PseudoMotor/PseudoMotor.cpp \
    $(srcdir)/PseudoMotor/PseudoMotorStateMachine.cpp \
    $(srcdir)/PoolBaseDev/PoolBaseDev.cpp \
    $(srcdir)/PoolIndBaseDev/PoolIndBaseDev.cpp \
    $(srcdir)/PoolIndBaseDev/PoolIndBaseUtil.cpp \
    $(srcdir)/PoolIndBaseDev/PoolDynAttr.cpp \
    $(srcdir)/PoolGroupBaseDev/PoolGroupBaseDev.cpp \
    $(srcdir)/CTExpChannel/CTExpChannelClass.cpp \
    $(srcdir)/CTExpChannel/CTExpChannel.cpp \
    $(srcdir)/CTExpChannel/CTExpChannelStateMachine.cpp \
    $(srcdir)/CTExpChannel/CTExpChannelUtil.cpp \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannelClass.cpp \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannel.cpp \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannelStateMachine.cpp \
    $(srcdir)/ZeroDExpChannel/ZeroDExpChannelUtil.cpp \
    $(srcdir)/OneDExpChannel/OneDExpChannelClass.cpp \
    $(srcdir)/OneDExpChannel/OneDExpChannel.cpp \
    $(srcdir)/OneDExpChannel/OneDExpChannelStateMachine.cpp \
    $(srcdir)/OneDExpChannel/OneDExpChannelUtil.cpp \
    $(srcdir)/TwoDExpChannel/TwoDExpChannelClass.cpp \
    $(srcdir)/TwoDExpChannel/TwoDExpChannel.cpp \
    $(srcdir)/TwoDExpChannel/TwoDExpChannelStateMachine.cpp \
    $(srcdir)/TwoDExpChannel/TwoDExpChannelUtil.cpp \
    $(srcdir)/PseudoCounter/PseudoCounterClass.cpp \
    $(srcdir)/PseudoCounter/PseudoCounter.cpp \
    $(srcdir)/PseudoCounter/PseudoCounterUtil.cpp \
    $(srcdir)/PseudoCounter/PseudoCounterStateMachine.cpp \
    $(srcdir)/MeasurementGroup/MeasurementGroupClass.cpp \
    $(srcdir)/MeasurementGroup/MeasurementGroup.cpp \
    $(srcdir)/MeasurementGroup/MeasurementGroupStateMachine.cpp \
    $(srcdir)/MeasurementGroup/MeasurementGroupUtil.cpp \
    $(srcdir)/CommunicationChannel/CommunicationChannelClass.cpp \
    $(srcdir)/CommunicationChannel/CommunicationChannel.cpp \
    $(srcdir)/CommunicationChannel/CommunicationChannelStateMachine.cpp \
    $(srcdir)/CommunicationChannel/CommunicationChannelUtil.cpp \
    $(srcdir)/IORegister/IORegisterClass.cpp \
    $(srcdir)/IORegister/IORegister.cpp \
    $(srcdir)/IORegister/IORegisterStateMachine.cpp \
    $(srcdir)/IORegister/IORegisterUtil.cpp

