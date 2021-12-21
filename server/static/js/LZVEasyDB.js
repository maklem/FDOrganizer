//Initialization Function
$(document).ready(function() {
    var ct = getLocalStorage('easyDBToken');
    if (ct && ct != '') {
        updateContentAfterLogin();
    }
    if (checkLZVLogin()) {
        $('#logout_lzv').show();
    }
});

var easyDBCollections = {
    collections: Array()
};

/*
    We should really consider if we should give the option to download a complete pool. If there is
    a public pool with a lot of elements, it can easily cluster the server with a lot of data if
    random people download this pool. Maybe we should limit this to pools where the user is also an
    admin/owner of the pool which is intented to be downloaded. Pools are in the
*/
var easyDBPools = {
    pools: Array()
};

function authenticate(form) {
    console.log("trying to auth")
    var username = form.elements.username.value;
    var password = form.elements.pwd.value;
    interface_easydb_authenticate(username, password, function(xhttp_repsonse) {
        data = JSON.parse(xhttp_repsonse);
        if(!("error" in data)) {
            var easyDBToken = data.token;
            setLocalStorage("easyDBToken",  easyDBToken);
            updateContentAfterLogin();
        }

    });
}

function clearLocalStorage() {
    easyDBCollections = Array();
    easyDBPools = Array();
}

function clearCookies() {
    deleteLocalStorage("easyDBToken");
    deleteLocalStorage("easyDBCollections");
    deleteLocalStorage("easyDBToken");
}



function logout() {
    interface_easydb_logout(getLocalStorage("easyDBToken"), function() {
        $('form[id=selectableEntries]').empty();
        $("#repositoryLoginform").show();
        $("#repositoryLoginSuccesful").hide();
        $("#repositoryFailedLogin").hide();
        $("#easyDBDownloadButton").hide();
    });
}


$("#downloadSelectedElements").click(function() {
    downloadSelectedElements();
});


function downloadSelectedElements() {
        downloadSelectedCollections();
/*        getStorageFile();*/
}



function updateSelectionCollectionPool(clicked) {
    var collections = getLocalStorage("easyDBCollections");
    if (collections === null || collections == "") {
        getCollections();
        setLocalStorage("easyDBCollections", JSON.stringify(easyDBCollections))
    }
    else {
        easyDBCollections = JSON.parse(collections);
    }
    /*var pools = getLocalStorage("easyDBPools");
    if (pools === null || pools == "") {
        getPools();
        setLocalStorage("easyDBPools", JSON.stringify(easyDBPools))
    }
    else {
        easyDBPools = JSON.parse(pools);
    }*/

}

function updateContentAfterLogin() {
    $("#repositoryFailedLogin").hide();
    $("#repositoryLoginform").hide();
    $("#repositoryLoginSuccesful").show();
    $("#easyDBDownloadButton").show();
    getCollections();
    /*getCollectionContentInfo();*/
}

function getCollections() {
    interface_easydb_get_collections(getLocalStorage("easyDBToken"), function(xhttp_response){
        console.log(xhttp_response);
        easyDBCollections = JSON.parse(xhttp_response);
        setLocalStorage("easyDBCollections", xhttp_response);
        updateEasyDBSelectableElements();
    });
}

function getCollectionContentInfo(id) {
    interface_easydb_get_collection_content_info(getLocalStorage("easyDBToken"), id, function(xhttp_response){
        console.log(xhttp_response);
        return JSON.parse(xhttp_response);
    });
}

