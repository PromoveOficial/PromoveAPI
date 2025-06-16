#!/bin/bash

sudo pacman -Syu httpd postgresql python python-pip
#git pull origin main

$PATH_SERVER_DIR=/etc/httpd/conf/extra

if [ ! -e "$PATH_SERVER_DIR/promove_api.conf" ]; then
    cp server/promove_api.conf $PATH_SERVER_DIR/promove_api.conf
fi

if [ ! diff -q "$PATH_SERVER_DIR/promove_api.conf" "/server/promove_api.conf" > /dev/null]
    cp server/promove_api.conf $PATH_SERVER_DIR/promove_api.conf
fi

sudo httpd -t
sudo systemctl reload httpd

sudo cp server/promove_api.service /etc/systemd/system/promove_api.service

sudo chmod 644 /etc/systemd/system/promove_api.service

sudo systemctl daemon-reload
sudo systemctl start promove_api.service

echo "Concluido"