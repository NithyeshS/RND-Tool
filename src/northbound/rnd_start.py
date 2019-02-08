###################################################
#                                                 #
#           RND-TOOL                              #
#                                                 #
#       rnd_start.py                              #
#       Usage: rnd_start.py <input_json>          #
#                                                 #
###################################################

import sys,os
import subprocess
import shlex
import time
import glob
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../logiclayer')
from rnd_create_topo import rnd_create_start
from rnd_delete_topo import rnd_delete_start
from rnd_update_topo import rnd_update_start
from rnd_read_topo import rnd_read_start
from utilities import alias_create
from utilities import alias_delete


def main():
    if (len(sys.argv) != 3):
        print("Invalid Input format. \n Usage: run_config <option:1-create/2-update/3-delete/4-read/others-nothing-exit> <topology-name> ")
        sys.exit(0)

    option = int(sys.argv[1])

    if option > 4 or option < 1:
        print("Invalid Options. \n Usage: run_config <option:1-create/2-update/3-delete/4-read/others-nothing-exit> <topology-name> ")
        sys.exit(0)

    ip = "/etc/RNDTool/" + sys.argv[2] + ".json"

    if os.path.exists(ip):
        #print("Topology exists")
	print("Rnd-tool started at " + str(time.time()))
    else:
        print("Topology does not exist. Please provide an existing topology name")
        sys.exit(0)

    if option == 1:
        rnd_create_start(sys.argv[2])
        print("Called create")
        # Create aliases in /etc/hosts
        alias_create(sys.argv[2])

    if option == 2:
        rnd_update_start(sys.argv[2])
        print("Called update")
        alias_delete(sys.argv[2])
        alias_create(sys.argv[2])

    if option == 3:
        rnd_delete_start(sys.argv[2])
        print("Called delete")
        alias_delete(sys.argv[2])

    if option == 4:
        rnd_read_start(sys.argv[2])
        print("Called Read")

    sys.exit(0)


if __name__ == '__main__':
    main()

