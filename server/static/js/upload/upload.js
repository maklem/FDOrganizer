import Button from "../button/button.js";
import UploadFile from "../upload-file/upload-file.js";
import VideoDialog from "../video-dialog/video-dialog.js";
import { formatFilesize } from "../format-util.js";
import { store } from "./state.js"
import { store as editStore } from '../package-edit/state.js'
import { setup } from "../setup.js";

const template = await setup('upload');

export default {
    components: {
        Button,
        UploadFile,
        VideoDialog
    },
    data() {
        return {
            store,
            editStore,
            formatFilesize
        }
    },
    computed: {
        dialogText() {
            if (this.store.loading.upload) return `Currently uploading ${this.store.files.length} files!`
            if (this.store.failedUploads.length) return `Upload finished! ${this.store.failedUploads.length} files could not be uploaded!`
            return `Do you really want to upload ${this.store.files.length} selected files?`
        }
    },
    methods: {
        selectFiles(event) {
            const files = [...event.currentTarget.files]
            this.store.files.push(...files);
        },
        /**
         * @param {DragEvent} event
         */
        addFileProxy(event) {
            event.preventDefault();

            this.store.draggedFiles = [...event.dataTransfer.items]
                ?.filter(item => item.kind === 'file');
        },
        /**
         * @param {DragEvent} event
         */
        removeFileProxy(event) {
            event.preventDefault();


            this.store.draggedFiles = []
        },
        /**
         * @param {DragEvent} event
         */
        dropFiles(event) {
            event.preventDefault();

            this.store.draggedFiles = []
            this.store.addFilesFromDragging(event);
        },
        closeDialog() {
            this.$refs.uploadFiles.close()
            this.store.failedUploads = []
            this.store.error = ""
        },
        async startUpload() {
            await this.store.startUpload()
            if (!this.store.failedUploads.length && !this.store.error.length) this.closeDialog()
        }
    },
    template
}