"""
    Macro library containning diffractometer related macros for the macros 
    server Tango device server as part of the Sardana project.
    
"""
import time
from macro import *

class _diffrac:
    """Internal class used as a base class for the diffractometer macros"""

    env = ('DiffracDevice',)
    
    def prepare(self):

        self.prepared = False
        
        dev_name = self.getEnv('DiffracDevice')        
        self.diffrac = self.getDevice(dev_name)
        
        h_dev_name = dev_name + "-h"       
        self.h_device = self.getDevice(h_dev_name)
        
        k_dev_name =  dev_name + "-k"       
        self.k_device = self.getDevice(k_dev_name)
        
        l_dev_name =  dev_name + "-l"     
        self.l_device = self.getDevice(l_dev_name)
        
        hkl_simu_dev_name =  dev_name + "-sim-hkl"       
        self.hkl_simu_device = self.getDevice(hkl_simu_dev_name)
        
        psi_simu_dev_name =  dev_name + "-sim-psi"       
        self.psi_simu_device = self.getDevice(psi_simu_dev_name)
        
        prop = self.diffrac.get_property(['DiffractometerType'])        
        for v in prop['DiffractometerType']:       
            self.type = v
    
        prop = self.diffrac.get_property(['RealAxisProxies'])        
        self.angle_device_name = {}         
        self.angle_names = []       
        for v in prop['RealAxisProxies']:       
            name_list = v.split(":")       
            self.angle_names.append(name_list[0])      
            self.angle_device_name[name_list[0]] = name_list[1]
            
        if self.diffrac.Crystal == "":
            if(self.diffrac.read_attribute("CrystalNames").dim_x > 0):
                 crystals = self.diffrac.CrystalNames
                 self.diffrac.write_attribute("Crystal", crystals[0])

        self.prepared = True


    def set_reflection(self,i,*params):

        print self.diffrac.crystal

        reflections = []   

        reflections = self.diffrac.Reflections

        nb_reflections = len(reflections)
        
        if i > nb_reflections:
            self.output("Only " + str(nb_reflections) + " reflections are defined.")
            self.output("Reflection " + str(i) + " cannot be added/updated.")
            self.output("Select other reflection index: 0 < index < " + str(nb_reflections + 1))
            return
                
        if self.type == 'E6C':  
            factor = 12               
        elif self.type == 'E4CV':  
            factor = 10
                
        nb_parameters = len(params)
        if nb_parameters > 3:

            if self.type == 'E6C':    
                if nb_parameters != 9:
                    self.output("Wrong number of parameters. 6 angles have to be given")
                    return  
            elif self.type == 'E4CV':    
                if nb_parameters != 7:
                    self.output("Wrong number of parameters. 4 angles have to be given")
                    return
            
            if i != nb_reflections:
                
                self.save_all_reflection()
                for k in range(0, nb_reflections):
                    # Use only index 0 in RemoveReflection, because when a reflection is moved the other ones change their index. It is necesary to remove the reflections because is the only way of changing the
                    # angles (writting to the attribute Reflections only allow to change hkl, and
                    # AddReflections takes the current angles.
                    self.diffrac.RemoveReflection(0)
                    
                for k in range(0, nb_reflections):
                    print self.saved_reflection
                    if i == k:
                        self.saved_reflection[factor*k + 1] = params[0]
                        self.saved_reflection[factor*k + 2] = params[1]
                        self.saved_reflection[factor*k + 3] = params[2]
                        self.saved_reflection[factor*k + 6] = params[3]
                        self.saved_reflection[factor*k + 7] = params[4]
                        self.saved_reflection[factor*k + 8] = params[5]
                        self.saved_reflection[factor*k + 9] = params[6]
                        if nb_parameters > 7:
                            self.saved_reflection[factor*k + 10] = params[7]
                            self.saved_reflection[factor*k + 11] = params[8]
                                
                    self.diffrac.write_attribute("Simulated",1)
                
                    if self.type == 'E6C':                 
                        self.diffrac.write_attribute("axisMu", self.saved_reflection[factor*k + 6])
                        self.diffrac.write_attribute("axisOmega", self.saved_reflection[factor*k + 7])
                        self.diffrac.write_attribute("axisChi", self.saved_reflection[factor*k + 8])
                        self.diffrac.write_attribute("axisPhi", self.saved_reflection[factor*k + 9])
                        self.diffrac.write_attribute("axisGamma", self.saved_reflection[factor*k + 10])
                        self.diffrac.write_attribute("axisDelta", self.saved_reflection[factor*k + 11])
                    elif self.type == 'E4CV':            
                        self.diffrac.write_attribute("axisOmega", self.saved_reflection[factor*k + 6])
                        self.diffrac.write_attribute("axisChi", self.saved_reflection[factor*k + 7])
                        self.diffrac.write_attribute("axisPhi", self.saved_reflection[factor*k + 8])
                        self.diffrac.write_attribute("axisTth", self.saved_reflection[factor*k + 9]) 

                        values = []                 
        
                        values.append(self.saved_reflection[factor*k + 0])        
                        values.append(self.saved_reflection[factor*k + 1])        
                        values.append(self.saved_reflection[factor*k + 2])
                        values.append(self.saved_reflection[factor*k + 3])
                        values.append(self.saved_reflection[factor*k + 4])
                        self.diffrac.AddReflection(values)
                    
                    # AddReflection doesn't use the arguments. It takes as HKL the current
                    # values, that means the values corresponding to the angles that
                    # we have just set. So we have to change them by wrinting the attribute
                    # Reflections with the values we want to set (writing to this attribute
                    # only modifies the h,k,l values, the angles are not modified)
        
                    self.diffrac.write_attribute("Reflections", self.saved_reflection,10,nb_reflections)
        
                    if not self.diffrac.Simulated:
                          self.diffrac.write_attribute("Simulated",1)
                    
                return
                       
            self.diffrac.write_attribute("Simulated",1)
                
            if self.type == 'E6C':                 
                self.diffrac.write_attribute("axisMu", params[3])                 
                self.diffrac.write_attribute("axisOmega", params[4])                 
                self.diffrac.write_attribute("axisChi", params[5])                 
                self.diffrac.write_attribute("axisPhi", params[6])                 
                self.diffrac.write_attribute("axisGamma", params[7])                 
                self.diffrac.write_attribute("axisDelta", params[8])               
            elif self.type == 'E4CV':                 
                self.diffrac.write_attribute("axisOmega", params[3])                 
                self.diffrac.write_attribute("axisChi", params[4])                 
                self.diffrac.write_attribute("axisPhi", params[5])                 
                self.diffrac.write_attribute("axisTth", params[6])

            values = []
        
            values.append(params[0])        
            values.append(params[1])        
            values.append(params[2])
            values.append(0)
            values.append(1)
            # AddReflection takes the current values for angles and hkl, it doesn't use the
            # arguments. 
            self.diffrac.AddReflection(values) 
                       
            self.save_all_reflection()  
                       
            self.saved_reflection[factor*i + 1] = params[0]                         
            self.saved_reflection[factor*i + 2] = params[1]                         
            self.saved_reflection[factor*i + 3] = params[2]                         
            self.saved_reflection[factor*i + 6] = params[3]                         
            self.saved_reflection[factor*i + 7] = params[4]                         
            self.saved_reflection[factor*i + 8] = params[5]                         
            self.saved_reflection[factor*i + 9] = params[6]                         
            if nb_parameters > 7:                         
                self.saved_reflection[factor*i + 10] = params[7]                         
                self.saved_reflection[factor*i + 11] = params[8]
                
            # The number of reflections is now increased by one.                         
            self.diffrac.write_attribute("Reflections", self.saved_reflection,10,nb_reflections+1)
                       
            return
    
        
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)

        if( nb_parameters < 4):
            if(i < nb_reflections):
                # It is only necesary to write in the attribute Reflections changing the hkl values
                
                self.save_all_reflection()
                
                self.saved_reflection[factor*i + 1] = params[0] 
                self.saved_reflection[factor*i + 2] = params[1]
                self.saved_reflection[factor*i + 3] = params[2] 
        
                self.diffrac.write_attribute("Reflections", self.saved_reflection,10,nb_reflections)
            else:
                values = []  
                values.append(params[0])  
                values.append(params[1])  
                values.append(params[2])
            # 0 -> relevance (obsolete). 1 -> for taking this reflection in affinement calculations 
                values.append(0)  
                values.append(1)
        
                self.diffrac.AddReflection(values)
                
                self.save_all_reflection()
                
                self.saved_reflection[factor*i + 1] = params[0] 
                self.saved_reflection[factor*i + 2] = params[1]
                self.saved_reflection[factor*i + 3] = params[2] 
        
                self.diffrac.write_attribute("Reflections", self.saved_reflection,10,nb_reflections + 1)

        self.diffrac.write_attribute("Simulated",0)


    def save_all_reflection(self):
        reflections = self.diffrac.Reflections
        nb_reflections = len(reflections)
        
        self.saved_reflection = []
        for i in range(0,nb_reflections):
            for k in range(0,10):
                self.saved_reflection.append(reflections[i][k])
                              

