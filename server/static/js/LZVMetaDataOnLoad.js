//Initialization Function
$( document ).ready(function() {
	getMetaDataStructureInformation(true);
	getMetaDataUserSets(true);
    getMetaDataExportDefinitions();
    getMetaDataExportMappings();
	if(checkLZVLogin())
	{
		$('#logout_lzv').show();
	}
	metaStruc = getLocalStorage("metaDataStructs");
});

var unsaved = false;

$(":input").change(function(){ //triggers change in all input fields including text type
    unsaved = true;
});

// Monitor dynamic inputs
$(document).on('change', 'input, select', function(){ //triggers change in all input fields including text type
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
