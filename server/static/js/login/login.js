import { createApp } from "../vue.js";
import { login } from "../authentication.js";
import Button from "../button/button.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";


const template = await setup('login');

createApp({
    components: {
        TopBanner,
        Button
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
        async login(event) {
            event.preventDefault();
            if (! await login(this.username, this.password)) this.setLoginFailed()
        },
        setLoginFailed() {
            this.showErrorText = true
        }
    },
    template
}).mount('#app-container')