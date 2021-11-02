$( document ).ready(function() {
	if(checkLZVLogin())
	{
		$('#logout_lzv').show();
	}
	getStorageFile();
	// var flat_storage = convertStorageFileToFlat();
	// setLocalStorage("labFolderStorageFileFlat", JSON.stringify(flat_storage));
	getMetaDataStructureInformation(false);
	getMetaDataUserSets(false);
	getUserIngests();
	getUserPackages();
	getSubmittedIngests();
});

var unsaved = false;

$(":input").change(function(){ //triggers change in all input fields including text type
    unsaved = true;
});

// Monitor dynamic inputs
$(document).on('change', 'input, select', function(){ //triggers change in all input fields including text type
    unsaved = true;
});

function getUserIngests() {
	var url = baseURL +  '/ingest/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("userIngests", JSON.stringify(parsedJSON));
					updateSideBarUserIngests(parsedJSON);
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function getUserPackages() {
	var url = baseURL +  '/data/packages';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("user_packages", JSON.stringify(parsedJSON));
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function getStorageFile() {
	var url = baseURL + '/labfolder/storage';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				labFolderStorageFile = JSON.parse(xhttp.response);
				setLocalStorage("labFolderStorageFile", JSON.stringify(labFolderStorageFile));
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function getSubmittedIngests() {
	var url = baseURL +  '/ingest/submitted';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					console.log(xhttp.response);
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("submittedIngests", JSON.stringify(parsedJSON.docs));
					updateSideBarSubmittedIngests(parsedJSON.docs);
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function searchUserIngestsByID(id) {
	var c_str = getLocalStorage("userIngests");
	cookieData = JSON.parse(c_str);
	return cookieData.user_sets.find(set=>set.ingest_id == id);
}

function toggleDisplaySubItems(clicked) {
	$(clicked).parent().children('#newItemsSubItems, #myItemsSubItems, #submittedItemsSubItems').toggle();
	if($(clicked).children(".arrow").html() == "v") {
		$(clicked).children(".arrow").text("x");
	}
	else {
		$(clicked).children(".arrow").text("v");
	}
}

function sendUserIngestsToServer(ingest_data) {
	var url = baseURL + '/ingest/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				updateSideBarUserIngests(JSON.parse(getLocalStorage("userIngests")));
			}
		}
	};
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(ingest_data));
}

function updateSideBarSubmittedIngests(submittedIngests)  {
	$('#submittedItemsSubItems').empty();
	var append = '';
	if (submittedIngests) {
	for (var ingest of submittedIngests) {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet sideBarSubmittedItems" id="' + ingest.ingest_id + '" onclick="createFormForSubmittedIngest(this);">' + ingest.name + '</button></div>';

	}
	$(append).appendTo('#submittedItemsSubItems');
	}
}

function updateSideBarUserIngests(userIngests) {
	$('#myItemsSubItems').empty();
	var append = '';
	var append_submitted = '';
	if (userIngests.user_sets) {
	for (var ingest of userIngests.user_sets) {
			console.log(ingest);
		if (ingest.state == "NEW") {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + ingest.ingest_id + '" onclick="createFormForExistingIngest(this);">' + ingest.name + '</button><div class="round-button">';
		append += '<button class="btn deleteSetButton" id="' + ingest.ingest_id + '" onclick="deleteIngest(this);"><span>-</span></button>';
		append += '</div></div>';
		}
	}
	$(append).appendTo('#myItemsSubItems');
	$(append).appendTo('#submittedItemsSubItems');
	}
}

//TODO This function is probably an entry for unwanted manipulation. This need to be checked: Users should only be able to delete ingests
//which are not submitted yet (or else we would lose data). alternatively we dont "store" submitted user ingests on the same place, but in
//a seperate database and gather data for the sidebar from 2 playes (one which is modifyable, one which is fixed)
function deleteIngest(clicked) {
	// if(!submitted) {
	if(confirm("Are you sure that you want to delete this Ingest? This can not be undone!")) {
		clicked_id = $(clicked).attr('id');
		deleteIngestFromStorage(clicked_id);
	}
	// }
}


