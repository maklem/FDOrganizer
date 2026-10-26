import {reactive} from 'vue';

export const store = reactive({
    errorMessages: [],
    setErrorMessages,
});

function setErrorMessages(value) {
    console.log(value)
    store.errorMessages = value
}