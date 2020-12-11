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
            fragmente.push('<li><strong>', f.name, '</strong> (', f.type || 'n/a',
                ') - ', f.size, ' bytes</li>');
        }
        console.log(files);
        // Alle Fragmente im fragmente Array aneinanderhängen, in eine unsortierte Liste einbetten
        // und das alles als HTML-Inhalt in das output-Elements mit id='dateiListe' einsetzen.
        console.log(fragmente);
        document.getElementById('dateiListe')
            .innerHTML = '<ul>' + fragmente.join('') + '</ul>';
    }
    // UI-Events erst registrieren wenn das DOM bereit ist!
document.addEventListener("DOMContentLoaded", function () {
    // Falls neue Eingabe, neuer Aufruf der Auswahlfunktion
    document.getElementById('dateien')
        .addEventListener('change', dateiauswahl, false);
});

const form = document.querySelector('form');

form.addEventListener('submit', (e) => {
  e.preventDefault();

  // const files = document.querySelector('[type=file]').files;
  // console.log(files);
  const formData = new FormData(formElem);

  // for (let i = 0; i < files.length; i++) {
  //   let file = files[i];

  //   formData.append('upload_files', file);
  // }
  upload_files(formData);
});

function upload_files(data) {
    var url = baseURL + '/test/upload';
    xhttp.onreadystatechange = function(e) {
        if (this.readyState == 4) {
            if (this.status == 200) {
                
            }
        }
    };
    xhttp.open('POST', url, false);
    // xhttp.setRequestHeader("Content-type", "multipart/form-data");
    xhttp.send(data);
}

// formElem.onsubmit = async (e) => {
//     e.preventDefault();

//     let response = await fetch('/test/upload', {
//       method: 'POST',
//       body: new FormData(formElem)
//     });

//     let result = await response.json();

//     alert(result.message);
//   };