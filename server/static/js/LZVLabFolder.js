//Initialization Function
$(document).ready(function() {
    var ct = getLocalStorage('labFolderToken');
    if (ct && ct != '') {
        $("#labFolderDownloadButton").show();
        labFolderToken = ct;
        updateContentAfterLogin();
    }
    if (checkLZVLogin()) {
        $('#logout_lzv').show();
    }
});
//contains the entries of the loged in user from labfolder, these are stored in cookies with same name
var labFolderEntries = {
    entries: Array()
};
var labFolderProjects = {
    projects: Array()
};
var labFolderMDB = {
    categories: Array()
};
var labFolderStorageFile; //storage file on server, will be filled with json object containing the files already available on server
$("#logoutButton").click(function() {
    logout();
});
$("#getEntries").click(function() {
    getEntries();
});
$("#downloadSelectedElements").click(function() {
    downloadSelectedElements();
});
$("#downloadMDB").click(function() {
    downloadMDB();
});
$("#getProjects").click(function() {
    getProjects();
});

function clearLocalStorage() {
    labFolderEntries.entries = Array();
    labFolderProjects.projects = Array();
    labFolderMDB.categories = Array();
    labFolderStorageFile = {};
    updateLabfolderSelectableProjects();
    updateProjectMaterialSelection();
}

function clearCookies() {
    deleteLocalStorage("labFolderToken");
    deleteLocalStorage("labFolderProjects");
    deleteLocalStorage("labFolderEntries");
    deleteLocalStorage("labFolderStorageFile");
    deleteLocalStorage("labFolderMDB");
}

function downloadSelectedElements() {
    if ($("#labFolderSelectProject").hasClass("selected")) {
        downloadSelectedEntries();
        getStorageFile();
        updateLabfolderSelectableElements();
    }
    if ($("#labFolderSelectMDB").hasClass("selected")) {
        downloadSelectedMDBCategories();
    }
}
$("#selectAllElements").click(function() {
    var childrenDiv = $('form[id=selectableEntries]').children();
    for (var i = 0; i < childrenDiv.length; i++) {
        var children = childrenDiv[i].children;
        for (var j = 0; j < children.length; j++) {
            if (children[j].type == 'checkbox') {
                children[j].checked = true;
            }
        }
    }
});
$("#deSelectAllElements").click(function() {
    var childrenDiv = $('form[id=selectableEntries]').children();
    for (var i = 0; i < childrenDiv.length; i++) {
        var children = childrenDiv[i].children;
        for (var j = 0; j < children.length; j++) {
            if (children[j].type == 'checkbox') {
                children[j].checked = false;
            }
        }
    }
});
$("#updateContent").click(function() {
    setLocalStorage("labFolderProjects", "");
    setLocalStorage("labFolderEntries", "");
    setLocalStorage("labFolderMDB", "");
    setLocalStorage("labFolderStorageFile", "");
    updateContentAfterLogin();
});
//switch between (currently) Project and MaterialDB to select. Updates Projects and Materials to display
function updateSelectionProjectMDB(clicked) {
    if ($(clicked).hasClass("selected")) {
        return;
    }
    $(clicked).siblings().removeClass("selected");
    $(clicked).addClass("selected");
    display_project_id = "";
    if ($(clicked).hasClass("labFolderProject")) {
        updateLabfolderSelectableProjects();
        updateLabfolderSelectableElements();
    }
    if ($(clicked).hasClass("labFolderMDB")) {
        // updateLabfolderSelectableDatabases();
        updateLabfolderSelectableCategories();
    }
}

function toggleDisplayVersions(clicked) {
    $(clicked).parent().parent().parent().parent().children(".versionList").children().toggle();
    if ($(clicked).children(".arrow").html() == "v") {
        $(clicked).children(".arrow").text("x");
    } else {
        $(clicked).children(".arrow").text("v");
    }
}

function downloadVersion(clicked) {
    window.open($(clicked).attr('id'));
}
//this var contains the current project ID which is used to filter the elements to display
var display_project_id = "";
//being called when another Project is clicked in the selection screen. Updates the globald project ID and calls update function
function updateSelectedProject(clicked) {
    if ($(clicked).hasClass("selected")) {
        return;
    }
    $(clicked).siblings().removeClass("selected");
    $(clicked).addClass("selected");
    display_project_id = $(clicked).attr('id');
    if ($(clicked).hasClass("labFolderProject")) {
        updateLabfolderSelectableElements();
    }
    if ($(clicked).hasClass("labFolderMDB")) {
        updateLabfolderSelectableCategories();
    }
}

function updateProjectMaterialSelection() {
    if (labFolderProjects.projects.length > 0) {
        $("#labFolderSelectProject").removeAttr("disabled");
    } else {
        $("#labFolderSelectProject").attr("disabled", true);
    }
    if (labFolderMDB.categories.length > 0) {
        $("#labFolderSelectMDB").removeAttr("disabled");
    } else {
        $("#labFolderSelectMDB").attr("disabled", true);
    }
}

