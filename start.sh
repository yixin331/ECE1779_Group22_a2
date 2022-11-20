#! /bin/bash
pip install -r requirements.txt
mysql mysql --host=ece1779-a2.cedgw5dhsseo.us-east-1.rds.amazonaws.com --port=3306 --user=root --password=ece1779pass -e "source A_2/frontend/app/initializeDB.sql"

tmux new -d -s memcache "python3 A_2/autoscaler/run.py"
tmux new -d -s manager "python3 A_2/manager/run.py"


python3 A_2/frontend/run.py
pkill -f tmux
echo "Server ended!"