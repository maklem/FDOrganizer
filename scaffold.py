import os
import sys


def create_dir(name: str):
    new_directory = os.path.join("./server/static/js", name)
    try:
        os.mkdir(new_directory)
        return new_directory
    except FileExistsError as exception:
        raise FileExistsError(
            f'ERROR! The component {new_directory} already exists') from exception


def scaffold_component(component: str):
    new_directory = create_dir(component)
    create_html(component, new_directory)
    create_component_js(component, new_directory)
    create_css(component, new_directory)


def scaffold_app(app: str):
    new_directory = create_dir(app)
    create_html(app, new_directory)
    create_app_js(app, new_directory)
    create_css(app, new_directory)


def scaffold(entity_type: str):
    type_methods = {
        'component': scaffold_component,
        'app': scaffold_app
    }
    try:
        return type_methods[entity_type]
    except KeyError as exception:
        raise KeyError(
            f'ERROR! {entity_type} is not a valid scaffolding entity') from exception


def create_component_js(component: str, path: str):
    with open(f'{path}/{component}.js', 'w', encoding='utf_8') as file:
        file.write("""import { setup } from "../setup.js";
const template = await setup('%s');

export default {
    components: {
    },
    data() {
        return {
        }
    },
    methods: {
    },
    template
}""" % (component))
    file.close()


def create_html(component: str, path: str):
    with open(f'{path}/{component}.html', 'x', encoding='utf_8') as file:
        file.close()


def create_css(component: str, path: str):
    with open(f'{path}/{component}.css', 'x', encoding='utf_8') as file:
        file.close()


def create_app_js(app: str, path: str):
    with open(f'{path}/{app}.js', 'w', encoding='utf_8') as file:
        file.write("""import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
import App from "../app/app.js";
import { setup } from "../setup.js";

const template = await setup('%s');

createApp({
    components: {
        App
    },
    data() {
        return {
        }
    },
    methods: {
    },
    template
}).mount('#app-container')""" % (app))
    file.close()


if __name__ == '__main__':
    if not sys.argv[1]:
        print(f'Usage: python scaffold-component.py <type=component|app> <name>')
        exit()
    scaffold(sys.argv[1])(sys.argv[2])
