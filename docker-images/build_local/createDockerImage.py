import subprocess
import os

ROUTER_IMAGE_NAME="rndtool-router"
HOST_IMAGE_NAME="rndtool-host"

def execute(cmd):
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    
def imageExists(imageName):
    cmd="sudo docker images -q {}".format(imageName)
    output=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = output.communicate()
    imageID=out.strip()
    return (imageID != "")

if not os.path.exists("router-dockerfile"):
    print("Router docker file is missing. Skipping..")
else:
    if imageExists(ROUTER_IMAGE_NAME):
        print("Docker image " + ROUTER_IMAGE_NAME + " already exists")
    else:
        print("Docker file for router found. Building image...")
        cmd = "sudo docker build -f router-dockerfile -t {} .".format(ROUTER_IMAGE_NAME)
        execute(cmd)

if not os.path.exists("host-dockerfile"):
    print("Host docker file is missing. Skipping..")
else:
    if imageExists(HOST_IMAGE_NAME):
        print("Docker image " + HOST_IMAGE_NAME + " already exists")
    else:
        print("Docker file for host found. Building image...")
        cmd = "sudo docker build -f host-dockerfile -t {} .".format(HOST_IMAGE_NAME)
        execute(cmd)

print("ALL DONE.")
