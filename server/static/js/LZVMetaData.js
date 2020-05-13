//Initialization Function
$( document ).ready(function() {
	getMetaDataStructureInformation();
	// metaStruc = getCookie("metaDataStructs");
	createFormForNewSchemeItem('DC1.1')
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
				parseMetaStructures(parsedJSON);	
			}
		}
	}
	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}

//TODO -> also backend for this!
function getMetaDataUserSchemes(){}

//TODO -> Save Active Metadataset on server. Also reload the page sidebar.
function saveActiveMetaDataSet(clicked) {

}
function createFormForNewSchemeItem(clickedScheme){
	metaStructure = JSON.parse(getCookie("metaDataStructs"));
	clickedID = 'DC1.1Mini';//$(clickedScheme).attr('id');
	var clickedStruc = metaStructure.schemes.find(struc=>struc.identifier == clickedID);
	if(clickedStruc) {
		fillMetaDataForm(clickedStruc);
	}
}


//this function creates a form for creation of meta data
//if userInput = NULL a new metaDataSet is created, if not null then an existing scheme is modified and already existing entries are displayed
//metaStruc a single metaStrucuture JSON object
//userInput the correlated userMetaSet for that struc
function fillMetaDataForm(metaStruc,userInput){
	setCookie("activeMetaDataForm",JSON.stringify(metaStruc));
	var headerHTML = '<div id="' + metaStruc.identifier + '">' + metaStruc.title + " v" + metaStruc.version + '</div>';
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
	var footerHTML = '<div id="footerButtonDiv"><button type="button" id="saveMetaDataForm" onclick="saveMetaDataSet(this);">Save</button></div>';
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

function parseMetaStructures(metaStruc) {
	$('#newItemsSubItems').empty();
	var append = '';
	for (scheme of metaStruc.schemes) {
		append += '<button class="sideBarItem sideBarSubItem" id="' + scheme.identifier + '" onclick="createFormForNewSchemeItem(this);">' + scheme.title + ' ' + scheme.version + '</button><br>';
	}
	$(append).appendTo('#newItemsSubItems');
	//create local storage of information -> cookie
	//update sidebar with information about schemes

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

