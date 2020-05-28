// var baseURL = 'http://localhost:5000';
// var labFolderToken = '';
// var DEBUGlogin = 'robert.guenther@uni-bayreuth.de';
// var DEBUGpassword = 'krQ3C3LTjIXFmwcpmEaM';

// if (window.XMLHttpRequest) {
//     // code for modern browsers
//     var xhttp = new XMLHttpRequest();
// } else {
//     // code for old IE browsers
//     var xhttp = new ActiveXObject('Microsoft.XMLHTTP');
// } 

//Initialization Function
$( document ).ready(function() {
	var ct = getCookie('labFolderToken');
	if (ct != '') {
		$("#labFolderDownloadButton").show();
		labFolderToken = ct;
		updateContentAfterLogin();
	}
});


var xhttpMutexLocked = false; 

//contains the entries of the loged in user from labfolder, these are stored in cookies with same name
var labFolderEntries = {
	entries: Array()
}

var labFolderProjects = {
	projects: Array()
}

var labFolderMDB = {
	categories: Array()
}

var labFolderStorageFile; //storage file on server, will be filled with json object containing the files already available on server



$("#logoutButton").click(function(){
	logout();
})
$("#getEntries").click(function(){
	getEntries();	
})

$("#downloadSelectedElements").click(function(){
	downloadSelectedElements();
})

$("#downloadMDB").click(function(){
	downloadMDB();
})

// $("#getMDBdatabases").click(function(){
// 	getCategories();
// })

// $("#getMDBcats").click(function(){
// 	getMDBCategory();
// })

$("#getProjects").click(function(){
	getProjects();
})

function clearLocalStorage() {
	labFolderEntries.entries = Array();
	labFolderProjects.projects = Array();
	labFolderMDB.categories = Array();
	labFolderStorageFile = {};
	updateLabfolderSelectableProjects();
	updateProjectMaterialSelection();
}
function clearCookies() {
	setCookie("labFolderToken", "");
	setLocalStorage("labFolderProjects", "");
	setLocalStorage("labFolderEntries", "");
	setLocalStorage("labFolderStorageFile", "");
	setLocalStorage("labFolderMDB", "");
}

function downloadSelectedElements() {
	if($("#labFolderSelectProject").hasClass("selected")) {
		downloadSelectedEntries();
		getStorageFile();
		updateLabfolderSelectableElements();
	}
	if($("#labFolderSelectMDB").hasClass("selected")) {
		downloadSelectedMDBCategories();
	}
} 


$("#selectAllElements").click(function(){
	var childrenDiv = $('form[id=selectableEntries]').children();
	for (var i = 0; i < childrenDiv.length; i++) {
		var children = childrenDiv[i].children;
		for (var j = 0; j < children.length; j++) {
			if (children[j].type == 'checkbox'){
				children[j].checked = true;
			}
		}
	}

})

$("#deSelectAllElements").click(function(){
	var childrenDiv = $('form[id=selectableEntries]').children();
	for (var i = 0; i < childrenDiv.length; i++) {
		var children = childrenDiv[i].children;
		for (var j = 0; j < children.length; j++) {
			if (children[j].type == 'checkbox'){
				children[j].checked = false;
			}
		}
	}

})

$("#updateContent").click(function(){
	setLocalStorage("labFolderProjects", "");
	setLocalStorage("labFolderEntries", "");
	setLocalStorage("labFolderMDB", "");
	setLocalStorage("labFolderStorageFile", "");
	updateContentAfterLogin();
})

//switch between (currently) Project and MaterialDB to select. Updates Projects and Materials to display
function updateSelectionProjectMDB(clicked) {
	if($(clicked).hasClass("selected")) { return;}
	$(clicked).siblings().removeClass("selected");
	$(clicked).addClass("selected");
	displayProjectID = "";
	if($(clicked).hasClass("labFolderProject")) {
		updateLabfolderSelectableProjects();
		updateLabfolderSelectableElements();
	}
	if($(clicked).hasClass("labFolderMDB")) {
		// updateLabfolderSelectableDatabases();
		updateLabfolderSelectableCategories();
	}
}

function toggleDisplayVersions(clicked) {
	$(clicked).parent().parent().parent().parent().children(".versionList").children().toggle();
	if($(clicked).children(".arrow").html() == "v") {
		$(clicked).children(".arrow").text("x");
	}
	else {
		$(clicked).children(".arrow").text("v");
	}
}
function downloadVersion(clicked) {
	window.open($(clicked).attr('id'));
}
//this var contains the current project ID which is used to filter the elements to display
var displayProjectID = "";