//TODO wrong function, needs to be reworked
// function deleteIngestFromStorage(ingest_id) {
// 	var c_str = getLocalStorage("userIngests");
// 	cookieData = JSON.parse(c_str);
// 	var delete_set = cookieData.user_sets.find(set=>set.ingest_id == ingest_id);
// 	if(delete_set) {
// 		var index = cookieData.user_sets.indexOf(delete_set);
// 		if (index > -1) {
// 			cookieData.user_sets.splice(index,1);
// 		}
// 	}
// 	setLocalStorage("userIngests", JSON.stringify(cookieData));
// 	sendUserIngestsToServer();
// }

function createFormForNewIngest(){
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
    closeMetaPopup();
	fillIngestForm();
}

function createFormForExistingIngest(clicked) {
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
    closeMetaPopup();
    var clicked_id = $(clicked).attr('id');
    var user_set = searchUserIngestsByID(clicked_id);
	fillIngestForm(user_set);
}

function createFormForSubmittedIngest(clicked) {
	if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
    closeMetaPopup();
	userSets= JSON.parse(getLocalStorage("submittedIngests"));
	var clicked_id = $(clicked).attr('id');
	var user_set = userSets.find(set=>set.ingest_id == clicked_id);
	fillSubmittedIngestForm(user_set);
}

function fillSubmittedIngestForm(userInputSet) {
	var headerHTML = '<div id="title" ingest_id="'+ userInputSet.ingest_id +'" name="ingestTitle">Submitted Ingest</div><hr>';
	headerHTML += '<div class="staticFormContent orig">';
	headerHTML += '<div class="staticText">Name of Ingest: ' + userInputSet.name + '</div>';
	headerHTML += '<div class="staticText">Ingest Metadata: '+ userInputSet.metadata.name +'</div>';
	headerHTML += '<div class="staticText">State: '+ userInputSet.state +'</div>';
	var date = new Date(userInputSet.ingest_metadata.submit_date);
	var formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
	headerHTML += '<div class="staticText">Submission Date: '+ formatted_date +'</div>';
	if(userInputSet.ingest_metadata.approve_date !== undefined) {
		date = new Date(userInputSet.ingest_metadata.approve_date);
		formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		headerHTML += '<div class="staticText">Review Date: '+ formatted_date +'</div>';
	}
	if(userInputSet.ingest_metadata.ingest_date !== undefined) {
		date = new Date(userInputSet.ingest_metadata.ingest_date);
		formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		headerHTML += '<div class="staticText">Ingest Date: '+ formatted_date +'</div>';
	}
	headerHTML += '</div><hr>';
	$('#ingestFormHeader').empty();
	$(headerHTML).appendTo('#ingestFormHeader');
	$('#ingestForm').empty();
	var inputHTML = '';
	inputHTML += '<div class="staticFormContent orig"><table><tr><th>Content</th><th>Metadata</th></tr>';
	for (var i = 0; i < userInputSet.content.length; i++) {
		var con = userInputSet.content[i];
		date = new Date(con.version_data.entry_version_date);
		formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		inputHTML += '<tr><td>' + con.version_data.entry_title +' - ' + formatted_date +'</td>';
		if (con.metadata_userset !== undefined) {
			inputHTML += '<td>' + con.metadata_userset.name + '</td>';
		}
		inputHTML += '</tr>';
	}
	inputHTML += '</table></div>';
	$(inputHTML).appendTo('#ingestForm');
	$('#ingestFormFooter').empty();
	var footerHTML = '<div id="footerButtonDiv">';
	// footerHTML += '<button type="button" class="btn lzvButton" id="submitIngest" onclick="submitIngest();">Submit</button>';
	// footerHTML += '<button type="button" class="btn lzvButton" id="saveIngest" onclick="saveActiveIngest();">Save</button>';
	//footerHTML += '<button type="button" class="btn lzvButton" id="copyMetaDataSet" onclick="copyActiveMetaDataSet();">Copy Set</button>';
	footerHTML += '</div>';
	$(footerHTML).appendTo('#ingestFormFooter');
}

