import { createApp } from "vue";
import { createI18n } from 'vue-i18n'
import Button from "../button/button.js";
import { setup } from "../setup.js";
import { store } from "./state.js";
import TopBanner from "../top-banner/top-banner.js";
import LabeledInput from "../labeled-input/labeled-input.js";
import Footer from "../footer/footer.js";
import LocaleSwitch from "../locale-switch/locale-switch.js";

import de from "/static/locale/de.json" with { type: "json" }
import en from "/static/locale/en.json" with { type: "json" }


const template = await setup('login');

const i18n = createI18n({
    locale: "de",
    globalInjection: true,
    messages: {
        de, en
    }
});

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
}).use(i18n).mount('#app-container')