class br(Macro, _diffrac):
    """The br macro is used to move the diffractometer to the reciprocal space 
    coordinates given by H, K and L. If a fourth parameter is given, the combination
    of angles to be set is the correspondig to the given index. The index of the
    angles combinations are then changed."""

    param_def = [
       ['H', Type.Float, None, "H value"],
       ['K', Type.Float, None, "K value"],
       ['L', Type.Float, 1.0, "L value"],
       ['AnglesIndex', Type.Integer, 0, "Angles index"]
    ]

    def prepare(self, H, K, L, AnglesIndex):
        _diffrac.prepare(self)
        
    def run(self, H, K, L, AnglesIndex):
        if not self.prepared:
            return
        
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
        
        if not AnglesIndex != 0:
            self.diffrac.write_attribute("AnglesIdx",AnglesIndex)
        
        self.hkl_simu_device.write_attribute("h",H)        
        self.hkl_simu_device.write_attribute("k",K) 
        self.hkl_simu_device.write_attribute("l",L)
        
#        values = []
        
#        values.append(H)        
#        values.append(K)        
#        values.append(L)
      
#        self.diffrac.SetHKL(values)
      
        angles_to_set = {}
    
        if self.type == 'E6C':    
            mu = self.diffrac.axisMu
            omega = self.diffrac.axisOmega
            chi = self.diffrac.axisChi
            phi = self.diffrac.axisPhi
            gamma = self.diffrac.axisGamma
            delta = self.diffrac.axisDelta
        
            angles_to_set["mu"] = mu
            angles_to_set["omega"] = omega
            angles_to_set["chi"] = chi
            angles_to_set["phi"] = phi
            angles_to_set["gamma"] = gamma
            angles_to_set["delta"] = delta        
        elif self.type == 'E4CV':
            omega = self.diffrac.axisOmega
            chi = self.diffrac.axisChi
            phi = self.diffrac.axisPhi
            tth = self.diffrac.axisTth
            
            angles_to_set["omega"] = omega
            angles_to_set["chi"] = chi
            angles_to_set["phi"] = phi
            angles_to_set["tth"] = tth
            
        for angle in self.angle_names:
            angle_dev = self.getDevice(self.angle_device_name[angle])
            angle_dev.write_attribute("Position",angles_to_set[angle])
            
        self.diffrac.write_attribute("Simulated",0)

        self.execMacro('printmove')

