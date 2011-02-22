import Controller

class CommunicationController(Controller.Controller):
    trace = ["AddDevice", "DeleteDevice", "SendToCtrl",
             "GetExtraAttributePar", "SetExtraAttributePar",
             "PreStateAll", "PreStateOne", "StateAll", "StateOne", 
             "OpenOne", "CloseOne", "ReadOne", "ReadLineOne", 
             "WriteOne", "WriteReadOne"]
