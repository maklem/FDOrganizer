import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
import { store as overviewStore } from '../package/state.js'
import Button from '../button/button.js';
const template = await setup('package-header');

export default {
    components: {
        Button
    },
    data() {
        return {
            store,
            overviewStore
        }
    },
    inject: ['editable'],
    methods: {
        back() {
            if(this.editable) this.store.climbPackagePath()
            else this.overviewStore.climbPackagePath()
        }
    },
    template
}