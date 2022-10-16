#! /bin/bash
#pip install -r requirements.txt
mysql --user=root --password=ece1779pass  -e "source frontend/app/initializeDB.sql"
pkill -f tmux

tmux new -d -s memcache "python3 memcache/run.py"

#tmux new -d -s frontend "python3 frontend/run.py"
python3 frontend/run.py
echo "Server ended!"


