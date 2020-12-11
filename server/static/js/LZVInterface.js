function interface_get_metadata_usersets(on_success_callback) {
    var url = baseURL + '/metadata/user';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_get_metadata_export_mappings(on_success_callback) {
    var url = baseURL + '/metadata/export_mappings';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_delete_metadata_usersets(data, on_success_callback) {
    var url = baseURL + '/metadata/user/delete';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('PUT', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(JSON.stringify(data));
}

function interface_store_metadata_usersets(data, on_success_callback) {
    var url = baseURL + '/metadata/user';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('PUT', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(JSON.stringify(data));
}

function interface_get_metadata_export_definitions(on_success_callback) {
    var url = baseURL + '/metadata/export_definitions';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_get_metadata_structure_information(on_success_callback) {
    var url = baseURL + '/metadata/structures';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_labfolder_authenticate(username, password, on_success_callback) {
    var url = baseURL + '/labfolder/auth/login';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    if (username != '' && password != '') {
        xhttp.open('POST', url, false);
        xhttp.setRequestHeader("Content-type", "application/json");
        var payload = '{\"password\": \"' + password + '\", \"user\": \"' + username + '\"}';
        xhttp.send(payload);
    }
}

function interface_labfolder_logout(token, on_success_callback) {
    if (token != '') {
        var url = baseURL + '/labfolder/auth/logout';
        xhttp.onreadystatechange = function(e) {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    on_success_callback();
                }
            }
        };
        xhttp.open('POST', url, false);
        xhttp.setRequestHeader("Content-type", "application/json");
        xhttp.setRequestHeader("Token", token);
        xhttp.send();
    }
}

function interface_labfolder_get_storagefile(on_success_callback) {
    var url = baseURL + '/labfolder/storage';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_labfolder_get_projects(token, on_success_callback) {
    var url = baseURL + '/labfolder/projects';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Token", token);
    xhttp.send();
}

function interface_labfolder_get_entries(token, on_success_callback) {
    var url = baseURL + '/labfolder/entries';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Token", token);
    xhttp.send();
}

function interface_labfolder_get_mdbcategories(token, on_success_callback) {
    var url = baseURL + '/labfolder/mdb/categories';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Token", token);
    xhttp.send();
}

function interface_labfolder_download_elements(data, token, on_success_callback) {
    var url = baseURL + '/labfolder/elements/download';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('POST', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Token", token);
    var payload = JSON.stringify(data);
    xhttp.send(payload);
}

function interface_labfolder_download_mdbcategories(id, token, on_success_callback) {
    url = baseURL + "/labfolder/mdb/items?category_id=" + id;
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Token", token);
    xhttp.send();
}

function interface_packages_get(on_success_callback) {
    var url = baseURL + '/storage/packages';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
}

function interface_packages_put(data, on_success_callback) {
    var url = baseURL + '/storage/packages';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('PUT', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    console.log("data");
    console.log(data);
    var payload = JSON.stringify(data);
    xhttp.send(payload);
}

function interface_packages_delete(data, on_success_callback) {
    var url = baseURL + '/storage/packages/delete';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    xhttp.open('PUT', url, false);
    xhttp.setRequestHeader("Content-type", "application/json");
    console.log("data");
    console.log(data);
    var payload = JSON.stringify(data);
    xhttp.send(payload);
}