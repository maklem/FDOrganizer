import {reactive} from '../vue.js';
import {post} from "../http.js"
import { store as editStore } from '../package-edit/state.js'

export const store = reactive({
    files: [],
    draggedFiles: [],
    failedUploads: [],
    loading: {
        upload: false
    },
    dialogText: undefined,
    startUpload,
    removeFile,
    addFilesFromDragging,
    displayFiles
});

function displayFiles() {
    return store.files.map(file => {
        return {
            name: file.name,
            type: file.type,
            size: file.size
        }
    })
}
async function startUpload() {
    store.loading.upload = true
    store.dialogText = `Currently uploading ${store.files.length} files!`
    
    const uploads = await uploadFiles()

    await editStore.getPackageContent()

    const failedUploads = uploads.failed
    if (failedUploads.length)
        store.dialogText = `Upload finished! ${failedUploads.length} files could not be uploaded!`
    else store.dialogText = undefined
    
    store.files = store.files.filter(file => failedUploads.map(upload => upload.file).includes(file.name))
    store.loading.upload = false
}

async function uploadFiles() {
    const {parent, parentType} = editStore.currentPath()
    const body = new FormData()
    body.append('parent', parent)
    body.append('parentType', parentType)

    store.files.forEach(file => {
        body.append(file.name, file)
    })
    return await post('/package/documents', body, {"Content-Type": 'multipart/form-data'})
}

function removeFile(name) {
    store.files = store.files.filter(file => file.name !== name);
}

function addFilesFromDragging(event) {
    const files = [...event.dataTransfer.items]
        ?.filter(item => item.kind === 'file')
        .map(item => item.getAsFile())
        ?? [...event.dataTransfer.files];

    store.files.push(...files)
}