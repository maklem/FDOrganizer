import {reactive} from '../vue.js';
import {post} from "../http.js"
import { store as editStore } from '../package-edit/state.js'

export const store = reactive({
    files: [],
    draggedFiles: [],
    failedUploads: [],
    error: "",
    loading: {
        upload: false
    },
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
    store.error = ""
    store.loading.upload = true
    try {
        const uploads = await uploadFiles()
        store.failedUploads = uploads.failed
        
        store.files = store.files.filter(file => store.failedUploads.map(upload => upload.file).includes(file.name))
    } catch (error) {
	    store.failedUploads = store.files
        store.error = String(error)
    } finally {
        await editStore.getPackageContent()
        store.loading.upload = false
    }
}

async function uploadFiles() {
    const {parent, parentType} = editStore.currentPath()
    const response = {"failed": []}
    
    store.files.forEach(file => {
        const body = new FormData()
        body.append('parent', parent)
        body.append('parentType', parentType)
        body.append(file.name, file)
        try{
            const reply = await post('/package/documents', body, {"Content-Type": 'multipart/form-data'})
        }
        catch {
            response.failed.append(file.name)
            return
        }
        reply.failed.forEach(filename => {
            response.failed.append(filename)
        })
    })
    return response
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
