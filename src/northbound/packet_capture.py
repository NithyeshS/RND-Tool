import sys,os,datetime
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../southbound')
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/..')
from SouthBoundWrapper import SouthBoundWrapper
import json
import logging

sbw = SouthBoundWrapper(logging.INFO)
if len(sys.argv) == 6:
        #Store the inputs into variables
		toponame=sys.argv[1]
		devicename=sys.argv[2]
        interface=sys.argv[3]
        options=sys.argv[4]
		input=sys.argv[5]
		
	varfile="/var/RNDTool/"+toponame+".json"
	with open(varfile) as f:
		var = json.load(f)

	topoid = var["TopoId"]
	for i in var["Details"]:
		if devicename == i["Device_name"]:
			devid = i["Device_id"]
			break

	myhost = topoid+"-"+devid

        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        #directory = '/var/RNDTool/capture-data/'
        #if not os.path.exists(directory):
        #        os.makedirs(directory)
	filename="/var/log/rndtool/capture-data/"+myhost+""+interface+""+timestamp+".pcap"



        #Run tcpdump
		if(options==1):
			Tcp_Cmd=" tcpdump -G "+input+" -i "+interface+" -W 1 -w "+filename   #exec_time
		if(options==2):
			Tcp_Cmd=" tcpdump -c "+input+" -i "+interface+" -W 1 -w "+filename   #number_of_packet 
        if(options==3):
			Tcp_Cmd=" tcpdump -C "+input+" -i "+interface+" -W 1 -w "+filename   #size_of_packet 
		sbw.runPacketCapture(myhost,Tcp_Cmd)

        #If tcpdump completes successfully scp the file to host
        if os.path.isfile(filename):
                print("Please find the file at " +filename)
        else:
                print("TCPdump capture failed. Please check the inputs. \n")
else:
        print("INVALID ARGUMENTS")
        print("packet_capture <<Topology-name>> <<Device-name>> <<Interface-Name>> <<Options>> <<Input>>")
