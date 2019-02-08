import json
import os
x = {}
y = 0

def l1_details():
    name_dict={}
    name={}
    for i in range(y):
        #print(x["Details"][i]["Device_name"])
        name_dict[x["Details"][i]["Device_name"]] = []
        name.update(name_dict)
        z = len(x["Details"][i]["Connections"])
        for j in range(z):
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Connected_to"])
    return(name)

def l2_details():
    name_dict={}
    name={}
    for i in range(y):
        z = len(x["Details"][i]["Connections"])  
        name_dict[x["Details"][i]["Device_name"]] = []
        name.update(name_dict)
        for j in range(z):
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Local_interface_name"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Connected_to"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["remoteInterfaceName"])
    return(name)

def l3_details():
    name_dict={}
    name={}
    for i in range(y):
        name_dict[x["Details"][i]["Device_name"]] = []
        name.update(name_dict)
        z = len(x["Details"][i]["Connections"])
        for j in range(z):
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Local_interface_name"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Local_ip_address"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["Connected_to"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["remoteInterfaceName"])
            name[x["Details"][i]["Device_name"]].append(x["Details"][i]["Connections"][j]["remoteIPAddress"])
    return(name)

def adj_l1(topologyName):
    a = l1_details()
    l1file="/var/RNDTool/"+topologyName+"-L1Details.json"

    if os.path.isfile(l1file) and os.path.getsize(l1file) > 0:
        return

    #print(a)
    with open(l1file,"w") as fi:
        fi.write("------------------------ \n ")
        for i in a:
            for j in a[i]:
                fi.write(i + " ------> " + j)
                fi.write(" \n ")

def adj_l2(topologyName):
    b = l2_details()
    l2file="/var/RNDTool/"+topologyName+"-L2Details.json"

    if os.path.isfile(l2file) and os.path.getsize(l2file) > 0:
        return
    with open(l2file,"w") as fi:
        fi.write("------------------------ \n ")
        for i in b:
            k = 0
            for j in range(int((len(b[i]))/3)):
                fi.write(i + " " + b[i][k] + " ------> " + b[i][k+1] + " " + b[i][k+2])
                fi.write(" \n ")
                k = k+3

def adj_l3(topologyName):
    c = l3_details()
    l3file="/var/RNDTool/"+topologyName+"-L3Details.json"
    if os.path.isfile(l3file) and os.path.getsize(l3file) > 0:
	return
    with open(l3file,"w") as fi:
        fi.write("------------------------ \n ")
        for i in c:
            k = 0
            for j in range(int((len(c[i]))/5)):
                fi.write(i + " " + c[i][k] + " " + c[i][k+1] + " ------> " + " " + c[i][k+2] + " " + c[i][k+3] + " " + c[i][k+4])
                fi.write(" \n ")
                k = k+5

def delete_lfiles(toponame):

    filepath = "/var/RNDTool/"+toponame+".json"

    if os.path.exists(filepath):
	lfiles=[]
        lfiles.append("/var/RNDTool/"+toponame+"-L1Details.json")
        lfiles.append("/var/RNDTool/"+toponame+"-L2Details.json")
        lfiles.append("/var/RNDTool/"+toponame+"-L3Details.json")

        for i in lfiles:
	    if os.path.exists(i):
		os.remove(i)

def create_lfiles(toponame):

    filepath = "/var/RNDTool/"+toponame+".json"

    if os.path.exists(filepath):
	with open(filepath, "r") as f:
	    data = f.read()
	    global x,y
	    x = json.loads(data)
	    y = len(x["Details"])
	    adj_l1(toponame)
	    adj_l2(toponame)
	    adj_l3(toponame)

def rnd_read_start(topoName):
    # Check if topology exists
    filepath = "/var/RNDTool/"+topoName+".json"

    if os.path.exists(filepath):

        retJSON = {}
        with open(filepath,"r") as f:
            data = f.read()
            global x,y
            x = json.loads(data)
            y = len(x["Details"])
            adj_l1(topoName)
            adj_l2(topoName)
            adj_l3(topoName)
            data = json.loads(data)

            retJSON['1-TopologyName'] = data['TopoName']
            retJSONDetails = []
            for dev in data['Details']:
                devDetails = {}
                devDetails['4-SSHUsername'] = dev['username']
                devDetails['6-SSHIPAddress'] = dev['sshIPAddress']
                devDetails['3-ImageType'] = dev['Image_type']
                devDetails['1-Name'] = dev['Device_name']
                devDetails['2-Type'] = dev['Device_type']
                devDetails['5-SSHPassword'] = dev['password']
                devConnections = []
                for link in dev["Connections"]:
                    linkDetails = {}                    
                    linkDetails['5-RemoteInterfaceName'] = link['remoteInterfaceName']
                    linkDetails['3-LocalInterfaceName'] = link['Local_interface_name']
                    linkDetails['4-LocalInterfaceIPAddress'] = link['Local_ip_address']
                    linkDetails['6-RemoteInterfaceIPAddress'] = link['remoteIPAddress']
                    linkDetails['1-ConnectedTo'] = link['Connected_to']
                    linkDetails['2-LinkType'] = link['Link_type']
                    devConnections.append(linkDetails)
                devDetails['7-Links'] = devConnections
                retJSONDetails.append(devDetails)

            retJSON['2-Devices'] = retJSONDetails
        print(json.dumps(retJSON, indent=4, sort_keys=True))
        print("\n\n")
        print("L1, L2 and L3 information of the topology can be found in /var/RNDTool/"+topoName+"-L<<X>>Details.json")
    else:
        print("No such topology exists. Check topology name and try again.")
