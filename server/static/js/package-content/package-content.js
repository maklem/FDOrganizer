import { setup } from "../setup.js";
import { store } from '../package-edit/state.js'
import PackageContentDocument from "../package-content-document/package-content-document.js";
import PackageContentFolder from "../package-content-folder/package-content-folder.js";
import PackageHeader from "../package-header/package-header.js";
import PackageCheck from "../package-check/package-check.js";
import VideoDialog from "../video-dialog/video-dialog.js";
const template = await setup('package-content');

export default {
    components: {
        PackageContentDocument,
        PackageContentFolder,
        PackageHeader,
        VideoDialog,
        PackageCheck
    },
    data() {
        return {
            store
        }
    },
    methods: {
    },
    template
}