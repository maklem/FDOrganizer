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
            return 'file-circle-question'
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
        case '.mov':
        case '.mp4':
        case '.avi':
        case '.wmv':
        case '.mpeg':
        case 'video/mp4':
        case 'video/mpeg':
        case 'video/webm':
        case 'video/quicktime':
        case 'video/x-ms-wmv':
        case 'video/x-msvideo':
            return 'file-video'
        case 'text/csv':
        case 'csv':
            return 'file-csv'
        case 'application/vnd.ms-excel':
        case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        case '.xls':
        case '.xlsx':
            return 'file-excel'
        case '.html':
        case '.js':
        case '.mjs':
        case '.css':
        case '.r':
        case 'text/css':
        case 'text/html':
        case 'text/javascript':
        case 'application/xhtml+xml':
        case 'application/xml':
        case 'text/xml':
            return 'file-code'
        case '.zip':
        case '.tar':
        case '.gz':
        case '.7z':
        case '.rar':
        case 'application/zip':
        case 'application/x-7z-compressed':
        case 'application/x-tar':
        case 'application/vnd.rar':
            return 'file-code'
        case '.docx':
        case 'application/msword':
        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return 'file-word'
        case 'text/markdown':
        case 'text/plain':
        case '.md':
        case '.txt':
            return 'file-lines'
        default:
            return 'file'
    }
}

export function localized(text) {
    if (text instanceof Object) return text['en']
    return text
}

export function formatRelativeDate(timestamp) {
    const relativeTimeDiff = timestamp - Date.now()
    const outputUnit = unit(relativeTimeDiff)
    if (outputUnit === 'exact') return formatDate(timestamp)

    const format = new Intl.RelativeTimeFormat(navigator.language, {style: 'long', numeric: 'auto'})
    return format.format(Math.ceil(timeIn(outputUnit, relativeTimeDiff)), outputUnit)
}

function unit(millisecondDiff) {
    const absoluteDiff = Math.abs(millisecondDiff)
    if (absoluteDiff < 60_000) return 'second'
    if (absoluteDiff < 3_600_000) return 'minute'
    if (absoluteDiff < 86_400_000) return 'hour'
    if (absoluteDiff < 604_800_000) return 'day'
    if (absoluteDiff < 2_419_200_000) return 'week'
    else return 'exact'
}

function timeIn(unit, milliseconds) {
    switch (unit) {
        case 'second':
            return milliseconds / 1000
        case 'minute':
            return milliseconds / 60_000
        case 'hour':
            return milliseconds / 3_600_000
        case 'day':
            return milliseconds / 86_400_000
        case 'week':
            return milliseconds / 604_800_000
        default:
            return milliseconds
    }
}

export function formatDate(timestamp) {

const date = new Date(timestamp);

const day = date.getDate();
const month = date.getMonth() + 1;
const year = date.getFullYear();

return `${day.toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${year}`
}