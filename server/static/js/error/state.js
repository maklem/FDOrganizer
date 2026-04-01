import {reactive} from '../vue.js';

export const store = reactive({
    errorMessages: [],
    setErrorMessages,
});

function setErrorMessages(value) {
    console.log(value)
    store.errorMessages = value
}