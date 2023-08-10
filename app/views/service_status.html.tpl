<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Heartbeat Monitor - BottleOnDocker</title>
	<link rel="stylesheet" href="/static/milligram.css" />
	<link rel="stylesheet" href="/static/heartbeat.css" />
	<script>
		var t = setTimeout(function(){ location.reload();},12000);
	</script>
</head>
<body>
	<h1>&hearts; Heartbeat Monitor Service</h1>
	<h2>Welcome to the simple pyBottle &quot;Heartbeat Monitor&quot;!</h2>
	<p>A simple, lean bottle on python on docker service meant to provide some protection against silent failure in cronjobs. Whether job fails silently or schedule is wrong or server time is wrong, whatever it is, if the job does *not* execute or doesn't check-in at the end, the hearbeat will automatically enter a "flatline" condition, and you can get actively notified abou that.</p>
	<p><span id="msg">{{!msg}}</span> <a href="/registration" class="button">Add Registration</a></p>
	<div class="container">
		<div class="row">
		<div id="status">...</div>
		<!--div class="column-60">
			<table>
				<th>
					<td>Status</td>
					<td>Name</td>
					<td>Last Checkin</td>
					<td>Notify Address</td>
					<td>Period Length</td>
					<td>Blackouts</td>
					<td colspan="2">Control</td>
				</th>
			x%x for registry_line in registry_lines:
				<tr>
				x%x  for col in registry_line:
					<td>{col}}</td>
				x%x  end
					<td><button class="button" onclick="send_registration_delete_request({registry_line[0]}});">X </a></td>
					<td><a href="todo">||</a></td>
				</tr>
			x%x end
			</table>
		</div-->
		</div>

		<%include('navindex.html.tpl')%>

	</div>
	<script>

	fetch("/api/service_status")
	  .then(function(response) {
	    // handle the response
		doculment.getElementById("ststus").innerText = response.text();
	  })
	  .catch(function() {
	    // handle the error
		console.error("uh oh, status???");
	  });
	</script>

	<%include('footer.html.tpl')%>
</body>
</html>
