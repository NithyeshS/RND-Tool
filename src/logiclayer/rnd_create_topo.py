###################################################
#                                                 #
#           RND-TOOL			          		  #
#                                                 #
#	rnd_create_topo.py                        	  #
#	Usage: rnd_create_topo.py <input_json>	  	  #
#	        				  					  #
###################################################

import os
import subprocess
import shlex
import time
import glob
import json
import logging
from collections import Counter

import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../southbound')
from SouthBoundWrapper import SouthBoundWrapper
from commonEnums import DeviceTypes
from commonEnums import ErrorCodes
from rnd_read_topo import create_lfiles

from utilities import *

from OutputJSONUtil import OutputJSONUtil 


sbw = SouthBoundWrapper(logging.INFO)

def make_changes_for_var_devices(schema, ret, i):
	ret = json.loads(ret)
	if ret["error"] == "NO_ERROR":
		ret["deviceID"] = i
		ret["deviceName"] = get_device_name_from_id(schema, i)
		ret["Device_cpu"] = get_device_cpu_from_id(schema, i)
		ret["Device_memory"] = get_device_memory_from_id(schema, i)
		ret["Image_type"] = get_device_image_type_from_id(schema, i)
	return json.dumps(ret)

def create_devices(schema, adjlist, topoid):
	hyphen = "-"
	for i in adjlist:
		
		ConName = topoid + hyphen + i

		#print("CREATING CONTAINER " + ConName)
		for j in adjlist[i]:
			if dev_type(j) == 1:
				dev = j

		dev_ty = DeviceTypes.getDeviceTypeFromStr(dev)

		ret = sbw.createDevice(ConName, dev_ty)
		ret = make_changes_for_var_devices(schema, ret, i)
		#print("Creating device with ", ConName,  dev_ty, ret)
		uj.constructDevice(ret)

def make_changes_for_var_links(schema, ret, d1, con_name, d2, end):
	ret = json.loads(ret)
	if ret["error"] == "NO_ERROR":
		#print(ret, d1, d2)
		for i in range(0, len(ret["devices"])):
			if ret["devices"][i]["connections"][0]["deviceName"] == con_name:
				ret["devices"][i]["connections"][0]["deviceName"] = get_device_name_from_id(schema, d1)
				ret["devices"][i]["connections"][0]["linkType"] = get_link_type_from_devices(schema, d1, d2)
                        if ret["devices"][i]["deviceName"] == con_name:
                                ret["devices"][i]["deviceName"] = get_device_name_from_id(schema, d1)
				ret["devices"][i]["linkType"] = get_link_type_from_devices(schema, d1, d2)
			if ret["devices"][i]["connections"][0]["deviceName"] == end:
				ret["devices"][i]["connections"][0]["deviceName"] = get_device_name_from_id(schema, d2)
				ret["devices"][i]["connections"][0]["linkType"] = get_link_type_from_devices(schema, d2, d1)
                        if ret["devices"][i]["deviceName"] == end:
                                ret["devices"][i]["deviceName"] = get_device_name_from_id(schema, d2)
				ret["devices"][i]["linkType"] = get_link_type_from_devices(schema, d2, d1)
		return json.dumps(ret)
	return json.dumps(ret)
		

def create_links(schema, count, topoid):
	ret = {}
	hyphen = "-"
	for i in count:
		
		ConName = topoid + hyphen + i
		#print(count[i]["Router"])
		#print("conn name is ", ConName)
		for j in count[i]:
			
			if dev_type(j) == 1:
				continue
			
			cnt = count[i][j]
			while cnt > 0:
				end = topoid + hyphen + j

				if1 = topoid + i + hyphen + j + hyphen + "if" + str(cnt)
				if2 = topoid + j + hyphen + i + hyphen + "if" + str(cnt)
				if get_interface_name(schema, i, j)!="":
					if1 = get_interface_name(schema, i, j)
				if get_interface_name(schema, j, i)!="":
					if2 = get_interface_name(schema, j, i)
				#print("Connname is ", ConName ,"conn is ", end ,"if1 is", if1 ,"if2 is", if2)

				dev1 = get_device_type(count, i)
				dev_type1 = DeviceTypes.getDeviceTypeFromStr(dev1)
				dev2 = get_device_type(count, j)
				dev_type2 = DeviceTypes.getDeviceTypeFromStr(dev2)
				#print("device type is ", dev_type1, dev_type2)

				ret = sbw.createLink(ConName, if1, dev_type1, end, if2, dev_type2)
				ret = make_changes_for_var_links(schema, ret, i, ConName, j, end)
				#print(ret)
				uj.constructConnection(ret)

				## Give IP-Address to links ##

				if count[i][j] == 1 or (count[i][j] > 1 and cnt == count[i][j]):
					subnet = get_subnet()
					#print("Subnet ", int(subnet), "for router", i[0])

				
				if dev_type1 != DeviceTypes.TYPE_BRIDGE:
					ip1 = get_ip(subnet)
					if get_ip_address_from_if(schema, i, if1)!="":
						ip1 = get_ip_address_from_if(schema, i, if1)
					#print(ip1)
					ret = sbw.assignInterfaceIP(ConName, if1, ip1)
					ret = json.loads(ret)
					ret["deviceName"] = get_device_name_from_id(schema, i)
					#print(ret)
					uj.addDeviceInterfaceIP(json.dumps(ret))

				if dev_type2 != DeviceTypes.TYPE_BRIDGE:
					ip2 = get_ip(subnet)
					if get_ip_address_from_if(schema, j, if2)!="":
                                                ip2 = get_ip_address_from_if(schema, j, if2)
					#print(ip2)
					ret = sbw.assignInterfaceIP(end, if2, ip2)
					ret = json.loads(ret)
					#print(ret)
					ret["deviceName"] = get_device_name_from_id(schema, j)
					uj.addDeviceInterfaceIP(json.dumps(ret))
				#print("ip1 is ", ip1, "ip2 is", ip2)

				cnt -= 1
				count[j][i] -= 1
				
			
def rnd_create_start(ip):
 
	print("Rnd Started creation of Topology  at Time:" + str(time.time()))

	etcfile = "/etc/RNDTool/" + ip + ".json"
	varfile = "/var/RNDTool/" + ip + ".json"

	if os.path.isfile(varfile) and os.path.getsize(varfile) > 0:
		print("Topology already exists. Please delete existing topology or give new topology")
		return

	with open(etcfile) as f:
		schema = json.load(f)

	topoid = schema["TopoId"]
	toponame = schema["TopoName"]
	username = schema["Username"]
	#print("Topoid is " + topoid)
	global uj
	uj = OutputJSONUtil(username, toponame, topoid)

	AdjList = CreateAdjList(schema)
	count  = FindCount(AdjList)
	#print(count)
	sbw.topologyName = toponame
	ipaddress = get_management_bridge_ip()
	sbw.createManagementBridge(ipaddress)
	create_devices(schema, count, topoid)

	create_links(schema, count, topoid)
	uj.writeVarJson()

	create_lfiles(toponame)
		
