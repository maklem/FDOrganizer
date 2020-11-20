function getMetaDataStructureInformation(updateSideBar = true){
	var url = baseURL +  '/metadata/structures';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				setLocalStorage("metaDataStructs", JSON.stringify(parsedJSON));
				if(updateSideBar) {
					updateSideBarMetaSchemes(parsedJSON);	
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

function getMetaDataExportDefinitions(){
	var url = baseURL +  '/metadata/export_definitions';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				setLocalStorage("metadata_export_definitions", JSON.stringify(parsedJSON));
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

function getMetaDataExportMappings(){
	var url = baseURL +  '/metadata/export_mappings';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
				setLocalStorage("metadata_export_mappings", JSON.stringify(parsedJSON));
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

function getMetaDataUserSets(updateSideBar = true) {
	var url = baseURL +  '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("metaDataUserSets", JSON.stringify(parsedJSON));
					if(updateSideBar) {
						updateSideBarUserSets(parsedJSON);
					}
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function deleter_user_metaset(delete_set) {
	var url = baseURL + '/metadata/user/delete';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				getMetaDataUserSets(true);
			}
		}
	};
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(delete_set));
}

function sendUserMetaSetsToServer(new_set) {
	var url = baseURL + '/metadata/user';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				getMetaDataUserSets(true);
			}
		}
	};
	xhttp.open('PUT', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(new_set));
}

function searchMetaDataUserSetsByID(id) {
	var c_str = getLocalStorage("metaDataUserSets");
	cookie_data = JSON.parse(c_str);
	return cookie_data.find(set=>set.set_id == id);
}

function crawl_meta_group(group) {
	var output = {"group_identifier" : $(group).attr('id'), "fields" : []};
	var group_subgroups = $(group).children('.meta_form_group');
	for (var subgroup of group_subgroups) {
		output.fields.push(crawl_meta_group(subgroup));
	}
	var group_fields = $(group).children('.metaFormElement');
	for (var gr_field of group_fields) {
		var fields = $(gr_field).find(':input');
		for(var field of fields){
		if(field.value) {
			var existing_field = output.fields.find(f=>f.field_identifier == field.name);
			if (existing_field) {
				existing_field.values.push(field.value);
			}
			else {
				output.fields.push({"field_identifier" : field.name, "values" : [field.value]});
			}
		}
	}
	}
	return output;
}

function getActiveMetaDataSet() {
	var saveData = {};
	var formHeaderFields = $('#metaDataFormHeader');
	saveData.name = formHeaderFields.find('input')[0].value;
	saveData.identifier = formHeaderFields.find('#title').attr('name');
	saveData.set_id = formHeaderFields.find('#title').attr('set_id');
	saveData.fields = [];
	var form_field_groups = $('#metaDataForm').children().children('.meta_form_group');
	for (var j = 0; j <form_field_groups.length; j++) {
		saveData.fields.push(crawl_meta_group(form_field_groups[j]));
	}
	var form_field_input = $('#metaDataForm').children().children('.metaFormElement');
	for (var gr_field of form_field_input) {
		var fields = $(gr_field).find(':input');
		for(var field of fields){
		if(field.value) {
			var name = field.name;
			var saveDataField = saveData.fields.find(f=>f.field_identifier == name);
			if (saveDataField) {
				saveDataField.values.push(field.value);

			}
			else {
				saveData.fields.push({"field_identifier" : field.name, "values" : [field.value]});
			}
		}
		}
	}
	// console.log(JSON.stringify(saveData));
	return saveData;
}

function saveActiveMetaDataSet() {
	saveData = getActiveMetaDataSet();
	if(saveData.name == ''){
		alert('Please enter a name for the data set before saving!');
		return;
	}
	unsaved = false;
	sendUserMetaSetsToServer(saveData);
}

