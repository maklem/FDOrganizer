import {reactive} from 'vue';
import { get, post } from '../http.js';

export const store = reactive({
    organisations: [],
    selectedOrganisation: undefined,
    username: undefined,
    password: undefined,
    failedLogin: false,
    loading: {
        button: false,
        organisations: false
    },
    consent: "",
    setPassword,
    setUsername,
    loginOIDC,
    loginKeycloak,
    loginLocal,
    getOrganisations,
    selectOrganisation,
    loadConsent
});

async function loadConsent() {
    let json = await get("/info/consent")
    store.consent = json.html
}

async function getOrganisations() {
    store.loading.organisations = true;
    store.organisations = await get('/organisations');
    store.selectedOrganisation = store.organisations[0];
    store.loading.organisations = false;
}

function selectOrganisation(organisationId) {
    store.selectedOrganisation = store.organisations.find(organisation => organisation.id === organisationId)
}

function setUsername(value) {
    store.username = value
    store.failedLogin = false
}

function setPassword(value) {
    store.password = value
    store.failedLogin = false
}

async function loginLocal() {
    const {username, password} = store
    try {
        await post(`/login-local/${store.selectedOrganisation.id}`, { username, password })
        window.history.go();
    } catch {
        store.failedLogin = true;
    }
}

async function loginOIDC() {
    const response = await get(`/login-oidc/${store.selectedOrganisation.id}`);
    window.location.href = response.auth_url
}

async function loginKeycloak() {
    const response = await get(`/login-keycloak/${store.selectedOrganisation.id}`);
    window.location.href = response.auth_url
}
