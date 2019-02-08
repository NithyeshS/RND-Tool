import json
import sys
import os

option = sys.argv[1]
#username = sys.argv[2]
toponame = sys.argv[2]

filename="/var/RNDTool/"+toponame+"-"+option+"Details.json"
print(filename)
if os.path.isfile(filename) and os.path.getsize(filename) > 0:
	with open(filename,"r") as fi:
		data = fi.read()
		print(data)
else:
	print("No such topology exists")
