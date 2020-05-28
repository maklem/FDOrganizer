//Initialization Function
$( document ).ready(function() {
	getMetaDataStructureInformation();
	getMetaDataUserSets();
	// metaStruc = getLocalStorage("metaDataStructs");
	// createFormForNewSchemeItem('DC1.1Mini')
});

var unsaved = false;

$(":input").change(function(){ //triggers change in all input fields including text type
	console.log("detected change f1");
    unsaved = true;
});

// Monitor dynamic inputs
$(document).on('change', 'input, select', function(){ //triggers change in all input fields including text type
	console.log("detected change f2");
    unsaved = true;
});

function unloadPage(){ 
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
}

function getMetaDataStructureInformation(){
	console.log("get strcuture data");
	var url = baseURL + '/metadata/structures';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				console.log(parsedJSON);
				console.log(JSON.stringify(parsedJSON));
				setLocalStorage("metaDataStructs", JSON.stringify(parsedJSON));
				setLocalStorage("test", JSON.stringify(parsedJSON));
				console.log("getLocalStorage");
				console.log(getLocalStorage("metaDataStructs"));
				updateSideBarMetaSchemes(parsedJSON);	
			}
		}
	}
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

function getMetaDataUserSets() {
	console.log("get user data");
	var url = baseURL + '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					console.log(xhttp.response);
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("metaDataUserSets", JSON.stringify(parsedJSON));
					updateSideBarUserSets(parsedJSON);
				}
			}
		}
	}
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function sendUserMetaSetsToServer() {
	console.log("sending Meta");
	var url = baseURL + '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				
			}
		}
	}
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(getLocalStorage("metaDataUserSets")));
}


function getActiveMetaDataSet() {
	var saveData = {};
	var formHeaderFields = $('#metaDataFormHeader');
	var formFieldsInput = $('#metaDataForm').find('input, select'); 
	saveData.name = formHeaderFields.find('input')[0].value;
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
	return saveData;
}

//TODO -> Save Active Metadataset on server. Also reload the page sidebar.
function saveActiveMetaDataSet() {
	saveData = getActiveMetaDataSet();
	if(saveData.name == ''){
		alert('Please entere a name for the data set before saving!');
		return;
	}
	var c_str = getLocalStorage("metaDataUserSets");
	var cookieData;
	if (c_str == ''){
		cookieData = {'user_sets' : []};
	}
	else {
		cookieData = JSON.parse(c_str);
	}
	var oldSet = cookieData.user_sets.find(set=>set.set_id == saveData.set_id);
	if (oldSet) {
		cookieData.user_sets.splice(cookieData.user_sets.indexOf(oldSet),1);
		cookieData.user_sets.push(saveData);
	}
	else {
		cookieData.user_sets.push(saveData);
	}
	console.log(cookieData);
	setLocalStorage("metaDataUserSets", JSON.stringify(cookieData));
	updateSideBarUserSets(cookieData);
	unsaved = false;
	sendUserMetaSetsToServer();
}

//TODO fill! Also Button required to do this!
function deleteMetaDataSet(clicked) {
	if(confirm("Are you sure that you want to delete this metadata set? This can not be undone!")){
		var c_str = getLocalStorage("metaDataUserSets");
		clickedID = $(clicked).attr('set_id');
		cookieData = JSON.parse(c_str);
		console.log("before:");
		console.log(cookieData);
		var delete_set = cookieData.user_sets.find(set=>set.set_id == clickedID);
		console.log("delete_set:");
		console.log(delete_set);
		if(delete_set) {
			var index = cookieData.user_sets.indexOf(delete_set);
			console.log("index:" + index);
			if (index > -1) {
				cookieData.user_sets.splice(index,1);
			}
		}
		console.log("after:");
		console.log(cookieData);
		setLocalStorage("metaDataUserSets", JSON.stringify(cookieData));
		updateSideBarUserSets(cookieData);
		sendUserMetaSetsToServer();
	}
}

