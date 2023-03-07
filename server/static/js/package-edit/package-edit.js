import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import PackageContent from "../package-content/package-content.js";
import Button from "../button/button.js";
import Upload from "../upload/upload.js";
import Metadata from "../metadata/metadata.js";
import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('package-edit');

const packageEdit = createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContent,
        Upload,
        Metadata
    },
    data() {
        return {
            store
        }
    },
    async mounted() {
        const packageId = location.pathname.split('/').at(-1)
        this.store.getPackage(packageId)

        const params = new URLSearchParams(location.search);
        const documentId = params.get("document");
        if (!!documentId) this.store.openDocument(documentId)
    },
    methods: {
    },
    template
})

packageEdit.provide("editable", true)
packageEdit.mount('#app-container')