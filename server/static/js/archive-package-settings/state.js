import {reactive} from '../vue.js';
import {patch, get, put, dlt} from "../http.js"

const TABS = [
    // {
    //     id: 'access',
    //     title: 'Access'
    // },
    {
        id: 'legal',
        title: 'Legal'
    },
    {
        id: 'reviews',
        title: 'Reviews'
    }
]

export const store = reactive({
    loading: {
        packageSettings: false,
        reviews: false
    },
    package: undefined,
    checkDuration: false,
    duration: undefined,
    checkTerms: false,
    checkDSGVO: false,
    personalData: 'none',
    reviews: [],
    currentReview: undefined,
    currentComment: "",
    modalRef: undefined,
    activeTab: 'legal',
    reviewReadonly: false,
    settingsReadonly: false,
    readyToSaveSettings,
    savePackageSettings,
    setPackage,
    openSettings,
    closeSettings,
    addComment,
    deleteComment,
    TABS
});
async function savePackageSettings() {
    store.loading.packageSettings = true
    const settings = (({
        checkDuration,
        duration,
        checkDSGVO,
        checkTerms,
        personalData
    }) => ({
        checkDuration,
        duration,
        checkDSGVO,
        checkTerms,
        personalData
    }))(store)
    
    await patch(`/archive/${store.package.id}/settings`, {settings: settings})
    store.loading.packageSettings = false
    return true
}

function setPackage(pkg) {
    store.loading.packageSettings = true
    store.package = pkg
    const {
        checkDuration = false,
        duration = undefined,
        checkDSGVO = false,
        checkTerms = false,
        personalData = '',
    } = pkg.archive_settings ?? {}
    store.checkDuration = checkDuration
    store.duration = duration
    store.checkDSGVO = checkDSGVO
    store.checkTerms = checkTerms
    store.personalData = personalData
    
    store.loading.packageSettings = false
}

function readyToSaveSettings() {
    return store.checkDuration &&
    store.checkTerms &&
    store.checkDSGVO &&
    !!store.duration &&
    !!store.personalData
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
    store.activeTab = 'legal'
}

function openSettings(settingsPackage, tab = 'legal', settingsReadonly = false, reviewReadonly = false) {
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