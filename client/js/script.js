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
var labFolderEntries = {
	entries: Array()
}

var labFolderProjects = {
	projects: Array()
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

$("#getProjects").click(function(){
	getProjects();
})

$("#labFolderSelectProject").click(function(){
	$("#labFolderSelectMDB").removeClass("selected");
	$("#labFolderSelectProject").addClass("selected");
})

$("#labFolderSelectMDB").click(function(){
	$("#labFolderSelectProject").removeClass("selected");
	$("#labFolderSelectMDB").addClass("selected");
})

/*
labFolderEntries.entries = new Array();
			for (i=0; i < parsedData.length; i++) {
				var obj = parsedData[i];
				var entry = {elements: Array(), title: obj['title'], entryID: obj['id']}
				for (j = 0; j < obj['elements'].length; j++) {
					var ele = obj['elements'][j];
					entry.elements.push(ele['id']);
				}
				labFolderEntries.entries.push(entry);				
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
	for (var j=0; j < labFolderEntries.entries.length; j++) {
		var entry = labFolderEntries.entries[j];
		console.log("entry:" + entry);
		for (i=0; i < ids.length; i++) {
			if (entry.entryID == ids[i]) {
				for (var k = 0 ; k < entry.elements.length; k++ ) {
					var element = {entryID: entry.entryID, entryTitle: entry.title, elementID: entry.elements[k].elementID, elementType: entry.elements[k].type};
					elements.push(element);	
				}
				
			}
		}
	}
	//elements contains the set of entryID, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
	console.log(elements);
	for(i=0; i < elements.length; i++) {
		console.log(elements[i].elementID + " " +   elements[i].type);
		downloadElement(elements[i].elementID, elements[i].type);
	}
}

function authenticate(form) {
	var url = baseURL + '/auth/login';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4 && this.status == 200) {
			data = JSON.parse(xhttp.response) ;
			if (!("error" in data))  {
				token = data.token;
				$("#labFolderFailedLogin").hide();
				$("#labfolderLoginform").hide();
				$("#labFolderLoginSuccesful").show();
				getProjects();
				//updateLabfolderSelectableProjects();
				getEntries();
				//updateLabfolderSelectableElements();
			}
			else
			{
				$("#labFolderFailedLogin").show();
			}
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
		console.log("readystatechangeProject");
		if(this.readyState == 4 && this.status == 200) {
			console.log("get project success");
			var parsedData = JSON.parse(xhttp.response);
			labFolderProjects.projects = new Array();
			console.log("parsedData: " + parsedData.length);
			for (i=0; i < parsedData.length; i++) {
				var obj = parsedData[i];
				var project = {
					title: obj['title'],
					id: obj['id'],
					ownerID: obj['owner_id'],
					groupID: obj['group_id'],
					folderID: obj['folder_id'],
					hidden: obj['hidden'],
					creationDate: obj['creation_date'],
					versionDate: obj['version_date']
				};
				labFolderProjects.projects.push(project);
			}
			updateLabfolderSelectableProjects();
		}
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
			labFolderEntries.entries = new Array();
			for (i=0; i < parsedData.length; i++) {
				var obj = parsedData[i];
				var entry = {
					elements: Array(),
					title: obj['title'],
					entryID: obj['id'],
					projectID: obj['project_id'],
					versionID: obj['version_id'],
					authorID: obj['author_id'],
					creationDate: obj['creation_date'],
					versionDate: obj['version_data'],
					entryNumber: obj['entry_number'],
					hidden: obj['hidden'],
					editable: obj['editable'],
				};
				for (j = 0; j < obj['elements'].length; j++) {
					var ele = obj['elements'][j];
					var element = {
						elementID: ele['id'],
						type: ele['type'],
						versionID: ele['version_id']
						};
					entry.elements.push(element);
				}
				labFolderEntries.entries.push(entry);				
			}
			updateLabfolderSelectableElements();
		}
	}
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", token);
	xhttp.send();	
}

function updateLabfolderSelectableProjects() {
	$("#labFolderProjectSelect").html("");
	var append = "";
	var displayProjectCount = 0;
	console.log("Projectcount:" + labFolderProjects.projects.length);
	for (i=0; i < labFolderProjects.projects.length; i++) {
		var obj = labFolderProjects.projects[i];
		if(obj.hidden == false) {
			displayProjectCount++;
			append += '<button class="btn btnEntrySelectionHeader btnEntrySelectionProject" id="' + obj.id + '" name="' + obj.id + '">'
			append += obj.title;
			append += "</button>"
		}
	}
	if (displayProjectCount > 0){
		$("#labFolderProjectSelect").html(append);
		$(".btnEntrySelectionProject").css("width", parseInt(100/displayProjectCount) + "%")
	}

}

function updateLabfolderSelectableElements() {
	$('form[id=selectableEntries]').empty();
	var append = '';
	console.log("Printing Element count: " + labFolderEntries.entries.length);
	for (i=0; i<labFolderEntries.entries.length; i++){
		var obj = labFolderEntries.entries[i];
		if (obj.hidden == false) {
			append += '<div class="entrySelect"><input type="checkbox" value="" name=' + obj.entryID + '>';
			append += obj.title;
			append += '</div><br>\n';
		}
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

		}
		if(this.status == 400) {
			alert("Fehler: Bitte ID mitgeben!");
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

