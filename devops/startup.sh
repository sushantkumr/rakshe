#!/bin/bash

# Anything that wasn't installed while creating the AMI goes here.
# We should probably move it to ami_setup the next time an AMI is created
# but things can be added here in the meantime.

# Do this while creating the AMI itself
# sudo add-apt-repository -y ppa:ethereum/ethereum
# sudo apt-get -y update
# sudo apt-get install -y software-properties-common ethereum

# Create ~/.ethereum and hand over ownership
sudo mkdir /home/ubuntu/.ethereum /home/ubuntu/.ethereum/keystore
sudo cp /var/www/rakshe/devops/UTC--2018-02-14T16-29-58.822045052Z--4de22441e9bdc4901235d9c2b83947c562114355 /home/ubuntu/.ethereum/keystore
sudo chown -R ubuntu:www-data /home/ubuntu/.ethereum/

sudo mkdir /var/log/geth
sudo chmod -R 0775 /var/log/geth
sudo chown -R ubuntu:www-data /var/log/geth

# If this doesn't work out try other options from:
# TODO: This has been daemonized (see the end of this file). Remove this section.
# https://ethereum.stackexchange.com/questions/366/how-can-i-run-go-ethereum-as-daemon-process-on-ubuntu
# https://stackoverflow.com/a/11856575
# nohup geth --dev --datadir /home/ubuntu/.ethereum --ipcpath "/home/ubuntu/geth.ipc" >> /var/log/geth/geth 2>&1 &

# Allow all authorized users to log into instances via SSH
cat /var/www/rakshe/devops/public_keys.txt >> /home/ubuntu/.ssh/authorized_keys

# Replace config with production config
sudo mv /var/www/rakshe/lib/core/production_config.py /var/www/rakshe/lib/core/config.py

sudo chown -R ubuntu:www-data /var/www/rakshe

cd /var/www/rakshe

virtualenv -p python3 /var/www/rakshe/venv
. /var/www/rakshe/venv/bin/activate

pip install -r /var/www/rakshe/devops/requirements-manual.txt

sudo chown -R ubuntu:www-data /var/www/rakshe

export ENV=PRODUCTION

sudo rm /etc/nginx/sites-enabled/default

sudo ln -s /var/www/rakshe/devops/nginx.conf /etc/nginx/conf.d
sudo mkdir -p /var/log/uwsgi
sudo chown ubuntu:www-data /var/log/uwsgi
sudo chmod g+w /var/log/uwsgi
sudo /etc/init.d/nginx start

sudo /etc/init.d/nginx restart

sudo mkdir -p /etc/uwsgi/vassals
sudo ln -s /var/www/rakshe/devops/uwsgi.ini /etc/uwsgi/vassals

sudo cp /var/www/rakshe/devops/systemd.service /etc/systemd/system
sudo systemctl enable systemd
sudo systemctl start systemd

sudo cp /var/www/rakshe/devops/geth-service.service /etc/systemd/system
sudo systemctl enable geth-service
sudo systemctl start geth-service
