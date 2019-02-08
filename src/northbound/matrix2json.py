import json
import os, sys

import input_validation

if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            connectivity_mat = f.read()


            ## Reading the node names
            connectivity_mat_row = connectivity_mat.strip().split("\n")
            Toponame=connectivity_mat_row[-1].strip().split(':')[1]
            Username=connectivity_mat_row[-2].strip().split(':')[1]
            nodes = connectivity_mat_row[0].strip().split()
            node_num = len(nodes)
            data={"TopoName":Toponame,"Username": Username, 'Details':[]}
            temp=[]
            for i in range(1,(node_num+1)):
                current_node = connectivity_mat_row[i].strip().split()
                Device=current_node[0]
                
                if 'R' in Device:
                    data2 = {'Device_name': Device, 'Device_type': 'Router', "Device_cpu": "4","Device_memory":"12","Image_type": "Quagga",'Connections':[]}
                if 'B' in Device:
                    data2 = {'Device_name': Device, 'Device_type': 'Switch', "Device_cpu": "4","Device_memory":"12","Image_type": "Quagga",'Connections':[]}
                if 'H' in Device:
                    data2 = {'Device_name': Device, 'Device_type': 'Host', "Device_cpu": "4","Device_memory":"12","Image_type": "Quagga",'Connections':[]}    
                Connections = []
                for j in range(1,(node_num+1)):
                        
                        if current_node[j] !="0":
                            
                            num=int(current_node[j])
                            Connection=nodes[j-1]
                            for x in range(0,num):
                                Connections.append({'Connected_to':Connection,'Link_type':"","Local_interface_name":"","Local_ip_address":"","Interface_mac":""})
                            
                                                                    
                            
                data2['Connections'] = Connections
                temp.append(data2)
            data['Details']=temp
            #print(json.dumps(data, indent=4))
            input_validation.init(data)

    else:
        print("File does not exist")

else:
    print("Invalid input format. "+"\n"+"Usage: save_config_matrix <<matrix-input-file>>")
