#!/bin/bash

#git pull origin main
sudo cp server/promove_api.conf /etc/httpd/conf/extra/promove_api.conf
sudo httpd -t
sudo systemctl reload httpd

sudo cp server/promove_api.service /etc/systemd/system/promove_api.service

sudo chmod 644 /etc/systemd/system/promove_api.service

sudo systemctl daemon-reload
sudo systemctl start promove_api.service

echo "Concluido"