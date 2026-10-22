import { createApp } from "vue";
import App from "../app/app.js";
import { setup } from "../setup.js";
import VideoDialog from "../video-dialog/video-dialog.js"
import { vue_i18n } from "../i18n.js";

const template = await setup('index');

const TUTORIALS = {
    manage: [
        {
            header: "index.tutorial.manage.createProject.header",
            title: "index.tutorial.manage.createProject.title",
            video: "HowToAddAProject"
        },
        {
            header: "index.tutorial.manage.createFolder.header",
            title: "index.tutorial.manage.createFolder.title",
            video: "HowToEdit_CreateFolder"
        },
        {
            header: "index.tutorial.manage.uploadFiles.header",
            title: "index.tutorial.manage.uploadFiles.title",
            video: "HowToEdit_FileUpload"
        },
        {
            header: "index.tutorial.manage.importFiles.header",
            title: "index.tutorial.manage.importFiles.title",
            video: "HowToEdit_FileImport",

        },
    ],
    metadata: [
        {
            header: "index.tutorial.metadata.openMetadata.header",
            title: "index.tutorial.metadata.openMetadata.title",
            video: "HowToAddMetadata",
        },
        {
            header: "index.tutorial.metadata.addMetadata.header",
            title: "index.tutorial.metadata.addMetadata.title",
            video: "HowToAddMetadata_Form",
        }
    ],
    archive: [
        {
            header: "index.tutorial.archive.archiveProject.header",
            title: "index.tutorial.archive.archiveProject.title",
            video: "HowToArchive_Active"
        },
        {
            header: "index.tutorial.archive.reviseProject.header",
            title: "index.tutorial.archive.reviseProject.title",
            video: "HowToArchive_Rework"
        }
    ]
};
        
createApp({
    components: {
        App,
        VideoDialog
    },
    data(){
        return {
            tutorials: TUTORIALS
        }
    },
    template
}).use(vue_i18n).mount('#app-container')