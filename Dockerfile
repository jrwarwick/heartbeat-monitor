FROM ubuntu
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev python3
# This one is just for dev and troubleshooting. Comment out for "release builds"
## RUN apt-get install -y vim.tiny 
#lTODO noninteractive-ify installs that ask questions?
RUN apt-get install -y python3-bottle python3-requests

RUN  mkdir /db
#RUN /usr/bin/sqlite3 /db/heartbeat_monitor.db
RUN  sqlite3 /db/heartbeat_monitor.db
COPY db/initialize_db.sql  /tmp
#RUN cat /db/initialize_db.sql  |  sqlite3 /db/heartbeat_monitor.db
##TODO: I don't htink this is persistent during build... might just need to make it a prereq
RUN  cat /tmp/initialize_db.sql |  sqlite3 /db/heartbeat_monitor.db
COPY app/ /app/
RUN chmod 664 /app/*.py /app/*.sh
WORKDIR /app

CMD /bin/sh /app/launch.sh
#CMD cat /tmp/initialize_db.sql |  sqlite3 /db/heartbeat_monitor.db ; python3 heartbeat_server.py 

#You will almost certainly want to persist the db file inside some host OS folder.
#Maybe /home/databases or /var/somethingorother or /usr/local/share/docker/whatever /var/lib/things .
#if you don't have deep knowledge or preference, then just keep it simple: 
#a few files in subfolders right under this here package alongside the Dockerfile.
#something sort of like:  docker run -it -v /home/username/db/:/db imagename
#There will be a full, copy-n-pasteable docker invocation line at the end of this file
#that will include this idea.

#If you want to build it from "source":
#docker build -t heartbeatmon .
#If you want to fiddle around inside the container, mabye sqlite client direct access, for instance:
#docker run -it heartbeatmon bash
#docker run -it -v $(pwd)/db/:/db heartbeatmon bash
##TODO: does that still get the main thread online? or is that "instead of"?


#FROM jitesoft/sqlite
#docker run -v $pwd:/tmp --rm jitesoft/sqlite:latest /tmp/test.db "create table tbl1(one varchar(10), two smallint)"


#And now the fully functional, copy-and-pasteable invocation line to get you launched:
#  docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db  -e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" heartbeatmon
# docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db  -e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" -e "NOTIFICATION_MESSAGE_PREFIX=Heartbeat flatlined!" heartbeatmon

#need env var for MS_TEAMS_WEBHOOK_URI
