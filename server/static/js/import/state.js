import {reactive} from '../vue.js';
import { get, post } from "../http.js"
import { loginSource, getSessionToken } from '../authentication.js';
import {store as editStore} from '../package-edit/state.js'


export const store = reactive({
    sources: [],
    documents: [],
    selectedDocuments: [],
    remotePath:[],
    folders: [],
    activeSource: undefined,
    username: undefined,
    password: undefined,
    loading: {
        content: false,
        sources: false,
        authentication: false
    },
    getFolders,
    resetContent,
    toggleSelectFile,
    getFolderContent,
    activateSource,
    climbRemotePath,
    importSelected,
    importAll,
    openFolder,
    pathNames,
    getSources,
    getSource,
    authenticate,
    showImportButtons
});
/**
 * @param  {string} sourceId
 * @param  {string} collectionId
 * @returns {Promise<ImportFile[]>}
 */
async function getFolderContent(sourceId, folderId) {
    store.loading.content = true
    const content = await get(`/import/${sourceId}/${folderId}`)
    store.folders = content.folders
    store.documents = content.documents
    store.loading.content = false
}

function getFolders() {
    return store.folders
    .map(folder => ({...folder, count: folder.documents.length + folder.folders.length}))
}

function showImportButtons() {
    if(!store.activeSource) return false
    return store.sources.find(source => source.id === store.activeSource).authenticated
    
}

function toggleSelectFile(documentId) {
    const fileToSelect = store.documents.find(document => document.source_id === documentId)
    if (!fileToSelect) return
    if (store.selectedDocuments.find(document => document.source_id === documentId)) 
        return store.selectedDocuments = store.selectedDocuments.filter(document => document.source_id !== documentId)
    
    store.selectedDocuments.push(fileToSelect)
}

function resetContent() {
    store.documents = []
    store.folders = []
    store.selectedDocuments = []
}

function activateSource(sourceId) {
    if (store.activeSource === sourceId) return
    store.resetContent()
    store.remotePath = []
    if (store.sources.find(source => source.id === sourceId).authenticated) store.getSource(sourceId)
    store.activeSource = sourceId
}

async function getSource(sourceId) {
    store.loading.content = true
    let content = await get(`/import/${sourceId}`)
    store.folders = content.folders
    store.documents = content.documents
    store.loading.content = false
}

async function getSources() {
    store.loading.sources = true
    const sources = await get('/import/sources')
    const token = getSessionToken()
    store.sources = sources.map(source => ({...source, authenticated: !!token[source.id]}))
    store.loading.sources = false
    if (!!store.activeSource) await getContent()
}

function pathNames() {
    return store.remotePath.map(path => path.name)
}

async function openFolder(folderId) {
    const folder = store.folders.find(folder => folder.id === folderId)
    store.remotePath.push(folder);
    resetContent()
    getFolderContent(this.activeSource, folderId)
}

async function climbRemotePath() {
    store.remotePath.pop()
    getContent()
}

async function authenticate(sourceId) {
    store.loading.content = true
    const {username, password} = {...store}
    await loginSource(sourceId, {username, password})
    store.username = undefined
    store.password = undefined
    store.sources = store.sources.map(source => ({...source, authenticated: source.id === sourceId ? true : source.authenticated}))
    store.getSource(sourceId)
    store.loading.content = false
}

async function importSelected() {
    store.loading.content = true
    const sourceIds = store.selectedDocuments.map(document => document.source_id)

    await importDocuments(sourceIds)
    store.selectedDocuments = []
    store.loading.content = false
}

async function importAll(){
    store.loading.content = true
    const sourceIds = store.documents.map(document => document.source_id)

    await importDocuments(sourceIds)
    store.loading.content = false
}
async function importDocuments(sourceIds) {
    const {parent,parentType} = editStore.currentPath()

    await post(`/import/${store.activeSource}`, {
        parent,
        parentType,
        sourceIds
    })
    await editStore.getPackageContent()
    
}

async function getContent() {
    store.loading.content = true
    resetContent()
    if (!store.remotePath.length) await getSource(store.activeSource)
    else await getFolderContent(store.activeSource, store.remotePath.at(-1).id)
    store.loading.content = false
}