function copyActiveMetaDataSet() {
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	userSets= JSON.parse(getLocalStorage("metaDataUserSets"));
	clicked_set_id = $('#title').attr('set_id');
	var user_set = userSets.find(set=>set.set_id == clicked_set_id);
	if (user_set && user_set !== null){
		var meta_struc = metaStructure.find(struc=>struc.identifier == user_set.identifier);
		fillMetaDataForm(meta_struc,user_set,true);
	}
}

//TODO fill! Also Button required to do this!
//TODO: This needs to be reworked, so deleting is done on server after checking for correct set_id, since this provides entry for falsely deleting a not self owned entry.
function deleteMetaDataSet(clicked) {
	if(confirm("Are you sure that you want to delete this metadata set? This can not be undone!")){
		var c_str = getLocalStorage("metaDataUserSets");
		clicked_id = $(clicked).attr('set_id');
		cookie_data = JSON.parse(c_str);
		var delete_set = cookie_data.find(set=>set.set_id == clicked_id);
		deleter_user_metaset(delete_set);
	}
}

// function exportSetToJSON() {
// 	var print_json = {};
// 	let data = getActiveMetaDataSet();
// 	if(data.fields.length == 0) {
// 		return;
// 	}
// 	for (var i = 0; i < data.fields.length; i++) {
// 		var field = data.fields[i];
// 		if (field.values.length > 1) {
// 			print_json[field.field_name] = [];
// 			for(var j = 0; j < field.values.length; j++) {
// 				var value = field.values[j];
// 				print_json[field.field_name].push(value);
// 			}
// 		}
// 		else{
// 			print_json[field.field_name] = field.values[0];
// 		}
// 	}
// 	var new_page = window.open();
//   	new_page.document.write(JSON.stringify(print_json));
// }

// function exportSetToDC() {
//   let data = getActiveMetaDataSet();
//   if(data.fields.length == 0) {
// 		return;
// 	}
//   let print_text = '';
//   for(var i = 0; i < data.fields.length; i++){
//   	for(var j = 0; j < data.fields[i].values.length; j++) {
//   		print_text += data.fields[i].field_name + ': ' + data.fields[i].values[j] + "<br>";
//   }
//   }
//   var new_page = window.open();
//   new_page.document.write(print_text);
// }

function createFormForNewSchemeItem(clicked){
    if(unsaved){
    	if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
        	return;
        }
    }
	metaStructure = JSON.parse(getLocalStorage("metaDataStructs"));
	clicked_id = $(clicked).attr('id');
	var clickedStruc = metaStructure.find(struc=>struc.identifier == clicked_id);
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
	var user_set = userSets.find(set=>set.set_id == clicked_set_id);
	var meta_struc = metaStructure.find(struc=>struc.identifier == user_set.identifier);
	fillMetaDataForm(meta_struc,user_set);
}

function toggle_visibility_meta_form_group(clicked) {
	$(clicked).parent().children('.meta_form_group').toggle();
}

