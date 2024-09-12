import {reactive} from '../vue.js';
import {put, get, dlt, patch} from "../http.js"
import {store as editStore} from '../package-edit/state.js'

export const store = reactive({
    packages: [],
    selectedPackage: undefined,
    zipfile: undefined,
    loading: {
        packageList: false,
    },
    createPackage,
    deletePackage,
    getPackages,
    selectPackage,
    openDetails,
    climbPackagePath,
    uploadZip,
    changePackageName
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

async function uploadZip() {
    store.loading.packageList = true
    const body = new FormData()

    body.append(store.zipfile.name, store.zipfile)
    const result =  await put('/package/zip', body, {"Content-Type": 'multipart/form-data'})
    store.zipfile = undefined
    store.getPackages()
    store.loading.packageList = false
    return result
}

async function changePackageName(id, newName) {
   store.loading.packageList = true
   await patch(`package/${id}/rename`, {name: newName})
   await store.getPackages()
   store.loading.packageList = false
}