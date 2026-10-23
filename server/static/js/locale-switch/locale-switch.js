import { setup } from "../setup.js";

const template = await setup('locale-switch');

// Native language names, intentionally not translated.
const languageNames = {
    de: "Deutsch",
    en: "English",
};

export default {
    data() {
        return {
            open: false,
        };
    },
    computed: {
        languages() {
            return this.$i18n.availableLocales.map(code => ({
                code,
                name: languageNames[code] ?? code,
            }));
        }
    },
    mounted() {
        document.addEventListener("click", this.closeOnOutsideClick);
    },
    beforeUnmount() {
        document.removeEventListener("click", this.closeOnOutsideClick);
    },
    methods: {
        closeOnOutsideClick(event) {
            if (!this.$el.contains(event.target)) {
                this.open = false;
            }
        },
        closeMenu() {
            this.open = false;
            this.$refs.toggle.focus();
        },
        selectLanguage(locale) {
            this.$i18n.locale = locale;
            this.updateLanguage();
            this.open = false;
            this.$refs.toggle.focus();
        },
        updateLanguage() {
            localStorage.setItem("language", this.$i18n.locale);
        }
    },
    template
}
