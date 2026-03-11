export function relTime(iso) {
    const d = new Date(iso + 'Z')
    const diff = Date.now() - d
    if (diff < 60000) return 'just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return d.toLocaleDateString()
}

export function fmtSecs(s) {
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

export function safeName(caller) {
    return caller.replace(/\W/g, '')
}

export function randomBars(count = 40) {
    return Array.from({ length: count }, () => ({
        height: 4 + Math.random() * 18
    }))
}
