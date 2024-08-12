import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
import Button from '../button/button.js';
const template = await setup('package-header');

export default {
    components: {
        Button
    },
    data() {
        return {
            store
        }
    },
    inject: ['editable', 'archive'],
    methods: {
    },
    template
}