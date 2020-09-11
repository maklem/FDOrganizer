$( document ).ready(function() {
	getIngestsToReview();
	fillSidebar();
});

function toggleDisplayToReview(clicked) {
	$(clicked).parent().children('#toReviewIngestsSubItems, #reviewedIngestsSubItems').toggle();
	if($(clicked).children(".arrow").html() == "v") {
		$(clicked).children(".arrow").text("x");
	}
	else {
		$(clicked).children(".arrow").text("v");
	}
}

function fillSidebar() {
	var submittedIngests = JSON.parse(getLocalStorage("submittedIngests"));
	if(submittedIngests) {
	$('#toReviewIngestsSubItems').empty();
	$('#reviewedIngestsSubItems').empty();
	var appendToReview = '';
	var appendToSubmitted = '';
	for (var ingest of submittedIngests) {
		if (ingest.state == "REVIEW") {
			appendToReview += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + ingest.ingest_id + '" onclick="createFormForToReviewIngest(' + ingest.ingest_id + ');">' + ingest.name + '</button><div class="round-button">';
			appendToReview += '</div></div>';
		}
		if (ingest.state == "INGESTED") {
			appendToSubmitted += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" id="' + ingest.ingest_id + '" onclick="createFormForSubmittedIngest(' + ingest.ingest_id + ');">' + ingest.name + '</button><div class="round-button">';
			appendToSubmitted += '</div></div>';
		}
	}
	$(appendToReview).appendTo('#toReviewIngestsSubItems');
	$(appendToSubmitted).appendTo('#reviewedIngestsSubItems');
	}
}

function getIngestsToReview() {
	var url = baseURL +  '/ingest/toreview';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				if (xhttp.response != "") {
					parsedJSON =  JSON.parse(xhttp.response);
					setLocalStorage("submittedIngests", JSON.stringify(parsedJSON.docs));
				}
			}
		}
	};
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();
}

function createFormForToReviewIngest(clicked_id) {
	var submittedIngests = JSON.parse(getLocalStorage("submittedIngests"));
	var display_ingest = submittedIngests.find(set=>set.ingest_id == clicked_id);
	fillToReviewIngestForm(display_ingest);
}

function createFormForSubmittedIngest(clicked_id) {
	var submittedIngests = JSON.parse(getLocalStorage("submittedIngests"));
	var display_ingest = submittedIngests.find(set=>set.ingest_id == clicked_id);
}

function fillToReviewIngestForm(userInputSet) {
	console.log(JSON.stringify(userInputSet));
	var headerHTML = '<div id="title" ingest_id="'+ userInputSet.ingest_id +'" name="ingestTitle">Submitted Ingest</div><hr>';
	headerHTML += '<div class="staticFormContent orig">';
	headerHTML += '<div class="staticText">Name of Ingest: ' + userInputSet.name + '</div>';
	headerHTML += '<div class="staticText">Ingest Metadata: '+ userInputSet.metadata.name +'</div>';
	headerHTML += '<div class="staticText">State: '+ userInputSet.state +'</div>';
	var date = new Date(userInputSet.ingest_metadata.submit_date);
	var formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
	headerHTML += '<div class="staticText">Submission Date: '+ formatted_date +'</div>';
	if(userInputSet.ingest_metadata.review_date !== undefined) {
		date = new Date(userInputSet.ingest_metadata.review_date);
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

function createReviewPopupFormContent(metaStruc,userInputSet) {
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