class wh(Macro, _diffrac):
    """wh - where, principal axes and reciprocal space
        
    Prints the current reciprocal space coordinates (H K L) and the user 
    positions of the principal motors. Depending on the diffractometer geometry, 
    other parameters such as the angles of incidence and reflection (ALPHA and 
    BETA) and the incident wavelength (LAMBDA) may be displayed.""" 

    def prepare(self):
        _diffrac.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        for angle in self.angle_names:
            angle_device = self.getDevice(self.angle_device_name[angle])
            self.output("%s = %7.5f " % (angle,angle_device.Position))
            
        self.output("H = %7.5f  K = %7.5f L = %7.5f" % (self.h_device.position, self.k_device.position, self.l_device.position))
            
        self.output("Wavelength = %7.5f" % (self.diffrac.WaveLength))

class orn(Macro, _diffrac):
    """Set orientation reflection indicated by the index.""" 
    
    param_def = [
       ['i', Type.Integer, None, "reflection index (starting at 0)"],
       ['H', Type.Float,   None, "H value"],
       ['K', Type.Float,   None, "K value"],
       ['L', Type.Float,   None, "L value"],
       ['ang1', Type.Float, -9999., "mu/omega"],
       ['ang2', Type.Float, -9999., "omega/chi"],
       ['ang3', Type.Float, -9999., "chi/phi"],
       ['ang4', Type.Float, -9999., "phi/tth"],
       ['ang5', Type.Float, -9999., "gamma"],
       ['ang6', Type.Float, -9999., "delta"]
    ]
    
    def prepare(self, i, H, K, L, ang1, ang2, ang3, ang4, ang5, ang6):
        _diffrac.prepare(self)
    
    def run(self, i, H, K, L, ang1, ang2, ang3, ang4, ang5, ang6):
        if not self.prepared:
            return

        send4 = 0
        send6 = 0
        if ang1 != -9999.:
            if ang2 != -9999.:
                if ang3 != -9999:
                    if ang4 != -9999:
                        send4 = 1
                        if ang5 != -9999:
                            if ang6 != -9999:
                                send6 = 1

        if send6 == 1:                        
            self.set_reflection(i, H, K, L, ang1, ang2, ang3, ang4, ang5, ang6)
        elif send4 == 1:
            self.set_reflection(i, H, K, L, ang1, ang2, ang3, ang4)
        else:                         
            self.set_reflection(i, H, K, L)                            
       
class or0(Macro, _diffrac):
    """Set primary orientation reflection.""" 
    
    param_def = [
       ['H', Type.Float, None, "H value"],
       ['K', Type.Float, None, "K value"],
       ['L', Type.Float, None, "L value"],
    ]
    
    def prepare(self, H, K, L):
        _diffrac.prepare(self)
    
    def run(self, H, K, L):
        if not self.prepared:
            return
        
        self.set_reflection(0, H, K, L) 

