import {reactive} from '../vue.js';

export const store = reactive({
    package: undefined,
    loading: {
        content: false,
    },
    content: {
        folders: [],
        documents: [],
    },
    modalOpen:false,
    packagePath: [],
    climbPackagePath,
    createFolder,
    currentPath,
    deleteDocument,
    deleteFolder,
    folders,
    getPackage,
    getPackageContent,
    openFolder,
    openDocument,
    closeDocument,
    pathNames
});

function openDocument(documentId) {
    history.pushState({document: documentId}, '', `?document=${documentId}`)
    addEventListener('popstate', function close() {
        store.closeDocument()
        removeEventListener('popstate', close)
    })
    store.modalOpen = true
}

function closeDocument() {
    history.pushState({document: null}, '', `${location.origin}${location.pathname}`)
    store.modalOpen = false
}

function pathNames() {
    return store.packagePath.map(path => path.name)
}

function folders() {
    return store.content.folders
    .map(folder => ({...folder, count: folder.documents.length + folder.folders.length, content: {folders: folder.folders, documents: folder.documents}}))
}

async function getPackage(packageId) {
    const response = await fetch(`/package/${packageId}/content`, {method: 'GET'})
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    store.package = json.package
    store.content = json
    store.packagePath = []
}

async function getFolder(folderId) {
    const response = await fetch(`/folder/${folderId}/content`, {method: 'GET'})
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    store.content = json
}

async function openFolder(id) {
    const folder = store.content.folders.find(folder => folder.id === id)
    store.packagePath.push(folder);
    resetContent()
    getPackageContent()
}

async function climbPackagePath() {
    if (!store.packagePath.length)
        return location.assign(`${location.origin}/package`)
    store.packagePath.pop()
    resetContent()
    getPackageContent()
}

function resetContent() {
    store.content = {
        folders: [],
        documents:[]
    };
}

async function getPackageContent() {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    if (parentType === "package") await getPackage(parent)
    else await getFolder(parent)
    store.loading.content = false
}

async function createFolder(name) {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    const response = await fetch(`/package/folder`, {
        headers: {
            "Content-Type": "application/json"
        },
        method: 'PUT',
        body: JSON.stringify({
            name,
            parent,
            parentType
        })
    });
    const json = await response.json()
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    await getPackageContent()
    store.loading.content = false
}

async function deleteDocument(id) {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    const response = await fetch(`/package/document/${id}`, {
        headers: {
            "Content-Type": "application/json"
        },
        method: 'DELETE',
        body: JSON.stringify({
            parent,
            parentType
        })
    });
    const json = await response.json()
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    await getPackageContent()
    store.loading.content = false
}

async function deleteFolder(id) {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    const response = await fetch(`/package/folder/${id}`, {
        headers: {
            "Content-Type": "application/json"
        },
        method: 'DELETE',
        body: JSON.stringify({
            parent,
            parentType
        })
    });
    const json = await response.json()
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    await getPackageContent()
    store.loading.content = false
}

function currentPath() {
    if(store.packagePath.length)
        return {
            parentType: "folder",
            parent: store.packagePath.at(-1).id
        }
    return {
        parentType: "package",
        parent: store.package.id
    }
}