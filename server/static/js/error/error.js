import { createApp } from "vue";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";
import {store} from "./state.js";
import { vue_i18n } from "../i18n.js";

const template = await setup('error');

createApp({
    components: {
        TopBanner
    },
    data() {
        return {
            store
        }
    },
    async mounted() {
        const errorMessages = window.errorMessages;
        store.setErrorMessages(errorMessages);
    },
    template
}).use(vue_i18n).mount('#app-container')
