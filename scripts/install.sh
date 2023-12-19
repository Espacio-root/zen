sudo useradd --create-home mitmproxyuser
sudo -u mitmproxyuser -H bash -c 'nohup mitmdump &' # Generate certificates
sleep 2
sudo pkill -f mitmdump

sudo chmod -R 777 /home/mitmproxyuser/

sudo trust anchor /home/mitmproxyuser/.mitmproxy/mitmproxy-ca-cert.pem

echo "mitmproxyuser ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers
