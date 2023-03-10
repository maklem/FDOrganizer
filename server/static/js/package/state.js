import {reactive} from '../vue.js';
import {store as editStore} from '../package-edit/state.js'

export const store = reactive({
    packages: [],
    selectedPackage: undefined,
    loading: {
        packageList: false,
    },
    createPackage,
    deletePackage,
    getPackages,
    selectPackage,
    openDetails,
    climbPackagePath
});

function openDetails() {
    location.assign(`${location.origin}${location.pathname}/${store.selectedPackage.id}`)
}

async function getPackages() {
    store.loading.packageList = true
    const response = await fetch(`package/all`, {method: 'GET'})
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    store.packages = json
    store.loading.packageList = false
}

async function createPackage(name) {
    store.loading.packageList = true
    const response = await fetch(`package`, {
        headers: {
            "Content-Type": "application/json"
        },
        method: 'PUT',
        body: JSON.stringify({name: name})
    });
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    const pkg = await response.json()
    await store.getPackages()
    store.loading.packageList = false
}

async function deletePackage(id) {
    store.loading.packageList = true
    const response = await fetch(`package/${id}`, {method: 'DELETE'})
    const json = await response.json()
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    await store.getPackages()
    if (store.selectedPackage.id === id) store.selectedPackage = undefined
    store.loading.packageList = false
}

async function selectPackage(id) {
    store.selectedPackage = store.packages.find(pkg => pkg.id === id)
    editStore.package = store.selectedPackage
    editStore.getPackage(id);
}

function climbPackagePath() {
    if (!editStore.packagePath.length) store.selectedPackage = undefined
    else editStore.climbPackagePath()
}