function fillIngestForm(userInputSet = null, recreateID = false){
	var  hasUserInput = false;
	var set_id;
	if(userInputSet !== null) {
		hasUserInput = true;
		set_id = userInputSet.ingest_id;
	}
	if(recreateID || userInputSet === null){
		set_id = uuidv4();
	}
	var headerHTML = '<div id="title" ingest_id="'+ set_id +'" name="ingestTitle">LZV Ingest</div></div>';
	headerHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Ingest:</label>';
	var title = (hasUserInput) ? userInputSet.name : '';
	if( recreateID) {
		title = '';
	}
	headerHTML += '<div class="metaFormUIField"><input required name="ingestName" type="text" value="' + title + '"></div>';
	var mdUserSets = getLocalStorage("metaDataUserSets");
	var mdUserSetsJSON= JSON.parse(mdUserSets);
	console.log(mdUserSets);
	console.log(mdUserSetsJSON);
	if(mdUserSetsJSON &&  mdUserSets !== null) {
		headerHTML += '<select required name="ingest_header_metadata">';
		headerHTML += '<option selected value=""></option>';
		for (let j=0; j<mdUserSetsJSON.length; j++){
			headerHTML += '<option value="'+mdUserSetsJSON[j].set_id+'">'+mdUserSetsJSON[j].name+'</option>';
		}
		headerHTML += '</select>';
	}
	headerHTML += '</div><hr>';
	$('#ingestFormHeader').empty();
	$(headerHTML).appendTo('#ingestFormHeader');
	$('#ingestFormMain').empty();
	var inputHTML = '';
	inputHTML += '<table id="ingest_main_form_table" class="metaFormElement"><thead><td>Data Set(s)</td><td>Metadata Set (optional per Set)</td><td></td><td></td></thead><tbody>';
	// inputHTML += '<div class="metaFieldName"></div><div class="metaFieldDescription"></div></label>';
	var user_packages = getLocalStorage("user_packages");
	var user_packages_json = JSON.parse(user_packages);
	console.log(user_packages);
	console.log(user_packages_json);
	if( user_packages !== null && mdUserSets !== null) {
		inputHTML += '<tr class="table_form_ui_field metaFormCVField orig">';
		if (user_packages_json.length == 0){
			inputHTML += "No Data Sets have been created yet. Please create data packages before creating a lzv ingest!";
		}
		else {
			inputHTML += '<td class="table_field_select"><select class="select_content" name="ingest_content" required>\n';
			inputHTML += '<option selected value=""></option>';
			//fill with all data sets here
			for(let i = 0; i < user_packages_json.length; i++){
				let date = new Date(user_packages_json[i].package_object_metadata.last_change);
				let formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
				inputHTML += '<option value="'+user_packages_json[i].package_id +'">'+user_packages_json[i].name + ' - '+ formatted_date+'</option>';
			}
			inputHTML += '</select></td>';
		}
		if (mdUserSetsJSON.length == 0){
			inputHTML += "<p>No Metadata sets have been created yet. Please create Metadata sets before creating a lzv ingest!";
		}
		else {
		inputHTML += '<td class="table_field_select"><select name="ingest_metadata">';
		inputHTML += '<option selected value=""></option>';
		for (let j=0; j<mdUserSetsJSON.length; j++){
			inputHTML += '<option value="'+mdUserSetsJSON[j].set_id+'">'+mdUserSetsJSON[j].name+'</option>';
		}
		inputHTML += '</select></td><td class="table_field_button"><button type="button" class="open_meta_popup" onclick="openMetaPopup(this);">?</button></td>';
		}
	}
	if (user_packages_json.length > 0 && mdUserSetsJSON.length > 0){
		inputHTML += '<td class="table_field_button"><button type="button" id="duplicate_ingest_field" class="duplicate_field_button" id="ingest_content" onclick="duplicateIngestField(this);">+</button></td></tr>';
	}
	inputHTML += '</tbody></table>';
	$(inputHTML).appendTo('#ingestFormMain');
	$('#ingestFormFooter').empty();
	var footerHTML = '<div id="footerButtonDiv">';
	footerHTML += '<button type="button" class="btn lzvButton" id="submitIngest" onclick="submitIngest();">Submit</button>';
	footerHTML += '<button type="button" class="btn lzvButton" id="saveIngest" onclick="saveActiveIngest();">Save</button>';
	//footerHTML += '<button type="button" class="btn lzvButton" id="copyMetaDataSet" onclick="copyActiveMetaDataSet();">Copy Set</button>';
	footerHTML += '</div>';
	$(footerHTML).appendTo('#ingestFormFooter');
	if (userInputSet) { //fill fields with values from user field
		if (userInputSet.metadata_userset_id!= '') {
			let header_metadata = $('#ingestFormHeader').find('select[name=ingest_header_metadata]');
			header_metadata.val(userInputSet.metadata_userset_id);
		}
		for(let i = 0; i < userInputSet.content.length; i++) {
			let field = userInputSet.content[i];
			if (i==0){
				let select_content = $('#ingestForm').find('select[name=ingest_content]');
				select_content.val(field.version_id);
				let select_metadata = $('#ingestForm').find('select[name=ingest_metadata]');
				select_metadata.val(field.metadata_userset_id);
			}
			else {
				duplicateIngestField($('#ingestForm').find('select').siblings('button'), field.version_id, field.metadata_userset_id);
			}
			// var input = $('#ingestForm').find('input[name=' + field.field_name +  ']');
			// if (input.length>0){
			// 	input.attr('value',field.values[0]);
			// }
			// else {
			// 	var select = $('#ingestForm').find('select[name=' + field.field_name +  ']');
			// 	select.val(field.values[0]);
			// }
			// for( var j = 1; j < field.values.length; j++){
			// 	duplicateIngestField($('#ingestForm').find('input[name=' + field.field_name +  '], select[name=' + field.field_name +  ']').siblings('button'), field.values[j]);
			// }
		}
	}
}