class or1(Macro, _diffrac):
    """Set secondary orientation reflection.""" 
    
    param_def = [
       ['H', Type.Float, None, "H value"],
       ['K', Type.Float, None, "K value"],
       ['L', Type.Float, None, "L value"],
    ]
    
    def prepare(self, H, K, L):
        _diffrac.prepare(self)
    
    def run(self, H, K, L):
        if not self.prepared:
            return

        self.set_reflection(1, H, K, L) 

class setorn(Macro, _diffrac):
    """Set orientation reflection indicated by the index.""" 
    
    param_def = [
       ['i', Type.Integer, None, "reflection index (starting at 0)"],
    ]
 
    
    def prepare(self):
        _diffrac.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        self.set_reflection(i, H, K, L)

class setor0(Macro, _diffrac):
    """Set primary orientation reflection. Alternative to or0""" 
    
    def prepare(self):
        _diffrac.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        H = self.h_device.position
        K = self.k_device.position
        L = self.l_device.position
        
        self.set_reflection(0, H, K, L)
        
class setor1(Macro, _diffrac):
    """Set secondary orientation reflection. Alternative to or1""" 
    
    def prepare(self):
        _diffrac.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        self.set_reflection(1, H, K, L)
        
class setlat(Macro, _diffrac):
    """Set the crystal lattice parameters a, b, c, alpha, beta, gamma.
       for the currently active diffraction pseudo motor controller."""  
    
    param_def = [
       ['a', Type.Float, None, "Lattice 'a' parameter"],
       ['b', Type.Float, None, "Lattice 'b' parameter"],
       ['c', Type.Float, None, "Lattice 'c' parameter"],
       ['alpha', Type.Float, None, "Lattice 'alpha' parameter"],
       ['beta',  Type.Float, None, "Lattice 'beta' parameter"],
       ['gamma', Type.Float, None, "Lattice 'gamma' parameter"]
    ]

    hints = { 'interactive' : 'True' }

    def prepare(self, a, b, c, alpha, beta, gamma):
        _diffrac.prepare(self)
    
    def run(self, a, b, c, alpha, beta, gamma):
        if not self.prepared:
            return

        values = []  
        values.append(a)   
        values.append(b)  
        values.append(c)  
        values.append(alpha)  
        values.append(beta)  
        values.append(gamma)
        
        self.diffrac.ConfigureCrystal(values)
        
class diffrac_setmode(Macro, _diffrac):
    """Set operation mode.""" 
    
    param_def = [
       ['new_mode_1', Type.String, None, "Mode to be set"],
       ['new_mode_2', Type.String, " ", "Mode to be set"]
    ]    
   
    def prepare(self, new_mode_1, new_mode_2):
        _diffrac.prepare(self)
        
    def run(self, new_mode_1, new_mode_2):
        if not self.prepared:
            return   
        
        modes = self.hkl_simu_device.modeNames 
        
        mode = "%s %s" % (str(new_mode_1), str(new_mode_2))     
        
        set_mode = 0   
        
        for pd_mode in modes: 
            part_mode = pd_mode.split()
            if len(part_mode) == 1:
                if str(new_mode_1) == str(pd_mode): 
                    set_mode = pd_mode 
            else:
                if mode == pd_mode: 
                    set_mode = pd_mode
                    
        if set_mode == 0: 
            self.output("Wrong mode -> select one from the list:") 
            self.output(modes) 
            return
                    
        self.hkl_simu_device.write_attribute("mode",set_mode)

class diffrac_get_mode(Macro, _diffrac):
    """Get operation mode."""
    
    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.hkl_simu_device.mode)
        
class H(Macro, _diffrac):
    """x component of the scattering vector."""

    result_def = [
        ['H',  Type.Float, None, 'x component of the scattering vector']
    ]

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.h_device.position)

class K(Macro, _diffrac):
    """y component of the scattering vector.""" 

    result_def = [
        ['K',  Type.Float, None, 'y component of the scattering vector']
    ]

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return

        self.output(self.k_device.position)

class L(Macro, _diffrac):
    """z component of the scattering vector."""

    result_def = [
        ['L',  Type.Float, None, 'z component of the scattering vector']
    ]

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return

        self.output(self.l_device.position)
        
class LAMBDA(Macro, _diffrac):
    """x component of the scattering vector."""

    result_def = [
        ['LAMBDA',  Type.Float, None, 'Incident X-ray wavelength lambda.']
    ]

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.diffrac.WaveLength)
    
class showUB(Macro, _diffrac):
    """Prints the current crystal UB matrix."""

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.diffrac.UB)
      
