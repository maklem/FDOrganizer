import {reactive} from '../vue.js';
import {post} from "../http.js"
import { store as editStore } from '../package-edit/state.js'

export const store = reactive({
    files: [],
    draggedFiles: [],
    failedUploads: [],
    error: [],
    loading: {
        upload: false
    },
    startUpload,
    removeFile,
    addFilesFromDragging,
    displayFiles
});

function displayFiles() {
    let total_size = editStore.limits.current_size
    return store.files.map(file => {
        let error = ""
        if(file.size > editStore.limits.file){
             error="File exceeds file size limit"
        }else{
            total_size += file.size
            if(total_size > editStore.limits.package){
                error="File exceeds package limit"
            }
        }
        return {
            name: file.name,
            type: file.type,
            size: file.size,
            error: error,
        }
    })
}
async function startUpload() {
    store.error = []
    store.loading.upload = true
    try {
        const uploads = await uploadFiles()
        store.failedUploads = uploads.failed
        
        store.files = store.files.filter(file => store.failedUploads.map(upload => upload.file).includes(file.name))

        if(store.failedUploads.length > 0){
            store.error = store.failedUploads.map(e => e.file + " → " + e.error)
        }
    } catch (error) {
	    store.failedUploads = store.files
        store.error = [String(error)]
    } finally {
        await editStore.getPackageContent()
        store.loading.upload = false
    }
}

async function uploadFiles() {
    const {parent, parentType} = editStore.currentPath()
    const response = {"failed": []}
    
    for(const file of store.files){
        const body = new FormData()
        body.append('parent', parent)
        body.append('parentType', parentType)
        body.append(file.name, file)
        try{
            let reply = await post('/package/documents', body, {"Content-Type": 'multipart/form-data'})
            reply.failed.forEach(filename => {
                response.failed.push({
                    "file": filename,
                    "error": "upload rejected by server.",
                })
            })
        }
        catch (error) {
            response.failed.push({"file": file.name, "error": String(error)})
            continue
        }
    }
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