function authenticate(form) {
    var username = form.elements.username.value;
    var password = form.elements.pwd.value;
    interface_labfolder_authenticate(username, password, function(xhttp_response) {
        data = JSON.parse(xhttp_response);
        if (!("error" in data)) {
            labFolderToken = data.token;
            setLocalStorage("labFolderToken", labFolderToken);
            $("#labFolderDownloadButton").show();
            updateContentAfterLogin();
        } else {
            $("#labFolderFailedLogin").show();
        }
    });
}

function logout() {
    interface_labfolder_logout(labFolderToken, function() {
        $('form[id=selectableEntries]').empty();
        $("#labfolderLoginform").show();
        $("#labFolderLoginSuccesful").hide();
        $("#labFolderFailedLogin").hide();
        clearCookies();
        clearLocalStorage();
        $("#labFolderDownloadButton").hide();
    });
}

function updateContentAfterLogin() {
    $("#labFolderFailedLogin").hide();
    $("#labfolderLoginform").hide();
    $("#labFolderLoginSuccesful").show();
    var lfp = getLocalStorage("labFolderProjects");
    if (lfp === null || lfp == "") {
        getProjects();
        setLocalStorage("labFolderProjects", JSON.stringify(labFolderProjects));
    } else {
        labFolderProjects = JSON.parse(lfp);
    }
    var lfe = getLocalStorage("labFolderEntries");
    if (lfe === null || lfe == "") {
        getEntries();
        setLocalStorage("labFolderEntries", JSON.stringify(labFolderEntries));
    } else {
        labFolderEntries = JSON.parse(lfe);
    }
    var lfm = getLocalStorage("labFolderMDB");
    if (lfm === null || lfm == "") {
        getMDBCategories();
        setLocalStorage("labFolderMDB", JSON.stringify(labFolderMDB));
    } else {
        labFolderMDB = JSON.parse(lfm);
    }
    var lfs = getLocalStorage("labFolderStorageFile");
    if (lfs === null || lfs == "") {
        getStorageFile();
        setLocalStorage("labFolderStorageFile", JSON.stringify(labFolderStorageFile));
    } else {
        labFolderStorageFile = JSON.parse(lfs);
    }
    updateProjectMaterialSelection();
}

function getStorageFile() {
    interface_labfolder_get_storagefile(function(xhttp_response) {
        labFolderStorageFile = JSON.parse(xhttp_response);
        setLocalStorage("labFolderStorageFile", JSON.stringify(labFolderStorageFile));
    });
}

function getProjects() {
    interface_labfolder_get_projects(labFolderToken, function(xhttp_response) {
        var parsedData = JSON.parse(xhttp_response);
        labFolderProjects.projects = [];
        for (var i = 0; i < parsedData.length; i++) {
            var obj = parsedData[i];
            var project = {
                title: obj.title,
                id: obj.id,
                owner_id: obj.owner_id,
                group_id: obj.group_id,
                folder_id: obj.folder_id,
                hidden: obj.hidden,
                creation_date: obj.creation_date,
                version_date: obj.version_date
            };
            labFolderProjects.projects.push(project);
        }
    });
}

function getEntries() {
    interface_labfolder_get_entries(labFolderToken, function(xhttp_response) {
        var parsedData = JSON.parse(xhttp.response);
        labFolderEntries.entries = [];
        for (var i = 0; i < parsedData.length; i++) {
            var obj = parsedData[i];
            var entry = {
                elements: Array(),
                title: obj.title,
                id: obj.id,
                project_id: obj.project_id,
                version_id: obj.version_id,
                author_id: obj.author_id,
                creation_data: obj.creation_date,
                version_date: obj.version_date,
                entry_number: obj.entry_number,
                hidden: obj.hidden,
                editable: obj.editable
            };
            for (var j = 0; j < obj.elements.length; j++) {
                var ele = obj.elements[j];
                var element = {
                    element_id: ele.id,
                    type: ele.type,
                    version_id: ele.version_id
                };
                entry.elements.push(element);
            }
            labFolderEntries.entries.push(entry);
        }
    });
}

function getMDBCategories() {
    interface_labfolder_get_mdbcategories(labFolderToken, function(xhttp_response) {
        var parsedData = JSON.parse(xhttp.response);
        labFolderMDB.categories = [];
        for (var i = 0; i < parsedData.length; i++) {
            var obj = parsedData[i];
            var category = {
                title: obj.title,
                id: obj.id,
                creator_idID: obj.creator_id,
                creation_date: obj.creation_date,
                version_id: obj.version_id,
                version_date: obj.version_date,
                categories: []
            };
            labFolderMDB.categories.push(category);
        }
    });
}

function updateLabfolderSelectableProjects() {
    $("#labFolderProjectSelect").html("");
    var append = "";
    var displayProjectCount = 0;
    for (var i = 0; i < labFolderProjects.projects.length; i++) {
        var obj = labFolderProjects.projects[i];
        if (obj.hidden == false) {
            displayProjectCount++;
            append += '<button class="btn lzvButton btnEntrySelectionHeader btnEntrySelectionProject labFolderProject" id="' + obj.id + '" name="' + obj.id + '"onclick="updateSelectedProject(this);">';
            append += obj.title;
            append += "</button>";
        }
    }
    if (displayProjectCount > 0) {
        $("#labFolderProjectSelect").html(append);
        $(".btnEntrySelectionProject").css("width", 100 / displayProjectCount + "%");
    }
}

