function getMetaDataStructureInformation(updateSideBar = true){
	interface_get_metadata_structure_information(function(xhttp_repsonse){
		parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
        setLocalStorage("metaDataStructs", JSON.stringify(parsedJSON));
        if(updateSideBar) {
            updateSideBarMetaSchemes(parsedJSON);
        }
	});
}

function getMetaDataExportDefinitions(){
	interface_get_metadata_export_definitions(function(xhttp_response){
		parsedJSON =  JSON.parse(JSON.parse(xhttp.response));
        setLocalStorage("metadata_export_definitions", JSON.stringify(parsedJSON));
	});
}

function getMetaDataExportMappings(){
	interface_get_metadata_export_mappings(function(xhttp_response) {
		parsedJSON =  JSON.parse(JSON.parse(xhttp_response));
        setLocalStorage("metadata_export_mappings", JSON.stringify(parsedJSON));
    });
}

function getMetaDataUserSets(updateSideBar = true) {
	interface_get_metadata_usersets(function (xhttp_response) {
		parsedJSON =  JSON.parse(xhttp_response);
        setLocalStorage("metaDataUserSets", JSON.stringify(parsedJSON));
        if(updateSideBar) {
	        updateSideBarUserSets(parsedJSON);
        }
	});
}

function delete_user_metaset(delete_set) {
	interface_delete_metadata_usersets(delete_set, function() {
		getMetaDataUserSets(true);
	});
}

function sendUserMetaSetsToServer(new_set) {
	interface_store_metadata_usersets(new_set, function() {
		getMetaDataUserSets(true);
		unsaved = false;
	});
}

function searchMetaDataUserSetsByID(id) {
	var c_str = getLocalStorage("metaDataUserSets");
	cookie_data = JSON.parse(c_str);
	return cookie_data.find(set=>set.set_id == id);
}

function crawl_meta_group(group) {
	var output = {"group_identifier" : $(group).attr('id'), "fields" : []};
	var group_subgroups = $(group).children().children('.meta_form_group');
	for (var subgroup of group_subgroups) {
		var sub_output = crawl_meta_group(subgroup);
		if (sub_output.fields.length > 0){
			output.fields.push(sub_output);
		}
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
	// if (output.fields.length == 0) {
	// 	return {};
	// }
	// console.log(output);
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
		var output = crawl_meta_group(form_field_groups[j]);
		if (output.fields.length > 0) {
			saveData.fields.push(output);
		}
	}
	var form_field_input = $('#metaDataForm').children('.meta_form_container').children('.meta_form_field').children('.metaFormElement');
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
	return saveData;
}

function saveActiveMetaDataSet() {
	saveData = getActiveMetaDataSet();
	if(saveData.name == ''){
		alert('Please enter a name for the data set before saving!');
		return;
	}
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
		delete_user_metaset(delete_set);
	}
}

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

function toggle_visibility_meta_form_container(clicked) {
	$(clicked).parent().children('.meta_form_entity').toggle();
}

