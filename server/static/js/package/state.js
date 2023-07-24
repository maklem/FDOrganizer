import {reactive} from '../vue.js';
import {put, get, dlt} from "../http.js"
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
    store.packages = await get(`package/all`)
    store.loading.packageList = false
}

async function createPackage(name) {
    store.loading.packageList = true
    await put(`package`, {name: name})
    await store.getPackages()
    store.loading.packageList = false
}

async function deletePackage(id) {
    store.loading.packageList = true
    await dlt(`package/${id}`)
    await store.getPackages()
    if (store.selectedPackage?.id === id) store.selectedPackage = undefined
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
