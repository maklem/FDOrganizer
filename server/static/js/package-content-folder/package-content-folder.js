import { setup } from "../setup.js";
import {store} from '../package/state.js'
import { formatFilesize } from "../format-util.js";
const template = await setup('package-content-folder');

export default {
    components: {
    },
    props: {
        id: String,
        name: String,
        size: Number,
        count: Number
    },
    data() {
        return {
        }
    },
    methods: {
        open() {
            store.openFolder(this.id, this.name)
        }
    },
    computed: {
        formattedSize() {
            return formatFilesize(this.size)
        }
    },
    template
}