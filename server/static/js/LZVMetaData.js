function getMetaDataStructureInformation(){
	var url = baseURL + '/metadata/structures';
	xhttp.onreadystatechange  = function(e) {
		if(this.readyState == 4) {
			if(this.status == 200) {
				metaSturctureJSON = JSON.parse(xhttp.response);
				parseMetaStructures(metaSturctureJSON);	
			}
		}
	}

	xhttp.open('GET', url, false);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send();	
}



function parseMetaStructures(metaStruc) {
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

function metaTest() {
	console.log("test")
}
