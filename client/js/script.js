var baseURL = "http://localhost:5000";
var token = "";
var DEBUGlogin = "robert.guenther@uni-bayreuth.de";
var DEBUGpassword = "krQ3C3LTjIXFmwcpmEaM";

if (window.XMLHttpRequest) {
    // code for modern browsers
    var xhttp = new XMLHttpRequest();
 } else {
    // code for old IE browsers
    var xhttp = new ActiveXObject("Microsoft.XMLHTTP");
} 

//contains the entries of the loged in user from labfolder
var userObjects = {
	entries: Array()
}

$("#logoutButton").click(function(){
	logout();
})
$("#getEntries").click(function(){
	getEntries();
	
})

$("#download").click(function(){
	download();

})

/*
userObjects.entries = new Array();
			for (i=0; i < parsedData.length; i++) {
				var obj = parsedData[i];
				var entry = {elements: Array(), title: obj['title'], entryID: obj['id']}
				for (j = 0; j < obj['elements'].length; j++) {
					var ele = obj['elements'][j];
					entry.elements.push(ele['id']);
				}
				userObjects.entries.push(entry);				
			}
			*/
function download() {
	//first get ids to download, then do that
	var ids = new Array(); //ids for entry which will be downloaded
	var form = $('form[id=selectableEntries]')[0];
	for (i = 0; i < form.elements.length; i++) {
		if(form.elements[i].checked){
			ids.push(form.elements[i].name);
		}
	}
	var elements = new Array(); //these are to single elements to be downloaded later
	for (var j=0; j < userObjects.entries.length; j++) {
		var entry = userObjects.entries[j];
		console.log("entry:" + entry);
		for (i=0; i < ids.length; i++) {
			if (entry.entryID == ids[i]) {
				for (var k = 0 ; k < entry.elements.length; k++ ) {
					var element = {entryID: entry.entryID, entryTitle: entry.title, elementID: entry.elements[k].elementID, elementType: entry.elements[k].elementType};
					elements.push(element);	
				}
				
			}
		}
	}
	//elements contains the set of entryID, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
	console.log(elements);
	for(i=0; i < elements.length; i++) {
		console.log(elements[i].elementID + " " +   elements[i].elementType);
		downloadElement(elements[i].elementID, elements[i].elementType);
	}
}

function authenticate(form) {
	var url = baseURL + '/auth/login';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			document.getElementById("zusatzText").textContent = xhttp.response;
			data = JSON.parse(xhttp.response) ;
			if (!("error" in data))  {
				token = data.token;
				$("#labFolderFailedLogin").hide();
				$("#labfolderLoginform").hide();
				$("#labFolderLoginSuccesful").show();
				getEntries();
			}
			else
			{
				console.log("test2");
				$("#labFolderFailedLogin").show();
			}
			return;
			}

	}
	var username = form.elements['username'].value;//DEBUGlogin;//document.getElementById("loginLabFolderUsername").value;
	var password = form.elements['pwd'].value;;//DEBUGpassword;//document.getElementById("loginLabFolderPassword").value;
	if (username != '' && password != '') {
		xhttp.open('POST', url, true);
		xhttp.setRequestHeader("Content-type", "application/json");
		var payload = '{\"password\": \"' + password + '\", \"user\": \"' + username + '\"}';
		xhttp.send(payload);	
	}
}

function logout() {
	if (token != '') { 
	var url = baseURL + '/auth/logout';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			document.getElementById("zusatzText").textContent = xhttp.response;
			$('form[id=selectableEntries]').empty();
			$("#labfolderLoginform").show();
			$("#labFolderLoginSuccesful").hide();
		}
		return;
	}
	xhttp.open('POST', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", token);
	xhttp.send();
	}
	else
	{
		alert("Not Logged in!");
	}
}


function getProjects() {
	var url = baseURL + '/projects';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			document.getElementById("zusatzText3").textContent = xhttp.response;
		}
		return;
	}
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", token);
	xhttp.send();	
}

function getEntries() {
	var url = baseURL + '/entries';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			var parsedData = JSON.parse(xhttp.response);
			var ids = new Array();
			userObjects.entries = new Array();
			for (i=0; i < parsedData.length; i++) {
				var obj = parsedData[i];
				var entry = {elements: Array(), title: obj['title'], entryID: obj['id']}
				for (j = 0; j < obj['elements'].length; j++) {
					var ele = obj['elements'][j];
					var element = {elementID: ele['id'], elementType: ele['type']}
					entry.elements.push(element);
				}
				userObjects.entries.push(entry);				
			}
			updatePageWithEntries();
			return;
			//document.getElementById("zusatzText4").textContent = ids;
		}
	}
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", token);
	xhttp.send();	
}

function updatePageWithEntries() {
	$('form[id=selectableEntries]').empty();
	var append = '';
	for (i=0; i<userObjects.entries.length; i++){
		var obj = userObjects.entries[i];
		append += '<div class="entrySelect"><input type="checkbox" value="" name=' + obj.entryID + '>';
		append += obj.title;
		append += '</div><br>\n';
	}

	$(append).appendTo('#selectableEntries');

}

function downloadElement(id, type) {
	var url = baseURL;
	switch(type) {
		case 'IMAGE':
			console.log("Image");	
			url = baseURL + '/elements/file';
			break;
		case 'TABLE':
			console.log("Table");	
			url = baseURL + '/elements/table';		
			break;
		case 'TEXT':
			console.log("Text");	
			url = baseURL + '/elements/text';
			break;
		default:
			console.log("Error returning");
			return;
	}
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			var answer = xhttp.response;

			console.log("Answer:" +  answer);
			return;

		}
		if(this.status == 400) {
			alert("Fehler: Bitte ID mitgeben!");
			return;
		}

	}
	url = url + "?id=" + id;
	//add random element to url to prevent caching
	url = url + "&rnd=" + new Date().getTime();
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", token);
	xhttp.send();	
}


// function downloadFile(id) {
// 	var url = baseURL + '/elements/file';
// 	xhttp.onreadystatechange  = function(e) {
// 		if(this.readyState == 4 && this.status == 200) {
// 			var answer = xhttp.response;

// 			console.log("Answer:" +  answer);

// 		}
// 		if(this.status == 400) {
// 			alert("Fehler: Bitte ID mitgeben!");
// 		}

// 	}
// 	url = url + "?id=" + id;
// 	xhttp.open('GET', url, true);
// 	xhttp.setRequestHeader("Content-type", "application/json");
// 	xhttp.setRequestHeader("Authorization", token);
// 	xhttp.send();	
// }

// function downloadTable(id) {
// 	var url = baseURL + '/elements/table';
// 	xhttp.onreadystatechange  = function(e) {
// 		if(this.readyState == 4 && this.status == 200) {
// 			var answer = xhttp.response;

// 			console.log("Answer:" +  answer);

// 		}
// 		if(this.status == 400) {
// 			alert("Fehler: Bitte ID mitgeben!");
// 		}

// 	}
// 	url = url + "?id=" + id;
// 	xhttp.open('GET', url, true);
// 	xhttp.setRequestHeader("Content-type", "application/json");
// 	xhttp.setRequestHeader("Authorization", token);
// 	xhttp.send();	
// }