function createHTMLOutputForMetaSchemeEntity(field, prefill_values = undefined, create_dupe=false) {
	var output = '';
	if (field.entity_type == "GROUP") {
		// console.log(field.identifier);
		// console.log("Field");
		// console.log(JSON.stringify(field));
		// console.log("prefill:");
		// console.log(JSON.stringify(prefill_values));
		if (create_dupe)
		{
			output += '<div class="meta_form_group clone" style="display:block;" id="' + field.identifier + '">';
		}
		else
		{
			output += '<div class="meta_form_container">';
			output += '<button class="meta_form_group_descriptor" onclick="toggle_visibility_meta_form_container(this);">';
			output += '<p class="meta_group_name">' + field.name.charAt(0).toUpperCase() + field.name.slice(1) + '</p><p class="meta_group_description">'+ field.description +'</p></button>';
			output += '<div class="meta_form_group orig" id="' + field.identifier + '">';
		}
		for(var i=0; i<field.fields.length; i++){
			if(prefill_values){
			if (field.fields[i].entity_type == "GROUP")
			{
				// console.log(field.fields[i].identifier);
				// console.log("field[i]");
				// console.log(JSON.stringify(field.fields[i]));
				var prefills = prefill_values.fields.filter(f=>f.group_identifier == field.fields[i].identifier);
				for(var prefill of prefills){
					output += createHTMLOutputForMetaSchemeEntity(field.fields[i],prefill);
				}
			}
			else
			{
				var prefill = undefined;
				prefill = prefill_values.fields.find(f=>f.field_identifier == field.fields[i].identifier);
				output += createHTMLOutputForMetaSchemeEntity(field.fields[i],prefill);
			}
			}
			else {
				output += createHTMLOutputForMetaSchemeEntity(field.fields[i]);
			}
		}
		if(field.multiple) {
			if(create_dupe) {
				output += '<button type="button" class="meta_form_button remove_button" onclick="remove_meta_group(this);">delete</button>';
			}
			else{
				output += '<button type="button" class="meta_form_button duplicate_button" id="' + field.identifier + '"onclick="duplicate_meta_group(this);">duplicate</button>';
				output += '</div>';
			}
		}
		output += '</div>';
	}
	else { //entity_type == FIELD
		if (prefill_values)
		{
			for(var j = 0; j < prefill_values.values.length; j++){
				if (j ==0)
				{
					output += create_htmlfield_from_template(field,prefill_values.values[j],false);
				}
				else
				{
					output += create_htmlfield_from_template(field,prefill_values.values[j],true);
				}
			}
		}
		else
		{
			output += create_htmlfield_from_template(field);
		}
	}
	return output;
}

function create_htmlfield_from_template(field, value=undefined, dupe=false){
	var output = '';
	output += '<div class="metaFormElement"><label class="formDescriptor" for="';
		output += field.identifier + '" ';
		output += '><div class="metaFieldName">' + field.name.charAt(0).toUpperCase() + field.name.slice(1) + '</div>';
		if (field.identifier !== undefined) {
			output += '<div class="metaFieldDescription">'+ field.description +'</div></label>';
		}
		if (field.field_type != 'cv') {
			if (value)
			{output += '<div class="table_form_ui_field orig"><input value="' + value + '"';}
		else
			{output += '<div class="table_form_ui_field orig"><input value=""';}
		}
		else {
			output += '<div class="table_form_ui_field metaFormCVField orig"><select ';
		}
		output += 'name="' + field.identifier + '" ';
		if (field.mandatory){
			output += 'required ';
		}
		switch(field.field_type) {
			case 'string':
				output += 'type="text" ';
				break;
			case 'int':
				output += 'type="number" ';
				break;
			case 'float':
				output += 'type="number" step="any" ';
				break;
			case 'cv':
				output += '>\n';
				if(value){
					output += '<option value=""></option>';
				}
				else{
					output += '<option selected value=""></option>';
				}
				for (var option of field.field_options){
					if(option == value)
					{
						output += '<option selected value="'+option+'">'+option+'</option>';
					}
					else
					{
						output += '<option value="'+option+'">'+option+'</option>';
					}
				}
				break;
		}
		if (field.field_type != 'cv') {
			if(field.field_verification) {
				output += 'pattern="' + field.field_verification + '" ';
			}
			output += '>';
		}
		else {
			output += '</select>';
		}
		if(field.multiple) {
			if (!dupe)
			{
				output += '<button type="button" class="meta_form_button duplicate_button" id="' + field.name +'" onclick="duplicateMetaDataField(this);">+</button>';
			}
			else{
				output += '<button type="button" class="meta_form_button remove_button" onclick="removeMetaDataField(this);">-</button>';
			}
		}
		output += '</div></div>';
	return output;
}