function openMetaPopup(clicked){
	var meta_id = $(clicked).parent().parent().find('select[name="ingest_metadata"]')[0].value;
	if (!meta_id) { //catch case when no metaset has been selected
		return;
	}
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	userSets= JSON.parse(getLocalStorage("metaDataUserSets"));
	var user_set = userSets.find(set=>set.set_id == meta_id);
	var meta_struc = metaStructure.find(struc=>struc.identifier == user_set.identifier);
	fillMetaDataForm(meta_struc, user_set, false, false);
	// var html = createPopupFormContent(meta_struc,user_set);
	// $('#popupForm').empty();
	// $(html).appendTo('#popupForm');
	// prefillWithUserValue(user_set);
	$('#ingestDataMainForm').hide();
	$('#popupForm').show();
}

// function createPopupFormContent(metaStruc,userInputSet) {
// 	var	set_id = userInputSet.set_id;
// 	var returnHTML = '<div id="ingestDataMainForm"><div id="metaDataFormHeader">';
// 	returnHTML += '<div id="title" set_id="'+ set_id +'" name="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div>';
// 	returnHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Metadata Set:</label>';
// 	returnHTML += '<div class="metaFormUIField"><input required name="metaSchemeName" type="text" value="' + userInputSet.name + '"></div></div><hr></div>';
// 	returnHTML += '<form id="metaDataForm">';
// 	for (var i=0; i<metaStruc.fields.length; i++){
// 		var field = metaStruc.fields[i];
// 		returnHTML += '<div class="metaFormElement"><label class="formDescriptor" for="';
// 		returnHTML += field.field_identifier + '" ';
// 		returnHTML += '><div class="metaFieldName">' + field.field_name.charAt(0).toUpperCase() + field.field_name.slice(1) + '</div><div class="metaFieldDescription">'+ field.field_description +'</div></label>';
// 		if (field.field_type != 'cv') {
// 			returnHTML += '<div class="metaFormUIField orig"><input ';
// 		}
// 		else {
// 			returnHTML += '<div class="metaFormUIField metaFormCVField orig"><select ';
// 		}
// 		returnHTML += 'name="' + field.field_identifier + '" ';
// 		if (field.field_mandatory){
// 			returnHTML += 'required ';
// 		}
// 		switch(field.field_type) {
// 			case 'string':
// 				returnHTML += 'type="text" ';
// 				break;
// 			case 'int':
// 				returnHTML += 'type="number" ';
// 				break;
// 			case 'float':
// 				returnHTML += 'type="number" step="any" ';
// 				break;
// 			case 'cv':
// 				returnHTML += '>\n';
// 				returnHTML += '<option selected value=""></option>';
// 				for (var j=0; j<field.field_options.length; j++){
// 					option = field.field_options[j];
// 					returnHTML += '<option value="'+option+'">'+option+'</option>';
// 				}
// 				break;
// 		}
// 		if (field.field_type != 'cv') {
// 			if(field.field_verification) {
// 				returnHTML += 'pattern="' + field.field_verification + '" ';
// 			}
// 			returnHTML += '>';
// 		}
// 		else {
// 			returnHTML += '</select>';
// 		}
// 		if(field.field_multiple) {
// 			returnHTML += '<button type="button" class="duplicate_field_button" id="' + field.field_name +'" onclick="duplicateMetaDataField(this);">+</button>';
// 		}
// 		returnHTML += '</div></div>';
// 	}
// 	returnHTML += '</form><div id="metaDataFormFooter">';
// 	returnHTML += '<div id="footerButtonDiv">';
// 	returnHTML += '<button type="button" class="btn lzvButton" id="saveAndCloseMetaDataForm" onclick="saveAndCloseMetaPopup();">Save & Close</button>';
// 	returnHTML += '<button type="button" class="btn lzvButton" id="closeMetaDataForm" onclick="closeMetaPopup();">Close</button>';
// 	// footerHTML += '<button type="button" class="btn lzvButton" id="exportToXML" onclick="exportSetToXML();">Export to XML</button>';
// 	// function exportSetToXML() {}
// 	returnHTML += '</div></div>';
// 	return returnHTML;
// }

