import { createApp } from "vue";
import { createI18n } from 'vue-i18n'
import Button from "../button/button.js";
import { setup } from "../setup.js";
import { store } from "./state.js";
import TopBanner from "../top-banner/top-banner.js";
import LabeledInput from "../labeled-input/labeled-input.js";
import Footer from "../footer/footer.js";
import LocaleSwitch from "../locale-switch/locale-switch.js";

import { vue_i18n } from "../i18n.js";

const template = await setup('login');

createApp({
    components: {
        TopBanner,
        Button,
        LabeledInput,
        Footer,
        LocaleSwitch
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
}).use(vue_i18n).mount('#app-container')