class pa(Macro, _diffrac):
    """Prints information about the active diffractometer."""
    
    suffix = ("st","nd","rd","th")
    
    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        if self.type == 'E6C':
            str_type = "Eulerian 6C"        
        elif self.type == 'E4CV':
            str_type = "Eulerian 4C Vertical"
            
        self.output("%s Geometry, %s" % (str_type, self.diffrac.mode))
        self.output("Sector %s" % "[ToDo]")
        self.output("")

        
        nb_reflections = self.diffrac.GetReflectionSize()

        
        for i in range(0,nb_reflections):
            if i < len(self.suffix): sf = self.suffix[i]
            else: sf = self.suffix[3]
            reflection = self.diffrac.GetReflection(i)
            self.output("  %d%s Reflection (index %d): " % (i+1,sf,i))
            j = 0
            part = []
            for par in reflection:
                part.append(par)
                j = j + 1
            self.output("H %7.5f K %7.5f  L %7.5f  " % (part[0], part[1], part[2]))
            self.output("Angles ")
            for k in range(5, len(part)):
                self.output(part[k])
            self.output("")
        
        self.output("  Lattice Constants (lengths / angles):")
        self.output("%24s = %s %s %s / %s %s %s" % ("real space", self.diffrac.a, 
                                                    self.diffrac.b, self.diffrac.c, self.diffrac.alpha, 
                                                    self.diffrac.beta, self.diffrac.gamma))
        
        self.output("  Reciprocal Space (lengths / angles):")
        self.output("%24s = %7.5f %7.5f %7.5f / %s %s %s" % ("real space", self.diffrac.aStar, 
                                                    self.diffrac.bStar, self.diffrac.cStar, self.diffrac.alphaStar, 
                                                    self.diffrac.betaStar, self.diffrac.gammaStar))
        
        self.output("")
        self.output("  Azimuthal Reference:")
        self.output("%24s = %s" %("[ToDo]","[ToDo]"))
        self.output("")
        self.output("%24s = %s" %("Lambda",self.diffrac.WaveLength))
        self.output("")
        self.output(" Cut Points:")
        self.output("    [ToDo]")
        
class ca(Macro, _diffrac):
    """Calculate motor positions for given H K L according to the current
    operation mode."""
    
    param_def = [
       ['H', Type.Float, None, "H value for the azimutal vector"],
       ['K', Type.Float, None, "K value for the azimutal vector"],
       ['L', Type.Float, None, "L value for the azimutal vector"],
    ]    
    
    def prepare(self, H, K , L):
        _diffrac.prepare(self)    
    
    def run(self, H, K, L):
        if not self.prepared:
            return
        
        self.diffrac.write_attribute("Simulated",1)
        
        self.hkl_simu_device.write_attribute("h",H)        
        self.hkl_simu_device.write_attribute("k",K) 
        self.hkl_simu_device.write_attribute("l",L)

#        values = []
        
#        values.append(H)        
#        values.append(K)        
#        values.append(L)
       
#        self.diffrac.SetHKL(values)                
                
        if self.type == 'E6C':
            self.output("Mu = %7.5f  Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Gamma %7.5f Delta %7.5f " % (self.diffrac.axisMu, self.diffrac.axisOmega, self.diffrac.axisChi, self.diffrac.axisPhi, self.diffrac.axisGamma, self.diffrac.axisDelta,))                               
        elif self.type == 'E4CV':
            self.output("Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Tth %7.5f " % (self.diffrac.axisOmega, self.diffrac.axisChi, self.diffrac.axisPhi, self.diffrac.axisTth,))
            
        self.output("Alpha = %s  Beta = %s  Azimuth = %s" % ("[ToDo]","[ToDo]","[ToDo]",))
            
        self.output("Omega = %s  Lambda = %7.5f" %("[TODO]",self.diffrac.WaveLength))
        
        self.diffrac.write_attribute("Simulated",0)
        
class cal(Macro, _diffrac):
    """Calculate motor positions for given H K L according to the current
    operation mode. Leave the motors in the calculated positions."""
    
    param_def = [
       ['H', Type.Float, None, "H value for the azimutal vector"],
       ['K', Type.Float, None, "K value for the azimutal vector"],
       ['L', Type.Float, None, "L value for the azimutal vector"],
    ]    
    
    def prepare(self, H, K , L):
        _diffrac.prepare(self)    
    
    def run(self, H, K, L):
        if not self.prepared:
            return
        
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
        
        self.hkl_simu_device.write_attribute("h",H)        
        self.hkl_simu_device.write_attribute("k",K) 
        self.hkl_simu_device.write_attribute("l",L)
        

#        values = []
        
#        values.append(H)        
#        values.append(K)        
#        values.append(L)
        
