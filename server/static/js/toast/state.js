import {reactive, nextTick} from '../vue.js';

export const store = reactive({
    messages: [],
    active: undefined,
    addMessage,
    next
});

function addMessage(type, text) {
    if (store.active === undefined) store.active = {type, text}
    else store.messages.push({type, text})
}

async function next() {
    store.active = undefined
    await nextTick()
    const nextActive = store.messages.length ? store.messages.shift() : undefined
    store.active = nextActive
}
