import { setup } from "../setup.js";
import {formatFilesize, filetypeIcon} from '../format-util.js';

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
            formatFilesize,
            filetypeIcon
        }
    },
    methods: {
    },
    template
}