//being called when another Project is clicked in the selection screen. Updates the globald project ID and calls update function
function updateSelectedProject(clicked) {
	if($(clicked).hasClass("selected")) { return;}
	$(clicked).siblings().removeClass("selected");
	$(clicked).addClass("selected");
	displayProjectID = $(clicked).attr('id');
	if($(clicked).hasClass("labFolderProject")) {
		updateLabfolderSelectableElements();
	}
	if($(clicked).hasClass("labFolderMDB")) {
		updateLabfolderSelectableCategories();
	}		
}

function updateProjectMaterialSelection() {
	if (labFolderProjects.projects.length > 0 ) {
		$("#labFolderSelectProject").removeAttr("disabled");
	}
	else {
		$("#labFolderSelectProject").attr("disabled", true);	
	}
	if (labFolderMDB.categories.length > 0 ) {
		$("#labFolderSelectMDB").removeAttr("disabled");	
	}
	else {
		$("#labFolderSelectMDB").attr("disabled", true);	
	}
}

function authenticate(form) {
	var url = baseURL + '/auth/login';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				data = JSON.parse(xhttp.response) ;
				if (!("error" in data))  {
					labFolderToken = data.token;
					setCookie("labFolderToken", labFolderToken);
					$("#labFolderDownloadButton").show();
					updateContentAfterLogin();
				}
				else
				{
					$("#labFolderFailedLogin").show();
				}
			}
		// unlockXMLHTTPRequest();
	}
}
	var username = form.elements['username'].value;//DEBUGlogin;//document.getElementById("loginLabFolderUsername").value;
	var password = form.elements['pwd'].value;;//DEBUGpassword;//document.getElementById("loginLabFolderPassword").value;
	// lockXMLHTTPRequest();
	if (username != '' && password != '') {
		xhttp.open('POST', url, false);
		xhttp.setRequestHeader("Content-type", "application/json");
		var payload = '{\"password\": \"' + password + '\", \"user\": \"' + username + '\"}';
		xhttp.send(payload);	
	}
}

function logout() {
	if (labFolderToken != '') { 
		var url = baseURL + '/auth/logout';
		xhttp.onreadystatechange  = function(e) {
			if(this.readyState == 4) {
				if(this.status == 200) {
					$('form[id=selectableEntries]').empty();
					$("#labfolderLoginform").show();
					$("#labFolderLoginSuccesful").hide();
					$("#labFolderFailedLogin").hide();
					clearCookies();
					clearLocalStorage();
					$("#labFolderDownloadButton").hide();					

				}
		// unlockXMLHTTPRequest();
	}
}
	// lockXMLHTTPRequest();
	xhttp.open('POST', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", labFolderToken);
	xhttp.send();
}
else
{
	alert("Not Logged in!");
}
}

function updateContentAfterLogin() {
	$("#labFolderFailedLogin").hide();
	$("#labfolderLoginform").hide();
	$("#labFolderLoginSuccesful").show();
	if (getLocalStorage("labFolderProjects") == "") {
		getProjects();
		setLocalStorage("labFolderProjects", JSON.stringify(labFolderProjects));	
	}
	else {
		labFolderProjects = JSON.parse(getLocalStorage("labFolderProjects"));
	}

	if (getLocalStorage("labFolderEntries") == "") {
		getEntries();
		setLocalStorage("labFolderEntries", JSON.stringify(labFolderEntries));	
	}
	else {
		labFolderEntries = JSON.parse(getLocalStorage("labFolderEntries"));
	}

	if (getLocalStorage("labFolderMDB") == "") {
		getMDBCategories();
		// getMDBCategory();
		setLocalStorage("labFolderMDB", JSON.stringify(labFolderMDB));	
	}
	else {
		labFolderMDB = JSON.parse(getLocalStorage("labFolderMDB"));
	}

	if (getLocalStorage("labFolderStorageFile") == "") {
		getStorageFile();
		setLocalStorage("labFolderStorageFile", JSON.stringify(labFolderStorageFile));	
	}
	else {
		labFolderStorageFile = JSON.parse(getLocalStorage("labFolderStorageFile"));
	}
	
	updateProjectMaterialSelection();
}

function getStorageFile() {
	var url = baseURL + '/storage';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				labFolderStorageFile = JSON.parse(xhttp.response);
				setLocalStorage("labFolderStorageFile", JSON.stringify(labFolderStorageFile));	
			}
		}
	}

	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", labFolderToken);
	xhttp.send();	
}

