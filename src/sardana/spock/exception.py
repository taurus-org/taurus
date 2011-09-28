
class SpockException(Exception):
    pass

class SpockBadInstallation(SpockException):
    pass

class SpockMissingRequirement(SpockException):
    pass

class SpockMissingRecommended(SpockException):
    pass
