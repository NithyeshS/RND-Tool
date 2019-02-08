# -*- coding: utf-8 -*-
import os
import pickle
import json
import sys
sys.path.append('..')
sys.path.append('../southbound')
from SouthBoundWrapper import SouthBoundWrapper
from commonEnums import DeviceTypes
from commonEnums import ErrorCodes

from collections import Counter

subnet=[0]*255
ip_addr = "192.168."
mgmt_ip = "10.10."
mask = "/24"

def get_management_bridge_ip():
	global mgmt_ip
	global mask
	mgmt_subnet = get_mgmt_subnet()
	mgmt_ip_addr = mgmt_ip + mgmt_subnet + ".0" + mask
	return mgmt_ip_addr

def get_mgmt_subnet():
	global subnet
	fname = "mgmt_subnet.txt"
	if os.path.isfile(fname):
		sub = find_subnet(fname)
		return sub+1
	else:
		with open(fname,"w+") as fh:
			pickle.dump(subnet, fh)
		fh.close()
		sub = find_subnet(fname)
		return sub+1

def free_management_bridge_ip(toponame):
	varfile = "/var/RNDTool/"+toponame+".json"
	with open(ip) as f:
                schema = json.load(f)

	details = schema["Details"]
	for device in details:
		if device["sshIPAddress"] != "":
			ssh_ip = device["sshIPAddress"]
			break

	mgmt_subnet = get_subnet_from_ip(ssh_ip)
	free_mgmt_subnet(mgmt_subnet)
	

def free_mgmt_subnet(subnet):
        fname = "mgmt_subnet.txt"
        fh = open(fname, "r")
        arr = pickle.load(fh)
        index = int(subnet)-1
        fh = open(fname, "w+b")
        arr[index]=0
        pickle.dump(arr, fh)
        fh.close()
        return

def get_device_name_from_id(schema, dev_id):
	for item in schema["Details"]:
		if item["Device_id"] == dev_id:
			return item["Device_name"]

def get_interface_name(schema, dev, end):
	for item in schema["Details"]:
		if item["Device_id"] == dev:
			for conn in item["Connections"]:
				if end == get_dev_id(schema, conn["Connected_to"]):
					return conn["Local_interface_name"]

def get_ip_address_from_if(schema, dev, intf):
	for item in schema["Details"]:
                if item["Device_id"] == dev:
                        for conn in item["Connections"]:
				if intf == conn["Local_interface_name"]:
					#print("Returning", conn["Local_ip_address"])
					return conn["Local_ip_address"]
			return ""

def get_device_type_from_name(schema, dev):
	for item in schema["Details"]:
		if item["Device_name"] == dev:
			return item["Device_type"]

def get_link_type_from_devices(schema, d1, d2):
	for item in schema["Details"]:
		if item["Device_id"] == d1:
			for conn in item["Connections"]:
				if d2 == get_dev_id(schema, conn["Connected_to"]):
					return conn["Link_type"]

def get_device_cpu_from_id(schema, dev_id):
	for item in schema["Details"]:
		if item["Device_id"] == dev_id:
			if item["Device_type"] == "Switch" or item["Device_type"] == "switch" or item["Device_type"] == "SWITCH":
				return ""
			return item["Device_cpu"]

def get_device_memory_from_id(schema, dev_id):
	for item in schema["Details"]:
		if item["Device_id"] == dev_id:
			if item["Device_type"] == "Switch" or item["Device_type"] == "switch" or item["Device_type"] == "SWITCH":
				return ""
			return item["Device_memory"]

def get_device_image_type_from_id(schema, dev_id):
        for item in schema["Details"]:
                if item["Device_id"] == dev_id:
                        if item["Device_type"] == "Switch" or item["Device_type"] == "switch" or item["Device_type"] == "SWITCH":
                                return ""
			#print("Returning image-type", item["Image_type"], "for", dev_id)
                        return item["Image_type"]

def get_ip(current_subnet):
	global ip_addr
	global mask
	base_ip = get_base(current_subnet)
	ip = ip_addr + str(current_subnet) + "." + str(base_ip) + mask
	return ip
	
def get_device_type(count, i):
	for item in count:
		if item == i:
			for j in count[i]:
				if dev_type(j) == 1:
					return j

