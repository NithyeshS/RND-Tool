import os
import time
import glob
import json
import logging

import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../southbound')
from SouthBoundWrapper import SouthBoundWrapper
from commonEnums import DeviceTypes
from commonEnums import ErrorCodes
from rnd_read_topo import delete_lfiles

from OutputJSONUtil import OutputJSONUtil 

from utilities import *

sbw = SouthBoundWrapper(logging.INFO)

def delete_topology(schema, count):
	
	hyphen = "-"
	topoid = schema["TopoId"]
	for device in schema["Details"]:
		devid = device["Device_id"]
		dev_id = topoid + hyphen + devid
		dev1 = device["Device_type"]
		dev_type1 = DeviceTypes.getDeviceTypeFromStr(dev1)
		for conn in device["Connections"]:
			
			end = get_dev_id(schema, conn["Connected_to"])
			end_id = topoid + hyphen + end
			if count[devid][end]> 0:

				if1 = conn["Local_interface_name"]
				if2 = conn["remoteInterfaceName"]
				#print("Connname is ", dev_id ,"conn is ", end_id ,"if1 is", if1 ,"if2 is", if2)

				dev2 = get_device_type_from_name(schema, conn["Connected_to"])
				dev_type2 = DeviceTypes.getDeviceTypeFromStr(dev2)
				#print("device type is ", dev_type1, dev_type2)

                                free_ip_address(schema, devid, if1, dev_type1)
                                free_ip_address(schema, end, if2, dev_type2)

				ret = sbw.deleteLink(dev_id, if1, dev_type1, end_id, if2, dev_type2)

				count[end][devid] -= 1
		ret = sbw.deleteDevice(dev_id, dev_type1)
		#print("Deleting device " + dev_id, dev_type1)
		

def rnd_delete_start(topo):

	global uj

	print("Rnd Started deletion of Topology  at Time:" + str(time.time()))

	ip = "/var/RNDTool/"+topo+".json"	
	with open(ip) as f:
		schema = json.load(f)

	topoid = schema["TopoId"]
	toponame = schema["TopoName"]
	username = schema["Username"]

	AdjList = CreateAdjList(schema)
	count  = FindCount(AdjList)
	#print(count)
	uj = OutputJSONUtil(username, toponame, topoid)

	delete_topology(schema, count)
	delete_lfiles(toponame)
	sbw.topologyName = toponame
	free_management_bridge_ip(toponame)
	sbw.deleteManagementBridge()
	uj.removeVarJson(username, toponame, topoid)


