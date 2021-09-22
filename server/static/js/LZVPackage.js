$( document ).ready(function() {
    get_user_packages();
    get_user_storage();
    update_sidebar_user_packages();
    create_empty_package_form();
    if(checkLZVLogin())
    {
        $('#logout_lzv').show();
    }
});

var unsaved = false;

$(":input").change(function(){ //triggers change in all input fields including text type
    unsaved = true;
});

// Monitor dynamic inputs
$(document).on('change', 'input, select', function(){ //triggers change in all input fields including text type
    unsaved = true;
});

function get_user_packages() {
    interface_packages_get(function(xhttp_response){
        parsedJSON =  JSON.parse(xhttp_response);
        setLocalStorage("user_packages", JSON.stringify(parsedJSON));
    });
}

function get_user_storage() {
    interface_storage_get(function(xhttp_response){
        parsedJSON =  JSON.parse(xhttp_response);
        setLocalStorage("user_storage", JSON.stringify(parsedJSON));
    });
}


function update_sidebar_user_packages(){
    $('#myItemsSubItems').empty();
    var parsedJSON = JSON.parse(getLocalStorage('user_packages'));
    var user_packages = parsedJSON.filter(x => x.package_object_metadata.modifiable);
    var append = '';
    for (let item of user_packages) {
        append += '<div class="sidebarSubItemContainer"><button class="sidebarItem sidebarSubItem sidebarUserSet" package_id="' + item.package_id + '" onclick="create_form_for_existing_package(this);">' + item.name + '</button><div class="round-button"><button class="btn deleteSetButton" package_id="'+ item.package_id + '" onclick="delete_package(this);"><span>-</span></button></div></div>';
    }
    $(append).appendTo('#myItemsSubItems');
}

function create_form_for_existing_package(clicked) {
    if(unsaved){
        if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
            return;
        }
    }
    user_packages = JSON.parse(getLocalStorage("user_packages"));
    clicked_id = $(clicked).attr('package_id');

    fill_package_form(clicked_id, user_packages);
}

function create_empty_package_form() {
    if(unsaved){
        if(confirm("You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?")){}
        else {
            return;
        }
    }
    $('#package_name').val("");
    $('#package_description').val("");
    $('#package_content_container').empty();
    $('#package_options_container').empty();
    $('#package_manager_form_header').attr('package_id', uuidv4());
    user_packages = JSON.parse(getLocalStorage("user_packages"));
    var output = '';
    console.log(user_packages);
    for (let item of user_packages) {
        if(!item.package_object_metadata.modifiable) {
            output += create_html_for_container_content(item);
        }
    }
    $(output).appendTo('#package_options_container');
}

function fill_package_form(clicked_id, user_packages) {
    var user_package = user_packages.find(set=>set.package_id == clicked_id);
    $('#package_content_container').empty();
    $('#package_options_container').empty();
    $('#package_manager_form_header').attr('package_id', user_package.package_id);
    $('#package_name').val(user_package.name);
    $('#package_description').val(user_package.description);
    var output = '';
    console.log(user_packages);
    for (let search_id of user_package.child_data_objects) {
        app_package = user_packages.find(set=>set.package_id == search_id);
        output += create_html_for_container_content(app_package);
    }
    $(output).appendTo('#package_content_container');
    output = '';
    for (let item of user_packages) {
        if(!item.package_object_metadata.modifiable && item.id != clicked_id && !user_package.child_data_objects.includes(item.package_id)) {
            output += create_html_for_container_content(item);
        }
    }
    $(output).appendTo('#package_options_container');
}

function create_html_for_container_content(user_package) {
    var output = '';
    output += '<div class="container_subitem" package_id="'+user_package.package_id+'">';
    output += '<button type="button" class="btn container_item_select" package_id="'+user_package.package_id+'" onclick="select_deselect_item(this)">';
    output += user_package.name;
    output += '</button>';
    output += '<button type="button" class="btn open_info_button" package_id="'+user_package.package_id+'" onclick="open_item_info(this);"> </button>';
    output += '</div>';
    return output;
}