function updateEasyDBSelectableElements() {
    $('form[id=selectableEntries]').empty();
    var append = '';
        for (var i = 0; i < easyDBCollections.length; i++) {
            var obj = easyDBCollections[i];
            append += '<div><div class="entrySelect lzvButton easyDBCollection"><input type="checkbox" value="" id="' + obj.collection._id + '" name="' + obj.collection._id + '">';
            append += '<label for="' + obj.collection._id + '" class="selectLabel">' + Object.values(obj.collection.displayname)[0];
            append += '<button type="button" class="expandVersionButton" id="'+ obj.collection._id +'"onclick="toggleDisplayCollectionInfo(this)">Details</button>';
            /*if (display_objects_storage && storage_entry && unique_entry_versions > 0) {
                append += '<span class="versionCounter"><button type="button" class="expandVersionButton" onclick="toggleDisplayVersions(this);">';
                append += unique_entry_versions + ' version';
                if (unique_entry_versions > 1) {
                    append += 's ';
                } else {
                append += ' ';
                }
                append += '<span class="arrow">v</span></button></span>';
            }*/
            append += '</label>';
            append += '</div>\n';
            append += '<div class="versionList collectionInfo">';
                /*if (unique_entry_versions > 0) {
                    var done_versions = {};
                    for (var j = 0; j < storage_entry.length; j++) {
                        var entry_version_id = storage_entry[j].origin_metadata.entry_version_id;
                        if (done_versions[entry_version_id]) {
                            continue;
                        }
                        done_versions[entry_version_id] = true;
                        date = new Date(storage_entry[j].origin_metadata.entry_version_date);
                        let formatted_date = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
                        append += '<div class="versionDetail"><span>';
                        append += formatted_date;
                        var dlurl = baseURL + '/labfolder/download?project_id=' + display_project_id + '&entry_id=' + obj.id + '&entry_version_id=' + storage_entry[j].origin_metadata.entry_version_id;
                        append += '</span><button type="button" class="expandVersionButton" id="' + dlurl + '" + onclick="downloadVersion(this);">Download</button></div>';
                    }
                }*/
                append += '</div></div></div>';
        }
        $(append).appendTo('#selectableEntries');
}

function toggleDisplayCollectionInfo(clicked) {
    if($(clicked).parent().parent().parent().find('.collectionDetail').length){
        $(clicked).parent().parent().parent().children('.versionList').empty();
        return;
    }
    interface_easydb_get_collection_content_info(getLocalStorage("easyDBToken"), $(clicked).attr('id'), function(xhttp_response){
        var collection_info = JSON.parse(xhttp_response);
        console.log(collection_info);
        let total_filesize = 0;
        let filecount = 0;
        let filetypes = {};

        let num_obj = collection_info.objects.length;
        for (const ele of collection_info.objects) {
            console.log("ele");
            console.log(ele);
            if(ele.object.file){
                filecount++;
                total_filesize += ele.object.file[0].filesize; //filesize if in Byte
                filetypes[ele.object.file[0].extension] = true;
            }
        }
        if (total_filesize > 1000000000) //GB
        {
            total_filesize = String(Math.round(total_filesize/10000000)/100)+ "GB";
        }
        else if(total_filesize > 1000000)
        {
            total_filesize = String(Math.round(total_filesize/10000)/100)+ "MB";
        }
        else if(total_filesize > 1000)
        {
            total_filesize = String(Math.round(total_filesize/10)/100)+ "kB";
        }
        else
        {
            total_filesize = String(total_filesize)+ "B";
        }
        var str_filetypes = '';
        for (const [key, value] of Object.entries(filetypes)) {
            str_filetypes += key + ","
        }
        str_filetypes = str_filetypes.slice(0, -1);
        console.log(filecount);
        console.log(total_filesize);
        console.log(str_filetypes);
        var append = '<div class="collectionDetail">';
        append += '<span id="collectionInfoHeader">Collection Info:</span>';
        append += '<span id="collectionFileCount">Number of files: ' + filecount + '</span>';
        append += '<span id="collectionTotalSize">Total File Size: ' + total_filesize + '</span>';
        append += '<span id="collectionFileTypes">File Types: ' + str_filetypes + '</span>';
        append += '</div>';
        console.log($(clicked).parent().parent().parent().children('.versionList'));
        $(append).appendTo($(clicked).parent().parent().parent().children('.versionList'));
    });
}

function downloadSelectedCollections() {
    //first get ids to download, then do that
    var ids = []; //ids for entry which will be downloaded
    var form = $('form[id=selectableEntries]')[0];
    for (var i = 0; i < form.elements.length; i++) {
        if (form.elements[i].checked) {
            ids.push(form.elements[i].name);
        }
    }
    console.log(ids);
    if (ids.length > 0) {
        for(const id of ids)
        {
            interface_easydb_download_collection(getLocalStorage('easyDBToken'), id, function() {});
        }
    }
}