import { createApp } from "../vue.js";
import App from "../app/app.js";
import ReviewListItem from "../review-list-item/review-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import Metadata from "../metadata/metadata.js"
import ArchivePackageSettings from "../archive-package-settings/archive-package-settings.js"


import {store, STATUS} from './state.js'
import {store as metadataStore} from "../metadata/state.js"
import {store as settingsStore} from "../archive-package-settings/state.js"
import { setup } from "../setup.js";

const template = await setup('review');

const review = createApp({
    components: {
        App,
        Button,
        ReviewListItem,
        PackageContent,
        Metadata,
        ArchivePackageSettings
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
review.provide("pageContext", "review")
review.mount('#app-container')