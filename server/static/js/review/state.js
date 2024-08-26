import {reactive} from '../vue.js';
import {get, post} from "../http.js"
import {store as editStore} from '../package-edit/state.js'
import {store as settingsStore} from '../archive-package-settings/state.js'

export const STATUS = [
    {
        id: "review",
        name: "Needs review",
        icon: 'fa-list-check'
    },
    {
        id: "rework",
        name: "Rejected",
        icon: 'fa-wrench'
    },
    {
        id: "archived",
        name: "Accepted",
        icon: 'fa-check'
    }
] 

export const store = reactive({
    packages: [],
    selectedPackage: undefined,
    loading: {
        packageList: false,
    },
    getPackages,
    selectPackage,
    climbPackagePath,
    packagesWithStatus,
    requestReview,
    acceptReview,
    rejectReview
});

function packagesWithStatus(status) {
        return store.packages.filter(pkg => pkg.status === status)
}

async function getPackages() {
    store.loading.packageList = true
    store.packages = await get(`/review/packages`)
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

async function requestReview() {
    const request = post(`/archive/submit/${store.selectedPackage.id}`)
    store.selectedPackage = undefined
    await request;
    store.getPackages()
}

async function acceptReview() {
    const request = post(`/export/${store.selectedPackage.id}`)
    store.selectedPackage = undefined
    await request;
    store.getPackages()
}

async function rejectReview() {
    const request = post(`/reject/${store.selectedPackage.id}`)
    store.selectedPackage = undefined
    await request;
    store.getPackages()
}