//this function creates a form for creation of meta data
//if userInput = NULL a new metaDataSet is created, if not null then an existing scheme is modified and already existing entries are displayed
//metaStruc a single metaStrucuture JSON object
//userInput the correlated userMetaSet for that struc, which is required when a existing set should be updated
function fillMetaDataForm(metaStruc,userInputSet = null, recreateID = false, is_not_popup_form = true){
	var  hasUserInput = false;
	var set_id;
	if(userInputSet !== null) {
		hasUserInput = true;
		set_id = userInputSet.set_id;
	}
	if(recreateID || userInputSet === null){
		set_id = uuidv4();
	}
	var headerHTML = '<div id="title" set_id="'+ set_id +'" name="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div></div>';
	headerHTML += '<div class="metaFormElement"><label class="formDescriptor" for="metaSchemeName">Name of Metadata Set:</label>';
	var title = (hasUserInput) ? userInputSet.name : '';
	if( recreateID) {
		title = '';
	}
	headerHTML += '<div class="table_form_ui_field"><input required name="metaSchemeName" type="text" value="' + title + '"></div></div><hr>';
	$('#metaDataFormHeader').empty();
	$(headerHTML).appendTo('#metaDataFormHeader');
	$('#metaDataForm').empty();
	console.log("Meta");
	console.log(JSON.stringify(metaStruc));
	console.log("uis");
	console.log(JSON.stringify(userInputSet));
	for (var i=0; i<metaStruc.fields.length; i++){
		var inputHTML = '';
		var field = metaStruc.fields[i];
		if(hasUserInput) {
			if (field.entity_type == "GROUP")
			{
				var prefills = userInputSet.fields.filter(f=>f.group_identifier == field.identifier);
				for(var prefill of prefills){
					inputHTML += createHTMLOutputForMetaSchemeEntity(field,prefill,false);
				}
			}
			else
			{
				var prefill = undefined;
				prefill = userInputSet.fields.find(f=>f.field_identifier == field.identifier);
				inputHTML += createHTMLOutputForMetaSchemeEntity(field,prefill,false);
			}
		}
		else {
			inputHTML =  createHTMLOutputForMetaSchemeEntity(field, create_dupe=false);
		}
		$(inputHTML).appendTo('#metaDataForm');
	}
	if(is_not_popup_form){
		$('#right_sidebar').empty();
		var footerHTML = '<div id="sidebar_buttons"><div id="general_metadata_buttons">';
		footerHTML += '<button type="button" class="btn lzvButton" id="saveMetaDataForm" onclick="saveActiveMetaDataSet();">Save</button>';
		footerHTML += '<button type="button" class="btn lzvButton" id="copyMetaDataSet" onclick="copyActiveMetaDataSet();">Copy Set</button>';
		footerHTML += '</div><div id="export_metadata_buttons">';
		footerHTML += add_export_buttons_to_sidebar();
		footerHTML += '</div></div>';
		$(footerHTML).appendTo('#right_sidebar');
	}
	else {
		$('#metaDataFormFooter').empty();
		var footerHTML = '<div id="general_metadata_buttons">';
		footerHTML += '<button type="button" class="btn lzvButton" id="saveMetaDataForm" onclick="saveActiveMetaDataSet();">Save</button>';
		footerHTML += '<button type="button" class="btn lzvButton" id="closeMetaDataForm" onclick="closeMetaPopup();">Close</button>';
		footerHTML += '</div>';
		$(footerHTML).appendTo('#metaDataFormFooter');
	}
}

function add_export_buttons_to_sidebar() {
	var output = '';
	var scheme_identifier = get_active_scheme_identifier();
	var export_definitions = JSON.parse(getLocalStorage("metadata_export_definitions"));
	var export_mappings = JSON.parse(getLocalStorage("metadata_export_mappings"));
	for (var ex of export_definitions) {
		var map = export_mappings.find(x=>x.identifier_source_schemes.includes(scheme_identifier) && x.identifier_target_export.includes(ex.identifier));
		if(map) {
			output += '<button type="button" class="btn lzvButton" map_id="' + map.identifier + '" ex_id="' + ex.identifier + '" onclick="export_set_to_target(this);">Export to '+ ex.name + '</button>';
		}
	}
	return output;
}

