import { createApp } from "../vue.js";
import App from "../app/app.js";
import Button from "../button/button.js";
import { formatFilesize } from "../format-util.js";
import { setup } from "../setup.js";
import UploadFile from "../upload-file/upload-file.js";

const template = await setup('upload');

createApp({
    components: {
        App,
        Button,
        UploadFile
    },
    data() {
        return {
            files: [],
            fileProxy: undefined,
            failedUploads: [],
            uploadInProgress: false
        }
    },
    methods: {
        openDialog() {
            const dialog = document.getElementsByTagName('dialog')[0]
            dialog.showModal()
        },
        closeDialog() {
            const dialog = document.getElementsByTagName('dialog')[0]
            this.failedUploads = []
            dialog.close()
        },
        /**
         * @param  {Event} event
         */
        selectFiles(event) {
            const files = [...event.currentTarget.files]
            this.files.push(...files);
        },
        /**
         * @param {DragEvent} event
         */
        addFileProxy(event) {
            event.preventDefault();

            const transferItems = [...event.dataTransfer.items]
                ?.filter(item => item.kind === 'file');

            this.fileProxy = {
                name: `+ ${transferItems.length} files`,
                icon: 'file-lines',
                proxy: true
            }
        },
        /**
         * @param {DragEvent} event
         */
        removeFileProxy(event) {
            event.preventDefault();


            this.fileProxy = undefined
        },
        /**
         * @param {DragEvent} event
         */
        dropFiles(event) {
            event.preventDefault();

            const files = extractFiles(event)

            this.fileProxy = undefined;
            this.files.push(...files);
        },
        /**
         * @param {string} name
         */
        removeFile(name) {
            this.files = this.files.filter(file => file.name !== name);
        },
        prepareFile(file) {
            return {
                name: file.name,
                size: formatFilesize(file.size),
                icon: getIcon(file.type),
            };
        },
        async startUpload() {
            this.uploadInProgress = true;
            this.failedUploads = await upload(this.files)
            this.files = this.files.filter((file) => this.failedUploads.map(promise => promise.value).includes(file.name))
            if (!this.failedUploads?.length) this.closeDialog();
            this.uploadInProgress = false;
        }
    },
    template
}).mount('#app-container')
/**
 * @param  {File} file
 */
function getIcon(filetype) {
    switch (filetype) {
        case 'application/pdf':
            return 'file-pdf'
        case 'application/octet-stream':
            return 'file-binary'
        case 'image/avif':
        case 'image/bmp':
        case 'image/gif':
        case 'image/jpeg':
        case 'image/png':
            return 'file-image'
        case 'text/csv':
            return 'file-csv'
        default:
            return 'file-lines'
    }
}
/**
 * @param  {DragEvent} event
 * @returns {File[]}
 */
function extractFiles(event) {
    return [...event.dataTransfer.items]
        ?.filter(item => item.kind === 'file')
        .map(item => item.getAsFile())
        ?? [...event.dataTransfer.files];
}

/**
 * @typedef CustomFile
 * @type {object}
 * @property {string} name
 * @property {string} size
 * @property {boolean} [proxy]
 * @property {string} icon
 */
/**
 * @param  {File} file
 * @param  {boolean} ephemereal
 * @returns {CustomFile} CustomFile
 */


async function upload(files) {
    const promises = files.map(file => {
        const body = new FormData()
        body.append('file', file)
        return fetch('upload/file', {
            method: 'POST',
            body
        })
        .then(response => response.json())
        .then(json => json.file)
    })
    return Promise.allSettled(promises).then((promiseArray) => {
        return promiseArray
        .filter(promise => promise.status === 'rejected')
    })
}
