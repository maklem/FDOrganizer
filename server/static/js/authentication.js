/**
 * @param  {string} username
 * @param  {string} password
 * @returns {Promise<void>}
 */
export function login(username, password) {
	return fetch('/login', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
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