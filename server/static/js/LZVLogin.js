function authenticate(form) {
	var url = baseURL + '/login';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			switch (this.status) {
				case 200:
					data = JSON.parse(xhttp.response) ;
					var sessionid = data.session_id;
					var username = data.username;
					setCookie("session_auth", sessionid);
					console.log("sessionid: " + sessionid);
					setCookie("session_user", username);
					console.log("session_user: " + username);
					window.location.reload(true); 
					break;
				case 401:
					$("#lzvFailedLogin").show();
					break;
				default:
					break;
			}
			
	}
	}
	var username = form.elements['username'].value;
	var password = form.elements['pwd'].value;
	if (username != '' && password != '') {
		xhttp.open('POST', url, false);
		xhttp.setRequestHeader("Content-type", "application/json");
		var payload = '{\"password\": \"' + password + '\", \"username\": \"' + username + '\"}';
		xhttp.send(payload);	
	}
}