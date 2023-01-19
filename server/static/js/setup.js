async function getTemplate(component) {
    const url = `/static/js/${component}/${component}.html`
    return fetch(url).then(response => response.text());
}

async function getStyles(component) {
    return new Promise((resolve) => {
        const styles = document.createElement('link');

        styles.setAttribute('href', `/static/js/${component}/${component}.css`);
        styles.setAttribute('type', 'text/css');
        styles.setAttribute('rel', 'stylesheet');
        styles.onload = () => resolve();
        document.getElementsByTagName('head')[0].appendChild(styles)
    });
}

export async function setup(component) {
    return Promise.all([getTemplate(component), getStyles(component)]).then(promises => { return promises[0]; });
}