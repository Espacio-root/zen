#!/bin/bash

directory="/home/espacio/projects/zen"

# Extract individual directories in the path
IFS='/' read -r -a directories <<< "$directory"

# Loop through the parent directories and set permissions
for ((i=1; i<${#directories[@]}; i++)); do
    parent_directory=$(IFS='/' ; echo "${directories[*]:0:i}")
    sudo chmod g+r "$parent_directory"
done
sudo chmod -R g+r "$directory"

