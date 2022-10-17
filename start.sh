#! /bin/bash
#pip install -r requirements.txt
mysql --user=root --password=ece1779pass  -e "source A_1/frontend/app/initializeDB.sql"

tmux new -d -s memcache "python3 A_1/memcache/run.py"

python3 A_1/frontend/run.py
pkill -f tmux
echo "Server ended!"


