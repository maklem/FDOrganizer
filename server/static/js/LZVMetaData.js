//Initialization Function
$( document ).ready(function() {
	getMetaDataStructureInformation();
	// metaStruc = getCookie("metaDataStructs");
	// createFormForNewSchemeItem('DC1.1Mini')
});


function getType(p) {
    if (Array.isArray(p)) return 'array';
    else if (typeof p == 'string') return 'string';
    else if (p != null && typeof p == 'object') return 'object';
    else return 'other';
}

function getMetaDataStructureInformation(){
	var url = baseURL + '/metadata/structures';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				setCookie("metaDataStructs", JSON.stringify(parsedJSON));
				updateSideBarMetaSchemes(parsedJSON);	
			}
		}
	}
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

function getMetaDataUserSets() {
	var url = baseURL + '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				setCookie("metaDataUserSets", JSON.stringify(parsedJSON));
				updateSideBarUserSets(parsedJSON);
			}
		}
	}
	xhttp.open('GET', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function sendUserMetaSetsToServer() {
	var url = baseURL + '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				
			}
		}
	}
	xhttp.open('PUT', url, true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(getCookie("metaDataUserSets")));
}


//TODO -> Save Active Metadataset on server. Also reload the page sidebar.
function saveActiveMetaDataSet(clicked) {
	saveData = {};
	var formHeaderFields = $('#metaDataFormHeader');
	var formFieldsInput = $('#metaDataForm').find('input, select'); 
	saveData.name = formHeaderFields.find('input')[0].value;
	if(saveData.name == ''){
		alert('Please entere a name for the data set before saving!');
		return;
	}
	saveData.identifier = formHeaderFields.find('#title').attr('name');
	saveData.set_id = formHeaderFields.find('#title').attr('set_id');
	saveData.fields = [];
	for (var i = 0; i <formFieldsInput.length; i++) {
		var field = formFieldsInput[i];
		if(field.value) {
			var name = field.name
			var saveDataField = saveData.fields.find(f=>f.field_name == name);
			if (saveDataField) {
				saveDataField.values.push(field.value);
			}
			else {
				saveData.fields.push({"field_name" : name, "values" : [field.value]});
			}
		}
	}
	var c_str = getCookie("metaDataUserSets");
	var cookieData;
	if (c_str == ''){
		cookieData = {'user_sets' : []};
	}
	else {
		cookieData = JSON.parse(c_str);
	}
	var oldSet = cookieData.user_sets.find(set=>set.set_id == saveData.set_id);
	if (oldSet && oldSet.length > 0) {
		oldSet[0] = saveData;}
	else {
		cookieData.user_sets.push(saveData);
	}
	setCookie("metaDataUserSets", JSON.stringify(cookieData));
	console.log(cookieData);
	updateSideBarUserSets(cookieData);

}
//TODO fill! Also Button required to do this!
function deleteActiveMetaDataSet() {

}

//LATER
function exportSetToXML() {}
function exportSetToJSON() {}

function createFormForNewSchemeItem(clicked){
	metaStructure = JSON.parse(getCookie("metaDataStructs"));
	clickedID = $(clicked).attr('id');
	var clickedStruc = metaStructure.schemes.find(struc=>struc.identifier == clickedID);
	if(clickedStruc) {
		fillMetaDataForm(clickedStruc);
	}
}

function createFormForExistingSchemeSet(clicked) {
	metaStructure = JSON.parse(getCookie("metaDataStructs"));
	userSets= JSON.parse(getCookie("metaDataUserSets"));
	clicked_set_id = $(clicked).attr('id');
	var user_set = userSets.find(set=>set.set_id == clicked_set_id);
	var meta_struc = metaStructure.find(struc=>struc.identifier = user_set.identifier);
	fillMetaDataForm(meta_struc,user_set);
}


