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
    newFolderName: '',
    metadataEntity: undefined,
    limits: {"current_size": 0, "file": 0, "package": 0},
    climbPackagePath,
    createFolder,
    currentPath,
    deleteDocument,
    deleteFolder,
    folders,
    getPackage,
    getPackageContent,
    openFolder,
    checkMetadataParameters,
    openMetadata,
    closeDocument,
    pathNames
});

function openMetadata(entityType, entityId) {
    history.pushState({[entityType]: entityId}, '', `?${entityType}=${entityId}`)
    addEventListener('popstate', function close() {
        store.closeDocument(entityType)
        removeEventListener('popstate', close)
    })
    store.metadataEntity = entityType
    store.modalOpen = true
}

function closeDocument(entityType) {
    history.pushState({[entityType]: null}, '', `${location.origin}${location.pathname}`)
    store.modalOpen = false
    store.metadataEntity = undefined
}

function checkMetadataParameters() {
    const params = new URLSearchParams(location.search);
    const entityId = getParameter(params)
    if (!!entityId.length) store.openMetadata(entityId[0], entityId[1])
}

function getParameter(params) {
    if (!!params.get('document')) return ["document", params.get('document')]
    if (!!params.get('folder')) return ["folder", params.get('folder')]
    if (!!params.get('package')) return ["package", params.get('package')]
    return []
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
    const limits = await get(`/package/${packageId}/limits`)
    store.limits = limits
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
        return history.back()
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