import {reactive} from '../vue.js';
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
    setPassword,
    setUsername,
    loginLDAP,
    loginOIDC,
    loginSAML,
    getOrganisations,
    selectOrganisation
});

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

async function loginLDAP() {
    const {username, password} = store
    try {
        await post(`/login-ldap/${store.selectedOrganisation.id}`, { username, password })
        window.history.go();
    } catch {
        store.failedLogin = true;
    }
}

async function loginOIDC() {
    get(`/login-oidc/${store.selectedOrganisation.id}`);
}

async function loginSAML() {
    // TODO
    // get(`/login-saml/${store.selectedOrganisation.id}`);
    try {
        const json = await post(`/login-ldap/${store.selectedOrganisation.id}`, { username: 'test', password: "asdfsdfasd" })
        window.history.go();
    } catch {
        store.failedLogin = true;
    }
}
