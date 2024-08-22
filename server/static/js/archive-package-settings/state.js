import {reactive} from '../vue.js';
import {patch} from "../http.js"

const LICENSES = {
    cc: [
        {
            id: 'https://creativecommons.org/publicdomain/zero/1.0/',
            label: 'CC0 1.0 - Public Domain'
        },
        {
            id: 'https://creativecommons.org/licenses/by/4.0/',
            label: 'CC BY 4.0 - Attribution'
        },
        {
            id: 'https://creativecommons.org/licenses/by-sa/4.0/',
            label: 'CC BY-SA 4.0 - Attribution & Share Alike'
        },
        {
            id: 'https://creativecommons.org/licenses/by-nc/4.0/',
            label: 'CC BY-NC 4.0 - Attribution & Non Commercial'
        }
    ],
    gdl: [
        {
            id: 'https://www.govdata.de/dl-de/zero-2-0',
            label: 'dl-zero-de 2.0 - Public Domain'
        },
        {
            id: 'https://www.govdata.de/dl-de/by-2-0',
            label: 'dl-by-de 2.0 - Attribution'
        },
    ]
}
export const store = reactive({
    loading: {
        packageSettings: false
    },
    package: undefined,
    findability: 'open',
    accessibility: 'open',
    embargodate: undefined,
    licenseType: 'cc',
    licenseTiming: 'now',
    creativecommons: undefined,
    germandatalicense: undefined,
    contactemail: undefined,
    checkDuration: false,
    duration: undefined,
    checkTerms: false,
    checkDSGVO: false,
    personalData: 'none',
    modalRef: undefined,
    readyToSaveSettings,
    savePackageSettings,
    setPackage,
    openSettings,
    closeSettings,
    LICENSES
});

async function savePackageSettings() {
    store.loading.packageSettings = true
    const settings = (({
        findability,
        licenseType,
        licenseTiming,
        checkDuration,
        duration,
        checkDSGVO,
        checkTerms,
        personalData
    }) => ({
        findability,
        licenseType,
        licenseTiming,
        checkDuration,
        duration,
        checkDSGVO,
        checkTerms,
        personalData
    }))(store)
    if (settings.licenseType === "gdl") settings.license = store.germandatalicense
    if (settings.licenseType === "cc") settings.license = store.creativecommons
    if (settings.findability === 'open') settings.accessibility = store.accessibility
    if (settings.accessibility === 'embargo') settings.embargodate = store.embargodate
    if (settings.accessibility === 'request') settings.contactemail = store.contactemail
    
    await patch(`/archive/${store.package.id}/settings`, {settings: settings})
    store.loading.packageSettings = false
    return true
}

function setPackage(pkg) {
    store.loading.packageSettings = true
    store.package = pkg
    const {
        findability = 'open',
        accessibility = 'open',
        embargodate = undefined,
        licenseType = 'cc',
        licenseTiming = 'now',
        contactemail = undefined,
        checkDuration = false,
        duration = undefined,
        checkDSGVO = false,
        checkTerms = false,
        personalData = 'none',
        license = undefined
    } = pkg.archive_settings ?? {}
    store.findability = findability
    store.accessibility = accessibility
    store.embargodate = embargodate
    store.licenseType = licenseType
    store.licenseTiming = licenseTiming
    store.contactemail = contactemail
    store.checkDuration = checkDuration
    store.duration = duration
    store.checkDSGVO = checkDSGVO
    store.checkTerms = checkTerms
    store.personalData = personalData

    if (licenseType === 'gdl') store.germandatalicense = license
    if (licenseType === 'cc') store.creativecommons = license
    
    store.loading.packageSettings = false
}

function readyToSaveSettings() {
    return store.checkDuration &&
    store.checkTerms &&
    store.checkDSGVO &&
    !!store.duration &&
    (!!store.creativecommons || store.germandatalicense) &&
    (store.accessibility === 'embargo' ? !!store.embargodate : true) &&
    (store.accessibility === 'request' ? !!store.contactemail : true)
}

function openSettings(settingsPackage) {
    setPackage(settingsPackage)
    store.modalRef.showModal()
}

function closeSettings() {
    store.package = undefined
    store.modalRef.close()
}