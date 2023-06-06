CONTAINER_ALREADY_STARTED="/db/CONTAINER_ALREADY_STARTED_FLAGFILE"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
	date >> $CONTAINER_ALREADY_STARTED
	echo "-- First container startup --"
	# YOUR_JUST_ONCE_LOGIC_HERE
	cat /tmp/initialize_db.sql |  sqlite3 /db/heartbeat_monitor.db 
else
    echo "-- Not first container startup --"
fi

# Always run first time or otherwise:
cd /app
#python3 -m pdb ./heartbeat_server.py 
python3 ./heartbeat_server.py 

