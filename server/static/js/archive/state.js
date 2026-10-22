import {reactive} from 'vue';
import {get, post} from "../http.js"
import {store as editStore} from '../package-edit/state.js'
import {store as statusStore} from "../status-dialog/state.js"
import { vue_i18n } from "../locale-switch/loadLocale.js"

export const STATUS = [
    {
        id: "active",
        name: "Active",
        icon: "fa-user"
    },
    {
        id: "review",
        name: "In Review",
        icon: 'fa-list-check'
    },
    {
        id: "rework",
        name: "Needs Rework",
        icon: 'fa-wrench'
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
    packagesWithStatus,
    requestReview,
    metadataReadonly,
    settingsReadonly,
    openDetails
});

function packagesWithStatus(status) {
        return store.packages.filter(pkg => pkg.status === status)
}

function openDetails() {
    location.assign(`${location.origin}/package/${store.selectedPackage.id}`)
}

async function getPackages() {
    store.loading.packageList = true
    store.packages = await get(`archive/packages`)
    store.packages.sort((p1, p2) => {
        return p1.keep_until - p2.keep_until
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
    statusStore.openDialog(vue_i18n.global.t('archive.submitPending'), 'ok', [])

    const request = post(`/archive/submit/${store.selectedPackage.id}`)
    const response = await request;

    if(response.status == 'ok') {
        statusStore.closeDialog()
        store.selectedPackage = undefined
    }else
    if(response.status == 'error') {
        statusStore.openDialog(vue_i18n.global.t('archive.submitFailed'), 'error', response.details)
    }else{
        statusStore.openDialog(vue_i18n.global.t('archive.submitFailed'), 'error', [vue_i18n.global.t('archive.connectionFailed'), vue_i18n.global.t('archive.tryAgainLater')])
    }
    store.getPackages()
}

function metadataReadonly(pkg) {
    return ['review', 'archived'].includes(pkg.status)
}

function settingsReadonly(pkg) {
    return ['review', 'archived'].includes(pkg.status)
}