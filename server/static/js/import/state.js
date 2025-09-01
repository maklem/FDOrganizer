import {reactive} from '../vue.js';
import { get, post } from "../http.js"
import { loginSource, getSessionToken, logoutSource } from '../authentication.js';
import {store as editStore} from '../package-edit/state.js'

const AUTH_TYPES = {
    password: 'USERNAME_AND_PASSWORD',
    APIKey: 'API_KEY'
}
export const store = reactive({
    sources: [],
    documents: [],
    selectedDocuments: [],
    remotePath:[],
    folders: [],
    activeSource: undefined,
    username: undefined,
    password: undefined,
    APIKey: undefined,
    failedLogin: false,
    loading: {
        content: false,
        sources: false,
        authentication: false
    },
    setPassword,
    setUsername,
    setAPIKey,
    getFolders,
    resetContent,
    resetPath,
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
    logout,
    showImportButtons,
    AUTH_TYPES
});
/**
 * @param  {string} sourceId
 * @param  {string} collectionId
 * @returns {Promise<ImportFile[]>}
 */
async function getFolderContent(sourceId, folderId) {
    store.loading.content = true
    try {
        const content = await get(`/import/${sourceId}/${folderId}`)
        store.folders = content.folders
        store.documents = content.documents
    } catch (error) {
        if (error.status === 401) {
            await store.logout(sourceId)
        }
    }
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
    
    store.setUsername(undefined)
    store.setPassword(undefined)
}

function setPassword(password) {
    store.password = password
    store.failedLogin = false
}

function setUsername(username) {
    store.username = username
    store.failedLogin = false
}


function setAPIKey(value) {
    store.APIKey = value
    store.failedLogin = false
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
     try {
        const content = await get(`/import/${sourceId}`)
        store.folders = content.folders
        store.documents = content.documents
    } catch (error) {
        if (error.status === 401) {
            await store.logout(sourceId)
        }
    }
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

function resetPath() {
    store.remotePath = []
}

async function authenticate(sourceId, authType) {
    store.loading.authentication = true
    const {username, password, APIKey} = {...store}
    try {
        if (authType === AUTH_TYPES.password) await loginSource(sourceId, {username, password})
        if (authType === AUTH_TYPES.APIKey) await loginSource(sourceId, {APIKey})
    } catch {
        store.failedLogin = true
        store.loading.authentication = false
        return
    }
    store.setUsername(undefined)
    store.setPassword(undefined)
    store.setAPIKey(undefined)
    store.sources = store.sources.map(source => ({...source, authenticated: source.id === sourceId ? true : source.authenticated}))
    store.loading.authentication = false
    store.getSource(sourceId)
}

async function logout(sourceId) {
    store.loading.authentication = true
    await logoutSource(sourceId)
    store.sources = store.sources.map(source => ({...source, authenticated: source.id === sourceId ? false : source.authenticated}))
    store.resetContent()
    store.resetPath()
    store.loading.authentication = false
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
     try {
        await post(`/import/${store.activeSource}`, {
            parent,
            parentType,
            sourceIds
        })
        await editStore.getPackageContent()
    } catch (error) {
        if (error.status === 401) {
            await store.logout(store.activeSource)
        }
    }
    
}

async function getContent() {
    store.loading.content = true
    resetContent()
    if (!store.remotePath.length) await getSource(store.activeSource)
    else await getFolderContent(store.activeSource, store.remotePath.at(-1).id)
    store.loading.content = false
}