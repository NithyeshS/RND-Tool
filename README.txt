--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
-				 RND-Tool   				       -
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

				INITIAL SETUP
--------------------------------------------------------------------------------

sudo apt update

sudo apt install git

git clone https://github.ncsu.edu/nsankar2/RND-Tool.git

cd RND-Tool

./initScript.sh

source /home/$USER/.bashrc


			 	RUN THE CODE
--------------------------------------------------------------------------------

cd RND-Tool

Validate and save topology info - JSON INPUT
	
	save_config_json <<input-json-file-path>>
	

Validate and save topology info - MATRIX INPUT

	save_config_matrix <<input-matrix-file-path>>


Deploy, delete and get information about topology

	run_config <<OPTION>> <<topology-name>>

	OPTION:

	1 -	Create topology. Should save topology information prior to this step.
	2 -	Update existing topology. Should create topology prior to this step.
	3 -	Delete existing topology. Should create topology prior to this step.
	4 -	Read info about topology. Should create topology prior to this step.
	
Get L1/L2/L3 Topology Details:

	get_config <<L1/L2/L3>> <<topology-name>>

Capture packets inside containers
	
	OPTION:
	1-	Pass input as execution time
	2-	Pass input as number of packets to be captured
	3-	Pass input as size of packet  
	packet_capture <<Topology-name>> <<Device-name>> <<interface-name>> <<options>> <<input>>


				TOPOLOGY INFO
--------------------------------------------------------------------------------

Topology related information can be found at /var/RNDTool/ directory. 

Packet captures will be available in /var/log/rndtool/capture-data directory.

Files related to a topology will have the topology name as part of the file name.


			      DEBUGGING/LOG FILES
--------------------------------------------------------------------------------

Log files for southbound APIs can be found in /var/log/rndTool.log

Topology related files can be found in
	Current topology - /var/RNDTool/<topology-name>.json
	Desired topology - /etc/RNDTool/<topology-name>.json


				SOUTHBOUND API DOCS
--------------------------------------------------------------------------------

Refer docs/SouthBoundWrapper.html


				       TESTS
--------------------------------------------------------------------------------

SouthBound - TO TEST AND MANUALLY VERIFY SOUTHBOUND APIs

    cd RND-Tool
    sudo python tests/southboundtest.py

Test log file will be generated in /var/log/southboundtest.log

Application log file will be generated in /var/log/rndTool.log
