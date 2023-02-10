import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";

import {store} from './state.js'
import {editStore} from "../package-edit/state.js"
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
            store,
            editStore
        }
    },

async mounted() {
        this.store.getPackages()

        const params = new URLSearchParams(location.search);
        const documentId = params.get("document");
        console.log(!!documentId)
        if (!!documentId) this.editStore.openDocument(documentId)
    },
    methods: {
    },
    template
})
pkg.provide("editable", false)
pkg.mount('#app-container')