#        self.diffrac.SetHKL(values)
      
        angles_to_set = {}
    
        if self.type == 'E6C':    
            mu = self.diffrac.axisMu
            omega = self.diffrac.axisOmega
            chi = self.diffrac.axisChi
            phi = self.diffrac.axisPhi
            gamma = self.diffrac.axisGamma
            delta = self.diffrac.axisDelta
        
            angles_to_set["mu"] = mu
            angles_to_set["omega"] = omega
            angles_to_set["chi"] = chi
            angles_to_set["phi"] = phi
            angles_to_set["gamma"] = gamma
            angles_to_set["delta"] = delta
            self.output("Mu = %7.5f  Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Gamma %7.5f Delta %7.5f " % (mu, omega, chi, phi, gamma, delta,))        
        elif self.type == 'E4CV':
            omega = self.diffrac.axisOmega
            chi = self.diffrac.axisChi
            phi = self.diffrac.axisPhi
            tth = self.diffrac.axisTth
            
            angles_to_set["omega"] = omega
            angles_to_set["chi"] = chi
            angles_to_set["phi"] = phi
            angles_to_set["tth"] = tth
            self.output("Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Tth %7.5f " % (omega, chi, phi, tth,))
            
  
            
        self.output("Alpha = %s  Beta = %s  Azimuth = %s" % ("[ToDo]","[ToDo]","[ToDo]",))
            
        self.output("Omega = %s  Lambda = %7.5f" %("[TODO]",self.diffrac.WaveLength))
    
        for angle in self.angle_names:
            angle_dev = self.getDevice(self.angle_device_name[angle])
            angle_dev.write_attribute("Position",angles_to_set[angle])
            
        self.diffrac.write_attribute("Simulated",0)

        self.execMacro('printmove')

        
class ci(Macro, _diffrac):
    """Display calculated H K L for input angles."""
    
    param_def = [
       ['ang1', Type.Float, None, "mu/omega"],
       ['ang2', Type.Float, None, "omega/chi"],
       ['ang3', Type.Float, -1, "chi/phi"],
       ['ang4', Type.Float, -1, "phi/tth"],
       ['ang5', Type.Float, -1, "gamma"],
       ['ang6', Type.Float, -1, "delta"]
    ]    
    
    def prepare(self, ang1, ang2, ang3, ang4, ang5, ang6):
        _diffrac.prepare(self)    
    
    def run(self, ang1, ang2, ang3, ang4, ang5, ang6):
        if not self.prepared:
            return
        
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
                
        if self.type == 'E6C':                 
            self.diffrac.write_attribute("axisMu", ang1)                 
            self.diffrac.write_attribute("axisOmega", ang2)                 
            self.diffrac.write_attribute("axisChi", ang3)                 
            self.diffrac.write_attribute("axisPhi", ang4)                 
            self.diffrac.write_attribute("axisGamma", ang5)                 
            self.diffrac.write_attribute("axisDelta", ang6)               
        elif self.type == 'E4CV':                 
            self.diffrac.write_attribute("axisOmega", ang1)                 
            self.diffrac.write_attribute("axisChi", ang2)                 
            self.diffrac.write_attribute("axisPhi", ang3)                 
            self.diffrac.write_attribute("axisTth", ang4)
            
        self.output("H = %7.5f  K = %7.5f  L  = %7.5f " % (self.hkl_simu_device.h, self.hkl_simu_device.k, self.hkl_simu_device.l,))
            
        self.diffrac.write_attribute("Simulated",0)
        
            
class calcA(Macro, _diffrac):
    """Calculate motor positions for current H K L."""
    
    def prepare(self):
        _diffrac.prepare(self)    
    
    def run(self):
        if not self.prepared:
            return
        
        H = self.h_device.position        
        K = self.k_device.position        
        L = self.l_device.position
        
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
        
        self.hkl_simu_device.write_attribute("h",H)        
        self.hkl_simu_device.write_attribute("k",K) 
        self.hkl_simu_device.write_attribute("l",L)
        
#        values = []
        
#        values.append(H)        
#        values.append(K)        
#        values.append(L)
      
#        self.diffrac.SetHKL(values)
        
        if self.type == 'E6C':
            self.output("Mu = %7.5f  Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Gamma %7.5f Delta %7.5f " % (self.diffrac.axisMu, self.diffrac.axisOmega, self.diffrac.axisChi, self.diffrac.axisPhi, self.diffrac.axisGamma, self.diffrac.axisDelta,))        
        elif self.type == 'E4CV':
            self.output("Omega = %7.5f  Chi  = %7.5f Phi = %7.5f Tth %7.5f  " % (self.diffrac.axisOmega, self.diffrac.axisChi, self.diffrac.axisPhi, self.diffrac.axisTth,))
            
        self.diffrac.write_attribute("Simulated",0)
        
class calcHKL(Macro, _diffrac):
    """Calculate H K L for current motor positions"""

    def prepare(self):
        _diffrac.prepare(self)
            
    def run(self):
        if not self.prepared:
            return
      
        angles_real = {}
    
        for angle in self.angle_names:
            angle_dev = self.getDevice(self.angle_device_name[angle])
            angles_real[angle] = angle_dev.Position
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
    
        if self.type == 'E6C':    
            self.diffrac.write_attribute("axisMu", angles_real["mu"])
            self.diffrac.write_attribute("axisOmega", angles_real["omega"])
            self.diffrac.write_attribute("axisChi", angles_real["chi"])
            self.diffrac.write_attribute("axisPhi", angles_real["phi"])
            self.diffrac.write_attribute("axisGamma", angles_real["gamma"])
            self.diffrac.write_attribute("axisDelta", angles_real["delta"])
        elif self.type == 'E4CV':
            self.diffrac.write_attribute("axisOmega", angles_real["omega"])
            self.diffrac.write_attribute("axisChi", angles_real["chi"])
            self.diffrac.write_attribute("axisPhi", angles_real["phi"])
            self.diffrac.write_attribute("axisTth", angles_real["tth"])
        
        self.output("H = %7.5f  K = %7.5f  L  = %7.5f " % (self.h_device.position, self.k_device.position, self.l_device.position))
            
        self.diffrac.write_attribute("Simulated",0)

