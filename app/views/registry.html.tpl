<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Heartbeat Monitor - BottleOnDocker</title>
	<link rel="stylesheet" href="/static/milligram.css" />
	<link rel="stylesheet" href="/static/heartbeat.css" />
	<script>
		function send_registration_delete_request(id) {
			console.log("DELETE attempt...");
			fetch("/api/registry/"+id, { method: 'DELETE' })
			    .then((res)=>{
				console.log("DELETE result: "+ res);
				let resultInfo = res.json();
				document.getElementById("msg").innerText = resultInfo;
				//could be neat to just grey-out or popoff that row, but we'd need to iterate through rows for that//document.getElementById
				//window.location.href = '/'
				var t = setTimeout(function(){ location.reload();},1200);
			    });
		}
	</script>
</head>
<body>
	<h1>&hearts; Heartbeat Monitor Service</h1>
	<h2>Welcome to the simple pyBottle &quot;Heartbeat Monitor&quot;!</h2>
	<p>simple, lean bottle on python on docker service sorta like deadman's snitch</p>
	<p><span id="msg">{{!msg}}</span> <a href="/registration" class="button">Add Registration</a></p>
	<div class="container">
		<div class="row">
		<div class="column-60">
			<table>
				<thead><tr>
					<th>Status</th>
					<th>Name</th>
					<th>Last Checkin</th>
					<th>Notify Address</th>
					<th>Period Length</th>
					<th>Blackouts</th>
					<th colspan="2">Control</th>
				</tr></thead>
				<tbody>
				%for registry_line in registry_lines:
					<tr>
					%for col in registry_line:
						<td>{{col}}</td>
					%end
						<td><button class="button" onclick="send_registration_delete_request({{registry_line[0]}});">X </a></td>
						<td><a href="todo">||</a></td>
					</tr>
				%end
				</tbody>
			</table>
		</div>
		</div>

		
		<%include('navindex.html.tpl')%>

	</div>
        <%include('footer.html.tpl')%>
</body>
</html>
