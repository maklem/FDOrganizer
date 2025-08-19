import Button from "../button/button.js";
import { setup } from "../setup.js";
const template = await setup('video-dialog');

export default {
    components: {
        Button
    },
    props: {
        video: String,
        title: String
    },
    data() {
        return {
        thumbnailUrl: this.videoUrl,
        dialogOpen: false
        }
    },
    computed: {
        videoUrl() {
            return '/static/videos/' + this.video + '.mp4'
        },
        subtitleUrl() {
            return '/static/videos/' + this.video + '.vtt'
        }
    },
    methods: {
        openDialog() {
        this.dialogOpen = true
        this.$refs.dialog.showModal()
        },
        closeDialog() {
        this.dialogOpen = false
        this.$refs.video.pause()
        this.$refs.dialog.close()
        }
    },
    template
}