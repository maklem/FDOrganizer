import { setup } from "../setup.js";

const template = await setup('locale-switch');

export default {
    methods: {
        updateLanguage() {
            localStorage.setItem("language", this.$i18n.locale); 
        }
    },
    template
}
