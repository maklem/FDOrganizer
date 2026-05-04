import { setup } from "../setup.js";
import { store } from "./state.js";

const template = await setup('navbar-whoami');

export default {
    props: {
    },
    computed: {
    },
    data() {
        return {
            store
        }
    },
    mounted() {
        this.$nextTick().then(store.loadUserInfo);
    },
    template
}
