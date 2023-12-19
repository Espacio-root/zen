#!/bin/bash

directory="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Extract individual directories in the path
IFS='/' read -r -a directories <<< "$directory"

# Loop through the parent directories and set permissions
for ((i=2; i<${#directories[@]}; i++)); do
    parent_directory=$(IFS='/' ; echo "${directories[*]:0:i}")
    sudo chmod g+r "$parent_directory"
done
sudo chmod -R g+r "$directory"

sudo groupadd zenmode
sudo chown $USER:zenmode $HOME

sudo useradd --create-home zenuser
sudo chown zenuser:zenmode /home/zenuser
sudo gpasswd -a $USER zenmode
sudo gpasswd -a zenuser zenmode

sudo -u zenuser -H bash -c 'nohup mitmdump &' # Generate certificates
sleep 2
sudo pkill -f mitmdump

sudo chmod -R 777 /home/zenuser/

sudo trust anchor /home/zenuser/.mitmproxy/mitmproxy-ca-cert.pem

# echo "mitmproxyuser ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers
