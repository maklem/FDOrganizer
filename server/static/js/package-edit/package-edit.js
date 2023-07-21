import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import PackageContent from "../package-content/package-content.js";
import Button from "../button/button.js";
import Upload from "../upload/upload.js";
import Import from "../import/import.js"
import Metadata from "../metadata/metadata.js";
import LabeledInput from "../labeled-input/labeled-input.js"
import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('package-edit');

const packageEdit = createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContent,
        LabeledInput,
        Upload,
        Import,
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

        this.store.checkMetadataParameters()
    },
    methods: {
        enterPressed(event) {
            if (event.which !== 13) return
            this.store.createFolder()
            this.$refs.newFolder.close()
        }
    },
    template
})

packageEdit.provide("editable", true)
packageEdit.mount('#app-container')