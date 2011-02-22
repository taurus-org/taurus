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

SUBDIRS = Ctrl sandbox

lib_LTLIBRARIES = libpool.la

libpool_la_LIBADD = $(PYTHON_LDFLAGS) \
    -lltdl \
    -lrt \
    -lpthread

libpool_ladir = $(pkgincludedir)

libpool_la_LDFLAGS = -module -export-dynamic

libpool_la_CXXFLAGS = -Wall -ansi -DREENTRANT -Wno-invalid-offsetof

libpool_la_CPPFLAGS = $(PYTHON_CPPFLAGS) \
    -I@TANGO_ROOT@/include \
    -I@OMNI_ROOT@/include \
    -I$(srcdir)/../include \
    -I$(srcdir) \
    -I$(srcdir)/Ctrl \
    -I$(srcdir)/Motor \
    -I$(srcdir)/Controller \
    -I$(srcdir)/MotorGroup \
    -I$(srcdir)/PseudoMotor \
    -I$(srcdir)/PseudoCounter \
    -I$(srcdir)/CTExpChannel \
    -I$(srcdir)/ZeroDExpChannel \
    -I$(srcdir)/OneDExpChannel \
    -I$(srcdir)/TwoDExpChannel \
    -I$(srcdir)/MeasurementGroup \
    -I$(srcdir)/CommunicationChannel \
    -I$(srcdir)/IORegister \
    -I$(srcdir)/Instrument \
    -I$(srcdir)/../src \
    -I$(srcdir)/../src/Motor \
    -I$(srcdir)/../src/MotorGroup \
    -I$(srcdir)/../src/PseudoMotor \
    -I$(srcdir)/../src/PseudoCounter \
    -I$(srcdir)/../src/CTExpChannel \
    -I$(srcdir)/../src/ZeroDExpChannel \
    -I$(srcdir)/../src/OneDExpChannel \
    -I$(srcdir)/../src/TwoDExpChannel \
    -I$(srcdir)/../src/MeasurementGroup \
    -I$(srcdir)/../src/CommunicationChannel \
    -I$(srcdir)/../src/IORegister \
    -I$(srcdir)/../src/PoolBaseDev \
    -I$(srcdir)/../src/PoolIndBaseDev \
    -I$(srcdir)/../src/PoolGroupBaseDev


