import { post, get } from "./http.js"

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
	document.cookie = cname + "=" + cvalue + ";path=/;SameSite=Strict";
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

export async function logoutSource(source) {
	const json = await post(`/import/${source}/logout`)
	setCookie("token", json.token);
}