#!/bin/bash

# This script will be run once at the time of creating an AMI, probably manually.
# If you want something to be run each time an instance is booted this is NOT the right place to put it in.
# Eg: git clone, npm install, pip install etc do not belong here.

add-apt-repository ppa:nginx/stable -y
add-apt-repository -y ppa:ethereum/ethereum
apt-get -y update
apt-get install -y --allow-unauthenticated python3-pip python3-dev nginx libpcre3 libpcre3-dev python-virtualenv build-essential libffi-dev libssl-dev autoconf mysql-client-core-5.7 libmysqlclient-dev software-properties-common ethereum

# Create script that has to be run on startup

# Writing into file from command line: https://unix.stackexchange.com/a/44143

cat > /home/ubuntu/rakshe_startup_script.sh << EOF
#!/bin/bash
git clone https://rohithpr:B4mYr__g5bw__CdF6Gj3@bitbucket.org/rakshe/rakshe.git /var/www/rakshe
sh /var/www/rakshe/devops/startup.sh
EOF

chmod 0744 /home/ubuntu/rakshe_startup_script.sh

# Setup systemd startup task

cat > /etc/systemd/system/rakshe-boot.service << EOF
[Unit]
Description=Runs script on system boot.

[Service]
ExecStart=/home/ubuntu/rakshe_startup_script.sh

[Install]
WantedBy=multi-user.target
EOF

chmod 0644 /etc/systemd/system/rakshe-boot.service

systemctl enable rakshe-boot.service
