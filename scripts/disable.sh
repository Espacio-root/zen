#!/bin/bash

function proxy_off(){
    unset http_proxy https_proxy ftp_proxy rsync_proxy \
          HTTP_PROXY HTTPS_PROXY FTP_PROXY RSYNC_PROXY
    echo -e "Proxy environment variable removed."
}
proxy_off

sudo iptables -t nat -F
sudo ip6tables -t nat -F
