import { post } from "./http.js"

/**
 * @param  {string} username
 * @param  {string} password
 * @returns {Promise<void>}
 */
export async function login(username, password) {
	const json = await post('/login', { username, password })
	if (!json.success) return false
	setCookie("token", json.token);
	window.history.go();
	return true
}
/**
 * @returns {Promise<void>}
 */
export function logout() {
	setCookie("token", '');
	window.history.go();
}

/**
 * @param  {string} cname
 * @param  {string} cvalue
 */
function setCookie(cname, cvalue) {
	document.cookie = cname + "=" + cvalue + ";path=/";
}

function getCookie(cname) {
	let name = cname + "=";
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(';');
	for(let i = 0; i <ca.length; i++) {
	  let c = ca[i];
	  while (c.charAt(0) == ' ') {
		c = c.substring(1);
	  }
	  if (c.indexOf(name) == 0) {
		return c.substring(name.length, c.length);
	  }
	}
	return "";
}

export function getSessionToken() {
	const payload = getCookie('token').split('.')[1];
	return JSON.parse(atob(payload))
}

export async function loginSource(source, credentials) {
	const json = await post(`/import/${source}/login`, credentials)
	setCookie("token", json.token);
}

export async function login_oidc_response(url = 'Null') {
	const state = getCookie('state')
	const json = await post('/login_oidc', {url, state} );
	if (!json.success) return false;
	setCookie("token", json.token);
	
	window.history.go();
	return true;
}

export async function login_oidc_request() {
	const json = await get('/login_oidc');
	setCookie("state", json.state)
	window.location.href = json.redirect;
}