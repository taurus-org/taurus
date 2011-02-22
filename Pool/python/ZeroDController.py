import Controller

class ZeroDController(Controller.Controller):
    trace = ["AddDevice", "DeleteDevice", "SendToCtrl",
             "GetExtraAttributePar", "SetExtraAttributePar",
             "PreStateAll", "PreStateOne", "StateAll", "StateOne", 
             "PreReadAll", "PreReadOne", "ReadAll", "ReadOne", "Abort"]
