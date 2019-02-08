import docker
import json
import sys

DOCKER_ID = 'swarnaragz'

DOCKER_PASS = raw_input("Enter docker password:")

REPO_NAME = 'swarnaragz/rnd_tool'
TAGS = ['rndtool-router', 'rndtool-host']
# Login to docker hub and pull images
dockerClient = docker.from_env()

try:
    res = dockerClient.login(DOCKER_ID, DOCKER_PASS)
except docker.errors.APIError as e:
    print(e)
    sys.exit(1)

if res['Status'] == 'Login Succeeded':
    for tag in TAGS:
        try:
            for line in dockerClient.pull(REPO_NAME, tag, stream=True):
                print(json.dumps(json.loads(line), indent=4))
        except docker.errors.APIError as e:
            print(e)
            sys.exit(1)
