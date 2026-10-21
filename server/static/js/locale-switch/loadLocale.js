import { createI18n } from "vue-i18n";

import de from "/static/locale/de.json" with { type: "json" }
import en from "/static/locale/en.json" with { type: "json" }


const i18n = createI18n({
    locale: "de",
    globalInjection: true,
    messages: {
        de, en
    }
});

export { i18n as vue_i18n };
