import { createApp } from "../vue.js";
import App from "../app/app.js";
import PackageListItem from "../package-list-item/package-list-item.js";
import Button from "../button/button.js";
import PackageContent from "../package-content/package-content.js";
import LabeledInput from "../labeled-input/labeled-input.js"
import Metadata from "../metadata/metadata.js"
import VideoDialog from "../video-dialog/video-dialog.js"

import {store} from './state.js'
import {store as metadataStore} from "../metadata/state.js"
import { setup } from "../setup.js";

const template = await setup('package');

const pkg = createApp({
    components: {
        App,
        PackageListItem,
        Button,
        PackageContent,
        Metadata,
        LabeledInput,
        VideoDialog
    },
    data() {
        return {
            store,
            metadataStore,
            source: 'empty',
        }
    },

async mounted() {
        this.store.getPackages()
    },
    methods: {
        createPackage() {
            store.createPackage()
            this.$refs.newPackage.close()
        },
        enterPressed(event) {
            if (event.which !== 13) return
            this.createPackage()
        },
        setZip(event) {
            const zipfile = [...event.currentTarget.files][0]
            this.store.zipfile = zipfile;
        },
        uploadZip() {
            this.$refs.newPackage.close()
            this.store.uploadZip()
        }
    },
    template
})
pkg.provide("editable", false)
pkg.mount('#app-container')