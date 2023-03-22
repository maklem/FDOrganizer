import {reactive} from '../vue.js';
import {put, get, dlt} from "../http.js"


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
    activeTab: 'upload',
    newFolderName: undefined,
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
    const json = await get(`/package/${packageId}/content`)
    store.package = json.package
    store.content = json
    store.packagePath = []
}

async function getFolder(folderId) {
    const json = await get(`/folder/${folderId}/content`)
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

async function createFolder() {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    console.log(store.newFolderName)
    await put(`/package/folder`, {
        name: store.newFolderName,
        parent,
        parentType
    });

    await getPackageContent()
    store.newFolderName = undefined
    store.loading.content = false
}

async function deleteDocument(id) {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    await dlt(`/package/document/${id}`, {
        parent,
        parentType
    });

    await getPackageContent()
    store.loading.content = false
}

async function deleteFolder(id) {
    store.loading.content = true
    const {parent, parentType} = currentPath()
    await dlt(`/package/folder/${id}`,{
        parent,
        parentType
    });

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