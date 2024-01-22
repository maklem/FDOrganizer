import { createApp } from "../vue.js";
import Button from "../button/button.js";
import { setup } from "../setup.js";
import { store } from "./state.js";
import TopBanner from "../top-banner/top-banner.js";
import LabeledInput from "../labeled-input/labeled-input.js";


const template = await setup('login');

createApp({
    components: {
        TopBanner,
        Button,
        LabeledInput
    },
    data() {
        return {
            store
        }
    },
    computed: {
        organisations() {
            return store.organisations.map(organisation => ({id: organisation.id, label: organisation.name}))
        }
    },
    async mounted() {
        await store.getOrganisations()
    },
    template
}).mount('#app-container')