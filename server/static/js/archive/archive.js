import { createApp } from "../vue.js";
import App from "../app/app.js";
import ArchiveListItem from "../archive-list-item/archive-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import Metadata from "../metadata/metadata.js"

import {store, STATUS} from './state.js'
import {store as editStore} from "../package-edit/state.js"
import { setup } from "../setup.js";

const template = await setup('archive');

const archive = createApp({
    components: {
        App,
        Button,
        ArchiveListItem,
        PackageContent,
        Metadata
    },
    data() {
        return {
            store,
            editStore,
            STATUS
        }
    },
    mounted() {
        this.store.getPackages()

        const params = new URLSearchParams(location.search);
        const documentId = params.get("document");
        if (!!documentId) this.editStore.openDocument(documentId)
    },
    methods: {
    },
    template
})

archive.provide("archive", true)
archive.mount('#app-container')