function upload_file(data, package_id, on_success_callback) {
    // console.log($('formElem').serialize());
    var url = baseURL + '/upload/file?package_id=' + package_id;
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback();
            }
        }
    };
    //send as form data
    const formData = new FormData();
    formData.append('uploaded_file', data);
    xhttp.open('POST', url, false);
    xhttp.send(formData);
}

function query_new_package(name, on_success_callback) {
    var url = baseURL + '/upload/package?name=' + name;
    console.log(url);
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success_callback(xhttp.response);
            }
        }
    };
    xhttp.open('GET', url, false);
    xhttp.send();
}

$('#upload_choose_files_hidden_input').change(function() {
    append_to_upload_list(this);
    update_upload_file_list();
});
var form_upload_data = [];

function append_to_upload_list(input) {
    var len = input.files.length;
    console.log(len);
    for (let i = 0; i < len; i++) {
        const search_name = input.files[i].name;
        if (!form_upload_data.some(f => f.name == search_name)) {
            console.log("adding file");
            console.log(input.files[i].name);
            input.files[i].file_id = uuidv4();
            form_upload_data.push(input.files[i]);
        }
    }
}

function remove_from_upload_list(clicked) {
    var file_id = $(clicked).attr('file_id');
    form_upload_data.filter(f => f.file_id != file_id);
}

function update_upload_file_list() {
    var output = '';
    for (let ele of form_upload_data) {
        output += create_html_for_upload_indicator(ele);
    }
    console.log(output);
    $('#upload_list').empty();
    $(output).appendTo('#upload_list');
    // $('#upload_list').innerHTML = output;

}

function create_html_for_upload_indicator(upload_file) {
    var output = '';
    output += '<div class="upload_container_subitem" file_id="'+upload_file.file_id+'">';
    output += '<div class="upload_item" file_id="'+upload_file.file_id+'" onclick="select_deselect_item(this)">';
    output += '<span class="upload_item_description">' + upload_file.name + '</span><br>';
    var size = upload_file.size;
    if (size < 1024) {
        size = String(size) + 'B';
    }
    else if(size < 1048576) { //kB
        size = (size/1024).toFixed(2) + 'kB';
    }
    else { //mB
        size = (size/1048576).toFixed(2) + 'MB';
    }
    output += '<span class="upload_item_sub_description">' + upload_file.type + ' - ' + size + '</span>';
    output += '</div>';
    output += '<button type="button" class="btn upload_item_button remove_upload_item" file_id="'+upload_file.file_id+'" onclick="remove_from_upload_list(this);"> </button>';
    output += '</div>';
    return output;
}


// $('#upload_choose_files_hidden_input').addEventListener('change', append_to_upload_list(), false);
$('#upload_choose_files').click(function() {
    $('#upload_choose_files_hidden_input').click();
    console.log("test");
});


function ask_for_consent(){
    if($('#input_package_name').val() == ''){
        alert('Please enter a name for the package to be created before uploading!');
        return;
    }
    $('#metaDataMainForm').toggle();
    $('#popupForm').toggle();
}

function trigger_package_creation() {
    console.log("trying create package!");
    //visually display"upload" progres. (grey out delete button, show "circle" for pending upload)
    //disable namefield and buttons for item selection and uploadtrigger
    package_name = $('#input_package_name').val();
    query_new_package(package_name, function(response) {
        answer = JSON.parse(response);
        package_id = answer.package_id;
        console.log("received package id: " + package_id);
        upload_files(package_id);
    });
}

function upload_files(package_id) {
    console.log("uploading files");
    for (let file of form_upload_data) {
        console.log("new file");
        upload_file(file, package_id, function() {
            console.log("up succesfull, chaging display");
            console.log("filename: " + file.name);
            console.log("file_id: " + file.file_id);
            console.log(file);
            let button = $('#upload_list').find('button[file_id="'+file.file_id+'"');
            console.log(button);
            button.removeClass('remove_upload_item');
            button.addClass('success_upload_item');
            //graphical info about the progress (green checkmark above trashcan)
        });
    }
    //when finished show a success message and clear the form
}

function upload_package_agree() {
    console.log("agreed!");
    $('#metaDataMainForm').toggle();
    $('#popupForm').toggle();
    $('#upload_choose_files').prop('disabled', true);
    $('#button_save_package_object').prop('disabled', true);
    $('#input_package_name').prop('disabled', true);
    $('#upload_list').find('.remove_upload_item').prop('disabled', true);
    trigger_package_creation();
}

function upload_package_disagree() {
    $('#metaDataMainForm').toggle();
    $('#popupForm').toggle();
}