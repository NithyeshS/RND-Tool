
import sys
import os

from os.path import expanduser
#home = expanduser("~")

filename='/home/' + sys.argv[1] + '/.bashrc'
cmds = []
cmds.append("alias save_config_json=\'sudo python3 src/northbound/json_input.py\'"+"\n")
cmds.append("alias save_config_matrix=\'sudo python3 src/northbound/matrix2json.py\'"+"\n")
cmds.append("alias run_config=\'sudo python src/northbound/rnd_start.py\'"+"\n")
cmds.append("alias get_config='sudo python src/logiclayer/rnd_get_config.py\'"+"\n")
cmds.append("alias packet_capture=\'sudo python src/northbound/packet_capture.py\'"+"\n")
for i in cmds:
	with open(filename, 'a+') as f:
		f.write(i)

