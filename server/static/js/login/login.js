import { createApp } from "../vue.js";
import Button from "../button/button.js";
import { setup } from "../setup.js";
import { store } from "./state.js";
import TopBanner from "../top-banner/top-banner.js";
import LabeledInput from "../labeled-input/labeled-input.js";
import Footer from "../footer/footer.js";


const template = await setup('login');

createApp({
    components: {
        TopBanner,
        Button,
        LabeledInput,
        Footer
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
        let consent = store.loadConsent()
        let org = store.getOrganisations()
        await consent, org
    },
    template
}).mount('#app-container')