import { createApp } from "../vue.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";
import {store} from "./state.js";

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
}).mount('#app-container')
