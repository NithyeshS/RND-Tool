"""
Gets JSON snippets from the SouthBound Wrapper, recognizes success, failure in topology creation. Reports to user and writes to /var/RNDTool/topologyname.json. 
To be written into user specific folders in the future
"""
import json
import os
from collections import OrderedDict

import sys
sys.path.append('../southbound')
from SouthBoundWrapper import SouthBoundWrapper

class OutputJSONUtil:
	def __init__(self,username,toponame,tid):
		self.username = username
		self.toponame = toponame
		self.tid = tid
		self.directory = "/var/RNDTool/"
		if not os.path.exists(self.directory):
    			os.makedirs(self.directory)
		self.devices = []
		self.outputJSON = {}	

	def updateJSON(self,username,toponame,tid):
		"""
		[call when /var file needs to be updated due to a topology update.]
		Arguments:
		[username,topologyid]
		Returns:
		None 
		"""
		self.username = username
		self.toponame = toponame
		self.tid = tid
		self.directory = "/var/RNDTool/"
		fileName = self.directory+"/"+self.toponame+".json"
		if os.path.isfile(fileName) and os.path.getsize(fileName) > 0:
			fd = open(fileName,'r+')
			self.outputJSON = json.load(fd)
			self.devices = self.outputJSON["Details"]
			fd.seek(0)
			fd.truncate()
		else:
			print("var file does not exist.create topology and then update")	

	def updateTopo(self,username,toponame,tid):
                """
                [call when /var file needs to be updated due to a topology update.]
                Arguments:
                [username,topologyid]
                Returns:
                None 
                """
                self.username = username
                self.toponame = toponame
                self.tid = tid
                self.directory = "/var/RNDTool/"
                fileName = self.directory+"/"+self.toponame+".json"
                if os.path.isfile(fileName) and os.path.getsize(fileName) > 0:
                        fd = open(fileName,'r+')
                        self.outputJSON = json.load(fd)
                        self.devices = self.outputJSON["Details"]	
		else:
                        print("var file does not exist.create topology and then update")
	
	def checkForDeviceEntry(self,deviceName): 
		"""
		[check for device entry in self.devices list and return index if present]

		Arguments:
		[deviceName]
		Returns:
		index - list index of the device 
		"""
		for i in range(0,len(self.devices)):
			if self.devices[i]["Device_name"] == deviceName:
				return i
		 
	def checkForIntfEntry(self,deviceName,intfName,intftype):
		"""
		[check for interface entry in self.devices["Connections"] list and return index if present]

		Arguments:
		[deviceName,interfaceName]
		Returns:
		index i,j - list index of the interface entry in connections
		"""
		if intftype == "remote":
			for i in range(0,len(self.devices)):
				for j in range(0,len(self.devices[i]["Connections"])):
					if self.devices[i]["Connections"][j]["Connected_to"] == deviceName and self.devices[i]["Connections"][j]["remoteInterfaceName"] == intfName:
						return i,j
		else:
			for i in range(0,len(self.devices)):
				for j in range(0,len(self.devices[i]["Connections"])):
					if self.devices[i]["Device_name"] == deviceName and self.devices[i]["Connections"][j]["Local_interface_name"] == intfName:
						return i,j

	def checkForConnectionEntry(self,connections):
		"""
		[check for link in self.devices["Connections"] list and return index in device connections list if present]

		Arguments:
		[JSON] -- [JSON with device name, connection details and error code(if any).]
		Returns:
		index j - list index of the link entry in connections
		"""
		for i in range(0,len(self.devices)):
			for j in range(0,len(self.devices[i]["Connections"])):
				if (self.devices[i]["Connections"][j]["Connected_to"] == connections["deviceName"]) and (self.devices[i]["Connections"][j]["Local_interface_name"] == connections["localInterfaceName"]) and (self.devices[i]["Connections"][j]["remoteInterfaceName"]== connections["remoteInterfaceName"]):
					return j
			
	def addBridgeID(self,brJSON):
		"""
		[Receives a JSON Snippet with bridge ID information after addtion of interfaces to the bridge]

		Arguments:
		[JSON] -- [JSON containing bridge ID, name and error code(if any).]
		Returns:
		None
		""" 
		brJSON = json.loads(brJSON)
		if brJSON["error"] == "NO_ERROR":
			for i in range(0,len(self.devices)):
				if self.devices[i]["Device_name"] == brJSON["deviceName"]:
					self.devices[i]["Device_id"] = brJSON["deviceID"]
	def constructDevice(self,devJSON):
		"""
		[Receives a JSON Snippet with device information and Constructs the devices section of the /var file.]

		Arguments:
		[JSON] -- [JSON containing container ID, name, docker image, SSH IP and error code(if any).]
		Returns:
		device_data JSON snippet -- if device information add to JSON is successful
		error JSON snippet -- JSON snippet from southbound has an error. 
		""" 
		##checks for entries if device is a bridge
		devJSON = json.loads(devJSON)
		if devJSON["error"] == "NO_ERROR":
			device_data = {}
			try:
				device_data["Image_type"] = devJSON["Image_type"]
			except:
				device_data["Image_type"] = ""
			device_data["Device_type"] = devJSON["deviceType"]
			if device_data["Device_type"] != "Bridge":
				device_data["username"] = "root"
				device_data["password"] = "root"
			else:
				device_data["username"] = ""
				device_data["password"] = ""				
			try:
				device_data["dockerID"] = devJSON["dockerID"]
			except:
				device_data["dockerID"] = ""
			device_data["Device_id"] = devJSON["deviceID"]
			device_data["Device_name"] = devJSON["deviceName"]
			try:
				device_data["Device_cpu"] = devJSON["Device_cpu"]
			except:
				device_data["Device_cpu"] = ""
			try:
				device_data["Device_memory"] = devJSON["Device_memory"]
			except:
				device_data["Device_memory"] = ""
			try:
				device_data["sshIPAddress"] = devJSON["sshIPAddress"]
			except:
				device_data["sshIPAddress"] = ""
			device_data["Connections"] = []
			##append to devices list
			self.devices.append(device_data)
			return device_data
		else:
			return devJSON["error"]


	def constructConnection(self,linkJSON):
		"""
		[Receives a JSON Snippet with link information and Constructs the link section for each device.]
		Arguments:
		[JSON] -- [JSON with device name, connection details and error code(if any).]
		Returns:
		link_data JSON snippet -- if link information add to JSON is successful
		error JSON snippet -- JSON snippet from southbound has an error. 
		"""
		##checks for entries if intf is a bridge interface
		linkJSON = json.loads(linkJSON)
		if linkJSON["error"] == "NO_ERROR":
			link_data = {}
			for i in range(0,len(linkJSON["devices"])):
				link_data = {}
				index = self.checkForDeviceEntry(linkJSON["devices"][i]["deviceName"])
				##using index add connection info in "connections" section of device
				link_data["Connected_to"] = linkJSON["devices"][i]["connections"][0]["deviceName"]
				link_data["Link_type"] = linkJSON["devices"][i]["connections"][0]["linkType"]
				link_data["Local_interface_name"] = linkJSON["devices"][i]["connections"][0]["localInterfaceName"]
				link_data["Local_ip_address"] = ""
				link_data["localInterfaceUID"] = linkJSON["devices"][i]["connections"][0]["localInterfaceUID"]
				link_data["remoteInterfaceName"] = linkJSON["devices"][i]["connections"][0]["remoteInterfaceName"]
				link_data["remoteIPAddress"] = ""
				link_data["remoteInterfaceUID"] = linkJSON["devices"][i]["connections"][0]["remoteInterfaceUID"]
				#print("index is", index)
				self.devices[index]["Connections"].append(link_data)
			return link_data
		else:
			return linkJSON["error"]
									
		

	def addDeviceInterfaceIP(self,intfJSON):
		"""
		[Receives a JSON Snippet with interface IP information and adds IP address to the connections section for each device.]
		Arguments:
		[JSON] -- [JSON with device name, interface name, IP address and error(if any).]
		Returns:
		JSON snippet -- if link information add to JSON is successful
		error JSON snippet -- JSON snippet from southbound has an error. 
		"""
		intfJSON = json.loads(intfJSON)
		if intfJSON["error"] == "NO_ERROR":
			i,j = self.checkForIntfEntry(intfJSON["deviceName"],intfJSON["localInterfaceName"],"local")
			self.devices[i]["Connections"][j]["Local_ip_address"] = intfJSON["localInterfaceIP"]

			i1,j1 = self.checkForIntfEntry(intfJSON["deviceName"],intfJSON["localInterfaceName"],"remote")
			self.devices[i1]["Connections"][j1]["remoteIPAddress"] = intfJSON["localInterfaceIP"]
			return self.devices[i]["Connections"][j]
		else:
			return intfJSON["error"]
					
				
	def writeVarJson(self):
		"""
		[Constructs the varfile.JSON]
		Arguments:
		[username] -- username to identify user
		[tid] -- topology id created to identify topology
		Returns:
		[JSON] -- OutputJSON
		"""
		fileName = self.directory+"/"+self.toponame+".json"
		self.outputJSON["Username"] = self.username
 		self.outputJSON["TopoName"] = self.toponame
 		self.outputJSON["TopoId"] = self.tid
		self.outputJSON["Details"] = self.devices
		with open(fileName, 'w') as outfile:
			json.dump(self.outputJSON, outfile, indent=4)

	def removeDevice(self,devJSON):
		"""
		[Receives a JSON Snippet with device information and removes the device from the devices section of the /var file.]

		Arguments:
		[JSON] -- [JSON containing container ID, name, docker image, SSH IP and error code(if any).]
		Returns:
		device_data JSON snippet -- if device information remove from JSON is successful
		error JSON snippet -- JSON snippet from southbound has an error. 
		""" 
		devJSON = json.loads(devJSON)
		if devJSON["error"] == "NO_ERROR":
			##remove device based on index
			index = self.checkForDeviceEntry(devJSON["deviceName"])
			device_data = self.devices.pop(index) 
			return device_data
		else:
			return devJSON["error"]

		

	def removeConnection(self,linkJSON):
		"""
		[Receives a JSON Snippet with link information and removes the link section for each device.]
		Arguments:
		[JSON] -- [JSON with device name, connection details and error code(if any).]
		Returns:
		link_data JSON snippet -- if link information remove from JSON is successful
		error JSON snippet -- JSON snippet from southbound has an error. 
		"""
		linkJSON = json.loads(linkJSON)
		if linkJSON["error"] == "NO_ERROR":
			link_data = {}
			for i in range(0,len(linkJSON["devices"])):
				link_data = {}
				index = self.checkForDeviceEntry(linkJSON["devices"][i]["deviceName"])
				j = self.checkForConnectionEntry(linkJSON["devices"][i]["connections"][0])
				link_data = self.devices[index]["Connections"].pop(j)
			return link_data
		else:
			return linkJSON["error"]
		
	def removeVarJson(self,username,toponame,tid):
		"""
		[Remove /var JSON file in case of delete topology]
		Arguments:
		None
		Returns:
		None
		"""
		fileName = self.directory+"/"+self.toponame+".json"
		self.username = username
		self.toponame = toponame
		self.tid = tid
		self.directory = "/var/RNDTool/"
		fileName = self.directory+"/"+self.toponame+".json"
		if os.path.isfile(fileName) and os.path.getsize(fileName) > 0:
			os.remove(fileName)

			





	
