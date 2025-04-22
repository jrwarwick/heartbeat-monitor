#image check and/or build
(docker image ls heartbeatmon | grep heartbeatmon) || docker build -t heartbeatmon .

#env/config check
ls -1 heartbeat-monitor.*.env | grep -v '\.example\.'
#probably freak out and suggest creating an env file?

#container launch/reset
docker rm heartbeatmon 
docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db  \
	-e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" \
	--env-file heartbeat-monitor.test.env heartbeatmon

docker ps --last 3

##oneliner:   docker rm heartbeatmon ; docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db  -e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" --env-file heartbeat-monitor.test.env heartbeatmon