function export_set_to_target(clicked) {
	var target_export_identifier = $(clicked).attr('ex_id');
	var target_mapping_identifier = $(clicked).attr('map_id');
	var source_scheme_identifier = get_active_scheme_identifier();
	var export_definitions = JSON.parse(getLocalStorage("metadata_export_definitions"));
	var export_mappings = JSON.parse(getLocalStorage("metadata_export_mappings"));
	let export_handler = new metadata_export_handler(export_definitions.find(x=>x.identifier == target_export_identifier), export_mappings.find(x=>x.identifier == target_mapping_identifier))
	var export_text = export_handler.create_export(getActiveMetaDataSet());
	// var new_page = window.open();
	// window.open(export_text, "PopUpTextbox",  "width=270,height=300,top=200,left=200,toolbars=no,scrollbars=no,status=no,resizable=no"); 
	open_export_popup(export_text);
	// new_page.document.open ('content-type: text/xml');
	// new_page.document.write(export_text);
}

function open_export_popup(text) {
	$('#popupForm').empty();
	var html_text = '<textarea id="txtXML" readonly="readonly">' + String(text) +' </textarea>';
	html_text += '<button type="button" class="btn lzvButton" id="closeMetaDataForm" onclick="close_export_popup();">Close</button>';
	$(html_text).appendTo('#popupForm');
	$('#metaDataMainForm').hide();
	$('#right_sidebar').hide();

	$('#popupForm').show();
}

function close_export_popup() {
	$('#metaDataMainForm').show();
	$('#right_sidebar').show();
	$('#popupForm').hide();
}

//expects the user set for input
function prefill_form_input(content) {
	console.log("prefill");
	var done_groups = {};
	for( var item of content.fields){
		if (item.group_identifier && !done_groups.group_identifier) //group
		{
			done_groups[item.group_identifier] = true;
			var groups = content.fields.filter(f=>f.group_identifier == item.group_identifier);
			for (var i = 1; i < groups.length; i++){
				duplicate_meta_group_by_id(item.group_identifier,groups[i]);
			}
		}
		else //field
		{

		}
	}
}

function get_active_scheme_identifier(){
	return $('#metaDataFormHeader').find('#title').attr('name');
}
//search for group in meta schemes (struc), and returns strucuture downwoards from this group as json object
function search_for_group(struc, identifier) {
	console.log(struc);
	for (var field of struc.fields) {
		if(field.entity_type == 'GROUP') {
			if(field.identifier == identifier){
				return field;
			}
			else
			{
				var val = search_for_group(field,identifier);
				if (typeof val != "boolean") {
					return val;
				}

			}
		}
		else { //type == Field
			continue;
		}
	}
	return false;
}

function duplicate_meta_group(clicked, prefill_values = null) {
	var identifier = $(clicked).parent('.orig').attr('id');
	var metaStructures = JSON.parse(getLocalStorage("metaDataStructs"));
	var meta_struc = metaStructures.find(struc => struc.identifier == get_active_scheme_identifier());
	console.log("Meta Struc:");
	console.log(meta_struc);
	var dupe_group = search_for_group(meta_struc, identifier);
	if(typeof dupe_group == "boolean") {return;}
	var html_append = createHTMLOutputForMetaSchemeEntity(dupe_group, prefill_values, true,);
	$(html_append).insertAfter($(clicked).parent('.orig'));
}

function remove_meta_group(clicked) {
	var identifier = $(clicked).parent('.clone').remove();
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
	var removeButton = '<button type="button" class="meta_form_button remove_button" onclick="removeMetaDataField(this);">-</button>';
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
	for (var scheme of metaStruc) {
		if(scheme.active){
		append += '<button class="sidebarItem sidebarSubItem" id="' + scheme.identifier + '" onclick="createFormForNewSchemeItem(this);">' + scheme.title + ' ' + scheme.version + '</button><br>';
	}
	}
	$(append).appendTo('#newItemsSubItems');
}

function updateSideBarUserSets(userSets){
	console.log("updateSideBarUserSets");
	$('#myItemsSubItems').empty();
	var append = '';
	for (var set of userSets) {
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

