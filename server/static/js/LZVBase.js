var baseURL = 'http://localhost:5000';
var labFolderToken = '';
var DEBUGlogin = 'robert.guenther@uni-bayreuth.de';
var DEBUGpassword = 'krQ3C3LTjIXFmwcpmEaM';

if (window.XMLHttpRequest) {
    // code for modern browsers
    var xhttp = new XMLHttpRequest();
} else {
    // code for old IE browsers
    var xhttp = new ActiveXObject('Microsoft.XMLHTTP');
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
 