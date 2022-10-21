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
			setCookie("session_auth", payload.session_id);
			setCookie("session_user", username);
			window.history.go();
		});

}

export function logout() {
	fetch('/logout', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		}
	}).then(() => {
		setCookie("session_auth", '');
		setCookie("session_user", '');
		window.history.go();
	});
}


function setCookie(cname, cvalue) {
	document.cookie = cname + "=" + cvalue + ";path=/";
}