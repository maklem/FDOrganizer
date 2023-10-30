import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
import { store as overviewStore } from '../package/state.js'
import { store as archiveStore } from '../archive/state.js'
import Button from '../button/button.js';
const template = await setup('package-header');

export default {
    components: {
        Button
    },
    data() {
        return {
            store,
            overviewStore,
            archiveStore
        }
    },
    inject: ['editable', 'archive'],
    methods: {
    },
    template
}