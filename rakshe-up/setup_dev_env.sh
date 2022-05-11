#!/usr/bin/env bash

# There's no need for this here
# apt-get update

sudo apt-get install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum

# This runs `apt-get update` as well
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y --allow-unauthenticated nodejs python3-pip mypy build-essential libmysqlclient-dev ethereum

# There is no `python` in Ubuntu 17.10. Point `python` to `python3`
ln -sfn /usr/bin/python3 /usr/bin/python

pip3 install -r /home/vagrant/code/rakshe/devops/requirements-manual.txt

# Create ~/.ethereum and hand over ownership
mkdir /home/vagrant/.ethereum /home/vagrant/.ethereum/keystore
cp /home/vagrant/code/rakshe/devops/UTC--2018-02-14T16-29-58.822045052Z--4de22441e9bdc4901235d9c2b83947c562114355 /home/vagrant/.ethereum/keystore
chown vagrant -R /home/vagrant/.ethereum/
sudo chown vagrant:vagrant  -R /home/ubuntu

# Run geth using the following command
# geth --dev --datadir /home/vagrant/.ethereum --ipcpath "/tmp/geth.ipc"

# Add aliases here
touch /home/vagrant/.bash_aliases

echo '
alias z="pushd ~/code/rakshe"
alias x="python /home/vagrant/code/rakshe/server.py"
alias g="geth --dev --datadir /home/vagrant/.ethereum --ipcpath \"/home/ubuntu/geth.ipc\""
' >> /home/vagrant/.bash_aliases


# ******************************************************************* #
# NVM is not required, we're installing it directly.
# # install latest nvm
# git clone https://github.com/creationix/nvm.git /home/vagrant/.nvm && cd /home/vagrant/.nvm && git checkout `git describe --abbrev=0 --tags`
# source /home/vagrant/.nvm/nvm.sh
# echo "source /home/vagrant/.nvm/nvm.sh" >> /home/vagrant/.bashrc

# # Ensure that the command nvm is available
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# # # Install node 6
# nvm install 6
# ******************************************************************* #
