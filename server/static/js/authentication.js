/**
 * @param  {string} username
 * @param  {string} password
 * @returns {Promise<void>}
 */
export function login(username, password) {
	return fetch('/login', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		},
		body: JSON.stringify({ username, password })
	})
		.then((response) => response.json(), () => false)
		.then((payload) => {
			setCookie("token", payload.token);
			window.history.go();
		});
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
	const response = await fetch(`/import/${source}/login`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		},
		body: JSON.stringify(credentials)
	})
	const json = await response.json()
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
	setCookie("token", json.token);
}