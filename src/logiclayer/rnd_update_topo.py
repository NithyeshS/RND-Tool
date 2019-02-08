import sys,os
import time
import glob
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../southbound')

from utilities import *
from get_delta import *
#from get_delta2 import *
from rnd_create_topo import *
from rnd_read_topo import *

from SouthBoundWrapper import SouthBoundWrapper
from commonEnums import DeviceTypes
from commonEnums import ErrorCodes

from OutputJSONUtil import OutputJSONUtil 

def rnd_delete_link(current, dev, end):
    topoid = current["TopoId"]
    hyphen = "-"
    details = current["Details"]
    count = 0

    for i in details:
        if i["Device_name"] == dev:
            dev1 = i["Device_id"]
            dev_id = topoid + hyphen + i["Device_id"]
            dev_type = i["Device_type"]
            for j in i["Connections"]:
                if j["Connected_to"] == end:
                    if1 = j["Local_interface_name"]
                    if2 = j["remoteInterfaceName"]
                    ip1 = j["Local_ip_address"]
                    ip2 = j["remoteIPAddress"]
                    count += 1
        elif i["Device_name"] == end:
            dev2 = i["Device_id"]
            end_id = topoid + hyphen + i["Device_id"]
            end_type = i["Device_type"]
    #print("Removing link for", dev_id, if1, dev_type, end_id, if2, end_type)
    sb_dev_type = DeviceTypes.getDeviceTypeFromStr(dev_type)
    sb_end_type = DeviceTypes.getDeviceTypeFromStr(end_type)
    #return
    ret = sbw.deleteLink(dev_id, if1, sb_dev_type, end_id, if2, sb_end_type)
    ret = make_changes_for_var_links(current, ret, dev1, dev_id, dev2, end_id)
    #print(ret)
    uj.removeConnection(ret)
    if count == 1:
        free_ip_address(current, dev1, if1, sb_dev_type)
        free_ip_address(current, dev2, if2, sb_end_type)

def update_delete_links(current, dev, link_count):
    for i in dev:
        for j in dev[i]:
	    if(link_count[i][j]>0):
                rnd_delete_link(current, i, j)
		link_count[j][i]-=1

def rnd_update_delete_link(current, delink, link_count):
    for dev in delink:
        #print("length ", dev)
        update_delete_links(current, dev, link_count)

def update_delete_device(current, dev):
    topoid = current["TopoId"]
    hyphen = "-"
    details = current["Details"]
    for i in details:
        if i["Device_name"] == dev:
            dev_id = i["Device_id"]
            dev_type = i["Device_type"]
            break
    device = topoid + hyphen + dev_id
    #print("Deleting device", device, dev_type)
    sb_dev_type = DeviceTypes.getDeviceTypeFromStr(dev_type)
    #return
    ret = sbw.deleteDevice(device, sb_dev_type)
    ret = json.loads(ret)
    ret["deviceName"] = get_device_name_from_id(current, dev_id)
    uj.removeDevice(json.dumps(ret))

def rnd_update_delete_device(current, deletedev):
    for dev in deletedev:
        update_delete_device(current, dev)
    #print("In del device")

def update_add_device(new, dev):
    dev_con = []
    topoid = new["TopoId"]
    hyphen = "-"
    details = new["Details"]
    for i in details:
        if i["Device_name"] == dev:
            dev_id = i["Device_id"]
            dev_type = i["Device_type"]
            device = topoid + hyphen + dev_id
            #print("Adding device", device, dev_type)
	    sb_dev_type = DeviceTypes.getDeviceTypeFromStr(dev_type)
	    #return
            ret = sbw.createDevice(device, sb_dev_type)
	    ret = make_changes_for_var_devices(new, ret, dev_id)
            uj.constructDevice(ret)
            con = {}
            cons = []
            for j in i["Connections"]:
                cons.append(j["Connected_to"])
            con[dev] = cons
            break
    dev_con.append(con)
    #rnd_update_add_link(new, dev_con)


def rnd_update_add_device(new, addedev):
    for dev in addedev:
        update_add_device(new, dev)
    #print("In add device")