function saveAndCloseMetaPopup() {
	saveActiveMetaDataSet();
	closeMetaPopup();
}

function prefillWithUserValue(userInputSet) {
	for(var i = 0; i < userInputSet.fields.length; i++) {
		var field = userInputSet.fields[i];
		var input = $('#metaDataForm').find('input[name=' + field.field_identifier +  ']');
		if (input.length>0){
			input.attr('value',field.values[0]);
		}
		else {
			var select = $('#metaDataForm').find('select[name=' + field.field_identifier +  ']');
			select.val(field.values[0]);
		}
		for( var j = 1; j < field.values.length; j++){
			duplicateMetaDataField($('#metaDataForm').find('input[name=' + field.field_identifier +  '], select[name=' + field.field_identifier +  ']').siblings('button'), field.values[j]);
		}
	}
}

function closeMetaPopup() {
	$('#ingestDataMainForm').show();
	$('#popupForm').hide();
}

function duplicateIngestField(clicked, prefillValueIngest = null, prefillValueMetadata = null){
	var row = $('#ingest_main_form_table tbody tr').first().clone();
	var select_content = row.children('select[name=ingest_content]');
	var select_metadata = row.children('select[name=ingest_metadata]');
	if (prefillValueIngest !== null) {
		select_content.children('[selected=true]').removeAttr('selected');
		select_content.val(prefillValueIngest);
	}
	else {
		select_content.val('');
	}
	if (prefillValueMetadata !== null) {
		select_metadata.children('[selected=true]').removeAttr('selected');
		select_metadata.val(prefillValueMetadata);
	}
	else {
		select_metadata.val('');
	}
	row.find('#duplicate_ingest_field').replaceWith('<button type="button" class="remove_field_button" onclick="removeIngestField(this);">-</button>');
	$('#ingest_main_form_table tbody:last-child').append(row);
}

