import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
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
    inject:['editable'],
    data() {
        return {
            store
        }
    },
    methods: {
    },
    template
}