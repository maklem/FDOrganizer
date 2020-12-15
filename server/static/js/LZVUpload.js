function dateiauswahl(evt) {
    // FileList-Objekt des input-Elements auslesen, auf dem 
    // das change-Event ausgelöst wurde (event.target)
    var files = evt.target.files;
    // Deklarierung eines Array Objekts mit Namen "fragmente". Hier werden die Bausteine
    // für die erzeugte Listenausgabe gesammelt.
    var fragmente = [];
    // Zählschleife; bei jedem Durchgang den Namen, Typ und 
    // die Dateigröße der ausgewählten Dateien zum Array hinzufügen
    for (let f of files) {
        fragmente.push('<li><strong>', f.name, '</strong> (', f.type || 'n/a', ') - ', f.size, ' bytes</li>');
    }
    console.log(files);
    // Alle Fragmente im fragmente Array aneinanderhängen, in eine unsortierte Liste einbetten
    // und das alles als HTML-Inhalt in das output-Elements mit id='dateiListe' einsetzen.
    console.log(fragmente);
    document.getElementById('dateiListe').innerHTML = '<ul>' + fragmente.join('') + '</ul>';
}
// UI-Events erst registrieren wenn das DOM bereit ist!
document.addEventListener("DOMContentLoaded", function() {
    // Falls neue Eingabe, neuer Aufruf der Auswahlfunktion
});
const form = document.querySelector('form');
form.addEventListener('submit', (e) => {
    e.preventDefault();
    // const formData = new FormData(formElem);
    upload_files(formData);
});

function upload_files(data) {
    // console.log($('formElem').serialize());
    var url = baseURL + '/test/upload';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {}
        }
    };
    xhttp.open('POST', url, false);
    xhttp.send(data);
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
            form_upload_data.push(input.files[i]);
        }
    }
}

function remove_from_upload_list(clicked) {
    var remove_name = $(clicked).attr('filename');
    form_upload_data.filter(f => f.name != remove_name);
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
    output += '<div class="upload_container_subitem" filename="'+upload_file.name+'">';
    output += '<div class="upload_item" filename="'+upload_file.name+'" onclick="select_deselect_item(this)">';
    output += '<span class="upload_item_description">' + upload_file.name + '</span><br>';
    var size = upload_file.size;
    if (size < 1024) {
        size = String(size) + 'B';
    }
    else if(size < 1048576) { //kB
        size = String(size/1024) + 'kB';
    }
    else { //mB
        size = String(size/1048576) + 'MB';
    }
    output += '<span class="upload_item_sub_description">' + upload_file.type + ' - ' + size + '</span>';
    output += '</div>';
    output += '<button type="button" class="btn remove_upload_item" filename="'+upload_file.name+'" onclick="remove_from_upload_list(this);"> </button>';
    output += '</div>';
    return output;
}


// $('#upload_choose_files_hidden_input').addEventListener('change', append_to_upload_list(), false);
$('#upload_choose_files').click(function() {
    $('#upload_choose_files_hidden_input').click();
    console.log("test");
});