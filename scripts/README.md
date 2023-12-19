# File structure

1. `install.sh`: To add mitmproxyuser and store the necessary certificates in system's certificate-store
2. `enable.sh`: To update iptables rules to route all http and https traffic to port 8080 on mitmproxyuser
3. `disable.sh`: To remove iptables rules
4. `certs.sh`: To install the appropriate certificate into firefox and chromium's certificate-store (cert9.db)

Order in which these must be executed:
`install.sh > certs.sh > enable.sh > disable.sh`
