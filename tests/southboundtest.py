import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../src')
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../src/southbound')

from SouthBoundWrapper import SouthBoundWrapper

from commonEnums import ErrorCodes
from commonEnums import DeviceTypes
from commonEnums import LinkTypes

import logging
import json
import subprocess

def execute(cmd):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = output.communicate()
    logger.info(cmd)
    print(cmd)
    logger.info(out.strip())
    print(out.strip())

logger = logging.getLogger("SouthBoundTest")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("/var/log/southboundtest.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

failed=False
sbw = SouthBoundWrapper(logging.INFO)

sbw.topologyName = "SBTest"

retJSON=sbw.createManagementBridge("192.168.149.1/24")
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE MANAGEMENT BRIDGE ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE MANAGEMENT BRIDGE ----- FAIL")
    failed=True
    
router1Name = "SBTest-R1"
router2Name = "SBTest-R2"
router3Name = "SBTest-R3"
bridge1Name = "SBTest-BR1"


retJSON=sbw.createDevice(router1Name,DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- FAIL")
    failed=True

retJSON = sbw.createDevice(router2Name,DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- FAIL")
    failed=True

retJSON = sbw.createLink(router1Name, "r1r2-r1", DeviceTypes.TYPE_ROUTER, router2Name, "r2r1-r2", DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- FAIL")
    failed=True

retJSON=sbw.assignInterfaceIP(router1Name,"r1r2-r1","192.168.5.1/24")
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- FAIL")
    failed=True

retJSON=sbw.assignInterfaceIP(router2Name,"r2r1-r2","192.168.5.2/24")
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- FAIL")
    failed=True

retJSON = sbw.createDevice(router3Name,DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE CONTAINER ----- FAIL")
    failed=True

retJSON = sbw.createLink(router2Name,  "r2r3-r2", DeviceTypes.TYPE_ROUTER, router3Name, "r3r2-r3", DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- FAIL")
    failed=True

retJSON=sbw.deleteLink(router2Name, "r2r3-r2", DeviceTypes.TYPE_ROUTER, router3Name, "r3r2-r3", DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- FAIL")
    failed=True

retJSON=sbw.deleteDevice(router3Name,DeviceTypes.TYPE_ROUTER)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- FAIL")
    failed=True


retJSON=sbw.createDevice(bridge1Name,DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE BRIDGE ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE BRIDGE ----- FAIL")
    failed=True

retJSON=sbw.createLink(router1Name, "r1br1-r1", DeviceTypes.TYPE_ROUTER, bridge1Name, "br1r1-br1", DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- FAIL")
    failed=True

retJSON=sbw.createLink(router2Name, "r2br1-r2", DeviceTypes.TYPE_ROUTER, bridge1Name, "br1r2-br1", DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: CREATE LINK ----- FAIL")
    failed=True

retJSON=sbw.getBridgeID(bridge1Name)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: GET BRIDGE ID ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: GET BRIDGE ID ----- FAIL")
    failed=True

retJSON=sbw.assignInterfaceIP(router1Name,"r1br1-r1","192.168.10.1/24")
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- FAIL")
    failed=True

retJSON=sbw.assignInterfaceIP(router2Name,"r2br1-r2","192.168.10.2/24")
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: ASSIGN IP ----- FAIL")
    failed=True

retJSON=sbw.deleteLink(router2Name, "r2br1-r2", DeviceTypes.TYPE_ROUTER, bridge1Name, "br1r2-br1", DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- FAIL")
    print(json.dumps(retJSON))
    failed=True

retJSON=sbw.deleteLink(router1Name, "r1br1-r1", DeviceTypes.TYPE_ROUTER, bridge1Name, "br1r1-br1", DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE LINK ----- FAIL")
    print(json.dumps(retJSON))
    failed=True

retJSON=sbw.deleteDevice(bridge1Name,DeviceTypes.TYPE_BRIDGE)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE BRIDGE ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE BRIDGE ----- FAIL")
    failed=True

retJSON=sbw.deleteContainer(router1Name)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- FAIL")
    failed=True

retJSON=sbw.deleteContainer(router2Name)
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE CONTAINER ----- FAIL")
    failed=True

retJSON=sbw.deleteManagementBridge()
retJSON=json.loads(retJSON)
if retJSON['error'] == "NO_ERROR":
    logger.info("TEST: DELETE MANAGEMENT BRIDGE ----- PASS")
if retJSON['error'] != "NO_ERROR":
    logger.info("TEST: DELETE MANAGEMENT BRIDGE ----- FAIL")
    failed=True

if failed == True:
    print("TEST FAILED. CHECK LOG @ /var/log/southboundtest.log")
else:
    print("ALL TESTS SUCCEDDED")
