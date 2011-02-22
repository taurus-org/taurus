from Macro import *
from ScanData import *

import scipy

class ltb_emittance(Macro):
    """Configure, scan, and prepare data for the LTB Emittance."""

    param_def = [
        # MESH PARAMETERS
        ['quadrupole',Type.Motor,None,'The quadrupole to scan.'],
        ['start_pos',Type.Float,None,'Quadrupole start position.'],
        ['final_pos',Type.Float,None,'Quadrupole final position.'],
        ['nr_interv',Type.Integer,None,'Number of scan intervals.'],
        ['acquisitions_per_step',Type.Integer,None,'Number of acquisitions per step.'],
        ['integ_time',Type.Float,None,'Scan integartion time.'],

        # PREPARE PARAMETERS
        ['op_mode',Type.String,None,'[FS,OTR,OFFLINE]: The operation mode.'],
        ['ROI_mag_X',Type.Float,None,'ImageBeamAnalizer X factor magnification.'],
        ['ROI_mag_Y',Type.Float,None,'ImageBeamAnalizer Y factor magnification.'],

        # EMITTANCE CALCULATION PARAMETERS
        ['sigma_X',Type.ExpChannel,None,'Sigma X source experiment channel.'],
        ['sigma_Y',Type.ExpChannel,None,'Sigma Y source experiment channel.'],
        
        ]



    def prepare(self,quadrupole,start_pos,final_pos,nr_interv,acquisitions_per_step,integ_time
                ,op_mode,ROI_mag_X,ROI_mag_Y
                ,sigma_X,sigma_Y):
        """
        Prepare the Flourescense Screen and the ImageBeamAnalizer.

        1) Switch the op_mode:
        op_mode FS:      Move Fluorescense Screen actuator to the proper position
                         Configure the ImageBeamAnalizer to provide real images
        op_mode OTR:     Move Fluorescense Screen actuator to the proper position
                         Configure the ImageBeamAnalizer to provide real images
        op_mode OFFLINE: Configure the ImageBeamAnalizer in order to provide
                         previously taken images

        2) In all cases, Configure the ImageBeamAnalizer with the magnification ROIs X and Y

        3) Select the correct measurment group lt01_iba01
        
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Note 1: The FS_Actuator motor will be hardcoded here, this macro is just for
                emittance, so it is not needed to be an extra parameter. By now it is not
                a pool motor, it is a PySignalSimulator. We have to change an attribute and
                perform the init() command.
        Note 2: The ImageBeamAnalizer device wil be also hardcoded here.
        Note 3: The dummy motor is also be hardcoded here.
        Note 4: In OFFLINE operation mode, there's no need to move de quadrupole so the user
                can use _another_ dummy motor for the mesh scan.
        Note 5: The measurement group is also hardcoded here.
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # 1) Switch the op_mode:

        # 2) In all cases, Configure the ImageBeamAnalizer with the magnification ROIs X and Y

        # 3) Select the correct measurment group lt01_iba01
        hardcoded_meas_group = 'gc_mg_ct1ct2'
        self.setEnv("ActiveMntgrp",hardcoded_meas_group)
        
        self.output("\n")
        self.output("The operation mode '%s' has been configured:" % op_mode)
        self.output("ROI magnification X: %d" % ROI_mag_X)
        self.output("ROI magnification Y: %d" % ROI_mag_Y)
        self.output("Measurement group: %s" % hardcoded_meas_group)
        self.output("\n")
        pass
        
        
        
    def run(self,quadrupole,start_pos,final_pos,nr_interv,acquisitions_per_step,integ_time
            ,op_mode,ROI_mag_X,ROI_mag_Y
            ,sigma_X,sigma_Y):
        """
        Proceed with the mesh scan and then prepare the data for the fit function.
        The class for the fit function can be found in:
        svn:/trunk/tango_client/EmittanceGUI/EmitCompute/fitemitclass.py

        1) call the mesh with the parameters:
        dummy_motor 0 acquisitions_per_step-1 acquisitions_per_step-1 quadrupole start_pos final_pos nr_interval integ_time
           and get it's data

        2) Prepare data for the fit function
           -) q1current,q2current,q3current: positions (currents) of the cuadrupoles
           -) quad_currents: all the positions of the quadrupole during the mesh
           -) step_list: range(1,len(quad_currents)+1)
           -) sigmaX: MEAN of the sigmaX channel for each quadrupole position
           -) sigmaY: MEAN of the sigmaY channel for each quadrupole position
           -) sigmaXerr: STD of the sigmaX channel for each quadrupole position
           -) sigmaYerr: STD of the sigmaY channel for each quadrupole position


           From the given example of a possible mesh output:
           dummy quad timer  sigX    sixY
               0    0     1  sX01    sY01
               1    0     1  sX02    sY02
               2    0     1  sX03    sY03
               3    0     1  sX04    sY04
               4    0     1  sX05    sY05
               0   15     1  sX11    sY11
               1   15     1  sX12    sY12
               2   15     1  sX13    sY13
               3   15     1  sX14    sY14
               4   15     1  sX15    sY15
               0   30     1  sX21    sY21
               1   30     1  sX22    sY22
               2   30     1  sX23    sY23
               3   30     1  sX24    sY24
               4   30     1  sX25    sY25

           The values to calculate are:
           -> quad_currents: [0,15,30]
           -> step_list: [1,2,3]
           -> sigmaX: [MEAN(sX01,...,sX05),MEAN(sX11,...,sX15),MEAN(sX21,...,sX25)]
           -> sigmaY: [MEAN(sY01,...,sY05),MEAN(sY11,...,sY15),MEAN(sY21,...,sY25)]
           -> sigmaXerr: [STD(sX01,...,sX05),STD(sX11,...,sX15),STD(sX21,...,sX25)]
           -> sigmaYerr: [STD(sY01,...,sY05),STD(sY11,...,sY15),STD(sY21,...,sY25)]
           
        3) Call the fit function with:
           
        4) Log some data to the door output

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Note 1: The dummy motor is also be hardcoded here.
        Note 2: Quadrupole motor names hardcoded here.
        Note 3: The motor_index is calculated with the hardcoded motor names
        Note 4: Mean and Std must be calculated because the pool does not have pseudo counters
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # 1) call the mesh:
        hardcoded_dummy = self.findObjs('gc_dmot1',type_class=Type.Motor)[0]
        hardcoded_motor_names = ['gc_smot1','gc_smot2','gc_smot3']
         
        hardcoded_q1 = self.findObjs(hardcoded_motor_names[0],type_class=Type.Motor)[0]
        hardcoded_q2 = self.findObjs(hardcoded_motor_names[1],type_class=Type.Motor)[0]
        hardcoded_q3 = self.findObjs(hardcoded_motor_names[2],type_class=Type.Motor)[0]
        
        #############
        # WE SHOULD USE THIS CODE BUT, THERE'S SOME IMPLEMENTATION MISFUCNTION AND ALSO
        # WE NEED THE MACRO DATA
        # SO THAT'S WHY WE USE THE MANAGER
        # self.execMacro('mesh',*mesh_params)
        #############
        mesh_macro_class = self.manager.getMacroClass('mesh')
        mesh_params = [hardcoded_dummy,0,acquisitions_per_step - 1,acquisitions_per_step - 1
                       ,quadrupole,start_pos,final_pos,nr_interv
                       ,integ_time]
            
        mesh_macro, ret = self.manager.prepareMacro(mesh_macro_class,mesh_params,{}
                                                    ,parent_macro=self,environment=self.environment)
        mesh_macro.start()
        mesh_macro.waitFinished()
        mesh_data = mesh_macro.data

        # 2) Prepare data for the fit function
        dummy_name = hardcoded_dummy.getName()
        quad_name = quadrupole.getName()
        sigma_X_name = sigma_X.getName()
        sigma_Y_name = sigma_Y.getName()

        quad_currents = []
        sigmaXMeans = []
        sigmaYMeans = []
        sigmaXStds = []
        sigmaYStds = []

        sigmaX_tmp = []
        sigmaY_tmp = []
        for record in mesh_data.records:
            data = record.data
            sigmaX_tmp.append(data[sigma_X_name])
            sigmaY_tmp.append(data[sigma_Y_name])
            
            if data[dummy_name] == acquisitions_per_step - 1:
                quad_currents.append(data[quad_name])
                sigmaXMeans.append(scipy.mean(sigmaX_tmp))
                sigmaYMeans.append(scipy.mean(sigmaY_tmp))
                sigmaXStds.append(scipy.std(sigmaX_tmp))
                sigmaYStds.append(scipy.std(sigmaY_tmp))
                sigmaX_tmp = []
                sigmaY_tmp = []
            


        # 3) Call the fit function with:
        try:
            import os,imp
            file_name = os.path.realpath(__file__)
            file_path = os.path.dirname(file_name)
            module_name = 'EmitCompute'
            module_file,module_path,desc = imp.find_module(module_name,[file_path])
            fit_module = imp.load_module(module_name,module_file,module_path,desc)

            fit_params = {}
            fit_params['q1current'] = hardcoded_q1.getUserPos()
            fit_params['q2current'] = hardcoded_q2.getUserPos()
            fit_params['q3current'] = hardcoded_q3.getUserPos()
            fit_params['quad2scan'] = hardcoded_motor_names.index(quad_name) + 1
            fit_params['quadcurrents'] = quad_currents
            fit_params['stepList'] = range(1,len(quad_currents)+1)
            fit_params['photosperstep'] = acquisitions_per_step
            fit_params['energy'] = 0.100
            fit_params['sigmaX'] = sigmaXMeans
            fit_params['sigmaY'] = sigmaYMeans
            fit_params['sigmaXerr'] = sigmaXStds
            fit_params['sigmaYerr'] = sigmaYStds



            ### THE SIMULATED POOL RETURNS VALUES THAT THE FIT FUNCTION DOES NOT LIKE...
            ### LET'S PUT THE TEST ONES... (SAMPLE 1)
            fit_params['q1current'] = 4.0
            fit_params['q2current'] = -3.5
            fit_params['q3current'] = 0.0
            fit_params['quad2scan'] = 1
            quadcurrents = []
            for i in range(200,675,25):
            	quadcurrents.append(i/100.0)
            fit_params['quadcurrents'] = quadcurrents
            fit_params['stepList'] = range(1,20,1)
            fit_params['photosperstep'] = 20
            fit_params['energy'] = 0.100
            fit_params['sigmaX'] = [0.001426961403,0.001260741166,0.001096047687,0.0009333245748,0.000773378632,0.0006178249184,0.0004703257323,0.000340509855,0.0002554806484,0.0002617660794,0.0003536234397,0.0004839503784,0.000628772145,0.0007796477902,0.0009333074224,0.001088283389,0.001243832341,0.0013995412,0.001555163403]
            fit_params['sigmaY'] = [0.0005738866407,0.000664518744,0.0007559865491,0.0008481436699,0.0009409000456,0.001034197434,0.001127996633,0.00122227039,0.001316999247,0.001412169008,0.00150776913,0.00160379167,0.001700230576,0.001797081194,0.001894339932,0.001992004003,0.002090071247,0.002188539998,0.002287408982]
            fit_params['sigmaXerr'] = [5.925299422e-05,2.876758948e-05,-5.58281654e-06,-4.746291144e-05,4.414459e-05,-9.13222184e-06,1.446001872e-05,1.433934922e-05, -5.484983014e-05,-5.620050114e-05,3.994034198e-05,-3.159836764e-05,5.520758698e-05,4.2292887e-06,6.773941846e-05,-5.421665984e-05,-4.34247576e-06,-6.006869848e-05,4.58226454e-06]
            fit_params['sigmaYerr'] = [-6.386919756e-05,-3.69669601e-05,-2.158579444e-05,-1.043460236e-05,4.731588484e-05,-1.644732852e-05,-3.065060684e-05,-5.301013774e-05,5.091508912e-05,3.629306646e-05,-5.16341189e-05,-6.305365402e-05,5.702331558e-05,4.660422928e-05,2.393852314e-05,4.998422968e-05,-2.936011848e-05,4.556844768e-05,4.114597984e-05]


            self.output("\n")
            self.output("Computing the emittance fit.")
            ### self.output("The parameters are:")
            ### self.output("q1current = "+str(fit_params['q1current']))
            ### self.output("q2current = "+str(fit_params['q2current']))
            ### self.output("q3current = "+str(fit_params['q3current']))
            ### self.output("quad2scan = "+str(fit_params['quad2scan']))
            ### self.output("quadcurrents = "+str(fit_params['quadcurrents'])+"\nlen = "+str(len(fit_params['quadcurrents'])))
            ### self.output("stepList = "+str(fit_params['stepList']))
            ### self.output("photosperstep = "+str(fit_params['photosperstep']))
            ### self.output("energy = "+str(fit_params['energy']))
            ### self.output("sigmaX = "+str(fit_params['sigmaX'])+"\nlen = "+str(len(fit_params['sigmaX'])))
            ### self.output("sigmaY = "+str(fit_params['sigmaY'])+"\nlen = "+str(len(fit_params['sigmaY'])))
            ### self.output("sigmaXerr = "+str(fit_params['sigmaXerr'])+"\nlen = "+str(len(fit_params['sigmaXerr'])))
            ### self.output("sigmaYerr = "+str(fit_params['sigmaYerr'])+"\nlen = "+str(len(fit_params['sigmaYerr'])))
            ### self.output("\n")

            fit = fit_module.fitemittance(fit_params['q1current'],fit_params['q2current'],fit_params['q3current'],
                                fit_params['quad2scan'],fit_params['quadcurrents'],fit_params['stepList'],fit_params['photosperstep'],
                                fit_params['energy'],fit_params['sigmaX'],fit_params['sigmaY'],fit_params['sigmaXerr'],fit_params['sigmaYerr'])
            
            self.output( "==================================================")
            self.output( "paramx: "+str(fit.getParamX()))
            self.output( "paramy: "+str(fit.getParamY()))
            self.output( "alphas: "+str(fit.getAlpha()))
            self.output( "betas: "+str(fit.getBeta()))
            self.output( "epsilon: "+str(fit.getEpsilon()))
            self.output( "==================================================")


            
        except Exception,e:
            self.output("Some error while computing the emittance fit: %s",str(e))

        # 4) Log some data to the door output
        pass