def dev_type(dev):
    if dev == "Router" or dev == "router" or dev == "ROUTER":
        return 1
    if dev == "Switch" or dev == "switch" or dev == "SWITCH":
        return 1
    if dev == "Host" or dev == "host" or dev == "HOST":
        return 1
    return 0

def get_dev_id(schema, dev_name):
	for item in schema["Details"]:
		if item["Device_name"] == dev_name:
			return item["Device_id"]

def CreateAdjList(schema):
	AdjList = {}
	dict1 = {}

	for device in schema["Details"]:
		dict1[device["Device_id"]] = []
		AdjList.update(dict1)
	#print("Initial adj list", AdjList)

	for dev in schema["Details"]:
		AdjList[dev["Device_id"]].append(dev["Device_type"])
		for conn in dev["Connections"]:
			con_id = get_dev_id(schema, conn["Connected_to"])
			AdjList[dev["Device_id"]].append(con_id)
	#print("Final Adj list ", AdjList)
	return AdjList

def create_count(dev_list):
	Adjlist = {}
	dict1 = {}

	for item in dev_list:
		for i,j in item.iteritems(): 
			dict1[i] = []
			Adjlist.update(dict1)
	#print("Initial adj list", Adjlist)

	for item in dev_list:
		for i, j in item.iteritems():
			for end in j:
				Adjlist[i].append(end)
	#print("Final Adj list ", Adjlist)
	count = FindCount(Adjlist)
	return count
		

def FindCount(adjlist):
	keys = {}
	for dev in adjlist:
		keys[dev] = dict(Counter(adjlist[dev]))
	return keys      

def find_subnet(fname):
    fh = open(fname, "r")
    sub = pickle.load(fh)
    fh.close()
    fh = open(fname, "w+b")
    for i in range(255):
        if sub[i] == 0:
            sub[i] = 1
            pickle.dump(sub, fh)
            fh.close()
            return i
    fh.close()

def get_subnet():
    global subnet
    fname = "subnet.txt"
    if os.path.isfile(fname):
        sub = find_subnet(fname)
        return sub+1
    else:
        with open(fname,"w+") as fh:
            pickle.dump(subnet, fh)
        fh.close()
        sub = find_subnet(fname)
        return sub+1

def free_subnet(subnet):
	fname = "subnet.txt"
	fh = open(fname, "r")
	arr = pickle.load(fh)
	index = int(subnet)-1
	fh = open(fname, "w+b")
	arr[index]=0
	pickle.dump(arr, fh)
	fh.close()
	return

def get_subnet_from_ip(ipaddr):
	subs = ipaddr.split(".")
        #print("ip is", ipaddr, subs[2])
	return subs[2]

def free_ip_address(schema, dev_id, intf, dev_type):
	if dev_type == DeviceTypes.TYPE_BRIDGE:
		return

	for item in schema["Details"]:
                #print("dev id is", dev_id)
		if item["Device_id"] == dev_id:
                        #print("Dev_id is ", item["Device_id"], dev_id)
			for j in item["Connections"]:
                                #print("local is ", j["localInterfaceName"], intf)
				if j["Local_interface_name"] == intf:
					ipaddr = j["Local_ip_address"]
					subnet = get_subnet_from_ip(ipaddr)
					free_subnet(subnet)

def get_base(curr_subnet):
    global subnet
    act = curr_subnet-1
    i = int(subnet[act])
    subnet[act] = i+1
    return (subnet[act])

#Method to add SSH aliases to /etc/hosts - Will read from /var file
def alias_create(toponame):
        #Check if topology file exists
        filepath = "/var/RNDTool/"+toponame+".json"
        if os.path.exists(filepath):
                b = []
                c = []
                y = 0
                with open(filepath,"r") as f:
                        x = json.load(f)
                        a = (x["TopoName"])
                        y = len(x["Details"])
                        for i in range(y):
                                b.append(x["Details"][i]["Device_name"])
                                c.append(x["Details"][i]["sshIPAddress"])

                for i in range(y):
                        with open("/etc/hosts","a+") as f:
                                command = c[i]+"  "+a+"-"+b[i]+"\n"
                                f.write(command)
                return True
        else:
                return False

#Method to delete SSH aliases to /etc/hosts
def alias_delete(toponame):
        cmd = "sudo sed -i \'/"+toponame+"-/d\' /etc/hosts"
        os.system(cmd)
        return True

