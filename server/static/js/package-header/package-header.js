import { setup } from "../setup.js";
import Button from '../button/button.js';
import {store} from "../package/state.js";
const template = await setup('package-header');

export default {
    components: {
        Button
    },
    data() {
        return {
            store: store
        }
    },
    methods: {
        back() {
            this.store.climbPackagePath()
        }
    },
    template
}