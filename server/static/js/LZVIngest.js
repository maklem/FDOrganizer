$( document ).ready(function() {
	if(checkLZVLogin())
	{
		$('#logout_lzv').show();
	}
	getStorageFile();
	var flat_storage = convertStorageFileToFlat();
	console.log(flat_storage);
	setLocalStorage("labFolderStorageFileFlat", JSON.stringify(flat_storage));
	getMetaDataStructureInformation(false);
	getMetaDataUserSets(false);
	getUserIngests();
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
	}
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
	}
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
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("submittedIngests", JSON.stringify(parsedJSON.docs));
					updateSideBarSubmittedIngests(parsedJSON.docs);
				}
			}
		}
	}
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

function sendUserIngestsToServer() {
	var url = baseURL + '/ingest/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				updateSideBarUserIngests(JSON.parse(getLocalStorage("userIngests")));
			}
		}
	}
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(getLocalStorage("userIngests")));
}

function updateSideBarSubmittedIngests(submittedIngests)  {
	$('#submittedItemsSubItems').empty();
	var append = '';
	if (submittedIngests) {
	for (ingest of submittedIngests) {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet sideBarSubmittedItems" id="' + ingest.ingest_id + '" onclick="createFormForSubmittedIngest(this);">' + ingest.name + '</button>';
		append += '</div>';
	}
	$(append).appendTo('#submittedItemsSubItems');
	}
}

function updateSideBarUserIngests(userIngests) {
	$('#myItemsSubItems').empty();
	var append = '';
	if (userIngests.user_sets) {
	for (ingest of userIngests.user_sets) {
		if (ingest.state == "NEW") {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + ingest.ingest_id + '" onclick="createFormForExistingIngest(this);">' + ingest.name + '</button><div class="round-button">';
		// if(!ingest.state == "SUBMITTED") {
			append += '<button class="btn deleteSetButton" ingest_id="'+ ingest.ingest_id + '" onclick="deleteIngest(this);"><span>-</span></button>';
		// }
		append += '</div></div>';
		}
	}
	$(append).appendTo('#myItemsSubItems');
	}
}

//TODO This function is probably an entry for unwanted manipulation. This need to be checked: Users should only be able to delete ingests 
//which are not submitted yet (or else we would lose data). alternatively we dont "store" submitted user ingests on the same place, but in
//a seperate database and gather data for the sidebar from 2 playes (one which is modifyable, one which is fixed)
function deleteIngest(clicked) {
	// if(!submitted) {
	if(confirm("Are you sure that you want to delete this Ingest? This can not be undone!")) {
		clickedID = $(clicked).attr('ingest_id');
		deleteIngestFromStorage(clickedID);
	}
	// }
}

function deleteIngestFromStorage(ingest_id) {
	var c_str = getLocalStorage("userIngests");
	cookieData = JSON.parse(c_str);
	var delete_set = cookieData.user_sets.find(set=>set.ingest_id == ingest_id);
	if(delete_set) {
		var index = cookieData.user_sets.indexOf(delete_set);
		if (index > -1) {
			cookieData.user_sets.splice(index,1);
		}
	}
	setLocalStorage("userIngests", JSON.stringify(cookieData));
	sendUserIngestsToServer();
}

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
	// userSets= JSON.parse(getLocalStorage("userIngests"));
	clicked_set_id = $(clicked).attr('id');
    var user_set = searchUserIngestsByID(clicked_set_id);
	// var user_set = userSets.user_sets.find(set=>set.ingest_id == clicked_set_id);
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
	clicked_set_id = $(clicked).attr('id');
	var user_set = userSets.find(set=>set.ingest_id == clicked_set_id);
	fillSubmittedIngestForm(user_set);
}