//this function creates a form for creation of meta data
//if userInput = NULL a new metaDataSet is created, if not null then an existing scheme is modified and already existing entries are displayed
//metaStruc a single metaStrucuture JSON object
//userInput the correlated userMetaSet for that struc, which is required when a existing set should be updated
//TODO if userinputset is filled we need to prefill the fields
function fillMetaDataForm(metaStruc,userInputSet){
	var headerHTML = '<div id="title" set_id="'+ uuidv4() +'" name="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div></div>';
	headerHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Metadata Set:</label>';
	headerHTML += '<div class="metaFormUIField"><input required name="metaSchemeName" type="text"></div></div>';
	$('#metaDataFormHeader').empty();
	$(headerHTML).appendTo('#metaDataFormHeader');
	$('#metaDataForm').empty();
	for (var i=0; i<metaStruc.fields.length; i++){
		var inputHTML = '';
		var field = metaStruc.fields[i];
		inputHTML += '<div class="metaFormElement"><label class="formDescriptor" for="';
		inputHTML += field.field_name + '" ';
		inputHTML += '><div class="metaFieldName">' + field.field_name.charAt(0).toUpperCase() + field.field_name.slice(1) + '</div><div class="metaFieldDescription">'+ field.field_description +'</div></label>';
		if (field.field_type != 'cv') {
			inputHTML += '<div class="metaFormUIField orig"><input ';
		}
		else {
			inputHTML += '<div class="metaFormUIField metaFormCVField orig"><select ';
		}
		inputHTML += 'name="' + field.field_name + '" ';
		if (field.field_mandatory){
			inputHTML += 'required ';
		}
		switch(field.field_type) {
			case 'string':
				inputHTML += 'type="text" ';
				break;
			case 'int':
				inputHTML += 'type="number" ';
				break;
			case 'float':
				inputHTML += 'type="number" step="any" ';
				break;
			case 'cv':
				inputHTML += '>\n';
				for (var j=0; j<field.field_options.length; j++){
					option = field.field_options[j];
					inputHTML += '<option value="'+option+'">'+option+'</option>';
				}
				break;
		}
		if (field.field_type != 'cv') {
			inputHTML += '>';
		}
		else {
			inputHTML += '</select>';
		}
		if(field.field_multiple) {
			inputHTML += '<button type="button" class="duplicateMetaButton" id="' + field.field_name +'" onclick="duplicateMetaDataField(this);">+</button>';
		}
		inputHTML += '</div></div>';
		$(inputHTML).appendTo('#metaDataForm');
	}
	$('#metaDataFormFooter').empty();
	var footerHTML = '<div id="footerButtonDiv"><button type="button" id="saveMetaDataForm" onclick="saveActiveMetaDataSet(this);">Save</button></div>';
	$(footerHTML).appendTo('#metaDataFormFooter');
}

function duplicateMetaDataField(clicked){
	var tmp = $(clicked).parent('.orig').clone();
	tmp.children(':button').remove();
	tmp.removeClass('orig');
	tmp.addClass('clone');
	var removeButton = '<button type="button" class="removeMetaFieldButton" onclick="removeMetaDataField(this);">-</button>';
	$(removeButton).appendTo(tmp);
	tmp.appendTo($(clicked).parent().parent());
}

function removeMetaDataField(clicked){
	$(clicked).parent().remove();
}
//<label class="formDescriptor" for="username"><h3><b>Username</b></h3></label>
//<input name="username" type="text" placeholder="Enter Username" required value="robert.guenther@uni-bayreuth.de">

function updateSideBar() {
	var metaSchemes = JSON.parse(getCookie("metaDataStructs"));
	if (metaSchemes) {
		updateSideBarMetaSchemes(metaSchemes);
	}
	var userSets = JSON.parse(setCookie("metaDataUserSets"));
	if (userSets) {
		updateSideBarUserSets(userSets);
	}

}

function updateSideBarMetaSchemes(metaStruc) {
	$('#newItemsSubItems').empty();
	var append = '';
	console.log(metaStruc);
	for (scheme of metaStruc.schemes) {
		append += '<button class="sideBarItem sideBarSubItem" id="' + scheme.identifier + '" onclick="createFormForNewSchemeItem(this);">' + scheme.title + ' ' + scheme.version + '</button><br>';
	}
	$(append).appendTo('#newItemsSubItems');
}

function updateSideBarUserSets(userSets){
	$('#myItemsSubItems').empty();
	var append = '';
	console.log (userSets);
	for (set of userSets.user_sets) {
		append += '<button class="sideBarItem sideBarSubItem" id="' + set.set_id + '" onclick="createFormForExistingSchemeSet(this);">' + set.name + '</button><br>';
	}
	$(append).appendTo('#myItemsSubItems');
}

function toggleDisplaySubItems(clicked) {
	$(clicked).parent().children(".sideBarSubItem").toggle();
	if($(clicked).children(".arrow").html() == "v") {
		$(clicked).children(".arrow").text("x");
	}
	else {
		$(clicked).children(".arrow").text("v");
	}
}

