import json
import input_validation
import sys, os

# Driver Program
# input.json : incorrect input
if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            data = f.read()
            data = json.loads(data)
            input_validation.init(data)

    else:
        print("File does not exist")
else:
    print("Invalid input format. "+"\n"+"Usage: save_config_json <<json-input-file>>")