function updateLabfolderSelectableElements() {
    $('form[id=selectableEntries]').empty();
    var append = '';
    if (display_project_id != "") {
        let display_objects_storage = labFolderStorageFile.filter(proj => proj.origin_metadata.project_id == display_project_id);
        for (var i = 0; i < labFolderEntries.entries.length; i++) {
            var obj = labFolderEntries.entries[i];
            if (obj.hidden == false && obj.project_id == display_project_id) {
                var storage_entry;
                if (display_objects_storage) {
                    storage_entry = display_objects_storage.filter(entry => entry.origin_metadata.entry_id == obj.id);
                }
                var unique_entry_versions = storage_entry.map(item => item.origin_metadata.entry_version_id).filter((value, index, self) => self.indexOf(value) === index).length;
                append += '<div><div class="entrySelect lzvButton labFolderProject"><input type="checkbox" value="" id="' + obj.id + '" name="' + obj.id + '">';
                append += '<label for="' + obj.id + '" class="selectLabel">' + obj.title;
                if (display_objects_storage && storage_entry && unique_entry_versions > 0) {
                    append += '<span class="versionCounter"><button type="button" class="expandVersionButton" onclick="toggleDisplayVersions(this);">';
                    append += unique_entry_versions + ' version';
                    if (unique_entry_versions > 1) {
                        append += 's ';
                    } else {
                        append += ' ';
                    }
                    append += '<span class="arrow">v</span></button></span>';
                }
                append += '</label>';
                append += '</div>\n';
                append += '<div class="versionList">';
                if (unique_entry_versions > 0) {
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
                }
                append += '</div></div>';
            }
        }
        $(append).appendTo('#selectableEntries');
    }
}

function updateLabfolderSelectableCategories() {
    $("#labFolderProjectSelect").html("");
    $('form[id=selectableEntries]').empty();
    var append = '';
    for (var i = 0; i < labFolderMDB.categories.length; i++) {
        var obj = labFolderMDB.categories[i];
        // append += '<div class="entrySelect lzvButton labFolderMDB"><input type="checkbox" value=""  id="' + obj.id + '" name="' + obj.id + '">';
        append += '<div class="entrySelect lzvButton labFolderMDB">';
        append += '<label for="' + obj.id + '">' + obj.title + '</label>';
        var dlurl = baseURL + '/labfolder/mdb/items?category_id=' + obj.id + '&token=' + getLocalStorage("labFolderToken");
        append += '<button type="button" class="expandVersionButton floatRight" id="' + dlurl + '" + onclick="downloadVersion(this);">Download</button>';
        append += '</div>\n';
    }
    $(append).appendTo('#selectableEntries');
}

function downloadSelectedEntries() {
    //first get ids to download, then do that
    var ids = []; //ids for entry which will be downloaded
    var form = $('form[id=selectableEntries]')[0];
    for (var i = 0; i < form.elements.length; i++) {
        if (form.elements[i].checked) {
            ids.push(form.elements[i].name);
        }
    }
    console.log(labFolderEntries);
    if (ids.length > 0) {
        var elements = []; //these are to single elements to be downloaded later
        for (var j = 0; j < labFolderEntries.entries.length; j++) {
            var entry = labFolderEntries.entries[j];
            for (var i = 0; i < ids.length; i++) {
                if (entry.id == ids[i]) {
                    for (var k = 0; k < entry.elements.length; k++) {
                        let project = labFolderProjects.projects.find(proj => proj.id == entry.project_id);
                        var element = {
                            project_id: entry.project_id,
                            project_title: project.title,
                            entry_id: entry.id,
                            entry_title: entry.title,
                            entry_hidden: entry.hidden,
                            entry_version_date: entry.version_date,
                            entry_version_id: entry.version_id,
                            element_id: entry.elements[k].element_id,
                            element_type: entry.elements[k].type,
                            element_version_id: entry.elements[k].version_id
                        };
                        elements.push(element);
                    }
                }
            }
        }
        //elements contains the set of id, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
        if (elements.length > 0) {
            interface_labfolder_download_elements(elements, labFolderToken, function() {});
        }
    }
}

function downloadSelectedMDBCategories() {
    //first get ids to download, then do that
    var categoryIds = []; //ids for categories which will be downloaded
    var form = $('form[id=selectableEntries]')[0];
    for (var i = 0; i < form.elements.length; i++) {
        if (form.elements[i].checked) {
            categoryIds.push(form.elements[i].name);
        }
    }
    //elements contains the set of id, entryTitle, elementID. These should now be downloaded from server and saved in  a folder structure
    for (var i = 0; i < categoryIds.length; i++) {
        xhttp.onreadystatechange = function(e) {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var answer = xhttp.response;
                }
                if (this.status == 400) {
                    alert("Fehler: Bitte ID mitgeben!");
                }
            }
        };
        interface_labfolder_download_mdbcategories(categoryIds[i], labFolderToken, function() {});
    }
}