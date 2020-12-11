//var baseURL = 'btrvx159.rz.uni-bayreuth.de';
var baseURL = '';
var labFolderToken = '';
//TODO remove before prod
var DEBUGlogin = 'robert.guenther@uni-bayreuth.de';
var DEBUGpassword = 'krQ3C3LTjIXFmwcpmEaM';

if (window.XMLHttpRequest) {
    // code for modern browsers
    var xhttp = new XMLHttpRequest();
} else {
    // code for old IE browsers
    var xhttp = new ActiveXObject('Microsoft.XMLHTTP');
} 

function setLocalStorage(cname,cvalue) {
  sessionStorage.setItem(cname, cvalue);
}

function getLocalStorage(cname) {
  var item = sessionStorage.getItem(cname);
  return item;
}

function deleteLocalStorage(cname) {
  sessionStorage.removeItem(cname);
}

function clearAllLocalStorage() {
  sessionStorage.clear();
}

//we are only setting cookies which are deleted after closing browser window
function setCookie(cname, cvalue) {
  document.cookie = cname + "=" + cvalue + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function getType(p) {
    if (Array.isArray(p)) return 'array';
    else if (typeof p == 'string') return 'string';
    else if (p != null && typeof p == 'object') return 'object';
    else return 'other';
}

function checkLZVLogin() {
    var auth = getCookie("session_auth");
    var user = getCookie("session_user");
    if ( auth && user && auth != '' && user != ''){
      return true;
    }
    else {
      return false;
    }
}

function logout_lzv() {
  if (checkLZVLogin()) { 
    var url = baseURL + '/logout';
    xhttp.onreadystatechange  = function(e) {
      if(this.readyState == 4) {
        if(this.status == 200) {
          setCookie("session_auth", '');
          setCookie("session_user", '');
          window.location.reload(true);
        }
      }
    };
    xhttp.open('POST', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
  }
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


// function convertStorageFileToFlat() {
//   var storage_file = getLocalStorage("labFolderStorageFile");
//   var flat_storage = [];
//   storage_file = JSON.parse(storage_file);
//   for (var project of storage_file.projects) {
//     for (var entry of project.entries) {
//       for (var entry_version of entry.versions) {
//         for (var element of entry_version.elements) {
//           for (var element_version of element.versions) {
//             var append = {
//               "project_id" : project.projectID,
//               "project_title" : project.projectTitle,
//               "entry_id" : entry.entryID,
//               "entry_title" : entry.entryTitle,
//               "entry_version_id" : entry_version.versionID,
//               "entry_version_date" : entry_version.versionDate,
//               "element_id" : element.elementID,
//               "element_type" : element.elementType,
//               "element_version_id" : element_version.versionID,
//               "element_version_couchdb_doc_id" : element_version.couchdb_doc_id,
//               "element_version_couchdb_doc_item_att_name" : element_version.couchdb_doc_item_att_name
//             };
//             flat_storage.push(append);
//           }
//         }
//       }
//     }
//   }
//   return flat_storage;
// }