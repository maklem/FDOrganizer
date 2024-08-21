import { createApp } from "../vue.js";
import App from "../app/app.js";
import ArchiveListItem from "../archive-list-item/archive-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import Metadata from "../metadata/metadata.js"
import ArchivePackageSettings from "../archive-package-settings/archive-package-settings.js"


import {store, STATUS} from './state.js'
import {store as metadataStore} from "../metadata/state.js"
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
            STATUS
        }
    },
    mounted() {
        this.store.getPackages()

        const params = new URLSearchParams(location.search);
        const packageId = params.get("package");
        if (!!packageId) return this.store.openSettings(packageId)
     },
    methods: {
    },
    template
})

archive.mount('#app-container')