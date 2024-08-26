import { createApp } from "../vue.js";
import App from "../app/app.js";
import ArchiveListItem from "../archive-list-item/archive-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import Metadata from "../metadata/metadata.js"
import ArchivePackageSettings from "../archive-package-settings/archive-package-settings.js"


import {store, STATUS} from './state.js'
import {store as metadataStore} from "../metadata/state.js"
import {store as settingsStore} from "../archive-package-settings/state.js"
import { setup } from "../setup.js";

const template = await setup('archive');

const archive = createApp({
    components: {
        App,
        Button,
        ArchiveListItem,
        PackageContent,
        ArchivePackageSettings,
        Metadata
    },
    data() {
        return {
            store,
            metadataStore,
            settingsStore,
            STATUS
        }
    },
    mounted() {
        this.store.getPackages()
     },
    methods: {
    },
    template
})
archive.provide("pageContext", "archive")
archive.mount('#app-container')
archive.config.globalProperties.console = console