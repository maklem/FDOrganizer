import { setup } from "../setup.js";
import {formatFilesize} from '../format-util.js';

const template = await setup('package-content-document');

export default {
    props: {
        name: String,
        id: String,
        size: Number,
        sourceName: String,
        type: String
    },
    components: {
    },
    data() {
        return {
        }
    },
    methods: {
    },
    computed: {
        icon() {
            switch (this.type) {
                case 'application/pdf':
                case 'pdf':
                    return 'file-pdf'
                case 'application/octet-stream':
                case 'application/octet-stream':
                    return 'file-binary'
                case 'image/avif':
                case 'image/bmp':
                case 'image/gif':
                case 'image/jpeg':
                case 'image/png':
                case 'png':
                    return 'file-image'
                case 'text/csv':
                case 'csv':
                    return 'file-csv'
                case 'docx':
                    return 'file-word'
                default:
                    return 'file-lines'
            }
        },
        formattedSize() {
            return formatFilesize(this.size)
        }
    },
    template
}