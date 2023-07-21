import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import Metadata from "../metadata/metadata.js"

import {store} from './state.js'
import {store as editStore} from "../package-edit/state.js"
import { setup } from "../setup.js";

const template = await setup('package');

const pkg = createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContent,
        Metadata
    },
    data() {
        return {
            store,
            editStore
        }
    },

async mounted() {
        this.store.getPackages()

        this.editStore.checkMetadataParameters()
    },
    methods: {
    },
    template
})
pkg.provide("editable", false)
pkg.mount('#app-container')