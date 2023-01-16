import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import PackageContentDocument from "../package-content-document/package-content-document.js";
import PackageContentFolder from "../package-content-folder/package-content-folder.js";
import Button from "../button/button.js";
import PackageHeader from "../package-header/package-header.js";
import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('package');

createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContentDocument,
        PackageContentFolder,
        PackageHeader,
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
}).mount('#app-container')