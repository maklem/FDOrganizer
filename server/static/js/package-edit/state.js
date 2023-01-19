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
    packagePath: [],
    getPackage,
    createFolder,
    openFolder,
    climbPackagePath,
    pathNames,
    folders,
});

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
    store.package = json
    resetContent()
    if(!store.package.folders.length && !store.package.documents.length) return
    getPackageContent(store.package.folders, store.package.documents)
}

async function openFolder(id) {
    const folder = store.content.folders.find(folder => folder.id === id)
    store.packagePath.push(folder);
    resetContent()
    getPackageContent(folder.folders, folder.documents)
}

async function climbPackagePath() {
    if (!store.packagePath.length)
        return location.assign(`${location.origin}/package`)
    store.packagePath.pop()
    resetContent()
    let folders, documents;
    if (store.packagePath.length) {
        folders = store.packagePath.at(-1).folders
        documents = store.packagePath.at(-1).documents
    } else {
        folders = store.package.folders
        documents = store.package.documents
    }
    getPackageContent(folders, documents)
}

function resetContent() {
    store.content = {
        folders: [],
        documents:[]
    };
}

async function getPackageContent(folders, documents) {
    store.loading.content = true
    const response = await fetch('/package/content', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            folders,
            documents
        })
    })
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    store.content = json
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

    const folders = [...store.content.folders.map(folder => folder.id), json.id]
    const documents = store.content.documents.map(document => document.id)
    await getPackageContent(folders, documents)
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