libpool_la_SOURCES = $(srcdir)/Utils.h \
    $(srcdir)/PyUtils.h \
    $(srcdir)/CPoolExcept.h \
    $(srcdir)/CPoolElementContainer.h \
    $(srcdir)/CPool.h \
    $(srcdir)/CPoolElementEvent.h \
    $(srcdir)/CPoolObject.h \
    $(srcdir)/CPoolElement.h \
    $(srcdir)/CPoolGroupElement.h \
    $(srcdir)/CPoolMoveable.h \
    $(srcdir)/Ctrl/PyCtrl.h \
    $(srcdir)/Controller/CPoolController.h \
    $(srcdir)/Controller/CppCtrlFile.h \
    $(srcdir)/Controller/CppMotCtrlFile.h \
    $(srcdir)/Controller/CtrlFiCa.h \
    $(srcdir)/Controller/CtrlFile.h \
    $(srcdir)/Controller/ExternalFiCa.h \
    $(srcdir)/Controller/ExternalFile.h \
    $(srcdir)/Controller/PropertyData.h \
    $(srcdir)/Controller/PyCtrlFile.h \
    $(srcdir)/Controller/PyExternalFile.h \
    $(srcdir)/Controller/PyMotCtrlFile.h \
    $(srcdir)/Motor/CPoolMotor.h \
    $(srcdir)/Motor/MotorThread.h \
    $(srcdir)/Motor/MotionThread.h \
    $(srcdir)/MotorGroup/CPoolMotorGroup.h \
    $(srcdir)/PseudoMotor/CPoolPseudoMotor.h \
    $(srcdir)/PseudoCounter/CPoolPseudoCounter.h \
    $(srcdir)/Constraint/CPoolConstraint.h \
    $(srcdir)/CTExpChannel/CPoolCTExpChannel.h \
    $(srcdir)/CTExpChannel/CTPoolThread.h \
    $(srcdir)/ZeroDExpChannel/CPoolZeroDExpChannel.h \
    $(srcdir)/ZeroDExpChannel/ZeroDThread.h \
    $(srcdir)/OneDExpChannel/CPoolOneDExpChannel.h \
    $(srcdir)/OneDExpChannel/OneDThread.h \
    $(srcdir)/TwoDExpChannel/CPoolTwoDExpChannel.h \
    $(srcdir)/TwoDExpChannel/TwoDThread.h \
    $(srcdir)/MeasurementGroup/CPoolMeasurementGroup.h \
    $(srcdir)/CommunicationChannel/CPoolCommunicationChannel.h \
    $(srcdir)/IORegister/CPoolIORegister.h \
    $(srcdir)/Instrument/CPoolInstrument.h \
    $(srcdir)/Utils.cpp \
    $(srcdir)/PyUtils.cpp \
    $(srcdir)/CPoolExcept.cpp \
    $(srcdir)/CPoolElementContainer.cpp \
    $(srcdir)/CPool.cpp \
    $(srcdir)/CPoolElementEvent.cpp \
    $(srcdir)/CPoolObject.cpp \
    $(srcdir)/CPoolElement.cpp \
    $(srcdir)/CPoolGroupElement.cpp \
    $(srcdir)/Ctrl/ComCtrl.cpp \
    $(srcdir)/Ctrl/Constraint.cpp \
    $(srcdir)/Ctrl/CoTiCtrl.cpp \
    $(srcdir)/Ctrl/MotCtrl.cpp \
    $(srcdir)/Ctrl/ZeroDCtrl.cpp \
    $(srcdir)/Ctrl/OneDCtrl.cpp \
    $(srcdir)/Ctrl/TwoDCtrl.cpp \
    $(srcdir)/Ctrl/IORegisterCtrl.cpp \
    $(srcdir)/Ctrl/PyCtrl.cpp \
    $(srcdir)/Controller/CPoolController.cpp \
    $(srcdir)/Controller/CppCtrlFile.cpp \
    $(srcdir)/Controller/CppMotCtrlFile.cpp \
    $(srcdir)/Controller/CtrlFiCa.cpp \
    $(srcdir)/Controller/CtrlFile.cpp \
    $(srcdir)/Controller/ExternalFiCa.cpp \
    $(srcdir)/Controller/ExternalFile.cpp \
    $(srcdir)/Controller/PropertyData.cpp \
    $(srcdir)/Controller/PyCtrlFile.cpp \
    $(srcdir)/Controller/PyExternalFile.cpp \
    $(srcdir)/Controller/PyMotCtrlFile.cpp \
    $(srcdir)/Motor/CPoolMotor.cpp \
    $(srcdir)/Motor/MotorThread.cpp \
    $(srcdir)/Motor/MotionThread.cpp \
    $(srcdir)/MotorGroup/CPoolMotorGroup.cpp \
    $(srcdir)/PseudoMotor/CPoolPseudoMotor.cpp \
    $(srcdir)/PseudoCounter/CPoolPseudoCounter.cpp \
    $(srcdir)/CTExpChannel/CPoolCTExpChannel.cpp \
    $(srcdir)/CTExpChannel/CTPoolThread.cpp \
    $(srcdir)/ZeroDExpChannel/CPoolZeroDExpChannel.cpp \
    $(srcdir)/ZeroDExpChannel/ZeroDThread.cpp \
    $(srcdir)/OneDExpChannel/CPoolOneDExpChannel.cpp \
    $(srcdir)/OneDExpChannel/OneDThread.cpp \
    $(srcdir)/TwoDExpChannel/CPoolTwoDExpChannel.cpp \
    $(srcdir)/MeasurementGroup/CPoolMeasurementGroup.cpp \
    $(srcdir)/CommunicationChannel/CPoolCommunicationChannel.cpp \
    $(srcdir)/IORegister/CPoolIORegister.cpp \
    $(srcdir)/Instrument/CPoolInstrument.cpp


#    $(srcdir)/Ctrl/PyComCtrl.h \
#    $(srcdir)/Ctrl/PyConstraint.h \
#    $(srcdir)/Ctrl/PyCoTiCtrl.h \
#    $(srcdir)/Ctrl/PyMotCtrl.h \
#    $(srcdir)/Ctrl/PyZeroDCtrl.h \
#    $(srcdir)/Ctrl/PyOneDCtrl.h \
#    $(srcdir)/Ctrl/PyTwoDCtrl.h \
#    $(srcdir)/Ctrl/PyIORegisterCtrl.h \
#    $(srcdir)/Ctrl/PyPseudoCoCtrl.h \
#    $(srcdir)/Ctrl/PyPseudoMotCtrl.h \
#    $(srcdir)/Ctrl/PyComCtrl.cpp \
#    $(srcdir)/Ctrl/PyConstraint.cpp \
#    $(srcdir)/Ctrl/PyCoTiCtrl.cpp \
#    $(srcdir)/Ctrl/PyMotCtrl.cpp \
#    $(srcdir)/Ctrl/PyZeroDCtrl.cpp \
#    $(srcdir)/Ctrl/PyOneDCtrl.cpp \
#    $(srcdir)/Ctrl/PyTwoDCtrl.cpp \
#    $(srcdir)/Ctrl/PyIORegisterCtrl.cpp \
#    $(srcdir)/Ctrl/PyPseudoCoCtrl.cpp \
#    $(srcdir)/Ctrl/PyPseudoMotCtrl.cpp
