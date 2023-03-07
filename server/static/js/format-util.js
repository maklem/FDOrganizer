/**
 * @param  {number} bytes
 */
export function formatFilesize(bytes) {
    if (bytes === undefined) return ''
    return new Intl.NumberFormat('de-DE', {
        style: 'unit',
        maximumFractionDigits: 1,
        unit: getUnit(bytes)
    }).format(divide(bytes))
}
/**
 * @param  {number} bytes
 */
function getUnit(bytes) {
    if (bytes > 1000000000) return 'gigabyte';
    if (bytes > 1000000) return 'megabyte';
    if (bytes > 1000) return 'kilobyte';
    return 'byte';
}
/**
 * @param  {number} bytes
 */
function divide(bytes) {
    if (bytes > 1_000_000_000) return bytes / 1_000_000_000;
    if (bytes > 1_000_000) return bytes / 1_000_000;
    if (bytes > 1000) return bytes / 1_000;
    return bytes;
}

export function filetypeIcon(type) {
    switch (type) {
        case 'application/pdf':
        case 'pdf':
            return 'file-pdf'
        case 'application/octet-stream':
            return 'file-binary'
        case 'image/avif':
        case 'image/bmp':
        case 'image/gif':
        case 'image/jpeg':
        case 'image/png':
        case 'image/svg+xml':
        case 'image/tiff':
        case 'png':
            return 'file-image'
        case 'audio/aac':
        case 'audio/midi':
        case 'audio/x-midi':
        case 'audio/wav':
        case 'audio/mpeg':
        case '.aac':
        case '.midi':
        case '.mid':
        case '.mp3':
        case '.wav':
            return 'file-audio'
        case 'text/csv':
        case 'csv':
            return 'file-csv'
        case 'docx':
            return 'file-word'
        default:
            return 'file-lines'
    }
}

export function localized(text) {
    if (text instanceof Object) return text['en']
    return text
}