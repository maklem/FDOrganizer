import {reactive} from '../vue.js';

export const store = reactive({
    packages: [],
    selectedPackage: undefined,
    loading: {
        packageList: false,
        details: false,
        overview: false,
    },
    content: {
        documents: [],
        folders: []
    },
    packagePath: [],
    createPackage,
    deletePackage,
    getPackages,
    selectPackage,
    openFolder,
    climbPackagePath,
    pathNames,
    folders
});

function pathNames() {
    return store.packagePath.map(path => path.name)
}

function folders() {
    return store.content.folders
    .map(folder => ({...folder, count: folder.content.documents.length}))
}

async function getPackages() {
    store.loading.packageList = true
    const response = await fetch(`package/all`, {method: 'GET'})
    console.log(response)
    const json = await response.json()
    console.log(json)
    store.packages = json
    store.loading.packageList = false
}

async function createPackage(name) {
    store.loading.packageList = true
    const response = await fetch(`package`, {
        headers: {
            "Content-Type": "application/json"
        },
        method: 'PUT',
        body: JSON.stringify({name: name})
    });
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    const pkg = await response.json()
    console.log('created package', pkg)
    await store.getPackages()
    store.loading.packageList = false
}

async function deletePackage(id) {
    console.log('deleted', id)
    store.loading.packageList = true
    const response = await fetch(`package/${id}`, {method: 'DELETE'})
	if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    await store.getPackages()
    store.loading.packageList = false
}

function selectPackage(id) {
    store.selectedPackage = store.packages.find(pkg => pkg.id === id)
    resetContent()
    store.packagePath = [];
    getPackageContent(id);
}

async function openFolder(id, name) {
    store.packagePath.push({
        id,
        name
    });
    resetContent()
    getFolderContent(id)
}

async function climbPackagePath() {
    store.packagePath.pop()
    resetContent()
    if (store.packagePath.length > 0)
        getFolderContent(store.packagePath.at(-1).id)
    else getPackageContent(store.selectedPackage.id)
}

function resetContent() {
    store.content = {
        folders: [],
        documents:[]
    };
}

async function getPackageContent(packageId) {
    store.content = {
        folders: [
            {
                name: "Supplemental_Data",
                id: 1,
                size: 98923998832,
                content: {
                    folders: [3,5],
                    documents: [1,4,5,9]
                }
            },
            {
                name: "images",
                id: 2,
                size: 743384998832,
                content: {
                    folders: [],
                    documents: [1,4,5,9,13,22,35,57,92,149]
                }
            },
        ],
        documents: [
            {
                name: "Dataset_1.csv",
                id: 1,
                size: 19434634,
                sourceName: "Easy DB",
                sourceId: "987234",
                type: "csv"
            },
            {
                name: "Dataset_1_desc.pdf",
                id: 2,
                size: 727345,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "pdf"
            },
            {
                name: "Dataset_2_raw.mat",
                id: 3,
                size: 617343344,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "mat"
            }
        ]
    }
}

async function getFolderContent(folderId) {
    store.content = {
        folders: [
            {
                name: "Supplemental_Data",
                id: 1,
                size: 98923998832,
                content: {
                    folders: [3,5],
                    documents: [1,4,5,9]
                }
            },
        ],
        documents: [
            {
                name: "Image_1.png",
                id: "1",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_2.png",
                id: "2",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_3.png",
                id: "3",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_4.png",
                id: "4",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_5.png",
                id: "5",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_6.png",
                id: "6",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_7.png",
                id: "7",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_8.png",
                id: "8",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_9.png",
                id: "9",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
            {
                name: "Image_10.png",
                id: "10",
                size: 194348,
                sourceName: "Manueller Upload",
                sourceId: undefined,
                type: "png"
            },
        ]
    }
}
