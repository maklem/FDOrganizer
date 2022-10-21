import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
import { login } from "../authentication.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";


const template = await setup('login');

createApp({
    components: {
        TopBanner
    },
    data() {
        return {
            username: '',
            password: '',
            showErrorText: false
        }
    },
    methods: {
        setUsername(event) {
            this.username = event.currentTarget.value
            this.showErrorText = false
        },
        setPassword(event) {
            this.password = event.currentTarget.value
            this.showErrorText = false
        },
        login(event) {
            event.preventDefault();
            if (!login(this.username, this.password)) this.setLoginFailed()
        },
        setLoginFailed() {
            this.showErrorText = true
        }
    },
    template
}).mount('#app-container')