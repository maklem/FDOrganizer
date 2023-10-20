import { createApp } from "../vue.js";
import { login_oidc_request } from "../authentication.js";
import Button from "../button/button.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";

const template = await setup('test');

createApp({
    components: {
        TopBanner,
        Button
    },
    data() {
        return {
            showErrorText: false
        }
    },
    methods: {
        async login() {
            login_oidc_request()
        },
        setLoginFailed() {
            this.showErrorText = true
        }
    },
    template
}).mount('#app-container')