//TODO!
function open_item_info(clicked) {
    $('#popupForm').empty();

    var user_packages = JSON.parse(getLocalStorage("user_packages"));
    clicked_id = $(clicked).attr('package_id');
    var display_package = user_packages.find(set=>set.package_id == clicked_id);
    if (display_package) {
        var html = create_html_for_item_info(display_package);
        $(html).appendTo('#popupForm');
        display_popup();
    }

}

function create_html_for_item_info(clicked_package) {
    var html = '';
    html += '<div id="popup_form_content">';
    html += '<div id="popup_form_header">';
    html += '<div id="popup_header_name" class="popup_form_header_field">' + clicked_package.name + '</div>';
    html += '<div id="popup_header_creation_date" class="popup_form_header_field">' + clicked_package.package_object_metadata.creation_date + '</div>';
    html += '<div id="popup_header_last_change" class="popup_form_header_field">' + clicked_package.package_object_metadata.last_change + '</div>';
    html += '<div id="popup_header_description" class="popup_form_header_field">' + clicked_package.description + '</div>';
    html += '</div>';
    html += '<div id="popup_form_mainpage">';
    html += '</div>';
    html += '<div id="popup_form_footer"><button class="btn close_info_button" id="close_popup_form" onclick="hide_popup();">Close</button></div>';
    html += '</div>';
    return html;
}
//TODO TEST and finish
function recursive_create_item_info_content_item(item_id) {
    var html = ''
    var user_packages = JSON.parse(getLocalStorage("user_storage"));
    var item = user_packages.find(set=>set.package_id == item_id);
    if(item.type == 'PACKAGE'){
        html += '<div class="content_element package_info_package"><div class="package_info_package_icon"/><span>'+ item.name +'</span><button class="btn expand_package_info_button" id="'+item.package_id+'" onclick="expand_content_children">+</button></div>';
        for (let c of item.child_data_objects){
            html += recursive_create_item_info_content_item(c.package_id);
        }
    }
    else { //type == 'DATA'
        html += '<div class="content_element package_info_data"><div class="package_info_data_icon"/><span>' + item.name + '</span><span class="package_info_data_info">'+ item.data_object_metadata.file_type+'</span';
    }
}

function hide_popup() {
    $('#package_manager_main_form').show();
    $('#right_sidebar').show();
    $('#popupForm').hide();
}

function display_popup() {
    $('#package_manager_main_form').hide();
    $('#right_sidebar').hide();
    $('#popupForm').show();
}


function select_deselect_item(clicked) {
    if($(clicked).hasClass('selected')){
        $(clicked).removeClass('selected');
    }
    else {
        $(clicked).addClass('selected');
    }
}

function move_selected_to_package() {
    var selected = $('#package_options_container').find('.selected');
    $(selected).parent().appendTo('#package_content_container');
    $(selected).removeClass('selected');
    if(selected.length > 0) {
        unsaved = true;
    }
}

function remove_selected_from_package() {
    var selected = $('#package_content_container').find('.selected');
    $(selected).parent().appendTo('#package_options_container');
    $(selected).removeClass('selected');
    if(selected.length > 0) {
        unsaved = true;
    }
}

function save_package_object() {
    var package_data = get_active_package();
    console.log("package_data");
    console.log(package_data);
    interface_packages_put(package_data, function(){
        get_user_packages();
        update_sidebar_user_packages();
        unsaved = false;
    });
}

function get_active_package() {
    var output = {};
    output.name = $('#package_manager_form_header').find('#package_name').val();
    console.log($('#package_manager_form_header').find('#package_name').val());
    output.package_id = $('#package_manager_form_header').attr('package_id');
    output.type = "PACKAGE";
    output.description = $('#package_manager_form_header').find('#package_description').val();
    output.child_data_objects = [];
    var content = $('#package_content_container').children('.container_subitem');
    for (let c of content) {
        output.child_data_objects.push($(c).attr('package_id'));

    }
    console.log("output");
    console.log(output);
    return output;
}

function delete_package(clicked) {
        if(confirm("Are you sure that you want to delete this package? This can not be undone!")){
        var c_str = getLocalStorage("user_packages");
        clicked_id = $(clicked).attr('package_id');
        cookie_data = JSON.parse(c_str);
        var delete_set = cookie_data.find(set=>set.package_id == clicked_id);
        interface_packages_delete(delete_set, function (){
            get_user_packages();
            update_sidebar_user_packages();
        });
    }
}