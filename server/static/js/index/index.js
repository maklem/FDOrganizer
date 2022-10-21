import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
import App from "../app/app.js";
import { setup } from "../setup.js";

const template = await setup('index');

createApp({
    components: {
        App
    },
    template
}).mount('#app-container')