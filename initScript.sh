#!/bin/bash

echo "###################################################"
echo "             INSTALLING PREREQUISTES...            "
echo "###################################################"
echo ""
echo ""
sudo apt update
sudo apt -y install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt  update
sudo apt -y install ansible
sudo apt -y install python-pexpect
sudo apt -y install python-pip
sudo apt -y install openvswitch-switch
sudo pip install --upgrade pip
sudo apt -y install docker.io
sudo pip install docker-py


echo ""
echo ""
echo "###################################################"
echo "               INITIALZING RND TOOL                "
echo "###################################################"
echo ""
echo ""


# Create etc and var folder

ETC_DIR="/etc/RNDTool"
VAR_DIR="/var/RNDTool"

if [ ! -d "$ETC_DIR" ]; then
  sudo mkdir "$ETC_DIR"
fi

if [ ! -d "$VAR_DIR" ]; then
  sudo mkdir "$VAR_DIR"
fi

# Setup SSH key management for passwordless login
SSH_KEY_DIR="/var/RNDTool/ssh"
SSH_KEY_FILE_NAME="/var/RNDTool/ssh/keyfile"

if [ ! -d "$SSH_KEY_DIR" ]; then
  sudo mkdir "$SSH_KEY_DIR"
fi

if [ ! -f "$SSH_KEY_FILE_NAME" ]; then
  sudo ssh-keygen -t rsa -b 4096 -P '' -f "$SSH_KEY_FILE_NAME"
  sudo cp "$SSH_KEY_FILE_NAME".pub "$SSH_KEY_DIR"/authorized_keys
  echo "$USER"
  sudo chown "$USER" "$SSH_KEY_FILE_NAME"
  echo alias rndconnect=\"'ssh -i '$SSH_KEY_FILE_NAME\" >> /home/$USER/.bashrc
fi

echo ""
echo ""
echo "###################################################"
echo "             SETTING UP DOCKER IMAGES              "
echo "###################################################"
echo ""
echo ""
sudo python docker-images/pull_docker_hub/pullDockerImages.py
sudo python src/northbound/create_command_alias.py $USER
