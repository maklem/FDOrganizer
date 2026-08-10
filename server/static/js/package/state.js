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
    newPackage: {
        name: '',
        keepEmpty: false,
        keepStructure: false
    },
    createPackage,
    deletePackage,
    getPackages,
    selectPackage,
    openDetails,
    climbPackagePath,
    uploadZip,
    changePackageName,
    setNewPackageName
});

function openDetails() {
    location.assign(`${location.origin}${location.pathname}/${store.selectedPackage.id}`)
}

async function getPackages() {
    store.loading.packageList = true
    store.packages = await get(`package/all`)
    store.packages.sort((p1, p2) => {
        return p1.keep_until - p2.keep_until
    })
    store.loading.packageList = false
}

async function createPackage() {
    store.loading.packageList = true
    const created = await put(`package`, {name: store.newPackage.name})
    store.newPackage.name = ''
    await store.getPackages()
    store.selectPackage(created.id)
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
    body.append('keep_empty', store.newPackage.keepEmpty)
    body.append('keep_structure', store.newPackage.keepStructure)
    const result =  await put('/package/zip', body, {"Content-Type": 'multipart/form-data'})
    store.zipfile = undefined
    await store.getPackages()
    store.selectPackage(result.id)
    store.loading.packageList = false
    return result
}

async function changePackageName(id, newName) {
   store.loading.packageList = true
   await patch(`package/${id}/rename`, {name: newName})
   await store.getPackages()
   store.loading.packageList = false
}

function setNewPackageName(value) {
    console.log(value)
    store.newPackage.name = value
}