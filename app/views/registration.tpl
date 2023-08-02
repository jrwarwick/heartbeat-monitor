<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Heartbeat Monitor - BottleOnDocker</title>
        <link rel="stylesheet" href="/static/milligram.css" />
        <link rel="stylesheet" href="/static/heartbeat.css" />
</head>
<body>
	<h1>&hearts; Heartbeat Monitor Service</h1>
	<h2>Welcome to the simple pyBottle &quot;Heartbeat Monitor&quot;!</h2>
	<p>simple, lean bottle on python on docker service sorta like deadman's snitch</p>
	<p>{{!msg}}</p>
	<div class="container">
		<div class="row">
		<div class="column-60">
			<form action="/api/registry" method="post">
			<fieldset>
				<label>Name:
					<input id="name" name="name" type="text" placeholder="suggested name format: environment.hostname.jobtaskscript"/>
				</label>
				<label>Period:
					<input id="period" name="period" type="number" placeholder="integer quantity of minutes before heartbeat is overdue"/>
				</label>
				<div class="float-right">
					<a href="javascript:document.getElementById('period').value=60;" class="button button-outline float-right">Hourly</a>
					<a href="javascript:document.getElementById('period').value=24*60;" class="button button-outline float-right">Daily</a>
					<a href="javascript:document.getElementById('period').value=24*60*7;" class="button button-outline float-right">Weekly</a>
				</div>
				<label>Notification Address:
					<input id="notification_address" name="notification_address" type="text" placeholder="for now, just email address"/>
				</label>
				<label>Escalated Notification Address:
					<input id="notification_address_escalated" name="notification_address_escalated" type="text" />
				</label>
				<button type="submit">Register</button>
			</fieldset>
			</form>
		</div>
		</div>

		<div class="row">
			<ul><caption>views</caption>
				<li> <a href="/registry">Show Full Registry</a> </li>
				<li><a href="/service_status">Show Heartbeat Service Status</a></li>
				<li><a href="/report">Show Overdue Registrations</a></li>
			</ul>
		</div>

		<div class="row">
			<ul><caption>api</caption>
				<li> <a href="/api/registry">Show Full Registry</a> </li>
				<li><a href="/api/service_status">Show Heartbeat Service Status</a></li>
				<li><a href="/api/report">Show Overdue Registrations</a></li>
			</ul>
		</div>

		<div class="row">
			<pre><code id="utilization_hint">
	curl http://hostname.foo.tld:5000/api/heartbeat/4
	Invoke-RestMethod -Uri http://hostname.foo.tld:5000/api/heartbeat/4
			</code></pre>
		</div>
	</div>
	<script>//==Wire-up for client-side==//
		document.getElementById("name").onblur = function(){ 
			console.log('x'); 
			document.getElementById("utilization_hint").innerText += "\n\n" + location.origin + '/api/heartbeat/' + document.getElementById("name").value;
		}
	</script>
	<%include('footer.tpl')%>
</body>
</html>
