#! /bin/bash
#pip install -r requirements.txt
mysql --user=root --password=ece1779pass  -e "source A_2/frontend/app/initializeDB.sql"

tmux new -d -s memcache "python3 A_2/memcache/run.py"
tmux new -d -s manager "python3 A_2/manager/run.py"


python3 A_2/frontend/run.py
pkill -f tmux
echo "Server ended!"