import {reactive} from '../vue.js';
import {patch, get, put, dlt} from "../http.js"

const TABS = [
    {
        id: 'access',
        title: 'Access'
    },
    {
        id: 'legal',
        title: 'Legal'
    },
    {
        id: 'reviews',
        title: 'Reviews'
    }
]
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
        packageSettings: false,
        reviews: false
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
    reviews: [],
    currentReview: undefined,
    currentComment: "",
    modalRef: undefined,
    activeTab: 'access',
    reviewReadonly: false,
    settingsReadonly: false,
    readyToSaveSettings,
    savePackageSettings,
    setPackage,
    openSettings,
    closeSettings,
    addComment,
    deleteComment,
    LICENSES,
    TABS
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
        findability = '',
        accessibility = '',
        embargodate = undefined,
        licenseType = '',
        licenseTiming = '',
        contactemail = undefined,
        checkDuration = false,
        duration = undefined,
        checkDSGVO = false,
        checkTerms = false,
        personalData = '',
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
    ((store.licenseType === 'gdl' && !!store.germandatalicense) || (store.licenseType === 'cc' && !!store.creativecommons)) &&
    (store.accessibility === 'embargo' ? !!store.embargodate : true) &&
    (store.accessibility === 'request' ? !!store.contactemail : true)
}

async function getReviews(pkg) {
    store.loading.reviews = true
    const reviews = await get(`/review/${pkg.id}`)
    store.reviews = reviews.filter(review => review.status !== 'open')
    store.reviews.sort((r1, r2) => r2.creation_date - r1.creation_date)
    store.currentReview = reviews.find(review => review.status === 'open')
    store.loading.reviews = false
}

function reset() {
    store.settingsReadonly = false
    store.reviewReadonly = false
    store.activeTab = 'access'
}

function openSettings(settingsPackage, tab = 'access', settingsReadonly = false, reviewReadonly = false) {
    store.loading.reviews = true
    getReviews(settingsPackage)
    setPackage(settingsPackage)
    store.activeTab = tab
    store.settingsReadonly = settingsReadonly
    store.reviewReadonly = reviewReadonly
    store.modalRef.showModal()

}

function closeSettings() {
    store.package = undefined
    store.modalRef.close()
    reset()
}

async function addComment() {
    if (!store.currentComment) return
    const comment = {
        content: store.currentComment,
    }
    if (!store.currentReview) {
        comment.index = 1
        await addReview({comments: [comment]})
    } else {
        comment.index = store.currentReview.comments.length + 1
        const new_comment = await put(`/review/${store.currentReview.id}/comment`, comment)
        store.currentReview.comments.push(new_comment)
    }
    store.currentComment = ""
}

async function addReview(comments = undefined) {
    const review = await put(`/review/${store.package.id}`, comments)
    store.currentReview = review
}

async function deleteComment(index) {
    store.loading.reviews = true
    await dlt(`/review/${store.currentReview.id}/${index}`)
    store.currentReview.comments = store.currentReview.comments.filter(comment => comment.index !== index)
    store.loading.reviews = false
}