function setLocalStorage(cname, cvalue) {
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

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
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

function toggleDisplaySubItems(clicked) {
  $(clicked).parent().children('#newItemsSubItems, #myItemsSubItems').toggle();
  if ($(clicked).children(".arrow").html() == "v") {
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