function fillSubmittedIngestForm(userInputSet) {
	console.log(JSON.stringify(userInputSet));
	var headerHTML = '<div id="title" ingest_id="'+ userInputSet.ingest_id +'" name="ingestTitle">Submitted Ingest</div><hr>';
	headerHTML += '<div class="staticFormContent orig">';
	headerHTML += '<div class="staticText">Name of Ingest: ' + userInputSet.name + '</div>';
	headerHTML += '<div class="staticText">Ingest Metadata: '+ userInputSet.metadata.name +'</div>'
	headerHTML += '<div class="staticText">State: '+ userInputSet.state +'</div>'
	var date = new Date(userInputSet.ingest_metadata.submit_date);
	var formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
	headerHTML += '<div class="staticText">Submission Date: '+ formatted_date +'</div>'
	if(userInputSet.ingest_metadata.review_date !== undefined) {
		date = new Date(userInputSet.ingest_metadata.review_date);
		formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		headerHTML += '<div class="staticText">Review Date: '+ formatted_date +'</div>'
	}
	if(userInputSet.ingest_metadata.ingest_date !== undefined) {
		date = new Date(userInputSet.ingest_metadata.ingest_date);
		formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		headerHTML += '<div class="staticText">Ingest Date: '+ formatted_date +'</div>'
	}
	headerHTML += '</div><hr>';
	$('#ingestFormHeader').empty();
	$(headerHTML).appendTo('#ingestFormHeader');
	$('#ingestForm').empty();
	var inputHTML = '';
	inputHTML += '<div class="staticFormContent orig"><table><tr><th>Content</th><th>Metadata</th></tr>';
	for (var i = 0; i < userInputSet.content.length; i++) {
		var con = userInputSet.content[i];
		var date = new Date(con.version_data.entry_version_date);
		var formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
		inputHTML += '<tr><td>' + con.version_data.entry_title+' - ' + formatted_date +'</td>';
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
	var lfStorage = getLocalStorage("labFolderStorageFileFlat");
	var mdUserSets = getLocalStorage("metaDataUserSets");
	var metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	headerHTML += '<div class="metaFormUIField"><input required name="ingestName" type="text" value="' + title + '"></div>';
	if(mdUserSets != '') {
		var mdUserSetsJSON = JSON.parse(mdUserSets);
		headerHTML += '<select required name="ingest_header_metadata">\n';
		headerHTML += '<option selected value=""></option>';
		for (var j=0; j<mdUserSetsJSON.user_sets.length; j++){
			headerHTML += '<option value="'+mdUserSetsJSON.user_sets[j].set_id+'">'+mdUserSetsJSON.user_sets[j].name+'</option>';
		}
		headerHTML += '</select>';
	}
	headerHTML += '</div><hr>';
	$('#ingestFormHeader').empty();
	$(headerHTML).appendTo('#ingestFormHeader');
	$('#ingestForm').empty();
	var inputHTML = '';
	inputHTML += '<div class="metaFormElement"><label class="formDescriptor" for="ingest_content">';
	inputHTML += '<div class="metaFieldName">Data Set</div><div class="metaFieldDescription">Subtext</div></label>';
	if( lfStorage != '' && mdUserSets != '') {
		var lfStorageJSON = JSON.parse(lfStorage);
		inputHTML += '<div class="metaFormUIField metaFormCVField orig">';
		if (lfStorageJSON.length == 0){
			inputHTML += "No Data Sets have been created yet. Please create data packages before creating a lzv ingest!";
		}
		else {
		inputHTML += '<select class="select_content" name="ingest_content" required>\n';
		inputHTML += '<option selected value=""></option>';
		//fill with all data sets here
		for(var i = 0; i < lfStorageJSON.length; i++){
			// for (var j=0; j<lfStorageJSON.projects[i].entries.length; j++){
			// 	for(var k = 0; k < lfStorageJSON.projects[i].entries[j].versions.length; k++) {
					var date = new Date(lfStorageJSON[i].entry_version_date);
					var formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
					inputHTML += '<option value="'+lfStorageJSON[i].entry_version_id +'">'+lfStorageJSON[i].entry_title + ' - '+ formatted_date+'</option>';
			// 	}
			// }
		}
		inputHTML += '</select>';
		}
		if (mdUserSetsJSON.user_sets.length == 0){
			inputHTML += "No Metadata sets have been created yet. Please create Metadata sets before creating a lzv ingest!";
		}
		else {
		inputHTML += '<select name="ingest_metadata">\n';
		inputHTML += '<option selected value=""></option>';
		for (var j=0; j<mdUserSetsJSON.user_sets.length; j++){
			inputHTML += '<option value="'+mdUserSetsJSON.user_sets[j].set_id+'">'+mdUserSetsJSON.user_sets[j].name+'</option>';
		}
		inputHTML += '</select><button type="button" class="openMetaPopup" onclick="openMetaPopup(this);">?</button>';
		}
	}
	if (lfStorageJSON.length > 0 && mdUserSetsJSON.user_sets.length > 0){
	inputHTML += '<button type="button" class="duplicateMetaButton" id="ingest_content" onclick="duplicateIngestField(this);">+</button>';
	}
	inputHTML += '</div>';
	$(inputHTML).appendTo('#ingestForm');
	$('#ingestFormFooter').empty();
	var footerHTML = '<div id="footerButtonDiv">';
	footerHTML += '<button type="button" class="btn lzvButton" id="submitIngest" onclick="submitIngest();">Submit</button>';
	footerHTML += '<button type="button" class="btn lzvButton" id="saveIngest" onclick="saveActiveIngest();">Save</button>';
	//footerHTML += '<button type="button" class="btn lzvButton" id="copyMetaDataSet" onclick="copyActiveMetaDataSet();">Copy Set</button>';
	footerHTML += '</div>';
	$(footerHTML).appendTo('#ingestFormFooter');
	if (userInputSet) { //fill fields with values from user field
		if (userInputSet.metadata_userset_id!= '') {
			var header_metadata = $('#ingestFormHeader').find('select[name=ingest_header_metadata]');
			header_metadata.val(userInputSet.metadata_userset_id);
		}
		for(var i = 0; i < userInputSet.content.length; i++) {
			var field = userInputSet.content[i];
			if (i==0){
				var select_content = $('#ingestForm').find('select[name=ingest_content]');
				select_content.val(field.version_id);
				var select_metadata = $('#ingestForm').find('select[name=ingest_metadata]');
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
	var meta_id = $(clicked).siblings('select[name="ingest_metadata"]')[0].value;
	if (!meta_id) { //catch case when no metaset has been selected
		return;
	}
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	userSets= JSON.parse(getLocalStorage("metaDataUserSets"));
	var user_set = userSets.user_sets.find(set=>set.set_id == meta_id);
	var meta_struc = metaStructure.schemes.find(struc=>struc.identifier == user_set.identifier);
	var html = createPopupFormContent(meta_struc,user_set);
	$('#popupForm').empty();
	$(html).appendTo('#popupForm');
	prefillWithUserValue(user_set);
	$('#metaDataMainForm').hide();
	$('#popupForm').show();
}

function createPopupFormContent(metaStruc,userInputSet) {
	var	set_id = userInputSet.set_id;
	var returnHTML = '<div id="metaDataMainForm"><div id="metaDataFormHeader">';
	returnHTML += '<div id="title" set_id="'+ set_id +'" name="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div>';
	returnHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Metadata Set:</label>';
	returnHTML += '<div class="metaFormUIField"><input required name="metaSchemeName" type="text" value="' + userInputSet.name + '"></div></div><hr></div>';
	returnHTML += '<form id="metaDataForm">';
	for (var i=0; i<metaStruc.fields.length; i++){
		var field = metaStruc.fields[i];
		returnHTML += '<div class="metaFormElement"><label class="formDescriptor" for="';
		returnHTML += field.field_name + '" ';
		returnHTML += '><div class="metaFieldName">' + field.field_name.charAt(0).toUpperCase() + field.field_name.slice(1) + '</div><div class="metaFieldDescription">'+ field.field_description +'</div></label>';
		if (field.field_type != 'cv') {
			returnHTML += '<div class="metaFormUIField orig"><input ';
		}
		else {
			returnHTML += '<div class="metaFormUIField metaFormCVField orig"><select ';
		}
		returnHTML += 'name="' + field.field_name + '" ';
		if (field.field_mandatory){
			returnHTML += 'required ';
		}
		switch(field.field_type) {
			case 'string':
				returnHTML += 'type="text" ';
				break;
			case 'int':
				returnHTML += 'type="number" ';
				break;
			case 'float':
				returnHTML += 'type="number" step="any" ';
				break;
			case 'cv':
				returnHTML += '>\n';
				returnHTML += '<option selected value=""></option>';
				for (var j=0; j<field.field_options.length; j++){
					option = field.field_options[j];
					returnHTML += '<option value="'+option+'">'+option+'</option>';
				}
				break;
		}
		if (field.field_type != 'cv') {
			if(field.field_verification) {
				returnHTML += 'pattern="' + field.field_verification + '" ';
			}
			returnHTML += '>';
		}
		else {
			returnHTML += '</select>';
		}
		if(field.field_multiple) {
			returnHTML += '<button type="button" class="duplicateMetaButton" id="' + field.field_name +'" onclick="duplicateMetaDataField(this);">+</button>';
		}
		returnHTML += '</div></div>';
	}
	returnHTML += '</form><div id="metaDataFormFooter">';
	returnHTML += '<div id="footerButtonDiv">';
	returnHTML += '<button type="button" class="btn lzvButton" id="saveAndCloseMetaDataForm" onclick="saveAndCloseMetaPopup();">Save & Close</button>';
	returnHTML += '<button type="button" class="btn lzvButton" id="closeMetaDataForm" onclick="closeMetaPopup();">Close</button>';
	// footerHTML += '<button type="button" class="btn lzvButton" id="exportToXML" onclick="exportSetToXML();">Export to XML</button>';
	// function exportSetToXML() {}
	returnHTML += '</div></div>';
	return returnHTML;
}

function saveAndCloseMetaPopup() {
	saveActiveMetaDataSet();
	closeMetaPopup();
}

function prefillWithUserValue(userInputSet) {
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

function closeMetaPopup() {
	$('#metaDataMainForm').show();
	$('#popupForm').hide();
}

function duplicateIngestField(clicked, prefillValueIngest = null, prefillValueMetadata = null){
	var tmp = $(clicked).parent('.orig').clone();
	tmp.children(':button').remove();
	tmp.removeClass('orig');
	tmp.addClass('clone');
	var select_content = tmp.children('select[name=ingest_content]');
	var select_metadata = tmp.children('select[name=ingest_metadata]');
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
	var popup_button = '<button type="button" class="openMetaPopup" onclick="openMetaPopup(this);">?</button>';
	var removeButton = '<button type="button" class="removeMetaFieldButton" onclick="removeIngestField(this);">-</button>';
	$(popup_button).appendTo(tmp);
	$(removeButton).appendTo(tmp);
	tmp.appendTo($(clicked).parent().parent());
}

function removeIngestField(clicked){
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

function getActiveIngest() {
	var saveData = {};
	var formHeaderFields = $('#ingestFormHeader');
	var formFieldsInputContent = $('#ingestForm').find('select[name="ingest_content"]'); 
	var formFieldsInputMeta = $('#ingestForm').find('select[name="ingest_metadata"]'); 
	saveData.name = formHeaderFields.find('input')[0].value;
	saveData.metadata_userset_id = formHeaderFields.find('select[name="ingest_header_metadata"]')[0].value;
	saveData.metadata = searchMetaDataUserSetsByID(saveData.metadata_userset_id);
	saveData.ingest_id = formHeaderFields.find('#title').attr('ingest_id');
	saveData.state = 'NEW';
	saveData.content = [];
	var lfStorage = JSON.parse(getLocalStorage("labFolderStorageFileFlat"));
	for (var i = 0 ; i < formFieldsInputContent.length; i++) {
		var content_value = '';
		var content_data = {};
		if (formFieldsInputContent[i].value) {
			content_value = formFieldsInputContent[i].value;
			content_data = lfStorage.find(set=>set.entry_version_id == content_value);
		}
		var meta_value = '';
		if (formFieldsInputMeta[i].value) {
			meta_value = formFieldsInputMeta[i].value;
		}
		saveData.content.push({'version_id' : content_value, 'version_data' : content_data, 'content_origin' : "labfolder", 'metadata_userset_id' : meta_value, 'metadata_userset' : searchMetaDataUserSetsByID(meta_value)});
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
				getSubmittedIngests();
			}
		}
	}
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
	saveInLocalStorage('userIngests', payload);
	sendUserIngestsToServer();
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
	saveInLocalStorage('userIngests', saveData);
	unsaved = false;
	sendUserIngestsToServer();
}

function newLZVIngest(clicked) {
	createFormForNewIngest();
}