//LATER
// function exportSetToXML() {
// 	var new_page = window.open();
//   new_page.document.write("output");
// }

function exportSetToJSON() {
	var print_json = {};
	let data = getActiveMetaDataSet();
	if(data.fields.length == 0) {
		return;
	}
	for (var i = 0; i < data.fields.length; i++) {
		var field = data.fields[i];
		if (field.values.length > 1) {
			print_json[field.field_name] = [];
			for(var j = 0; j < field.values.length; j++) {
				var value = field.values[j];
				print_json[field.field_name].push(value);
			}
		}
		else{
			print_json[field.field_name] = field.values[0];
		}
	}
	var new_page = window.open();
  	new_page.document.write(JSON.stringify(print_json));
}

function exportSetToDC() {
  let data = getActiveMetaDataSet();
  if(data.fields.length == 0) {
		return;
	}
  let print_text = '';
  for(var i = 0; i < data.fields.length; i++){
  	for(var j = 0; j < data.fields[i].values.length; j++) {
  		print_text += data.fields[i].field_name + ': ' + data.fields[i].values[j] + "<br>";
  }
  }
  var new_page = window.open();
  new_page.document.write(print_text);
}

function createFormForNewSchemeItem(clicked){
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
    console.log(getLocalStorage("metaDataStructs"));
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	console.log(metaStructure);
	clickedID = $(clicked).attr('id');
	var clickedStruc = metaStructure.schemes.find(struc=>struc.identifier == clickedID);
	if(clickedStruc) {
		fillMetaDataForm(clickedStruc);
	}
}

function createFormForExistingSchemeSet(clicked) {
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	userSets= JSON.parse(getLocalStorage("metaDataUserSets"));
	clicked_set_id = $(clicked).attr('id');
	var user_set = userSets.user_sets.find(set=>set.set_id == clicked_set_id);
	var meta_struc = metaStructure.schemes.find(struc=>struc.identifier == user_set.identifier);

	fillMetaDataForm(meta_struc,user_set);
}


//this function creates a form for creation of meta data
//if userInput = NULL a new metaDataSet is created, if not null then an existing scheme is modified and already existing entries are displayed
//metaStruc a single metaStrucuture JSON object
//userInput the correlated userMetaSet for that struc, which is required when a existing set should be updated
function fillMetaDataForm(metaStruc,userInputSet = null){
	var  hasUserInput = false
	if(userInputSet !== null) {
		hasUserInput = true;
	}
	var set_id = (hasUserInput) ? userInputSet.set_id : uuidv4();
	var headerHTML = '<div id="title" set_id="'+ set_id +'" name="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div></div>';
	headerHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Metadata Set:</label>';
	var title = (hasUserInput) ? userInputSet.name : '';
	headerHTML += '<div class="metaFormUIField"><input required name="metaSchemeName" type="text" value="' + title + '"></div></div><hr>';
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
				inputHTML += '<option selected value=""></option>';
				for (var j=0; j<field.field_options.length; j++){
					option = field.field_options[j];
					inputHTML += '<option value="'+option+'">'+option+'</option>';
				}
				break;
		}
		if (field.field_type != 'cv') {

			if(field.field_verification) {
				console.log("text");
				console.log(field.field_verification);
				inputHTML += 'pattern="' + field.field_verification + '" ';
			}
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
	var footerHTML = '<div id="footerButtonDiv">';
	footerHTML += '<button type="button" class="btn lzvButton" id="saveMetaDataForm" onclick="saveActiveMetaDataSet();">Save</button>';
	footerHTML += '<button type="button" class="btn lzvButton" id="exportToDC" onclick="exportSetToDC();">Export to Dublin Core</button>';
	// footerHTML += '<button type="button" class="btn lzvButton" id="exportToXML" onclick="exportSetToXML();">Export to XML</button>';
	footerHTML += '<button type="button" class="btn lzvButton" id="exportToJSON" onclick="exportSetToJSON();">Export to JSON</button>';
	// function exportSetToXML() {}
	// function exportSetToJSON() {}
	// function exportSetToDC() {}
	footerHTML += '</div>';
	$(footerHTML).appendTo('#metaDataFormFooter');
	if (hasUserInput) { //fill fields with values from user field
		for(var i = 0; i < userInputSet.fields.length; i++) {
			var field = userInputSet.fields[i];
			var input = $('#metaDataForm').find('input[name=' + field.field_name +  ']');
			if (input.length>0){
				input.attr('value',field.values[0]);
			}
			else {
				var select = $('#metaDataForm').find('select[name=' + field.field_name +  ']');
				select.val(field.values[0]);
			}
			for( var j = 1; j < field.values.length; j++){
				duplicateMetaDataField($('#metaDataForm').find('input[name=' + field.field_name +  '], select[name=' + field.field_name +  ']').siblings('button'), field.values[j]);
			}
		}
	}
}

