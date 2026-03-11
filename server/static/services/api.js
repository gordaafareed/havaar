export const api = {
    async getStatus() { return _get('/api/status') },
    async getCalls() { return _get('/api/calls') },
    async getContacts() { return _get('/api/contacts') },

    async markListened(sid) { return _post(`/api/calls/${sid}/listened`) },
    async setLabel(safeId, label) { return _post(`/api/contacts/${safeId}/label`, { label }) },

    async uploadOutbound(safeId, blob) { return _uploadAudio(`/api/outbound/${safeId}`, blob) },
    async uploadDefault(blob) { return _uploadAudio('/api/outbound/default', blob) },
    async deleteOutbound(safeId) { return _delete(`/api/outbound/${safeId}`) },
    async deleteDefault() { return _delete('/api/outbound/default') },

    async logout() { return _post('/logout') },

    incomingUrl: (filename) => `/api/audio/incoming/${filename}`,
    outboundUrl: (safeId) => `/api/audio/outbound/${safeId}.wav`,
    defaultUrl: () => `/api/audio/outbound/default.wav`,
}

async function _get(url) {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`GET ${url} → ${res.status}`)
    return res.json()
}

async function _post(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: body ? { 'Content-Type': 'application/json' } : {},
        body: body ? JSON.stringify(body) : undefined,
    })
    if (!res.ok) throw new Error(`POST ${url} → ${res.status}`)
    return res.json()
}

async function _delete(url) {
    const res = await fetch(url, { method: 'DELETE' })
    if (!res.ok) throw new Error(`DELETE ${url} → ${res.status}`)
    return res.json()
}

async function _uploadAudio(url, blob) {
    const form = new FormData()
    form.append('audio', blob, 'recording.webm')
    const res = await fetch(url, { method: 'POST', body: form })
    if (!res.ok) throw new Error(`UPLOAD ${url} → ${res.status}`)
    return res.json()
}
