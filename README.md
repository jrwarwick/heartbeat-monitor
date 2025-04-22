# heartbeat-monitor
A figurative heartbeat monitor that alerts on "flatline" for periodic automated processes. Avoid chronic silent failures.

Inspired by some other clever projects. Scenario: cronjob has actually been failing for a while, but you didn't notice because you're busy and you sort of stopped checking the output logs.
This adds a little more "active" alert-on-exception, kind of like a heartbeat monitor in a hostpital where it gets your attention (with the flatline visual and sustained alert tone) upon *absence* of a signal. Another way to think of it: UptimeRobot/whatsup/etc., but for individual scheduled scripts/jobs/processes.

The way this works is the tail end of your job definition or script or whatever must invoke the heartbeat signal URI corresponding to it's particular monitoring registration. Failure to make a recent URI call (which is recorded) within time limit is what the monitor thread is looking for. Only then will it send out alerts, and only for those registrations that are overdue.

Hopefully putting this all into one single simple docker image so it is quick and easy to set up and throw away.

It seems like the only sensible thing to do is have an environment file for docker, but you could technically set everything via -e arguments on the docker run invocation.

Note this is not yet complete or fancy, and is not yet published to dockerhub or anything like that. One day, maybe. For now, you just have to clone this repo, perform the docker image build, then run your freshly built image.

# Quickstart

    git clone https://github.com/jrwarwick/heartbeat-monitor.git
    cd heartbeat-monitor
    sh launch.sh

# Examples 
first docker build:

    docker build -t heartbeatmon .

then docker launch:
 
	docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db --env-file heartbeat-monitor.test.env -e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" heartbeatmon

or maybe:

	docker run -it -p 5000:5000  --mount type=bind,source="$(pwd)"/db,target=/db  -e "SIGNAL_URI_BASE=http://$(hostname --fqdn):5000/" -e "NOTIFICATION_MESSAGE_PREFIX=Heartbeat flatlined!" -e "DEFAULT_NTFY_CHANNEL_NAME=foobar-ntfy-channelname" heartbeatmon

the checkin (where you replace the number "123" with the number of the corresponding heartbeat registration):
	curl http://dockerhost:5000/api/heartbeat/123