function checkIfActiveFormHasInput() {
	var fields = $('#metaDataForm').find('input, select');
}

function duplicateMetaDataField(clicked,prefillValue = null){
	var tmp = $(clicked).parent('.orig').clone();
	tmp.children(':button').remove();
	tmp.removeClass('orig');
	tmp.addClass('clone');
	var input = tmp.children('input');
	if(input.length>0) {
		if (prefillValue !== null) {
			input.val(prefillValue);
		}
		else {
			input.val('');
		}
	}
	else {
		var select = tmp.children('select');
		select.children('[selected=true]').removeAttr('selected');
		if (prefillValue !== null) {
			select.val(prefillValue);
		}
		else{
			select.val('');	
		}
	}
	var removeButton = '<button type="button" class="removeMetaFieldButton" onclick="removeMetaDataField(this);">-</button>';
	$(removeButton).appendTo(tmp);
	tmp.appendTo($(clicked).parent().parent());
}

function removeMetaDataField(clicked){
	if ($(clicked).parent().children('input, select').val() != ''){
		if(confirm("Are you sure you want to delete this field?")){
			$(clicked).parent().remove();	
		}
		else {
			return;
		}
	}
	else{
		$(clicked).parent().remove();
	}
}
//<label class="formDescriptor" for="username"><h3><b>Username</b></h3></label>
//<input name="username" type="text" placeholder="Enter Username" required value="robert.guenther@uni-bayreuth.de">

function updateSideBar() {
	var metaSchemes = JSON.parse(getLocalStorage("metaDataStructs"));
	if (metaSchemes) {
		updateSideBarMetaSchemes(metaSchemes);
	}
	var userSets = JSON.parse(getLocalStorage("metaDataUserSets"));
	if (userSets) {
		updateSideBarUserSets(userSets);
	}

}

function updateSideBarMetaSchemes(metaStruc) {
	$('#newItemsSubItems').empty();
	var append = '';
	for (scheme of metaStruc.schemes) {
		console.log(scheme.fields);
		if(scheme.active){
		append += '<button class="sidebarItem sidebarSubItem" id="' + scheme.identifier + '" onclick="createFormForNewSchemeItem(this);">' + scheme.title + ' ' + scheme.version + '</button><br>';
	}
	}
	$(append).appendTo('#newItemsSubItems');
}

function updateSideBarUserSets(userSets){
	$('#myItemsSubItems').empty();
	var append = '';
	for (set of userSets.user_sets) {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + set.set_id + '" onclick="createFormForExistingSchemeSet(this);">' + set.name + '</button><div class="round-button"><button class="btn deleteSetButton" set_id="'+ set.set_id + '" onclick="deleteMetaDataSet(this);"><span>-</span></button></div></div>';
	}
	$(append).appendTo('#myItemsSubItems');
}

function toggleDisplaySubItems(clicked) {
	$(clicked).parent().children('#newItemsSubItems, #myItemsSubItems').toggle();
	if($(clicked).children(".arrow").html() == "v") {
		$(clicked).children(".arrow").text("x");
	}
	else {
		$(clicked).children(".arrow").text("v");
	}
}

