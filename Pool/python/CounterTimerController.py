import Controller

class CounterTimerController(Controller.Controller):
    trace = ["AddDevice", "DeleteDevice", "SendToCtrl",
             "GetExtraAttributePar", "SetExtraAttributePar",
             "PreStateAll", "PreStateOne", "StateAll", "StateOne", 
             "PreReadAll", "PreReadOne", "ReadAll", "ReadOne", 
             "AbortOne", "PreStartAllCT", "StartOneCT", "StartAllCT", "LoadOne"]
