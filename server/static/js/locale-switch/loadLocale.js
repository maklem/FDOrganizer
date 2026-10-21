import { createI18n } from "vue-i18n";

import de from "/static/locale/de.json" with { type: "json" }
import en from "/static/locale/en.json" with { type: "json" }

const ls_language = localStorage.getItem("language")
const language = ls_language ? ls_language : "en";

const i18n = createI18n({
    locale: language,
    fallbackLocale: "de",
    globalInjection: true,
    messages: {
        de, en
    }
});

export { i18n as vue_i18n };
