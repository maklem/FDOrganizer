import { createApp } from "../vue.js";
import App from "../app/app.js";
import { setup } from "../setup.js";
import VideoDialog from "../video-dialog/video-dialog.js"

const template = await setup('index');

const TUTORIALS = {
    manage: [
        {
            header: "Creating projects",
            title: "How to create a project",
            video: "HowToAddAProject"
        },
        {
            header: "Creating folders",
            title: "How to add folders",
            video: "HowToEdit_CreateFolder"
        },
        {
            header: "Uploading files",
            title: "How to add files to a project",
            video: "HowToEdit_FileUpload"
        },
        {
            header: "Importing files",
            title: "How to import files from external sources",
            video: "HowToEdit_FileImport",

        },
    ],
    metadata: [
        {
            header: "Opening metadata",
            title: "How to add metadata to a project",
            video: "HowToAddMetadata",
        },
        {
            header: "Adding metadata",
            title: "How to add metadata",
            video: "HowToAddMetadata_Form",
        }
    ],
    archive: [
        {
            header: "Archiving projects",
            title: "How to archive a project",
            video: "HowToArchive_Active"
        },
        {
            header: "Revising projects",
            title: "How to rework a reviewed project",
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
}).mount('#app-container')