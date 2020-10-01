#!/bin/bash

# exit when any command fails
set -e

# create temp dir
DIR=`mktemp -d`
cd $DIR

# download gemalto .deb
wget https://www.luxtrust.lu/downloads/middleware/LuxTrust_Middleware_1.2.1_Ubuntu_64bit.tar.gz
tar -xzf LuxTrust_Middleware_1.2.1_Ubuntu_64bit.tar.gz

# download libssl 1.0.0 (ubuntu's 1.1.0 is not compatible)
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.0.0_1.0.2g-1ubuntu4.17_amd64.deb

# install
sudo apt install -y \
	./libssl1.0.0_1.0.2g-1ubuntu4.17_amd64.deb \
	./Gemalto_Middleware_Ubuntu_64bit_7.2.0-b04.deb

# cleanup
cd - > /dev/null
rm -rf $DIR

echo Installation completed succesfully