class diffrac_getAllAngles(Macro, _diffrac):
    """Displays all posible angles combination for the given HKL values"""

    param_def = [
       ['H', Type.Float, 100., "H value"],
       ['K', Type.Float, 100., "K value"],
       ['L', Type.Float, 100., "L value"]
    ]

    def prepare(self, H, K, L):
        _diffrac.prepare(self)
        
    def run(self, H, K, L):
        if not self.prepared:
            return
        
        if not H == K == L == 100.:
            if not self.diffrac.Simulated:
                self.diffrac.write_attribute("Simulated",1)
        
            self.hkl_simu_device.write_attribute("h",H)        
            self.hkl_simu_device.write_attribute("k",K) 
            self.hkl_simu_device.write_attribute("l",L)
        
#            values = []
        
#            values.append(H)        
#            values.append(K)        
#            values.append(L)
      
#            self.diffrac.SetHKL(values)
            
        self.output("Index H K L Angles")
            
        self.output(self.diffrac.Angles)
        
        self.diffrac.write_attribute("Simulated",0)

class diffrac_setAnglesIdx(Macro, _diffrac):
    """Set angles index to be used. It changes the order of the combinations"""

    param_def = [
       ['AngleIndex', Type.Integer, 0, "Angle Index"]
    ]

    def prepare(self, AngleIndex):
        _diffrac.prepare(self)
        
    def run(self, AngleIndex):
        if not self.prepared:
            return
        
        self.diffrac.write_attribute("AnglesIdx",AngleIndex)
    
class diffrac_angle(Macro, _diffrac):
    """If only the angle name is given as an argument, it returns the current angle value. If a new value for the angle is also given, it moves the motor to the given position."""

    param_def = [
       ['angle', Type.String, None, "Angle name"],
       ['set_value', Type.Float, -99999., "Value to set"]
    ]

    def prepare(self, angle, set_value):
        _diffrac.prepare(self)
        
    def run(self, angle, set_value):
        if not self.prepared:
            return 
    
        flag_ok = 0 
        for tmp_angle in self.angle_names:
            if tmp_angle == angle:
                flag_ok = 1
                
        if flag_ok is 0:
            self.output("This angle doesn't exist. Posible names are:")
            for tmp_angle in self.angle_names:
                self.output(tmp_angle)
            return                  
                        
        angle_dev = self.getDevice(self.angle_device_name[angle]) 
        
        if set_value == int(-99999):
            self.output(angle_dev.Position)
            return 
        
        angle_dev.write_attribute("Position",set_value)

class diffrac_getCrystalNames(Macro, _diffrac):
    """Display the names of the defined crystals"""

    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        if(self.diffrac.read_attribute("CrystalNames").dim_x > 0):
            self.output("List of crystals:")
            crystals = self.diffrac.CrystalNames
            for crystal in crystals:
                self.output(crystal)
        else:
            self.output("Not crystals defined")
        
class diffrac_setCrystal(Macro, _diffrac):
    """Set the current crystal to the one given as an argument"""

    param_def = [
       ['new_crystal', Type.String, None, "Crystal to set"]
    ]
    
    def prepare(self, new_crystal):
        _diffrac.prepare(self)
        
    def run(self, new_crystal):
        if not self.prepared:
            return

        self.diffrac.write_attribute("Crystal", new_crystal)
        self.output("Crystal changed to: ")
        self.output(self.diffrac.Crystal)

class diffrac_getCrystal(Macro, _diffrac):
    """Get current crystal"""
    
    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        
        self.output("Current crystal:  ")
        self.output(self.diffrac.Crystal) 
        
class diffrac_removeReflection(Macro, _diffrac):
    """Remove reflection indicated by index"""
        
    param_def = [
       ['index', Type.Integer, None, "Index of reflection to be removed"]
    ]
    
    def prepare(self, index):
        _diffrac.prepare(self)
        
    def run(self, index):
        if not self.prepared:
            return
        
        nb_reflections = self.diffrac.GetReflectionSize()
        if index > nb_reflections:
            self.output("Only " + str(nb_reflections) + " reflections are defined.")
            self.output("Reflection " + str(i) + " cannot be removed.")
            self.output("Select other reflection index: 0 < index < " + str(nb_reflections))   
        self.diffrac.RemoveReflection(index)
        