function createHTMLOutputForMetaSchemeEntity(field, prefill_values = undefined, create_dupe=false,create_container=false) {
	var output = '';
	if (field.entity_type == "GROUP") {
		if (create_dupe)
		{
			output += '<div class="meta_form_group clone" style="display:block;" id="' + field.identifier + '">';
		}
		else
		{
			output += '<div class="meta_form_container">';
			output += '<button type="button" class="meta_form_group_descriptor';
			if (field.mandatory) {
				output += ' mandatory_entity';
			}
			output += '" onclick="toggle_visibility_meta_form_container(this);">';
			output += '<span class="meta_group_name">' + field.name.charAt(0).toUpperCase() + field.name.slice(1) + '</span>';
			if (field.mandatory) {
				output += '<span class="mandatory_descriptor required_entity_descriptor">required</span>';
			}
			else {
				output += '<span class="mandatory_descriptor optional_entity_descriptor">optional</span>';
			}
			output += '<p><span class="meta_group_description">';
			if('description' in field) {
				output += field.description;
			}
			else {
				output += '&nbsp';
			}
			output += '</span></button>';
			output += '<div class="meta_form_group meta_form_entity orig" id="' + field.identifier + '">';
		}
		for(var i=0; i<field.fields.length; i++){
			if(prefill_values){
			if (field.fields[i].entity_type == "GROUP")
			{
				var prefills = prefill_values.fields.filter(f=>f.group_identifier == field.fields[i].identifier);
				if (prefills.length > 0) {
				for(var prefill of prefills){
					output += createHTMLOutputForMetaSchemeEntity(field.fields[i],prefill);
				}
				}
				else {
					output += createHTMLOutputForMetaSchemeEntity(field.fields[i]);
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
		if(create_container){
			output += '<div class="meta_form_container">';
			output += '<button type="button" class="meta_form_group_descriptor';
			if (field.mandatory) {
				output += ' mandatory_entity';
			}
			output += '" onclick="toggle_visibility_meta_form_container(this);">';
			output += '<span class="meta_group_name">' + field.name.charAt(0).toUpperCase() + field.name.slice(1) + '</span>';
			if (field.mandatory) {
				output += '<span class="mandatory_descriptor required_entity_descriptor">required</span>';
			}
			else {
				output += '<span class="mandatory_descriptor optional_entity_descriptor">optional</span>';
			}
			output += '<p><span class="meta_group_description">';
			if('description' in field) {
				output += field.description;
			}
			else {
				output += '&nbsp';
			}
			output += '</span></button>';
			output += '<div class="meta_form_field meta_form_entity orig" id="' + field.identifier + '">';
		}
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
		if(create_container){
			output += "</div></div>";
		}
	}
	return output;
}

function create_htmlfield_from_template(field, value=undefined, dupe=false){
	var output = '';
		output += '<div class="metaFormElement"><label class="formDescriptor" for="';
		output += field.identifier + '" ';
		output += '><div class="metaFieldName">' + field.name.charAt(0).toUpperCase() + field.name.slice(1);
		if (field.mandatory) {
			output += '<span class="mandatory_descriptor required_entity_descriptor">required</span>';
		}
		else {
			output += '<span class="mandatory_descriptor optional_entity_descriptor">optional</span>';
		}
		output +=  '</div>';
		if (field.identifier !== undefined) {
			output += '<div class="metaFieldDescription">';
			if('description' in field) {
				output += field.description;
			}
			else {
				output += '&nbsp';
			}
			output += '</div></label>';
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
	for (var i=0; i<metaStruc.fields.length; i++){
		var inputHTML = '';
		var field = metaStruc.fields[i];
		if(hasUserInput) {
			if (field.entity_type == "GROUP")
			{
				var prefills = userInputSet.fields.filter(f=>f.group_identifier == field.identifier);
				if (prefills.length > 0){
				for(var prefill of prefills){
					inputHTML += createHTMLOutputForMetaSchemeEntity(field,prefill,false);
				}
				}
				else {
					inputHTML += createHTMLOutputForMetaSchemeEntity(field,undefined,false);
				}
			}
			else
			{
				var prefill = undefined;
				prefill = userInputSet.fields.find(f=>f.field_identifier == field.identifier);
				inputHTML += createHTMLOutputForMetaSchemeEntity(field, prefill, false, create_container=true);
			}
		}
		else {
			inputHTML =  createHTMLOutputForMetaSchemeEntity(field, undefined, create_dupe=false, create_container=true);
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
	var dupe_group = search_for_group(meta_struc, identifier);
	if(typeof dupe_group == "boolean") {return;}
	var html_append = createHTMLOutputForMetaSchemeEntity(dupe_group, prefill_values, true,);
	$(html_append).insertAfter($(clicked));
}

function remove_meta_group(clicked) {
	var identifier = $(clicked).parent('.clone').remove();
}


function duplicateMetaDataField(clicked,prefillValue = null){
	var tmp = $(clicked).parent().parent().clone();
	tmp.find(':button').remove();
	// tmp.removeClass('orig');
	tmp.addClass('dupe');
	var input = tmp.find('input');
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
	$(removeButton).appendTo(tmp.children('.table_form_ui_field'));
	tmp.insertAfter($(clicked).parent().parent());
}

function removeMetaDataField(clicked){
	if ($(clicked).parent().children('input, select').val() != ''){
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
		append += '<button class="sidebarItem sidebarSubItem" id="' + scheme.identifier + '" onclick="createFormForNewSchemeItem(this);">' + scheme.title + ' ' + scheme.version + '</button>';
	}
	}
	$(append).appendTo('#newItemsSubItems');
}

function updateSideBarUserSets(userSets){
	$('#myItemsSubItems').empty();
	var append = '';
	for (var set of userSets) {
		append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + set.set_id + '" onclick="createFormForExistingSchemeSet(this);">' + set.name + '</button><div class="round-button"><button class="btn deleteSetButton" set_id="'+ set.set_id + '" onclick="deleteMetaDataSet(this);"><span>-</span></button></div></div>';
	}
	$(append).appendTo('#myItemsSubItems');
}

