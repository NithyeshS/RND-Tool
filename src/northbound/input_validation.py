from collections import Counter
import json
import sys
from shutil import copyfile

#Function to create adjacency list from input json file
def CreateAdjList(inp):
    AdjList={}
    dict1={}
    for dev in inp["Details"]:
    #dict={}
        dict1[dev['Device_name']]=[]
        AdjList.update(dict1)
    #print("initial Adj list", AdjList)
    for d in inp['Details']:
        for i in d['Connections']:
            AdjList[d['Device_name']].append(i['Connected_to'])
    return AdjList

# Function to convert the neighbor list in counters            
def ConvertToChar(d):
    return(dict(Counter(d)))
# function to check the no of bidirectional links between a pair of deviices
def CountCheck(ajl):
    check=False
    for i in ajl:
        for j in ajl[i]:
            if j in ajl:
                if i in ajl[j]:
                    if ConvertToChar(ajl[i])[j]==ConvertToChar(ajl[j])[i]:
                        check=True
                    else:
                        check=False
                        print("Mismatch in no of links between routers", i, j)
                        return check
                else:
                        check=False
                        print("Mismatch in no of links between routers", i, j)
                        return check
            else: 
                check=False
                print("device not present in input file", j)
                return check
    return check

# function to check if the input format is correct or not
def InvalidInput(inp):
    valid=True
    allowed_device_types=['Router', 'router', 'ROUTER','switch', 'Switch', 'SWITCH', 'HOST', 'host', 'Host']
    allowed_link_types=['VXLAN','vxlan','GRE','gre','bridge','Bridge','BRIDGE', 'P2P','p2p', '']
    for device in inp['Details']:
        #print(device['Device_type'])
        if device['Device_type'] not in allowed_device_types:
            valid=False
            print("Invalid Device Type")
            break
        for link in device['Connections']:
                if link['Link_type'] not in allowed_link_types:
                    print("Invalid Link Type")
                    valid=False
                    break
    return valid
def ipcheck(ip):
    if ip :
        a=ip.split(".")
        a = list(map(int, a))
        # print(a)
        if len(a)>4:
            print("invalid ip")
            return False    
        for i in a:
            if i<0 or i>255:
                print("invalid ip")
                return False
        return True
    return True	
	
def Check_ip(inp):
	valid=True
	for device  in inp['Details']:
		for link in device['Connections']:
			ip=ipcheck(link['Local_ip_address'])
			if ip==False:
				valid=False
				print("Incorrect Interface ip format")
				break
	return valid

#function to check dupliacte (device_name,device_type) pair
def CheckDuplicateDevice(inp):
    dev_tuple=[]
    check=True
    for device in inp['Details']:
        #dtup=(device['Device_name'], device['Device_type'])
        dev_tuple.append(device['Device_name'])
    if len(set(dev_tuple))!=len(dev_tuple):
    
        check=False
        print("Duplicate devices found")
    return check

#function to validate input
def Validate_Input(inp):
    valid=1
    v1=InvalidInput(inp)
    v2=CheckDuplicateDevice(inp)
    AdjList=CreateAdjList(inp)
    v3=CountCheck(AdjList)
    v4=Check_ip(inp)
    if (v1 and v2 and v3 and v4)==False:
        valid=0 #print("Invalid Input")
    return valid #else:
        #print("Valid Input")

def createid(user,filename):
    with open(filename, 'r') as fi:
        data = fi.read()
        data = json.loads(data)
    #print(data)
    topoid=(data['TopoName'])[0]+(data['TopoName'])[-2:]
    data['TopoId']=topoid
    detailjson=[] #data['Details']
    for dev in data['Details']:
            
            deviceid=dev['Device_name'][0]+dev['Device_name'][-1]
            dev['Device_id']=deviceid
            detailjson.append(dev)	
    data['Details']=detailjson
    with open(filename, 'w') as fi:		
        json.dump(data, fi, indent=4)  


def init(data):
    filename=data['TopoName']+".json"
    user=data['Username']
    for j in data["Details"] :
        for k in j['Connections']:
            print(j['Device_name']+" -----> " + k['Connected_to'], end=' ')
        print("\n")

    valid=Validate_Input(data)
    print("valid input" if valid==1 else "not valid")
    if valid == 1:
        filename="/etc/RNDTool/"+filename
        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=4))
        createid(user,filename)
