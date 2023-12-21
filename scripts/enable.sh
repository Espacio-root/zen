#!/bin/bash

dir="$(dirname "$(dirname "$(readlink -f "$0")")")"

sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
sysctl -w net.ipv4.conf.all.send_redirects=0

sudo iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner zenuser --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner zenuser --dport 443 -j REDIRECT --to-port 8080
sudo ip6tables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner zenuser --dport 80 -j REDIRECT --to-port 8080
sudo ip6tables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner zenuser --dport 443 -j REDIRECT --to-port 8080
sudo iptables -t nat -A OUTPUT -p udp -m owner ! --uid-owner zenuser --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A OUTPUT -p udp -m owner ! --uid-owner zenuser --dport 443 -j REDIRECT --to-port 8080
sudo ip6tables -t nat -A OUTPUT -p udp -m owner ! --uid-owner zenuser --dport 80 -j REDIRECT --to-port 8080
sudo ip6tables -t nat -A OUTPUT -p udp -m owner ! --uid-owner zenuser --dport 443 -j REDIRECT --to-port 8080

# Start mitmproxy
sudo -u zenuser -H bash -c "/usr/bin/mitmproxy -s $dir/zen/blocker.py --set args=\"-c coding\" --mode transparent --showhost --set block_global=false"
