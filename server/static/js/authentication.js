import { post, get } from "./http.js"
import { userStore } from "./user/userStore.js";

export async function logout() {
	await fetch(`/logout`, {method: "POST"}).then(
		response => window.location = response.url
	)
}

export async function loginSource(source, credentials) {
	await post(`/import/${source}/login`, credentials)
	await userStore.loadUserInfo();
}

export async function logoutSource(source) {
	await post(`/import/${source}/logout`)
	await userStore.loadUserInfo();
}