function removeIngestField(clicked){
	if ($(clicked).parent().parent().find('input, select').val() != ''){
		if(confirm("Are you sure you want to delete this field?")){
			$(clicked).parent().parent().remove();
		}
		else {
			return;
		}
	}
	else{
		$(clicked).parent().parent().remove();
	}
}

function getActiveIngest() {
	var saveData = {};
	var formHeaderFields = $('#ingestFormHeader');
	var formFieldsInputContent = $('#ingestFormMain').find('select[name="ingest_content"]');
	var formFieldsInputMeta = $('#ingestFormMain').find('select[name="ingest_metadata"]');
	saveData.name = formHeaderFields.find('input')[0].value;
	saveData.metadata_userset_id = formHeaderFields.find('select[name="ingest_header_metadata"]')[0].value;
	saveData.metadata = searchMetaDataUserSetsByID(saveData.metadata_userset_id);
	saveData.ingest_id = formHeaderFields.find('#title').attr('ingest_id');
	saveData.state = 'NEW';
	saveData.content = [];
	var user_packages  = JSON.parse(getLocalStorage("user_packages"));
	for (var i = 0 ; i < formFieldsInputContent.length; i++) {
		var content_value = '';
		var content_data = {};
		if (formFieldsInputContent[i].value) {
			content_value = formFieldsInputContent[i].value;
			content_data = user_packages.find(set=>set.package_id == content_value);
		}
		var meta_value = '';
		if (formFieldsInputMeta[i].value) {
			meta_value = formFieldsInputMeta[i].value;
		}
		if (meta_value != ''){
			saveData.content.push({'package_id' : content_value, 'package_data' : content_data, 'metadata_userset_id' : meta_value, 'metadata_userset' : searchMetaDataUserSetsByID(meta_value)});
		}
		else {
			saveData.content.push({'package_id' : content_value, 'package_data' : content_data});
		}

	}
	return saveData;
}

//start the ingest process
//create an ingest based of the data in the form and the metadata
//create a new database for submitted ingests, the entries need the metadata and files so we can verify the availability of these.
function submitIngest() {
	var url = baseURL + '/ingest/submit';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				console.log("test");
				alert("Ingest successfully submitted for review!");
				location.reload();
			}
		}
	};
	// var metaSets = JSON.parse(getLocalStorage("metaDataUserSets"));
	// var data = JSON.parse(getLocalStorage("labFolderStorageFile"));

	var payload = getActiveIngest();
	if(payload.name == '' || payload.metadata == "") {
		alert("Ingest Name and Metadata required for submission!");
		return;
	}
	var now = new Date();
	payload.ingest_metadata = {};
	payload.state = 'REVIEW';
	payload.ingest_metadata.submit_date = now.toString();
	payload.ingest_metadata.review_date = undefined;
	payload.ingest_metadata.ingest_date = undefined;
	// saveInLocalStorage('userIngests', payload);
	console.log("payload:");
	console.log(payload);
	sendUserIngestsToServer(payload);
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(payload));
}

function saveInLocalStorage(storage_name, save_data) {
	var c_str = getLocalStorage(storage_name) ;
	var cookieData;
	if (c_str === null || c_str == ''){
		cookieData = {'user_sets' : []};
	}
	else {
		cookieData = JSON.parse(c_str);
	}
	var oldSet = cookieData.user_sets.find(set=>set.ingest_id == save_data.ingest_id);
	if (oldSet) {
		cookieData.user_sets.splice(cookieData.user_sets.indexOf(oldSet),1);
		cookieData.user_sets.push(save_data);
	}
	else {
		cookieData.user_sets.push(save_data);
	}
	setLocalStorage(storage_name,  JSON.stringify(cookieData));
}

function saveActiveIngest() {
	saveData = getActiveIngest();
	if(saveData.name == ''){
		alert('Please entere a name for the data set before saving!');
		return;
	}
	// saveInLocalStorage('userIngests', saveData);
	unsaved = false;
	sendUserIngestsToServer(saveData);
}

function newLZVIngest(clicked) {
	createFormForNewIngest();
}