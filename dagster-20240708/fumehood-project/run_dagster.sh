#!/bin/bash
cd /home/adm1/dagster/fumehood-project/
sudo chmod 755 /run/screen
screen -dmS dagster-screen sudo -E dagster dev -p 3000