import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";

import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('package');

const pkg = createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContent
    },
    data() {
        return {
            store
        }
    },

async mounted() {
        this.store.getPackages()
    },
    methods: {
    },
    template
})
pkg.provide("editable", false)
pkg.mount('#app-container')