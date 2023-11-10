import {reactive} from '../vue.js';
import {get, post} from "../http.js"
import {store as editStore} from '../package-edit/state.js'
import {store as settingsStore} from '../archive-package-settings/state.js'

export const STATUS = [
    {
        id: "active",
        name: "Active",
        icon: "fa-user"
    },
    {
        id: "review",
        name: "Review",
        icon: 'fa-list-check'
    },
    {
        id: "archived",
        name: "Archived",
        icon: 'fa-lock'
    }
] 

export const store = reactive({
    packages: [],
    selectedPackage: undefined,
    loading: {
        packageList: false,
    },
    modalOpen:false,
    getPackages,
    selectPackage,
    climbPackagePath,
    openSettings,
    closeSettings,
    packagesWithStatus,
    exportPackage
});

function packagesWithStatus(status) {
        return store.packages.filter(pkg => pkg.status === status)
}

async function getPackages() {
    store.loading.packageList = true
    store.packages = await get(`archive/packages`)
    store.packages.sort((p1, p2) => {
        return p2.last_changed - p1.last_changed
    })
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

function openSettings(packageId) {
    history.pushState({package: packageId}, '', `?package=${packageId}`)
    addEventListener('popstate', function close() {
        store.closeSettings()
        removeEventListener('popstate', close)
    })
    const settingsPackage = store.packages.find(pkg => pkg.id === packageId)
    settingsStore.setPackage(settingsPackage)
    store.modalOpen = true
}

function closeSettings() {
    history.pushState({package: null}, '', `${location.origin}${location.pathname}`)
    settingsStore.package = undefined
    store.modalOpen = false
}

async function exportPackage() {
    const request = post(`/export/${store.selectedPackage.id}`)
    store.selectedPackage = undefined
    await request;
    store.getPackages()
}