def rnd_add_link(new, dev, end, count):
    topoid = new["TopoId"]
    hyphen = "-"
    details = new["Details"]

    for i in details:
        if i["Device_name"] == dev:
            dev1 = i["Device_id"]
            dev_id = topoid + hyphen + i["Device_id"]
            dev_type = i["Device_type"]
        elif i["Device_name"] == end:
            dev2 = i["Device_id"]
            end_id = topoid + hyphen + i["Device_id"]
            end_type = i["Device_type"]

    #print("dev1 is", dev1, "dev2 is", dev2, str(count[dev2][dev1]))
    if1 = topoid + dev1 + hyphen + dev2 + hyphen + "if" + str(count[dev2][dev1])
    if2 = topoid + dev2 + hyphen + dev1 + hyphen + "if" + str(count[dev2][dev1])
    if get_interface_name(new, dev1, dev2)!="":
	if1 = get_interface_name(new, dev1, dev2)
    if get_interface_name(new, dev2, dev1)!="":
        if2 = get_interface_name(schema, dev2, dev1)
    #print("Adding link for", dev_id, if1, dev_type, end_id, if2, end_type)
    count[dev2][dev1] -= 1
    #return
    sb_dev_type = DeviceTypes.getDeviceTypeFromStr(dev_type)
    sb_end_type = DeviceTypes.getDeviceTypeFromStr(end_type)
    ret = sbw.createLink(dev_id, if1, sb_dev_type, end_id, if2, sb_end_type)
    ret = make_changes_for_var_links(new, ret, dev1, dev_id, dev2, end_id)
    #print(ret)
    uj.constructConnection(ret)

    ##Also assign IP address

    if count[dev1][dev2] == 1 or (count[dev1][dev2] > 1):
        subnet = get_subnet()

    if sb_dev_type != DeviceTypes.TYPE_BRIDGE:
        ip1 = get_ip(subnet)
	if get_ip_address_from_if(new, dev1, if1)!="":
	    ip1 = get_ip_address_from_if(schema, dev1, if1)
        #print("IP1 is", ip1)
        ret = sbw.assignInterfaceIP(dev_id, if1, ip1)
        ret = json.loads(ret)
        ret["deviceName"] = get_device_name_from_id(new, dev1)
	#print(ret)
        uj.addDeviceInterfaceIP(json.dumps(ret))

    if sb_end_type != DeviceTypes.TYPE_BRIDGE:
        ip2 = get_ip(subnet)
	if get_ip_address_from_if(new, dev2, if2)!="":
            ip2 = get_ip_address_from_if(new, dev2, if2)
        #print("IP2 is", ip2)
        ret = sbw.assignInterfaceIP(end_id, if2, ip2)
        ret = json.loads(ret)
        ret["deviceName"] = get_device_name_from_id(new, dev2)
	#print(ret)
        uj.addDeviceInterfaceIP(json.dumps(ret))


def update_add_links(new, dev, count, al_cnt):
    for i in dev:
        for j in dev[i]:
	    if(al_cnt[i][j] > 0):
            	rnd_add_link(new, i, j, count)
		al_cnt[j][i]-=1

def rnd_update_add_link(new, addlink, al_cnt):
    adjlist = CreateAdjList(new)
    count = FindCount(adjlist)
    for dev in addlink:
        #print("length ", dev)
        update_add_links(new, dev, count, al_cnt)
    #print("In add link")

def rnd_update_start(ip):

    #print("Rnd Started updation of Topology  at Time:" + str(time.time()))

    varfile = "/var/RNDTool/" + ip +".json"
    etcfile = "/etc/RNDTool/" + ip +".json" 

    if os.path.isfile(varfile) and os.path.getsize(varfile) > 0:
	print("Rnd Started updation of Topology  at Time:" + str(time.time()))
    else:
	print("No such topology exists")
	return

    with open(varfile,"r") as f1:
        current = json.load(f1)

    with open(etcfile,"r") as f2:
        new = json.load(f2)

    topoid = current["TopoId"]
    toponame = current["TopoName"]
    username = current["Username"]

    global uj
    uj = OutputJSONUtil(username, toponame, topoid)
    uj.updateTopo(username, toponame, topoid)
    sbw.topologyName = toponame


    addedev,deletedev,addlink,delink = rnd_update_cmp(new, current)
    #addedev,deletedev,addlink,deletedev = hlcomp(current,new)
    #print("DELETE DEVICE",deletedev)
    #print("ADD DEVICE",addedev)
    #print("DELETE LINK" , delink)
    #print("ADD LINK",addlink)

    #adjlist = CreateAdjList(new)
    #count = FindCount(adjlist)
    #print(count)
    add_link_count = create_count(addlink)
    del_link_count = create_count(delink)
    #print(add_link_count)
    #print(del_link_count)
    #return

    print("DELETING LINK" , delink)
    rnd_update_delete_link(current, delink, del_link_count)
    print("DELETING DEVICE",deletedev)
    rnd_update_delete_device(current, deletedev)
    print("ADDING DEVICE",addedev)
    rnd_update_add_device(new, addedev)
    print("ADDING LINK",addlink)
    rnd_update_add_link(new, addlink, add_link_count)

    uj.writeVarJson()
    delete_lfiles(toponame)
    create_lfiles(toponame)
		