class diffrac_setPsi(Macro, _diffrac):
    """Set psi value"""
        
    param_def = [
       ['psi', Type.Integer, None, "Psi value to be set"]
    ]
    
    def prepare(self, psi):
        _diffrac.prepare(self)
        
    def run(self, psi):
        if not self.prepared:
            return
        if not self.diffrac.Simulated:
            self.diffrac.write_attribute("Simulated",1)
        
        if self.hkl_simu_device.mode!= 'psi_constant_vertical':
            self.psi_simu_device.AxisInit()
            self.psi_simu_device.write_attribute("psi",psi)
            angles_to_set = {}
    
            if self.type == 'E6C':    
                mu = self.diffrac.axisMu
                omega = self.diffrac.axisOmega
                chi = self.diffrac.axisChi
                phi = self.diffrac.axisPhi
                gamma = self.diffrac.axisGamma
                delta = self.diffrac.axisDelta
        
                angles_to_set["mu"] = mu
                angles_to_set["omega"] = omega
                angles_to_set["chi"] = chi
                angles_to_set["phi"] = phi
                angles_to_set["gamma"] = gamma
                angles_to_set["delta"] = delta        
            elif self.type == 'E4CV':
                omega = self.diffrac.axisOmega
                chi = self.diffrac.axisChi
                phi = self.diffrac.axisPhi
                tth = self.diffrac.axisTth
            
                angles_to_set["omega"] = omega
                angles_to_set["chi"] = chi
                angles_to_set["phi"] = phi
                angles_to_set["tth"] = tth
            
            for angle in self.angle_names:
                angle_dev = self.getDevice(self.angle_device_name[angle])
                angle_dev.write_attribute("Position",angles_to_set[angle])
            
            self.diffrac.write_attribute("Simulated",0)

            self.execMacro('printmove')
            
        else:
        
            H = self.h_device.position        
            K = self.k_device.position        
            L = self.l_device.position
            
            pars = []
            pars.append(1)
            pars.append(0)
            pars.append(0)
            pars.append(psi)
            names = []
            names.append("h2")
            names.append("k2")
            names.append("l2")
            names.append("psi")
            
            newtuple = []
            newtuple.append(pars)
            newtuple.append(names)
            
            self.diffrac.SetModeParameters(newtuple)
            
            self.diffrac.write_attribute("Simulated",1)
        
            self.hkl_simu_device.write_attribute("h",H)        
            self.hkl_simu_device.write_attribute("k",K) 
            self.hkl_simu_device.write_attribute("l",L)

            print H + " " + K + " " + L
      
            angles_to_set = {}
    
            if self.type == 'E6C':    
                mu = self.diffrac.axisMu
                omega = self.diffrac.axisOmega
                chi = self.diffrac.axisChi
                phi = self.diffrac.axisPhi
                gamma = self.diffrac.axisGamma
                delta = self.diffrac.axisDelta
        
                angles_to_set["mu"] = mu
                angles_to_set["omega"] = omega
                angles_to_set["chi"] = chi
                angles_to_set["phi"] = phi
                angles_to_set["gamma"] = gamma
                angles_to_set["delta"] = delta        
            elif self.type == 'E4CV':
                omega = self.diffrac.axisOmega
                chi = self.diffrac.axisChi
                phi = self.diffrac.axisPhi
                tth = self.diffrac.axisTth
            
                angles_to_set["omega"] = omega
                angles_to_set["chi"] = chi
                angles_to_set["phi"] = phi
                angles_to_set["tth"] = tth   
            
            for angle in self.angle_names:
                print "Device name " + self.angle_device_name[angle]
                angle_dev = self.getDevice(self.angle_device_name[angle])
                print "Angle to set " + str(angles_to_set[angle])
                angle_dev.write_attribute("Position",angles_to_set[angle])
            
            self.diffrac.write_attribute("Simulated",0)

            self.execMacro('printmove')
        

class diffrac_getPsi(Macro, _diffrac):
    """Get current psi value"""
    
    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return
        self.output("Psi value:")
        self.output(self.psi_simu_device.psi)

        

class printmove(Macro,_diffrac):


    def prepare(self):
        _diffrac.prepare(self)
        
    def run(self):
        if not self.prepared:
            return     
        moving = 1
        tmp_dev = {}
        for angle in self.angle_names:
            tmp_dev[angle] = self.getDevice(self.angle_device_name[angle])
        while(moving):
            moving = 0
            for angle in self.angle_names:
                if tmp_dev[angle].state() == 6:
                    moving = 1
            self.output("H = %7.5f  K = %7.5f L = %7.5f" % (self.h_device.position, self.k_device.position, self.l_device.position)) 
            self.flushOutput()
            time.sleep(1.0)
        self.output("H = %7.5f  K = %7.5f L = %7.5f" % (self.h_device.position, self.k_device.position, self.l_device.position)) 
        self.flushOutput()
  
        
                     
