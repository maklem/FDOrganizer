import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
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
            store
        }
    },
    methods: {
        openDialog(event) {
            event.stopPropagation()
            this.$refs.folderDelete.showModal()
        }
    },
    template
}