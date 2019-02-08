from enum import Enum

class DeviceTypes(Enum):
    """
    DeviceTypes
    
    [Enum to describe the type of the device to be created or deleted.]
    
    Values:
        Enum {[TYPE_ROUTER]}
        Enum {[TYPE_BRIDGE]}
        Enum {[TYPE_HOST]}
    """
    TYPE_ROUTER = 1
    TYPE_BRIDGE = 2
    TYPE_HOST = 3

    @staticmethod
    def getDeviceTypeFromStr(devType):
        if devType == "ROUTER" or devType == "Router" or devType == "router":
            return DeviceTypes.TYPE_ROUTER
        if devType == "HOST" or devType == "Host" or devType == "host":
            return DeviceTypes.TYPE_HOST
        if devType == "SWITCH" or devType == "Switch" or devType == "switch":
            return DeviceTypes.TYPE_BRIDGE

    @staticmethod
    def getImageName(imageType):
        if imageType == DeviceTypes.TYPE_ROUTER:
            return "swarnaragz/rnd_tool:rndtool-router"
        if imageType == DeviceTypes.TYPE_HOST:
            return "swarnaragz/rnd_tool:rndtool-host"
        else:
            return "swarnaragz/rnd_tool:rndtool-router"


"""
NAME: LINK TYPES
DESC: Enums to describe the type of link between 2 containers.
"""
class LinkTypes(Enum):
    TYPE_DEFAULT = 1
    TYPE_BRIDGE = 2
    TYPE_GRE = 3
    TYPE_VXLAN = 4
    TYPE_ETHERCHANNEL = 5

class ErrorCodes(Enum):
    NO_ERROR = 0
    INVALID_ARGUMENT = 1
    UNKNOWN_ERROR = 2
    CONTAINER_ALREADY_EXISTS = 3
    CONTAINER_DOESNOT_EXIST = 4
    BRIDGE_ALREADY_EXISTS = 5
    BRIDGE_DOESNOT_EXIST = 6
    DEPLOYMENT_ERROR = 7
    DOCKER_BRIDGE_MISSING = 8
    

    @staticmethod
    def getErrorDesc(errCode):
        switcher = {
            ErrorCodes.NO_ERROR: "NO_ERROR",
            ErrorCodes.INVALID_ARGUMENT: "INVALID_ARGUMENT",
            ErrorCodes.CONTAINER_ALREADY_EXISTS: "CONTAINER_ALREADY_EXISTS",
            ErrorCodes.CONTAINER_DOESNOT_EXIST: "CONTAINER_DOESNOT_EXIST",
            ErrorCodes.BRIDGE_ALREADY_EXISTS: "BRIDGE_ALREADY_EXISTS",
            ErrorCodes.BRIDGE_DOESNOT_EXIST: "BRIDGE_DOESNOT_EXIST",
            ErrorCodes.DEPLOYMENT_ERROR: "DEPLOYMENT_ERROR",
            ErrorCodes.DOCKER_BRIDGE_MISSING: "DOCKER_BRIDGE_MISSING"
        }
        return switcher.get(errCode, "UNKNOWN_ERROR")