import os


available = os.environ["AVAILABLE_QT_MOCKS"]
if available != "all" and __name__ not in available.split(","):
    raise ImportError("{} mock not enabled".format(__name__))
