import { createApp } from "../vue.js";
import App from "../app/app.js";
import { setup } from "../setup.js";

const template = await setup('index');

createApp({
    components: {
        App
    },
    template
}).mount('#app-container')