function getProjects() {
	// console.log("in getProjects");
	var url = baseURL + '/projects';
	xhttp.onreadystatechange  = function(e) {
		// console.log("readystatechangeProject");
		// console.log("ReadyState: " + this.readyState + " Status: " + this.status);
		if(this.readyState == 4) {
			if(this.status == 200) {
			// console.log("get project success");
			var parsedData = JSON.parse(xhttp.response);
			labFolderProjects.projects = new Array();
			// console.log("parsedData: " + parsedData.length);
			for (var i=0; i < parsedData.length; i++) {
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
			//updateLabfolderSelectableProjects();
		}
		// unlockXMLHTTPRequest();
	}
}
	// lockXMLHTTPRequest();
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", labFolderToken);
	xhttp.send();	
}

function getEntries() {
	// console.log("in getEntries");
	var url = baseURL + '/entries';
	xhttp.onreadystatechange  = function(e) {
		// console.log("readystatechangeEntries");
		// console.log("ReadyState: " + this.readyState + " Status: " + this.status);
		if(this.readyState == 4) {
			if(this.status == 200) {
				var parsedData = JSON.parse(xhttp.response);
				labFolderEntries.entries = new Array();
				for (var i=0; i < parsedData.length; i++) {
					var obj = parsedData[i];
					var entry = {
						elements: Array(),
						title: obj['title'],
						id: obj['id'],
						projectID: obj['project_id'],
						versionID: obj['version_id'],
						authorID: obj['author_id'],
						creationDate: obj['creation_date'],
						versionDate: obj['version_date'],
						entryNumber: obj['entry_number'],
						hidden: obj['hidden'],
						editable: obj['editable']
					};
					for (var j = 0; j < obj['elements'].length; j++) {
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
				//updateLabfolderSelectableElements();
				// console.log(labFolderEntries);
			}
		// unlockXMLHTTPRequest();
	}
}
	// lockXMLHTTPRequest();
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", labFolderToken);
	xhttp.send();	
}

function getMDBCategories() {
	// console.log("in getProjects");
	var url = baseURL + '/mdb/categories';
	xhttp.onreadystatechange  = function(e) {
		// console.log("readystatechangeProject");
		// console.log("ReadyState: " + this.readyState + " Status: " + this.status);
		if(this.readyState == 4) {
			if(this.status == 200) {
				// console.log("get project success");
				console.log(xhttp.response);
				var parsedData = JSON.parse(xhttp.response);
				labFolderMDB.categories = new Array();
				for (i=0; i < parsedData.length; i++) {
					var obj = parsedData[i];
					var category = {
						title: obj['title'],
						id: obj['id'],
						creatorID: obj['creator_id'],
						creationDate: obj['creation_date'],
						versionID: obj['version_id'],
						versionDate: obj['version_date'],
						categories: Array()
					};
					labFolderMDB.categories.push(category);
				}
			}
		// unlockXMLHTTPRequest();
	}
}
	// lockXMLHTTPRequest();
	// console.log(url);
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.setRequestHeader("Authorization", labFolderToken);
	xhttp.send();	
}

// function getMDBCategory() {
// 	// console.log("in getProjects");
// 	var urlBase = baseURL + '/mdb/categories';
// 	for (k=0; k<labFolderMDB.databases.length;k++)
// 	{
// 		var url = urlBase + '/' + labFolderMDB.databases[k].id;
// 		xhttp.onreadystatechange  = function(e) {
// 		// console.log("readystatechangeProject");
// 		// console.log("ReadyState: " + this.readyState + " Status: " + this.status);
// 		if(this.readyState == 4) {
// 			if(this.status == 200) {
// 				var parsedData = JSON.parse(xhttp.response);
// 				labFolderMDB.databases[k].categories = new Array();
// 				// console.log("parsedData: " + parsedData.length);
// 				for (i=0; i < parsedData.length; i++) {
// 					var obj = parsedData[i];
// 					var category = {
// 						title: obj['title'],
// 						id: obj['id'],
// 						creatorID: obj['creator_id'],
// 						creationDate: obj['creation_date'],
// 						versionID: obj['version_id'],
// 						versionDate: obj['version_date']
// 					};
// 					labFolderMDB.databases[i].categories.push(category);
// 				}
// 			}
// 		// unlockXMLHTTPRequest();
// 	}
// }
// 	// lockXMLHTTPRequest();
// 	xhttp.open('GET', url, false);
// 	xhttp.setRequestHeader("Content-type", "application/json");
// 	xhttp.setRequestHeader("Authorization", labFolderToken);
// 	xhttp.send();	
// }

// }

function updateLabfolderSelectableProjects() {
	$("#labFolderProjectSelect").html("");
	var append = "";
	var displayProjectCount = 0;
	// console.log("Projectcount:" + labFolderProjects.projects.length);
	for (var i=0; i < labFolderProjects.projects.length; i++) {
		var obj = labFolderProjects.projects[i];
		if(obj.hidden == false) {
			displayProjectCount++;
			append += '<button class="btn lzvButton btnEntrySelectionHeader btnEntrySelectionProject labFolderProject" id="' + obj.id + '" name="' + obj.id + '"onclick="updateSelectedProject(this);">'
			append += obj.title;
			append += "</button>"
		}
	}
	if (displayProjectCount > 0){
		$("#labFolderProjectSelect").html(append);
		$(".btnEntrySelectionProject").css("width", 100/displayProjectCount + "%")
	}

}

function updateLabfolderSelectableElements() {
	$('form[id=selectableEntries]').empty();
	var append = '';
	if (displayProjectID != "") {
		let storageProject = labFolderStorageFile.projects.find(proj=>proj.projectID == displayProjectID);
		for (var i=0; i<labFolderEntries.entries.length; i++){
			var obj = labFolderEntries.entries[i];
			// console.log("objProjID: " + obj.projeclet db = labFolderMDB.databases.find(db=>db.id == displayProjectID);tID + " displayProjectID: " +  displayProjectID);
			if (obj.hidden == false && obj.projectID == displayProjectID) {
				var storageEntry;
				if (storageProject){
					storageEntry = storageProject.entries.find(entry=>entry.entryID == obj.id);
				}
				append += '<div><div class="entrySelect lzvButton labFolderProject"><input type="checkbox" value="" id="' + obj.id + '" name="' + obj.id + '">';
				append += '<label for="' + obj.id + '" class="selectLabel">' + obj.title; 
				if (storageProject && storageEntry && storageEntry.versions.length > 0) {
					append += '<span class="versionCounter"><button type="button" class="expandVersionButton" onclick="toggleDisplayVersions(this);">';
					append += storageEntry.versions.length + ' version';
					if (storageEntry.versions.length > 1) {
						append += 's ';
					}
					else {
						append += ' ';
					}
					append += '<span class="arrow">v</span></button></span>';
				}
				append += '</label>';
				append += '</div>\n';
				append += '<div class="versionList">';
				if(storageEntry){
					for (version of storageEntry.versions) {
						date = new Date(version.versionDate);
						let formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
						append += '<div class="versionDetail"><span>';
						append += formatted_date;
						var dlurl = baseURL + '/download?project_id=' + displayProjectID + '&entry_id=' + obj.id + '&entry_version_id=' + version.versionID;
						append += '</span><button type="button" class="expandVersionButton" id="' + dlurl + '" + onclick="downloadVersion(this);">Download</button></div>';
					}
				}
				append += '</div></div>';
			}
		} 

		$(append).appendTo('#selectableEntries');
	}

}

// function updateLabfolderSelectableDatabases() {
// 	$("#labFolderProjectSelect").html("");
// 	var append = "";
// 	var displayProjectCount = 0;
// 	// console.log("Projectcount:" + labFolderProjects.projects.length);
// 	for (var i=0; i < labFolderMDB.databases.length; i++) {
// 		var obj = labFolderMDB.databases[i];
// 		displayProjectCount++;
// 		append += '<button class="btn lzvButton btnEntrySelectionHeader btnEntrySelectionProject labFolderMDB" id="' + obj.id + '" name="' + obj.id + '"onclick="updateSelectedProject(this);">'
// 		append += obj.title;
// 		append += "</button>"
// 	}
// 	if (displayProjectCount > 0){
// 		$("#labFolderProjectSelect").html(append);
// 		$(".btnEntrySelectionProject").css("width", 100/displayProjectCount + "%")
// 	}

// }

function updateLabfolderSelectableCategories() {
	$("#labFolderProjectSelect").html("");	
	$('form[id=selectableEntries]').empty();
	var append = '';
	// console.log("Printing Element count: " + labFolderEntries.entries.length);
	// if (displayProjectID != "") {
		// let db = labFolderMDB.categories.find(db=>db.id == displayProjectID);
		for (var i=0; i<labFolderMDB.categories.length; i++){
			var obj = labFolderMDB.categories[i];
			append += '<div class="entrySelect lzvButton labFolderMDB"><input type="checkbox" value=""  id="' + obj.id + '" name="' + obj.id + '">';
			append += '<label for="' + obj.id + '">' + obj.title + '</label>';
			append += '</div>\n';
		}


		$(append).appendTo('#selectableEntries');
	// }

}


function downloadSelectedEntries() {
	//first get ids to download, then do that
	var ids = new Array(); //ids for entry which will be downloaded
	var form = $('form[id=selectableEntries]')[0];
	for (var i = 0; i < form.elements.length; i++) {
		if(form.elements[i].checked){
			ids.push(form.elements[i].name);
		}
	}
	if(ids.length > 0) {
		var elements = new Array(); //these are to single elements to be downloaded later
		for (var j=0; j < labFolderEntries.entries.length; j++) {
			var entry = labFolderEntries.entries[j];
			//console.log("entry:" + entry);
			for (var i=0; i < ids.length; i++) {
				if (entry.id == ids[i]) {
					for (var k = 0 ; k < entry.elements.length; k++ ) {
						let project = labFolderProjects.projects.find(proj=>proj.id == entry.projectID);	
						var element = {
							entryID: entry.id,
							entryTitle: entry.title,
							projectID: entry.projectID,
							elementID: entry.elements[k].elementID,
							elementType: entry.elements[k].type,
							versionID : entry.elements[k].versionID,
							entryVersionID: entry.versionID,
							versionDate : entry.versionDate,
							projectTitle : project.title
						};
						//var element = {elementID: entry.elements[k].elementID, elementType: entry.elements[k].type};
						elements.push(element);	
					}
					
				}
			}
		}
		//elements contains the set of id, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
		console.log(elements);
		// for(var i=0; i < elements.length; i++) {
		// 	console.log(elements[i].elementID + " " +   elements[i].elementType);
		// 	downloadElement(elements[i].elementID, elements[i].elementType);
		// }
		if (elements.length > 0) {
			var url = baseURL + '/elements/download';
			xhttp.onreadystatechange  = function(e) {
				if(this.readyState == 4) {
					if(this.status == 200) {
						var answer = xhttp.response;

						console.log("Answer:" +  answer);

					}
					if(this.status == 400) {
						console.log("Fehler: Bitte ID mitgeben!");
					}
				}
			}


			xhttp.open('POST', url, false);
			xhttp.setRequestHeader("Content-type", "application/json");
			xhttp.setRequestHeader("Authorization", labFolderToken);
			var payload = JSON.stringify(elements);
			xhttp.send(payload);
		}
	}

}

function downloadSelectedMDBCategories() {
	console.log("download MDB");
	//first get ids to download, then do that
	var categoryIds = new Array(); //ids for categories which will be downloaded
	var form = $('form[id=selectableEntries]')[0];
	for (var i = 0; i < form.elements.length; i++) {
		if(form.elements[i].checked){
			categoryIds.push(form.elements[i].name);
		}
	}
	//elements contains the set of id, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
	// console.log(elements);
	for(var i=0; i < categoryIds.length; i++) {
		xhttp.onreadystatechange  = function(e) {
			if(this.readyState == 4) {
				if(this.status == 200) {
					var answer = xhttp.response;
					console.log("Answer:" +  answer);
				}
				if(this.status == 400) {
					alert("Fehler: Bitte ID mitgeben!");
				}
		// unlockXMLHTTPRequest();
	}
}
		// console.log(elements[i].elementID + " " +   elements[i].type);
		url = baseURL + "/mdb/items?category_id=" + categoryIds[i];
		// lockXMLHTTPRequest();
		console.log(url);
		xhttp.open('GET', url, false);
		xhttp.setRequestHeader("Content-type", "application/json");
		xhttp.setRequestHeader("Authorization", labFolderToken);
		xhttp.send();	
	}
}




