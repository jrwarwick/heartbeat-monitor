<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Heartbeat Monitor - BottleOnDocker</title>
	<link rel="stylesheet" href="/static/milligram.css" />
	<script type="application/javascript" src="/static/mustache.js"></script>
	<script>
		function send_registration_delete_request(id) {
			console.log("DELETE attempt...");
			fetch("/api/registry/"+id, { method: 'DELETE' })
			    .then((res)=>{
				console.log("DELETE result: "+ res);
				alert(res.json());
				//window.location.href = '/'
			    });
		}
	</script>
</head>
<body>
	<h1>&hearts; Heartbeat Monitor Service</h1>
	<h2>Welcome to the simple pyBottle &quot;Heartbeat Monitor&quot;!</h2>
	<p>simple, lean bottle on python on docker service sorta like deadman's snitch</p>
	<p>{{!msg}} <a href="/" class="button">Add Registration</a></p>
	<div class="container">
		<div class="row">
		<div class="column-60">
			<table>
				<th>
					<td>Status</td>
					<td>Name</td>
					<td>Last Checkin</td>
					<td>Notify Address</td>
					<td>Period Length</td>
					<td>Blackouts</td>
					<td>DELETE BTN</td>
					<td>PAUSE/BLACKOUT BTN</td>
				</th>
			%for registry_line in registry_lines:
				<tr>
				%for col in registry_line:
					<td>{{col}}</td>
				%end
					<td><button class="button" onclick="send_registration_delete_request({{registry_line[0]}});">X </a></td>
					<td><a href="todo">||</a></td>
				</tr>
			%end
			</table>
		</div>
		</div>
		<div class="row">
			<ul><caption>views</caption>
				<li> <a href="/registry">Show Full Registry</a> </li>
				<li><a href="/service_status">Show Heartbeat Service Status</a></li>
			</ul>
		</div>
		<div class="row">
			<a href="/report">Show Overdue Registrations</a>
		</div>

		<div class="row">
			<ul><caption>api</caption>
				<li> <a href="/api/registry">Show Full Registry</a> </li>
				<li><a href="/api/service_status">Show Heartbeat Service Status</a></li>
			</ul>
		</div>
		<div class="row">
			<a href="/api/report">Show Overdue Registrations</a>
		</div>

	</div>

</body>
</html>
