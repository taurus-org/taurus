import Controller

class MotorController(Controller.Controller):
    trace = ["AddDevice", "DeleteDevice", "SendToCtrl",
             "GetExtraAttributePar", "SetExtraAttributePar", 
             "PreStateAll", "PreStateOne", "StateAll", "StateOne", 
             "PreReadAll", "PreReadOne", "ReadAll", "ReadOne",
             "PreStartAll", "PreStartOne", "StartOne", "StartAll", 
             "SetPar", "GetPar", "DefinePosition", "AbortOne", "StopOne"]

