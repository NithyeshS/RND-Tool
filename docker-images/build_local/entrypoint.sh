#!/bin/bash

set -x

# Main Shell Script


echo "Restarting sshd service..."
service ssh restart
exec "$@"
  


