import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
import { store as metadataStore} from '../metadata/state.js'
import Button from "../button/button.js";
const template = await setup('package-content-folder');

export default {
    components: {
        Button
    },
    props: {
        id: String,
        name: String,
        size: Number,
        count: Number
    },
    inject:['editable'],
    data() {
        return {
            store,
            metadataStore
        }
    },
    methods: {
        deleteFolder(id) {
            this.store.deleteFolder(id)
            this.$refs.folderDelete.close()
        }
    },
    template
}