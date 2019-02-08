import os
import subprocess
from enum import Enum
import logging
import json
import pexpect
import re

import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../..')

from commonEnums import ErrorCodes
from commonEnums import DeviceTypes
from commonEnums import LinkTypes

class SouthBoundWrapper:
    """
    [Class SouthBoundWrapper]

    Provides access to all south bound APIs.

    Set topologyName for class object to identify docker bridge.

    createManagementBridge() must be called before calling createDevice().
    
    """
    topologyName=""

    def __init__(self, logLevel):

        # Set up logging
        self.logger = logging.getLogger("SBWrapper")
        self.logger.setLevel(logLevel)
        directory = '/var/RNDTool/log/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        fileName = directory + "rndTool.log"
        with open(fileName, 'w') as outfile:
            outfile.write("SouthBound Logs")
            self.handler = logging.FileHandler(fileName)
            self.handler.setLevel(logLevel)
            self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)

    def checkManagementBridgeExists(self, bridgeName):
        """
        [Checks if a docker bridge with the given name 'bridgeName' exists.]
        
        Note:
            [DO NOT CALL THIS METHOD.]
        
        Arguments:
            bridgeName {[str]} -- [Name of the bridge device.]

        Returns:
            [ErrorCode] -- [INVALID_ARGUMENT, BRIDGE_ALREADY_EXISTS, BRIDGE_DOESNOT_EXIST]
        """
        errCode = ErrorCodes.NO_ERROR
        if bridgeName == "":
            errCode = ErrorCodes.INVALID_ARGUMENT
        else:
            retData = SouthBoundActual.checkManagementBridgeExists(self.logger, bridgeName)
            if retData:
                errCode = ErrorCodes.BRIDGE_ALREADY_EXISTS
            else:
                errCode = ErrorCodes.BRIDGE_DOESNOT_EXIST
        return errCode

    def checkContainerExists(self,containerName):
        """
        [Checks if a container with the given name 'containerName' exists.]

        Note:
            [DO NOT CALL THIS METHOD fFROM LOGIC LAYER.] 

        Arguments:
            containerName {[str]} -- [Name of the container to be created.]

        Returns:
            [ErrorCode] -- [INVALID_ARGUMENT, CONTAINER_ALREADY_EXISTS, CONTAINER_DOESNOT_EXIST]

        """
        errCode = ErrorCodes.NO_ERROR
        if containerName == "":
            errCode = ErrorCodes.INVALID_ARGUMENT
        else:
            containerID = SouthBoundActual.getContainerID(self.logger, containerName)
            if(containerID != ""):
                errCode = ErrorCodes.CONTAINER_ALREADY_EXISTS
            else:
                errCode = ErrorCodes.CONTAINER_DOESNOT_EXIST
        return errCode

    def checkBridgeExists(self, bridgeName):
        """
        [Checks if a bridge with the given name 'bridgeName' exists.]
        
        Note:
            [DO NOT CALL THIS METHOD.]
        
        Arguments:
            bridgeName {[str]} -- [Name of the bridge device.]

        Returns:
            [ErrorCode] -- [INVALID_ARGUMENT, BRIDGE_ALREADY_EXISTS, BRIDGE_DOESNOT_EXIST]
        """
        errCode = ErrorCodes.NO_ERROR
        if bridgeName == "":
            errCode = ErrorCodes.INVALID_ARGUMENT
        else:
            retData = SouthBoundActual.checkBridgeExists(self.logger, bridgeName)
            if retData:
                errCode = ErrorCodes.BRIDGE_ALREADY_EXISTS
            else:
                errCode = ErrorCodes.BRIDGE_DOESNOT_EXIST
        return errCode

    def createManagementBridge(self, subnetCIDR):
        """
        [Checks if a management bridge device exists for the topology. If not, creates the bridge.]
        ['topologyName' must be set in the class object.]
        
        Arguments:
            subnetCIDR {[str]} -- [IP address to be assigned to the bridge along with subnet prefix. Eg. 10.10.10.1/24]

        Returns:
            [JSON] -- [JSON containing bridge name and error code(if any).]
        """
        errCode = ErrorCodes.NO_ERROR
        retJSON = {}
        if self.topologyName=="" or subnetCIDR=="" or (re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{2}',subnetCIDR) == None):
            self.logger.error("createManagementBridge - INVALID BRIDGE NAME - " + self.topologyName + " - " + subnetCIDR)
            errCode = ErrorCodes.INVALID_ARGUMENT
        bridgeName=self.topologyName+"br"
        retCode = self.checkManagementBridgeExists(bridgeName)
        if retCode == ErrorCodes.BRIDGE_ALREADY_EXISTS:
            self.logger.error("createManagementBridge - BRIDGE ALREADY EXISTS - " + bridgeName)
            errCode = ErrorCodes.BRIDGE_ALREADY_EXISTS
        else:
            SouthBoundActual.createManagementBridge(self.logger, bridgeName, subnetCIDR)

            #Verify if bridge was created
            if self.checkManagementBridgeExists(bridgeName) == ErrorCodes.BRIDGE_ALREADY_EXISTS:
                # ISSUE - BridgeID is all 0's when no interface is attached to it. Current workaround is to fetch it whenever an interface is added to the bridge.
                #retJSON["deviceID"]=SouthBoundActual.getBridgeID(self.logger,bridgeName)
                retJSON["deviceName"]=bridgeName
                retJSON["deviceType"]="ManagementSwitch"
                self.logger.info("createManagementBridge - CREATED BRIDGE. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def createBridge(self, bridgeName):
        """
        [Checks if a bridge device with the given name 'bridgeName' exists. If not, creates the bridge.]
        
        Note:
            [DO NOT CALL THIS METHOD. USE createDevice() INSTEAD.]
        
        Arguments:
            bridgeName {[str]} -- [Name of the bridge to be created.]

        Returns:
            [JSON] -- [JSON containing bridge name and error code(if any).]
        """ 
        errCode=ErrorCodes.NO_ERROR
        retJSON = {}
        retCode = self.checkBridgeExists(bridgeName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("createBridge - INVALID BRIDGE NAME - " + bridgeName)
            errCode=retCode
        if retCode == ErrorCodes.BRIDGE_ALREADY_EXISTS:
            self.logger.error("createBridge - BRIDGE ALREADY EXISTS - " + bridgeName)
            errCode=retCode
        if self.topologyName=="" or self.checkManagementBridgeExists(self.topologyName+"br") == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            errCode=ErrorCodes.DOCKER_BRIDGE_MISSING
            self.logger.error("createBridge - DOCKER BRIDGE MISSING - " + self.topologyName)
        else:
            SouthBoundActual.createBridge(self.logger, bridgeName)

            # Verify if bridge was created
            if self.checkBridgeExists(bridgeName) == ErrorCodes.BRIDGE_ALREADY_EXISTS:
                # ISSUE - BridgeID is all 0's when no interface is attached to it. Current workaround is to fetch it whenever an interface is added to the bridge.
                #retJSON["deviceID"]=SouthBoundActual.getBridgeID(self.logger,bridgeName)
                retJSON["deviceName"]=bridgeName
                retJSON["deviceType"]="Switch"
                self.logger.info("createBridge - CREATED BRIDGE. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def getBridgeID(self, bridgeName):
        """
        [Checks if a bridge device with the given name 'bridgeName' exists. If yes, fetches its ID.]

        Arguments:
            bridgeName {[str]} -- [Name of the bridge.]

        Returns:
            [JSON] -- [JSON containing bridge ID, name and error code(if any).]
        """
        errCode=ErrorCodes.NO_ERROR
        retJSON = {}
        retCode = self.checkBridgeExists(bridgeName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("getBridgeID - INVALID BRIDGE NAME - " + bridgeName)
            errCode=retCode
        if retCode == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("getBridgeID - BRIDGE DOESNOT EXISTS - " + bridgeName)
            errCode=retCode
        else:
            retJSON["deviceID"]=SouthBoundActual.getBridgeID(self.logger,bridgeName)
            retJSON["deviceName"]=bridgeName
            self.logger.info("getBridgeID - FETCHED BRIDGE ID. DETAILS:")
            self.logger.info(json.dumps(retJSON))
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def runPacketCapture(self, containerName, captureCommand):
        """
        [Runs tcpdump to capture packets inside a container using the command specified]
        
        Arguments:
            containerName {[str]} -- [Name of the contaier]
            captureCommand {[str]} -- [TCP DUMP command]
        
        Returns:
            [JSON] - [JSON containing error code(if any).]
        """
        errCode=ErrorCodes.NO_ERROR
        retJSON = {}
        retCode = self.checkContainerExists(containerName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("runPacketCapture - INVALID CONTAINER NAME - " + containerName)
            errCode=retCode
        if retCode == ErrorCodes.CONTAINER_DOESNOT_EXIST:
            self.logger.error("runPacketCapture - CONTAINER DOESNOT EXISTS - " + containerName)
            errCode=retCode
        else:
            SouthBoundActual.executeInContainer(self.logger,containerName,captureCommand)
            self.logger.info("runPacketCapture - Done")
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def createContainer(self, containerName, imageType):
        """
        [Checks if a container with the given name 'containerName' exists. If not, creates the container.]
        
        Note:
            [DO NOT CALL THIS METHOD. USE createDevice() INSTEAD.]
        
        Arguments:
            containerName {[str]} -- [Name of the container to be created.]
            imageType {[DeviceTypes]} -- [Type of docker image to be used to create the container.]

        Returns:
            [JSON] -- [JSON containing container ID, name, docker image, SSH IP and error code(if any).]
        """ 
        errCode=ErrorCodes.NO_ERROR
        retJSON = {}
        retCode = self.checkContainerExists(containerName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("createContainer - INVALID CONTAINER NAME - " + containerName)
            errCode=retCode
        if retCode == ErrorCodes.CONTAINER_ALREADY_EXISTS:
            self.logger.error("createContainer - CONTAINER ALREADY EXISTS - " + containerName)
            errCode=retCode
        if self.topologyName=="" or self.checkManagementBridgeExists(self.topologyName+"br") == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            errCode=ErrorCodes.DOCKER_BRIDGE_MISSING
            self.logger.error("createContainer - DOCKER BRIDGE MISSING - " + self.topologyName)
        else:
            imageName = DeviceTypes.getImageName(imageType)
            bridgeName = self.topologyName+"br"
            SouthBoundActual.createContainer(self.logger, containerName, imageName, bridgeName)

            # Verify if container was created
            if self.checkContainerExists(containerName) == ErrorCodes.CONTAINER_ALREADY_EXISTS:
                retJSON["dockerImage"]=imageName
                retJSON["dockerID"]=SouthBoundActual.getContainerID(self.logger,containerName)
                if imageType == DeviceTypes.TYPE_HOST:
                    retJSON["deviceType"]="Host"
                if imageType == DeviceTypes.TYPE_ROUTER:
                    retJSON["deviceType"]="Router"
                retJSON["deviceID"]=containerName
                retJSON["sshIPAddress"]=SouthBoundActual.getContainerSSHIP(self.logger, containerName, bridgeName)
                self.logger.info("createContainer - CREATED CONTAINER. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def createDevice(self, deviceName, deviceType):
        """
        [Creates a device of type deviceType with name deviceName.]
        
        Arguments:
            deviceName {[str]} -- [Name of the device.]
            deviceType {[DeviceTypes]} -- [Type of the device.]

        Returns:
            [JSON] -- [JSON containing device name, device type and other details depening on the type of device along with an error code(if any).]
        """
        if deviceType == DeviceTypes.TYPE_BRIDGE:
            return self.createBridge(deviceName)
        if deviceType == DeviceTypes.TYPE_HOST or deviceType == DeviceTypes.TYPE_ROUTER:
            return self.createContainer(deviceName,deviceType)
        else:
            retJSON={}
            retJSON["error"]=ErrorCodes.getErrorDesc(ErrorCodes.INVALID_ARGUMENT)
            return json.dumps(retJSON)

    def createLink(self, dev1Name, dev1IfaceName, dev1Type, dev2Name, dev2IfaceName, dev2Type):
        """
        [Creates a link to between 2 devices after checking if they exist.]
        
        Arguments:
            dev1Name {[str]} -- [Name of first device.]
            dev1IfaceName {[str]} -- [Name of first device's interface.]
            dev1Tyep {[DeviceTypes]} -- [Type of the first device.]
            dev2Name {[str]} -- [Name of the second device.]
            dev2IfaceName {[str]} -- [Name of the second device's interface.]
            dev2Tyep {[DeviceTypes]} -- [Type of the second device.]

        Returns:
            [JSON] -- [JSON with device name, connection details and error code(if any).]
        """
        errCode = ErrorCodes.NO_ERROR
        retJSON = {}
        retCode1 = ErrorCodes.NO_ERROR
        retCode2 = ErrorCodes.NO_ERROR
        if dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
            retCode1 = self.checkContainerExists(dev1Name)
        if dev1Type == DeviceTypes.TYPE_BRIDGE:
            retCode1 = self.checkBridgeExists(dev1Name)

        if dev2Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
            retCode2 = self.checkContainerExists(dev2Name)
        if dev2Type == DeviceTypes.TYPE_BRIDGE:
            retCode2 = self.checkBridgeExists(dev2Name)

        if dev1IfaceName == "" or dev2IfaceName == "" or len(dev1IfaceName) > 14 or len(dev2IfaceName) > 14:
            self.logger.error("createLink - INVALID DEVICE INTERFACE NAME - " + dev1IfaceName +", " + dev2IfaceName)
            errCode=ErrorCodes.INVALID_ARGUMENT
        if retCode1 == ErrorCodes.INVALID_ARGUMENT or retCode2 == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("createLink - INVALID DEVICE NAME - " + dev1Name +", " + dev2Name)
            errCode=ErrorCodes.INVALID_ARGUMENT
        if retCode1 == ErrorCodes.CONTAINER_DOESNOT_EXIST or retCode1 == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("createLink - DEVICE DOES NOT EXISTS - " + dev1Name)
            errCode=retCode1
        if retCode2 == ErrorCodes.CONTAINER_DOESNOT_EXIST or retCode2 == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("createLink - DEVICE DOES NOT EXISTS - " + dev2Name)
            errCode=retCode2
        if errCode == ErrorCodes.NO_ERROR:
            # CREATE A VETH
            SouthBoundActual.createVeth(self.logger,dev1IfaceName,dev2IfaceName)

            interface1UUID=SouthBoundActual.getInterfaceUUID(self.logger,dev1IfaceName)
            interface2UUID=SouthBoundActual.getInterfaceUUID(self.logger,dev2IfaceName)

            # DEVICE 1
            if dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
                # ATTACH TO CONTAINERS
                container1PID = SouthBoundActual.getContainerPID(self.logger,dev1Name)
                if container1PID == "":
                    self.logger.error("createLink - CONTAINER DOES NOT EXISTS - " + dev1Name +","+ container1PID)
                    errCode = ErrorCodes.CONTAINER_DOESNOT_EXIST
                else:
                    SouthBoundActual.attachInterface(self.logger,container1PID,dev1IfaceName, LinkTypes.TYPE_DEFAULT)

            if dev1Type == DeviceTypes.TYPE_BRIDGE:
                # ATTACH TO BRIDGE
                SouthBoundActual.attachInterface(self.logger,dev1Name, dev1IfaceName, LinkTypes.TYPE_BRIDGE)

            # DEVICE 2
            if dev2Type == DeviceTypes.TYPE_ROUTER or dev2Type == DeviceTypes.TYPE_HOST:
                # ATTACH TO CONTAINERS
                container2PID = SouthBoundActual.getContainerPID(self.logger,dev2Name)
                if container2PID == "":
                    self.logger.error("createLink - CONTAINER DOES NOT EXISTS - " + dev2Name +","+ container2PID)
                    errCode = ErrorCodes.CONTAINER_DOESNOT_EXIST
                else:
                    SouthBoundActual.attachInterface(self.logger,container2PID,dev2IfaceName, LinkTypes.TYPE_DEFAULT)

            if dev2Type == DeviceTypes.TYPE_BRIDGE:
                # ATTACH TO BRIDGE
                SouthBoundActual.attachInterface(self.logger,dev2Name, dev2IfaceName, LinkTypes.TYPE_BRIDGE)
                
            # Verify that interfaces was attached
            if dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
                verify1CmdStr = "ip addr show {}".format(dev1IfaceName)
                interface1Details = SouthBoundActual.executeInContainer(self.logger,dev1Name,verify1CmdStr)
                if (interface1Details == "") or (interface1UUID not in str(interface1Details)) or ("state UP" not in str(interface1Details)):
                    errCode = ErrorCodes.DEPLOYMENT_ERROR
            
            if dev1Type == DeviceTypes.TYPE_BRIDGE:                
                verify1CmdStr = "sudo ovs-vsctl list-ports {}".format(dev1Name)
                interface1Details = SouthBoundActual.executeOnHost(self.logger,verify1CmdStr)
                if (interface1Details == "") or (dev1IfaceName not in str(interface1Details)):
                    errCode = ErrorCodes.DEPLOYMENT_ERROR

            if dev2Type == DeviceTypes.TYPE_ROUTER or dev2Type == DeviceTypes.TYPE_HOST:
                verify2CmdStr = "ip addr show {}".format(dev2IfaceName)
                interface2Details = SouthBoundActual.executeInContainer(self.logger,dev2Name,verify2CmdStr)
                if (interface2Details == "") or (interface2UUID not in str(interface2Details)) or ("state UP" not in str(interface2Details)):
                    errCode = ErrorCodes.DEPLOYMENT_ERROR
            
            if dev2Type == DeviceTypes.TYPE_BRIDGE:
                verify2CmdStr = "sudo ovs-vsctl list-ports {}".format(dev2Name)
                interface2Details = SouthBoundActual.executeOnHost(self.logger,verify2CmdStr)
                if (interface2Details == "") or (dev2IfaceName not in str(interface2Details)):
                    errCode = ErrorCodes.DEPLOYMENT_ERROR

            if errCode == ErrorCodes.NO_ERROR:
                retJSONDev1={}
                retJSONDev1Connection={}
                retJSONDev1["deviceName"]=dev1Name
                retJSONDev1Connection["deviceName"]=dev2Name
                if dev2Type == DeviceTypes.TYPE_BRIDGE or dev2Type == DeviceTypes.TYPE_BRIDGE:
                    retJSONDev1Connection["linkType"]="BRIDGE"
                else:
                    retJSONDev1Connection["linkType"]="DEFAULT"
                retJSONDev1Connection["localInterfaceName"]=dev1IfaceName
                retJSONDev1Connection["localInterfaceUID"]=interface1UUID
                retJSONDev1Connection["remoteInterfaceName"]=dev2IfaceName
                retJSONDev1Connection["remoteInterfaceUID"]=interface2UUID
                retJSONDev1["connections"]=[retJSONDev1Connection]

                retJSONDev2={}
                retJSONDev2Connection={}
                retJSONDev2["deviceName"]=dev2Name
                retJSONDev2Connection["deviceName"]=dev1Name
                if dev1Type == DeviceTypes.TYPE_BRIDGE or dev2Type == DeviceTypes.TYPE_BRIDGE:
                    retJSONDev2Connection["linkType"]="BRIDGE"
                else:
                    retJSONDev2Connection["linkType"]="DEFAULT"
                retJSONDev2Connection["localInterfaceName"]=dev2IfaceName
                retJSONDev2Connection["localInterfaceUID"]=interface2UUID
                retJSONDev2Connection["remoteInterfaceName"]=dev1IfaceName
                retJSONDev2Connection["remoteInterfaceUID"]=interface1UUID
                retJSONDev2["connections"]=[retJSONDev2Connection]

                retJSON["devices"]=[retJSONDev1,retJSONDev2]
                self.logger.info("createLink - CREATED LINK BETWEEN {} - {}. DETAILS:".format(dev1Name,dev2Name))
                self.logger.info(json.dumps(retJSON))

        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def deleteManagementBridge(self):
        """
        [Checks if a docker bridge device exists for the topology. If yes, deletes the bridge.]
        
        Returns:
            [JSON] -- [JSON with the deleted bridge name and error code (if any).]
        """
        errCode = ErrorCodes.NO_ERROR
        retJSON = {}
        if self.topologyName=="":
            self.logger.error("deleteManagementBridge - INVALID BRIDGE NAME - " + self.topologyName)
            errCode = ErrorCodes.INVALID_ARGUMENT

        bridgeName=self.topologyName+"br"
        retCode = self.checkManagementBridgeExists(bridgeName)
        if retCode == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("deleteManagementBridge - BRIDGE DOES NOT EXISTS - " + bridgeName)
            errCode=retCode
        else:
            SouthBoundActual.deleteManagementBridge(self.logger, bridgeName)
            
            # Verify if docker bridge was deleted
            if self.checkManagementBridgeExists(bridgeName) == ErrorCodes.BRIDGE_DOESNOT_EXIST:
                retJSON["deviceName"]=bridgeName
                self.logger.info("deleteManagementBridge - DELETED BRIDGE. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def deleteBridge(self,bridgeName):
        """
        [Checks if a bridge device with the given name 'bridgeName' exists. If yes, deletes the bridge.]

        Note:
            [DO NOT CALL THIS METHOD. USE deleteDevice() INSTEAD.]
        
        Arguments:
            bridgeName {[str]} -- [Name of the bridge]
        
        Returns:
            [JSON] -- [JSON with the deleted bridge name and error code (if any).]
        """
        errCode=ErrorCodes.NO_ERROR
        retJSON={}
        retCode = self.checkBridgeExists(bridgeName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("deleteBridge - INVALID BRIDGE NAME - " + bridgeName)
            errCode=retCode
        if retCode == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("deleteBridge - BRIDGE DOES NOT EXISTS - " + bridgeName)
            errCode=retCode
        else:
            SouthBoundActual.deleteBridge(self.logger, bridgeName)
            
            # Verify if bridge was deleted
            if self.checkBridgeExists(bridgeName) == ErrorCodes.BRIDGE_DOESNOT_EXIST:
                retJSON["deviceName"]=bridgeName
                self.logger.info("deleteBridge - DELETED BRIDGE. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def deleteContainer(self, containerName):
        """
        [Checks if a container with the given name 'containerName' exists. If yes, deletes the container.]

        Note:
            [DO NOT CALL THIS METHOD. USE deleteDevice() INSTEAD.]
        
        Arguments:
            containerName {[str]} -- [Name of the container]
        
        Returns:
            [JSON] -- [JSON with the deleted container name and error code (if any).]
        """
        errCode=ErrorCodes.NO_ERROR
        retJSON={}
        retCode = self.checkContainerExists(containerName)

        if retCode == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("deleteContainer - INVALID CONTAINER NAME - " + containerName)
            errCode=retCode
        if retCode == ErrorCodes.CONTAINER_DOESNOT_EXIST:
            self.logger.error("deleteContainer - CONTAINER DOES NOT EXISTS - " + containerName)
            errCode=retCode
        else:
            SouthBoundActual.deleteContainer(self.logger, containerName)
            
            # Verify if container was deleted
            if self.checkContainerExists(containerName) == ErrorCodes.CONTAINER_DOESNOT_EXIST:
                retJSON["deviceName"]=containerName
                self.logger.info("deleteContainer - DELETED CONTAINER. DETAILS:")
                self.logger.info(json.dumps(retJSON))
            else:
                errCode = ErrorCodes.DEPLOYMENT_ERROR
        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)

    def deleteDevice(self, deviceName, deviceType):
        """
        [Deletes a device of type deviceType with name deviceName.]
        
        Arguments:
            deviceName {[str]} -- [Name of the device.]
            deviceType {[DeviceTypes]} -- [Type of the device.]

        Returns:
            [JSON] -- [JSON containing device name and an error code(if any).]
        """
        if deviceType == DeviceTypes.TYPE_BRIDGE:
            return self.deleteBridge(deviceName)
        if deviceType == DeviceTypes.TYPE_HOST or deviceType == DeviceTypes.TYPE_ROUTER:
            return self.deleteContainer(deviceName)
        else:
            retJSON={}
            retJSON["error"]=ErrorCodes.getErrorDesc(ErrorCodes.INVALID_ARGUMENT)
            return json.dumps(retJSON)

    def deleteLink(self, dev1Name, dev1IfaceName, dev1Type, dev2Name, dev2IfaceName, dev2Type):
        """
        [Deletes interfaces connecting 2 devices after checking if the containers exist.]
        
        Arguments:
            dev1Name {[str]} -- [Name of first device.]
            dev1IfaceName {[str]} -- [Name of first device's interface.]
            dev1Tyep {[DeviceTypes]} -- [Type of the first device.]
            dev2Name {[str]} -- [Name of the second device.]
            dev2IfaceName {[str]} -- [Name of the second device's interface.]
            dev2Tyep {[DeviceTypes]} -- [Type of the second device.]

        Returns:
            [JSON] -- [JSON with device name, connection details and error code(if any).]
        """
        errCode = ErrorCodes.NO_ERROR
        retJSON={}
        retCode1 = ErrorCodes.NO_ERROR
        retCode2 = ErrorCodes.NO_ERROR
        retCode3 = ErrorCodes.NO_ERROR
        if dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
            retCode1 = self.checkContainerExists(dev1Name)
        if dev1Type == DeviceTypes.TYPE_BRIDGE:
            retCode1 = self.checkBridgeExists(dev1Name)

        if dev2Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
            retCode2 = self.checkContainerExists(dev2Name)
        if dev2Type == DeviceTypes.TYPE_BRIDGE:
            retCode2 = self.checkBridgeExists(dev2Name)

        retCode3 = ErrorCodes.INVALID_ARGUMENT

        # Check if given interface1 is present in the device1
        if dev1Type == DeviceTypes.TYPE_HOST or dev1Type == DeviceTypes.TYPE_ROUTER:
            if dev1IfaceName != "" or len(dev1IfaceName) > 14:
                checkInterfaceCmdStr = "ip addr show {}".format(dev1IfaceName)
                interface1Details = SouthBoundActual.executeInContainer(self.logger,dev1Name,checkInterfaceCmdStr)
                if ("{}@".format(dev1IfaceName) in str(interface1Details)) and ("state UP" in str(interface1Details)):
                    retCode3 = ErrorCodes.NO_ERROR

        if dev1Type == DeviceTypes.TYPE_BRIDGE:
            if dev1IfaceName != "" or len(dev1IfaceName) > 14:
                checkInterfaceCmdStr = "ip addr show {}".format(dev1IfaceName)
                interface1Details = SouthBoundActual.executeOnHost(self.logger,checkInterfaceCmdStr)
                if ("{}@".format(dev1IfaceName) in str(interface1Details)) and ("{} state UP".format(dev1Name) in str(interface1Details)):
                    retCode3 = ErrorCodes.NO_ERROR

        # Check if given interface2 is present in the device2
        if dev2Type == DeviceTypes.TYPE_HOST or dev2Type == DeviceTypes.TYPE_ROUTER:
            if dev2IfaceName != "" or len(dev2IfaceName) > 14:
                checkInterfaceCmdStr = "ip addr show {}".format(dev2IfaceName)
                interface2Details = SouthBoundActual.executeInContainer(self.logger,dev2Name,checkInterfaceCmdStr)
                if ("{}@".format(dev2IfaceName) in str(interface2Details)) and ("state UP" in str(interface2Details)):
                    retCode3 = ErrorCodes.NO_ERROR

        if dev2Type == DeviceTypes.TYPE_BRIDGE:
            if dev2IfaceName != "" or len(dev2IfaceName) > 14:
                checkInterfaceCmdStr = "ip addr show {}".format(dev2IfaceName)
                interface2Details = SouthBoundActual.executeOnHost(self.logger,checkInterfaceCmdStr)
                if ("{}@".format(dev2IfaceName) in str(interface2Details)) and ("{} state UP".format(dev2Name) in str(interface2Details)):
                    retCode3 = ErrorCodes.NO_ERROR
        

        if dev1IfaceName == "" or dev2IfaceName == "":
            self.logger.error("deleteLink - INVALID DEVICE INTERFACE NAME - " + dev1IfaceName +", " + dev2IfaceName)
            errCode=ErrorCodes.INVALID_ARGUMENT
        if retCode1 == ErrorCodes.INVALID_ARGUMENT or retCode2 == ErrorCodes.INVALID_ARGUMENT or retCode3 == ErrorCodes.INVALID_ARGUMENT:
            self.logger.error("deleteLink - INVALID DEVICE/INTERFACE NAME - " + dev1Name +" - " + dev1IfaceName +", " + dev2Name +" - " + dev2IfaceName)
            errCode=ErrorCodes.INVALID_ARGUMENT
        if retCode1 == ErrorCodes.CONTAINER_DOESNOT_EXIST or retCode1 == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("deleteLink - DEVICE DOES NOT EXISTS - " + dev1Name)
            errCode=retCode1
        if retCode2 == ErrorCodes.CONTAINER_DOESNOT_EXIST or retCode2 == ErrorCodes.BRIDGE_DOESNOT_EXIST:
            self.logger.error("deleteLink - DEVICE DOES NOT EXISTS - " + dev2Name)
            errCode=retCode2
        else:
            # BOTH DEVICES ARE CONTAINERS
            if (dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST) and (dev2Type == DeviceTypes.TYPE_ROUTER or dev2Type == DeviceTypes.TYPE_HOST):
                delCmdStr = " ip link del {}".format(dev1IfaceName)
                SouthBoundActual.executeInContainer(self.logger,dev1Name,delCmdStr)

            # ONE DEVICE IS A CONTAINER AND THE OTHER IS BRIDGE
            if (dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST) and (dev2Type == DeviceTypes.TYPE_BRIDGE):
                delCmdStr = " ip link del {}".format(dev1IfaceName)
                SouthBoundActual.executeInContainer(self.logger,dev1Name,delCmdStr)

                delCmdStr1 = "sudo brctl delif {} {}".format(dev2Name, dev2IfaceName)
                delCmdStr2 = "sudo ip link del {}".format(dev2IfaceName)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr1)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr2)
            
            # ONE DEVICE IS A CONTAINER AND THE OTHER IS BRIDGE
            if (dev1Type == DeviceTypes.TYPE_BRIDGE) and (dev2Type == DeviceTypes.TYPE_ROUTER or dev2Type == DeviceTypes.TYPE_HOST):
                delCmdStr = " ip link del {}".format(dev2IfaceName)
                SouthBoundActual.executeInContainer(self.logger,dev2Name,delCmdStr)

                delCmdStr1 = "sudo brctl delif {} {}".format(dev1Name, dev1IfaceName)
                delCmdStr2 = "sudo ip link del {}".format(dev1IfaceName)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr1)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr2)

            # BOTH DEVICES ARE BRIDGES
            if (dev1Type == DeviceTypes.TYPE_BRIDGE) and (dev2Type == DeviceTypes.TYPE_BRIDGE):
                delCmdStr1 = "sudo brctl delif {} {}".format(dev1Name, dev1IfaceName)
                delCmdStr2 = "sudo ip link del {}".format(dev1IfaceName)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr1)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr2)

                delCmdStr1 = "sudo brctl delif {} {}".format(dev2Name, dev2IfaceName)
                delCmdStr2 = "sudo ip link del {}".format(dev2IfaceName)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr1)
                SouthBoundActual.executeOnHost(self.logger,delCmdStr2)

            #Verify if interface was deleted
            if dev1Type == DeviceTypes.TYPE_ROUTER or dev1Type == DeviceTypes.TYPE_HOST:
                verify1CmdStr = "ip addr show {}".format(dev1IfaceName)
                interface1Details = SouthBoundActual.executeInContainer(self.logger,dev1Name,verify1CmdStr)
            if dev1Type == DeviceTypes.TYPE_BRIDGE:
                verify1CmdStr = "ip addr show {}".format(dev1IfaceName)
                interface1Details = SouthBoundActual.executeOnHost(self.logger,verify1CmdStr)

            if dev2Type == DeviceTypes.TYPE_ROUTER or dev2Type == DeviceTypes.TYPE_HOST:
                verify2CmdStr = "ip addr show {}".format(dev2IfaceName)
                interface2Details = SouthBoundActual.executeInContainer(self.logger,dev2Name,verify2CmdStr)
            if dev2Type == DeviceTypes.TYPE_BRIDGE:
                verify2CmdStr = "ip addr show {}".format(dev2IfaceName)
                interface2Details = SouthBoundActual.executeOnHost(self.logger,verify2CmdStr)

            if interface1Details == "" or ("{}@".format(dev1IfaceName) in str(interface1Details)):
                errCode = ErrorCodes.DEPLOYMENT_ERROR
            if interface2Details == "" or ("{}@".format(dev2IfaceName) in str(interface2Details)):
                errCode = ErrorCodes.DEPLOYMENT_ERROR
            if errCode == ErrorCodes.NO_ERROR:
                retJSONDev1={}
                retJSONDev1Connection={}
                retJSONDev1["deviceName"]=dev1Name
                retJSONDev1Connection["deviceName"]=dev2Name
                if dev2Type == DeviceTypes.TYPE_BRIDGE or dev2Type == DeviceTypes.TYPE_BRIDGE:
                    retJSONDev1Connection["linkType"]="BRIDGE"
                else:
                    retJSONDev1Connection["linkType"]="DEFAULT"
                retJSONDev1Connection["localInterfaceName"]=dev1IfaceName
                retJSONDev1Connection["remoteInterfaceName"]=dev2IfaceName
                retJSONDev1["connections"]=[retJSONDev1Connection]

                retJSONDev2={}
                retJSONDev2Connection={}
                retJSONDev2["deviceName"]=dev2Name
                retJSONDev2Connection["deviceName"]=dev1Name
                if dev1Type == DeviceTypes.TYPE_BRIDGE or dev2Type == DeviceTypes.TYPE_BRIDGE:
                    retJSONDev1Connection["linkType"]="BRIDGE"
                else:
                    retJSONDev1Connection["linkType"]="DEFAULT"
                retJSONDev2Connection["localInterfaceName"]=dev2IfaceName
                retJSONDev2Connection["remoteInterfaceName"]=dev1IfaceName
                retJSONDev2["connections"]=[retJSONDev2Connection]

                retJSON["devices"]=[retJSONDev1,retJSONDev2]
                self.logger.info("deleteLink - DELETED LINK BETWEEN {} - {}. DETAILS:".format(dev1Name,dev2Name))
                self.logger.info(json.dumps(retJSON))

        retJSON["error"]=ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)
    
    def assignInterfaceIP(self, containerName, interfaceName, ipAddress):
        """
        [Assign IP address to an interface inside a container.]
        
        Arguments:
            containerName {[str]} -- [Name of the container.]
            interfaceName {[str]} -- [Name of the interface inside the container.]
            ipAddress {[str]} -- [IP address of the interface.]

        Returns:
            [JSON] -- [JSON with device name, interface name, IP address and error(if any).]
        """
        errCode=ErrorCodes.NO_ERROR
        retJSON={}
        retCode = self.checkContainerExists(containerName)
        retCode1 = ErrorCodes.INVALID_ARGUMENT

        # Check if given interface is present in the container
        if interfaceName != "" or len(interfaceName) > 14:
            checkInterfaceCmdStr = "ip addr show {}".format(interfaceName)
            interfaceDetails = SouthBoundActual.executeInContainer(self.logger,containerName,checkInterfaceCmdStr)
            if ("{}@".format(interfaceName) in str(interfaceDetails)) and ("state UP" in str(interfaceDetails)):
                retCode1 = ErrorCodes.NO_ERROR

        if retCode == ErrorCodes.INVALID_ARGUMENT or retCode1 == ErrorCodes.INVALID_ARGUMENT or ipAddress == "":
            self.logger.error("assignInterfaceIP - INVALID ARGUMENT - " + containerName + ", " +interfaceName + ", " + ipAddress)
            errCode=retCode
        
        if retCode == ErrorCodes.CONTAINER_DOESNOT_EXIST:
            self.logger.error("assignInterfaceIP - CONTAINER DOES NOT EXISTS - " + containerName)
            errCode=retCode
        else:
            ipAddCmd="ip addr add {} dev {}".format(ipAddress,interfaceName)
            SouthBoundActual.executeInContainer(self.logger, containerName,ipAddCmd)

            # Verify if IP address has been assigned
            checkInterfaceCmdStr = "ip addr show {}".format(interfaceName)
            interfaceDetails = SouthBoundActual.executeInContainer(self.logger,containerName,checkInterfaceCmdStr)
            if (interfaceDetails == "") or ("state UP" not in str(interfaceDetails)) or(ipAddress not in str(interfaceDetails)):
                    errCode = ErrorCodes.DEPLOYMENT_ERROR
            
            if errCode == ErrorCodes.NO_ERROR:
                retJSON["deviceName"]=containerName
                retJSON["localInterfaceName"]=interfaceName
                retJSON["localInterfaceIP"]=ipAddress

        retJSON["error"] = ErrorCodes.getErrorDesc(errCode)
        return json.dumps(retJSON)
    
class SouthBoundActual:
    @staticmethod
    def execute(logger,command):
        logger.info("execute - " + command)
        output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = output.communicate()
        if out.strip() != "":
            return out.strip()
        else:
            return err.strip()
        
    @staticmethod
    def getContainerPID(logger, containerName):
        return SouthBoundActual.execute(logger, "sudo docker inspect -f '{{.State.Pid}}' "+containerName)

    @staticmethod
    def getContainerID(logger, containerName):
        return SouthBoundActual.execute(logger, "sudo docker ps -f name={} -q".format(containerName))

    @staticmethod
    def getContainerSSHIP(logger, containerName, dockerBrName):
        keyValue='.NetworkSettings.Networks.{}.IPAddress'.format(dockerBrName)
        return SouthBoundActual.execute(logger, "sudo docker inspect -f '{{ "+ keyValue +" }}' "+containerName)
        
    @staticmethod
    def createManagementBridge(logger, bridgeName, ipAddr):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"createNetwork.yml -e '{ bridgeName: "+ bridgeName +", ipCidr: "+ ipAddr +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def checkManagementBridgeExists(logger, bridgeName):
        output = subprocess.Popen("sudo docker network ls | grep {}".format(bridgeName), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = output.communicate()
        retCode = False
        if bridgeName in str(out):
            retCode = True
        else:
            retCode = False
        return retCode

    @staticmethod
    def deleteManagementBridge(logger, bridgeName):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"deleteNetwork.yml -e '{ bridgeName: "+ bridgeName +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def getBridgeID(logger, bridgeName):
        cmd = "ip addr show "+bridgeName+" | grep "+bridgeName+" | awk '{print $1}'"
        return str(SouthBoundActual.execute(logger, cmd))[:-1]

    @staticmethod
    def checkBridgeExists(logger, bridgeName):
        output = subprocess.Popen("sudo ovs-vsctl show", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = output.communicate()
        retCode = False
        if output.returncode != 0:
            logger.error("checkBridgeExists - Non-zero return code")
            logger.error("checkBridgeExists - ERR: " + err)
        else:
            if bridgeName in str(out):
                retCode = True
            else:
                retCode = False
        return retCode

    @staticmethod
    def createBridge(logger, bridgeName):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"createBridge.yml -e '{ bridgeName: "+ bridgeName +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def deleteBridge(logger, bridgeName):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"deleteBridge.yml -e '{ bridgeName: "+ bridgeName +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def createContainer(logger, containerName, imageName, dockerBrName):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"createContainer.yml -e '{ containerName: "+ containerName +", imageName: \""+ imageName +"\", mgmtBridgeName: "+ dockerBrName +" }'"
        SouthBoundActual.execute(logger, cmd)

        # Start quagga, ssh services and set root password

        quaggaStartCmd = "/etc/init.d/quagga start"
        #sshStartCmd = "/etc/init.d/ssh start"
        SouthBoundActual.executeInContainer(logger, containerName, quaggaStartCmd)
        #SouthBoundActual.executeInContainer(logger, containerName, sshStartCmd)

        child =pexpect.spawn("sudo docker exec -it "+containerName+" passwd root")
        child.expect('Enter new UNIX password:')
        child.sendline('root')
        child.expect('Retype new UNIX password:')
        child.sendline('root')
        child.expect('passwd: password updated successfully')
        child.expect('\n')

    @staticmethod
    def deleteContainer(logger, containerName):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"deleteContainer.yml -e '{ containerName: "+ containerName +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def createVeth(logger, if1name, if2name):
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        cmd = "sudo ansible-playbook "+ scriptDir +"createVeth.yml -e '{ veth1: "+ if1name +", veth2: "+ if2name +" }'"
        SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def executeInContainer(logger, containerName, commandStr):
        cmd="sudo docker exec -it --privileged {} {}".format(containerName, commandStr)
        return SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def executeOnHost(logger, command):
        return SouthBoundActual.execute(logger, command)

    @staticmethod
    def attachInterface(logger,deviceID, interfaceName, linkType):
        cmd= ""
        cwd = os.path.abspath(os.path.dirname(__file__))
        scriptDir = cwd+"/ansible_scripts/"
        if linkType == LinkTypes.TYPE_DEFAULT:            
            cmd = "sudo ansible-playbook "+ scriptDir +"attachInterface.yml -e '{ containerPID: "+ deviceID +", interfaceName: "+ interfaceName +" }'"
        if linkType == LinkTypes.TYPE_BRIDGE:
            cmd = "sudo ansible-playbook "+ scriptDir +"attachToBridge.yml -e '{ bridgeName: "+ deviceID +", vethName: "+ interfaceName +" }'"
        if cmd != "":    
            SouthBoundActual.execute(logger, cmd)

    @staticmethod
    def getInterfaceUUID(logger,interfaceName):
        cmd = "ip addr show "+interfaceName+" | grep "+interfaceName+"@ | awk '{print $1}'"
        return str(SouthBoundActual.execute(logger, cmd))[:-1]
