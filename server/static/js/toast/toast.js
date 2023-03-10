import {store} from "./state.js"
import { setup } from "../setup.js";
const template = await setup('toast');

export default {
    components: {
    },
    data() {
        return {
            store
        }
    },
    methods: {
    },
    template
}